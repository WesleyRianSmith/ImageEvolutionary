from random import randint, random, shuffle, seed
import multiprocessing
import numpy
from PIL import Image, ImageDraw, ImageChops
from deap import creator, base, tools, algorithms

MAX = 255 * 200 * 200
TARGET = Image.open("darwin.png")
TARGET.load()  # read image and close the file


def draw(solution, save=False):
    image = Image.new("RGB", (200, 200))
    canvas = ImageDraw.Draw(image, "RGBA")
    for polygon in solution:
        canvas.polygon(polygon[1:], fill=polygon[0])
    if save:
        image.save("solution.png")
    return image


def sort_points(points):
    sum_y = sum([y[1] for y in points])
    centre_y = sum_y / len(points)  # Define a vertical middle point between all the points
    # Group up all the points based on which half they're in
    top_half = [x for x in points if x[1] >= centre_y]
    bottom_half = [x for x in points if x[1] < centre_y]
    # Sort the top half into ascending order and the bottom half into descending order
    top_half.sort(key=lambda x: x[0])
    bottom_half.sort(key=lambda x: x[0], reverse=True)
    # Return the sorted set of points
    return top_half + bottom_half


def evaluate(solution):
    image = draw(solution)  # Draw the solution as a 200x200 png
    diff = ImageChops.difference(image, TARGET)
    hist = diff.convert("L").histogram()
    count = sum(i * n for i, n in enumerate(hist))
    return (MAX - count) / MAX,


def mutate(solution, rate):
    polygon_count = len(solution)
    gaussian_amount = 10
    if polygon_count >= 100 and (mode == 3):
        gaussian_amount = 20
    chance = random()
    polygon_index = randint(0, len(solution) - 1)
    polygon = solution[polygon_index]
    mutate_point_chance = 0.5
    mutate_add_point_chance = 0.1
    mutate_color_chance = 0.2
    if chance < mutate_point_chance:
        coords = [x for point in polygon[1:] for x in point]
        tools.mutGaussian(coords, 0, gaussian_amount, rate)
        coords = [max(0, min(int(x), 200)) for x in coords]
        polygon[1:] = list(zip(coords[::2], coords[1::2]))
    elif chance < mutate_point_chance + mutate_add_point_chance and len(polygon) < 6 and mode == 1:
        color = polygon[0]
        coords = [point for point in polygon[1:]]
        new_point = (randint(0, 190), randint(0, 190))
        coords.append(new_point)
        coords = sort_points(coords)  # Ensure the new point is in the correct index
        polygon = [color] + coords
        solution[polygon_index] = polygon
    elif chance < mutate_point_chance + mutate_add_point_chance + mutate_color_chance:  # Change the color
        colors = [x for x in polygon[0]]
        tools.mutGaussian(colors, 0, gaussian_amount, rate)
        colors = [max(0, min(int(x), 256)) for x in colors]
        colors[3] = max(0, min(colors[3], 60))
        polygon[0] = tuple(colors)
    else:  # Add/remove/shuffle polygons
        if polygon_count < 100:
            if mode == 1:
                if polygon_count < 25:
                    solution.append(make_polygon(randint(3, 5), 0.8, 0.1))
                elif polygon_count < 50:
                    solution.append(make_polygon(randint(3, 5), 0.4, 0.4))
                else:
                    solution.append(make_polygon(randint(3, 5), 0.1, 0.8))
            else:
                solution.append(make_polygon(3, 0, 0))
        else:
            # Shuffle polygons or remove a random one
            rand = random()
            if rand < 0.5:
                shuffle(solution)
            else:
                solution.pop(polygon_index)

    return solution,


def make_polygon(n=3, large_chance=0.3, small_chance=0.3, background_polygon=False):
    color = [randint(0, 256) for _ in range(3)]
    color.append(randint(30, 60))
    color = [tuple(color)]
    chance = random()
    max_size = 110
    if background_polygon:
        return color + [(0, 200), (200, 200), (200, 0), (0, 0)]
    if chance < small_chance:
        max_size = 40
    elif chance < large_chance + small_chance:
        max_size = 190
    coordinates_x, coordinates_y = [randint(10, max_size) for _ in range(n)], [randint(10, 110) for _ in range(n)]
    max_x, max_y = max(coordinates_x), max(coordinates_y)
    min_x, min_y = min(coordinates_x), min(coordinates_y)
    x_right_room, y_right_room = 190 - max_x, 190 - max_y
    x_displacement, y_displacement = randint(-min_x + 10, x_right_room), randint(-min_y + 10,y_right_room)

    coordinates = []
    for x, y in zip(coordinates_x, coordinates_y):
        coordinates.append((x + x_displacement, y + y_displacement))

    coordinates = sort_points(coordinates)

    return color + coordinates


def create_individual():
    if mode == 1:
        # Returns a background polygons and 3 random polygons
        return [make_polygon(4, 0, 0, True)] + [make_polygon(randint(3, 5)) for _ in range(3)]
    else:
        return [make_polygon(3, 0, 0) for _ in range(3)]


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)


def run(generations, crossover_probability, mutation_probability, random_seed, population_size, gaussian_rate=0.5,
        tournament_size=10, verbose_value=True):
    seed(random_seed)
    toolbox = base.Toolbox()
    pool = multiprocessing.Pool()
    toolbox.register("map", pool.map)
    toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutate, rate=gaussian_rate)
    if mode == 2:
        toolbox.register("select", tools.selBest)
    else:
        toolbox.register("select", tools.selTournament, tournsize=tournament_size)

    population = toolbox.population(n=population_size)
    stats = tools.Statistics(lambda x: x.fitness.values[0])
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    stats.register("median", numpy.median)

    if mode == 3:
        population, log = algorithms.eaSimple(population, toolbox,
                                              cxpb=crossover_probability, mutpb=mutation_probability, ngen=generations,
                                              stats=stats, halloffame=None, verbose=verbose_value)
    else:
        population, log = algorithms.eaMuPlusLambda(population, toolbox, mu=(len(population) // 3),
                                                    lambda_=len(population), cxpb=crossover_probability,
                                                    mutpb=mutation_probability,
                                                    ngen=generations, stats=stats, halloffame=None,
                                                    verbose=verbose_value)

    fittest_individual = max(population, key=lambda individual: individual.fitness.values[0])
    draw(fittest_individual, True)
    for x in list(log):
        if x.get("max") > 0.95:
            generations_needed_amount = x.get("gen")
            return generations_needed_amount

    return generations


def RunParameterTest(generations, crossover_probability, mutation_probability, seed_number, population_size):
    generations_needed = run(generations, crossover_probability, mutation_probability, seed_number,
                             population_size, verbose_value=False)
    if generations_needed < generations:
        print(f"Generations needed are {str(generations_needed)} and mutation probability is {str(mutation_probability)}"
              f" and crossover probability is {str(crossover_probability)} and population is {str(population_size)}")
        generations = generations_needed
    return generations


def TestLambdaParameters(generations, population_size, seed_number):
    for i in range(10):
        mutation_probability = 10 - i
        crossover_probability = 10 - mutation_probability
        generations = RunParameterTest(generations, crossover_probability / 10, mutation_probability / 10, seed_number,
                                       population_size)
    print("Finished testing!")

def TestEaSimpleParameters(generations, population_size, seed_number):
    for i in range(10):
        mutation_probability = 10 - i
        for y in range(10):
            crossover_probability = 10 - y
            generations = RunParameterTest(generations, crossover_probability / 10,
                                           mutation_probability / 10, seed_number,
                                           population_size)
    print("Finished testing!")

def DecrementPopulationTest(generations, population_size, seed_number, mutation_probability, crossover_probability):
    while population_size >= 10:
        generations_needed = run(generations, crossover_probability, mutation_probability, seed_number,
                                 population_size, verbose_value=False)
        if generations_needed < generations:
            print(f"Generations needed are {generations_needed} and population is {population_size}")
            generations = generations_needed
        population_size -= 5
    print("Finished testing!")

mode = 0
seeds = [120, 298, 234, 1212, 3233]
if __name__ == "__main__":
    TestLambdaParameters(3000,30,120)
    pass
