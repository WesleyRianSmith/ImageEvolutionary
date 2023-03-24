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
    chance = random.random()
    mutate_point_chance = 0.5
    mutate_add_point_chance = 0.1
    mutate_color_chance = 0.2
    mutate_polygons_chance = 0.2
    polygon_index = random.randint(0, len(solution) - 1)
    polygon = solution[polygon_index]

    if chance < mutate_point_chance:  # Mutate points
        coords = [x for point in polygon[1:] for x in point]
        tools.mutGaussian(coords, 0, 10, rate)
        coords = [max(0, min(int(x), 200)) for x in coords]
        polygon[1:] = list(zip(coords[::2], coords[1::2]))
    elif chance < mutate_point_chance + mutate_add_point_chance and len(polygon) < 6:
        color = polygon[0]
        coords = [point for point in polygon[1:]]
        new_point = (random.randint(0, 190),random.randint(0, 190))
        coords.append(new_point)
        coords = sort_points(coords)  # Ensure the new point is in the correct index
        polygon = [color] + coords
        solution[polygon_index] = polygon
    elif chance < mutate_point_chance + mutate_color_chance:  # Change the color
        colors = [x for x in polygon[0]]
        tools.mutGaussian(colors, 0, 10, rate)
        colors = [max(0, min(int(x), 256)) for x in colors]
        colors[3] = max(0, min(colors[3], 60))
        polygon[0] = tuple(colors)
    elif chance <= mutate_point_chance + mutate_color_chance + mutate_polygons_chance:  # Add/remove/shuffle polygons
        if polygon_count < 100:
            solution.append(make_polygon(3))
        else:
            rand = random.random()
            if rand < 0.5:
                random.shuffle(solution)
            else:
                solution.pop(random.randint(0, polygon_count - 1))  # Remove a random polygon
    return solution,


def make_polygon(n=3):
    color = [random.randint(0, 256) for _ in range(3)]  # Generate the RGB values
    color.append(random.randint(30, 60))  # Generate the alpha value
    color = [tuple(color)]
    # Generate sizes for x and y
    coordinates_x, coordinates_y = [random.randint(10, 110) for _ in range(n)], [random.randint(10, 110) for _ in
                                                                                 range(n)]
    max_x, max_y = max(coordinates_x), max(coordinates_y)
    min_x, min_y = min(coordinates_x), min(coordinates_y)
    x_right_room, y_right_room = 190 - max_x, 190 - max_y
    # move the polygon into a random position
    x_displacement, y_displacement = random.randint(-min_x + 10, x_right_room), random.randint(-min_y + 10,
                                                                                               y_right_room)
    coordinates = []
    for x, y in zip(coordinates_x, coordinates_y):  # Create the array of coordinates
        coordinates.append((x + x_displacement, y + y_displacement))
    # Make sure that the coordinates follow a certain pattern
    coordinates = sort_points(coordinates)
    return color + coordinates


def create_individual():
    return [make_polygon(3) for _ in range(3)]


print(create_individual())

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)


def run(generations, crossover_probability, mutation_probability, random_seed, population_size, tournament_size,
        gaussian_rate):
    random.seed(random_seed)
    toolbox = base.Toolbox()
    pool = multiprocessing.Pool()
    toolbox.register("map", pool.map)
    toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutate, rate=gaussian_rate)
    toolbox.register("select", tools.selBest)
    population = toolbox.population(n=population_size)
    stats = tools.Statistics(lambda x: x.fitness.values[0])
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    stats.register("median", numpy.median)
    population, log = algorithms.eaMuPlusLambda(population, toolbox, mu=(len(population) // 3),
                                                lambda_=len(population), cxpb=crossover_probability,
                                                mutpb=mutation_probability,
                                                ngen=generations, stats=stats, halloffame=None, verbose=True)
    fittest_individual = max(population, key=lambda individual: individual.fitness.values[0])
    draw(fittest_individual, True)
    for x in list(log):
        if x.get("max") >= 0.95:
            generations_needed_amount = x.get("gen")
            return generations_needed_amount

    return generations


make_polygon(random.randint(3, 5))
