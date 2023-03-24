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
    if polygon_count >= 100 and (mode == 3 or mode == 5):
        guassian_amount = 20
    chance = random.random()
    polygon_index = random.randint(0, len(solution) - 1)
    polygon = solution[polygon_index]
    if chance < 0.5:
        coords = [x for point in polygon[1:] for x in point]
        tools.mutGaussian(coords, 0, guassian_amount, rate)
        coords = [max(0, min(int(x), 200)) for x in coords]
        polygon[1:] = list(zip(coords[::2], coords[1::2]))
    elif chance < 0.6 and len(polygon) < 6 and mode == 1:
        color = polygon[0]
        coords = [point for point in polygon[1:]]
        new_point = (random.randint(0, 190),random.randint(0, 190))
        coords.append(new_point)
        coords = sort_points(coords)
        polygon = [color] + coords
        solution[polygon_index] = polygon
    elif chance < 0.8: # Change the color
        colors = [x for x in polygon[0]]
        tools.mutGaussian(colors, 0, guassian_amount, rate)
        colors = [max(0, min(int(x), 256)) for x in colors]
        colors[3] = max(0, min(colors[3], 60))
        polygon[0] = tuple(colors)
    else: # Add/remove/shuffle polygons
        if polygon_count < 100:
            if mode == 1 or mode == 5:
                if polygon_count < 25:
                    solution.append(make_polygon(random.randint(3, 5), 0.8, 0.1))
                elif polygon_count < 50:
                    solution.append(make_polygon(random.randint(3, 5), 0.4, 0.4))
                else:
                    solution.append(make_polygon(random.randint(3, 5), 0.1, 0.8))
            else:
                solution.append(make_polygon(3, 0, 0))
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
        coordinates_x, coordinates_y = [random.randint(10, 40) for _ in range(n)], [random.randint(10, 40) for _ in
                                                                                     range(n)]
    elif chance < large_chance + small_chance:
        coordinates_x, coordinates_y = [random.randint(10, 190) for _ in range(n)], [random.randint(10, 190) for _ in
                                                                                     range(n)]
    else:
        coordinates_x, coordinates_y = [random.randint(10, 110) for _ in range(n)], [random.randint(10, 110) for _ in
                                                                                     range(n)]
    max_x, max_y = max(coordinates_x), max(coordinates_y)
    min_x, min_y = min(coordinates_x), min(coordinates_y)
    x_right_room, y_right_room = 190 - max_x, 190 - max_y
    x_displacement, y_displacement = random.randint(-min_x + 10, x_right_room), random.randint(-min_y + 10,
                                                                                               y_right_room)
    coordinates = []
    for x,y in zip(coordinates_x,coordinates_y):
        coordinates.append((x+x_displacement,y+y_displacement))

    coordinates = sort_points(coordinates)

    return color + coordinates

def create_individual():
    ind = []
    if mode == 1 or mode == 5:
        ind.append(make_polygon(1,0,0,True))
        for x in range(3):
            ind.append(make_polygon(random.randint(3,5)))
    else:
        for x in range(3):
            ind.append(make_polygon(3,0,0))
    return ind

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)



def run(generations,crossover_probability,mutation_probability, random_seed, population_size):
    print("Running!")
    random.seed(random_seed)
    toolbox = base.Toolbox()
    pool = multiprocessing.Pool()
    toolbox.register("map", pool.map)
    toolbox.register("individual", tools.initIterate, creator.Individual, create_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutate, rate=gaussian_rate)
    if mode == 2 or mode == 55:
        toolbox.register("select", tools.selBest)

    else:
        toolbox.register("select", tools.selTournament, tournsize=tournament_size)


    population = toolbox.population(n=population_size)
    #hof = tools.HallOfFame(3)
    stats = tools.Statistics(lambda x: x.fitness.values[0])
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    stats.register("median", numpy.median)
    stats.register("std", numpy.std)


    if mode == 3 or mode == 5 :
        population, log = algorithms.eaSimple(population, toolbox,
                                              cxpb=crossover_probability, mutpb=mutation_probability, ngen=generations,
                                              stats=stats, halloffame=None, verbose=True)
        #population, log = algorithms.eaMuCommaLambda(population, toolbox, mu=(len(population) // 3),
                                                     #lambda_=len(population), cxpb=crossover_probability,
                                                     #mutpb=mutation_probability,
                                                     #ngen=generations, stats=stats, halloffame=None, verbose=False)



    else:
        population, log = algorithms.eaMuPlusLambda(population, toolbox, mu=(len(population) // 3),
                                                     lambda_=len(population), cxpb=crossover_probability,
                                                     mutpb=mutation_probability,
                                                     ngen=generations, stats=stats, halloffame=None, verbose=True)



    fittest_individual = max(population, key=lambda individual: individual.fitness.values[0])
    image = draw(fittest_individual,True)
    for x in list(log):
        if x.get("max") > 0.95:
            generations_needed_amount = x.get("gen")
            return generations_needed_amount

    return generations

seed = 120
tournament_size = 10
gaussian_rate = 0.5
population_size = 30
mutation_probability = 0.75
#generations = 4000
crossover_probability = 0.75
mode = 0




if __name__ == "__main__":
    #image = [[(232, 146, 30, 255), (11, 45), (32   , 35), (33, 25), (32, 31)],[(232, 146, 30, 255), (11, 45), (32, 35), (33, 97), (193, 31)],[(232, 146, 30, 255), (11, 45), (32, 35), (120, 25), (32, 31)], [(96, 25, 41, 255), (106, 88), (118, 83), (119, 86), (98, 65)], [(3, 222, 116, 255), (119, 86), (122, 88), (129, 73), (127, 77)], [(216, 161, 233, 255), (177, 164), (190, 162), (187, 146), (185, 135)], [(141, 154, 256, 255), (49, 106), (50, 97), (44, 84), (35, 86)], [(253, 76, 134, 255), (171, 83), (173, 71), (164, 58), (162, 58)], [(28, 214, 155, 255), (65, 103), (77, 91), (87, 84), (76, 75)], [(95, 181, 144, 255), (96, 184), (91, 170), (76, 168), (70, 167)], [(69, 87, 108, 255), (144, 69), (151, 65), (139, 60), (132, 58)], [(12, 132, 19, 255), (143, 108), (148, 104), (124, 90), (120, 86)]]
    #image2 = [[(13, 164, 202, 255), (44, 177), (53, 164), (52, 168)],[(13, 164, 202, 255), (20, 177), (53, 164), (130, 30)],[(13, 164, 202, 255), (50, 177), (53, 164), (160, 30)], [(18, 19, 123, 255), (126, 142), (137, 128), (123, 122)], [(75, 36, 102, 255), (163, 167), (176, 173), (156, 154)], [(109, 80, 109, 255), (101, 120), (120, 124), (110, 105)], [(117, 209, 240, 255), (74, 55), (78, 47), (71, 42)], [(37, 254, 245, 255), (17, 155), (39, 157), (33, 153)], [(61, 216, 38, 255), (178, 94), (177, 74), (162, 83)], [(238, 5, 221, 255), (152, 91), (158, 100), (156, 79)], [(149, 55, 157, 255), (159, 55), (171, 65), (146, 37)], [(160, 129, 169, 255), (145, 63), (163, 48), (155, 44)]]
    #for x in range(10):
        #image2.append(make_polygon(3,0,1))
    #imageA = draw(image,False)
    #imageB = draw(image2, False)
    #imageA.save("SolutionA.png")
    #imageB.save("SolutionB.png")
    #CrossOver(image,image2)
    #imageA = draw(image, False)
    #imageB = draw(image2, False)
    #imageA.save("SolutionOffspring1.png")
    #imageB.save("SolutionOffspring2.png")
    #run(15000,0.3, 0.7)
    generations_needed = run(5000, 0, 1, 120, 30)
    generations = 5000
    seeds = [120,298,234,1212,3233]
    generations_needed = []
    generations_input = 4000
    for i in seeds:
        break
        needed_generations = run(generations_input, 0, 1, i, 30)
        generations_needed.append(needed_generations)
        print(generations_needed)

    for i in seeds:
        break
        generations_needed.append(run(generations,0,1,i))
        print(generations_needed)
    generations = 1172

    for i in range(10):
        break
        mutation_probability = (10 - i) / 10
        #crossover_probability = 1 - mutation_probability
        for y in range(10):
            crossover_probability = (10 - y) / 10
            generations_needed = run(generations, crossover_probability, mutation_probability,120,30)
            if generations_needed < generations:
                 message = "Generations needed are " + str(generations_needed) + " and mutation probability is " + str(
                    mutation_probability) + " and crossover probability is " + str(
                    crossover_probability) + " and guassian rate is " + str(
                    gaussian_rate) + " and population is " + str(population_size)
                 print(message)
                 generations = generations_needed

        #for x in range(10):


