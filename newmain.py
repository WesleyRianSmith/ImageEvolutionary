import random
import statistics
import multiprocessing
from math import atan2, pi

import numpy
from PIL import Image, ImageDraw, ImageChops
from deap import creator, base, tools, algorithms
MAX = 255 * 200 * 200
TARGET = Image.open("darwin.png")
TARGET.load()  # read image and close the file
def draw(solution,save=False):
    image = Image.new("RGB", (200, 200))
    canvas = ImageDraw.Draw(image, "RGBA")
    for polygon in solution:
        canvas.polygon(polygon[1:], fill=polygon[0])
    if save:
        image.save("solution.png")
    return image

def sort_points(points):
    #if len(points) <= 3:
        #return points
    sum_x = sum([x[0] for x in points])
    sum_y = sum([y[1] for y in points])
    centre_y = sum_y/len(points)
    top_half = [x for x in points if x[1] >= centre_y]
    bottom_half = [x for x in points if x[1] < centre_y]
    top_half.sort(key=lambda x: x[0])
    bottom_half.sort(key=lambda x: x[0],reverse = True)
    return top_half + bottom_half
def evaluate(solution):
    image = draw(solution)
    diff = ImageChops.difference(image, TARGET)
    hist = diff.convert("L").histogram()
    count = sum(i * n for i, n in enumerate(hist))
    return (MAX - count) / MAX,
def mutate(solution, rate):
    # print("-"* 30)
    maximum = 10
    polygon_count = len(solution)
    guassian_amount = 10
    if polygon_count >= 1000:
        guassian_amount = 20
    chance = random.random()
    polygon_index = random.randint(0, len(solution) - 1)
    polygon = solution[polygon_index]
    if chance < 0.5:
        # print("Random point change")

        coords = [x for point in polygon[1:] for x in point]
        tools.mutGaussian(coords, 0, guassian_amount, rate)
        coords = [max(0, min(int(x), 200)) for x in coords]
        polygon[1:] = list(zip(coords[::2], coords[1::2]))

        #coords = [x for x in polygon]
        #print("-" * 20)
        #print(coords)
        #point_index = random.randint(1, len(coords) - 1)
        #random_point = coords[point_index]
        #print(random_point)
        #new_point = tuple([int(x + random.gauss(0, 10)) for x in random_point])
        #coords[point_index] = new_point
        #solution[polygon_index] = coords


    elif chance < 0.8:
        # print("Change colour")

        colors = [x for x in polygon[0]]

        for x in range(3):
            colors[x] = max(0, min(256, int(colors[x] + random.gauss(0, guassian_amount))))
        polygon[0] = tuple(colors)
        colors = [x for x in polygon[0]]
        new_alpha = max(30, min(60, int(colors[3] + random.gauss(0, guassian_amount))))
        colors[3] = new_alpha
        polygon[0] = tuple(colors)

    else:
        # print("Add new polygon")
        if polygon_count < 280:
            solution.append(make_polygon(random.randint(3,5),0.8, 0.1))
        elif polygon_count < 400:
            solution.append(make_polygon(random.randint(3,5),0.4, 0.4))
        elif polygon_count < 1000:
            solution.append(make_polygon(random.randint(3,5),0.2, 0.7))
        else:
            rand = random.random()
            if rand < 0.5:
                random.shuffle(solution)
            else:
                solution.pop(random.randint(0,polygon_count-1))
        #solution.append(make_polygon(random.randint(3, 3),1,0))

    return solution,
def make_polygon(n=3,large_chance=0.3,small_chance=0.3,background_polygon=False):
    # 0 <= R|G|B < 256, 30 <= A <= 60, 10 <= x|y < 190
    color = [random.randint(0, 256) for _ in range(3)]
    color.append(random.randint(30, 60))
    color = [tuple(color)]
    chance = random.random()
    if background_polygon:
        return color + [(0,200),(200,200),(200,0),(0,0)]
    if chance < small_chance:
        coordinates_x = [random.randint(10, 40) for _ in range(n)]
        coordinates_y = [random.randint(10, 40) for _ in range(n)]
    elif chance < large_chance + small_chance:
        coordinates_x = [random.randint(10, 190) for _ in range(n)]
        coordinates_y = [random.randint(10, 190) for _ in range(n)]
    else:
        coordinates_x = [random.randint(80, 190) for _ in range(n)]
        coordinates_y = [random.randint(80, 190) for _ in range(n)]
    max_x = max(coordinates_x)
    max_y = max(coordinates_y)
    min_x = min(coordinates_x)
    min_y = min(coordinates_y)
    x_right_room = 190 - max_x
    y_right_room = 190 - max_y
    x_displacement = random.randint(-min_x+10, x_right_room)
    y_displacement = random.randint(-min_y+10, y_right_room)
    coordinates = []
    for x,y in zip(coordinates_x,coordinates_y):
        coordinates.append((x+x_displacement,y+y_displacement))

    coordinates = sort_points(coordinates)

    return color + coordinates

def create_individual():
    ind = []
    ind.append(make_polygon(1,0,0,True))
    for x in range(3):
        ind.append(make_polygon(3))
    return ind
seed = 120
tournament_size = 10
gaussian_rate = 0.5
population_size = 30
mutation_probability = 0.75
generations = 40000
crossover_probability = 0.7
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)


def run():
    random.seed(seed)


    toolbox = base.Toolbox()
    pool = multiprocessing.Pool(4)
    toolbox.register("map", pool.map)
    toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutate, rate=gaussian_rate)

    toolbox.register("select", tools.selTournament, tournsize=tournament_size)

    population = toolbox.population(n=population_size)
    hof = tools.HallOfFame(3)
    stats = tools.Statistics(lambda x: x.fitness.values[0])
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    stats.register("median", numpy.median)
    stats.register("std", numpy.std)

    population, log = algorithms.eaSimple(population, toolbox,
                                              cxpb=crossover_probability, mutpb=mutation_probability, ngen=generations,
                                              stats=stats, halloffame=hof, verbose=True)
    fittest_individual = max(population, key=lambda individual: individual.fitness.values[0])
    print(len(fittest_individual))
    image = draw(fittest_individual,True)
if __name__ == "__main__":
    image = []
    image.append(make_polygon(1,0,0,True))
    draw(image,True)
    #for x in range(1):
        #image.append(make_polygon(15,1,0))
    #draw(image,True)
    run()