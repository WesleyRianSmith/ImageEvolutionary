from evol import Population, Evolution
from PIL import Image, ImageDraw, ImageChops
import random

MAX = 255 * 200 * 200
TARGET = Image.open("darwin.png")
TARGET.load()  # read image and close the file


def mutate(solution, rate):
    # print("-"* 30)
    i = random.randint(1,5)
    if i == 1:
        # print("Random point change")
        polygon_index = random.randint(0, len(solution) - 1)
        polygon = solution[polygon_index]
        coords = [x for x in polygon]
        point_index = random.randint(1, len(coords) - 1)
        random_point = coords[point_index]
        new_point = tuple([max(10, min(190, int(x + random.gauss(0, 10)))) for x in random_point])
        coords[point_index] = new_point
        solution[polygon_index] = coords
    elif i == 2:
        # print("Add new polygon")
        solution.append(make_polygon(random.randint(3, 5)))
    elif i == 3:
        # print("Change colour")
        polygon_index = random.randint(0, len(solution) - 1)
        polygon = solution[polygon_index]
        colors = [x for x in polygon[0]]
        for x in range(3):
            colors[x] = max(0, min(256, int(colors[x] + random.gauss(0, 10))))
        polygon[0] = tuple(colors)
    elif i == 4:
        # print("shuffling polygons")
        random.shuffle(solution)
    else:
        # print("New alpha value")
        polygon_index = random.randint(0, len(solution) - 1)
        polygon = solution[polygon_index]
        colors = [x for x in polygon[0]]
        new_alpha = max(30, min(60, int(colors[3] + random.gauss(0, 10))))
        colors[3] = new_alpha
        polygon[0] = tuple(colors)
        pass

    return solution
    pass


def combine(*parents):
    print(*parents)
    return 2
    pass


def select(solution):
    groupA = random.sample(solution, 10)
    print(groupA)
    groupB = random.sample(solution, 10)
    print(groupB)
    return max(groupA, key=lambda x: x.fitness), max(groupB, key=lambda x: x.fitness)
    pass


def evaluate(solution):
    image = draw(solution)
    diff = ImageChops.difference(image, TARGET)
    hist = diff.convert("L").histogram()
    count = sum(i * n for i, n in enumerate(hist))
    return (MAX - count) / MAX


def draw(solution):
    image = Image.new("RGB", (200, 200))
    canvas = ImageDraw.Draw(image, "RGBA")
    for polygon in solution:
        canvas.polygon(polygon[1:], fill=polygon[0])

    image.save("solution.png")
    return image


def make_polygon(n):
    # 0 <= R|G|B < 256, 30 <= A <= 60, 10 <= x|y < 190
    color = [random.randint(0, 256) for _ in range(3)]
    color.append(random.randint(30, 60))
    color = [tuple(color)]
    coordinates = [(random.randint(10, 190), random.randint(10, 190)) for _ in range(n)]
    return color + coordinates


def initialise():
    return [make_polygon(3) for _ in range(3)]


evolution = (Evolution().survive(fraction=1)
             .breed(parent_picker=select, combiner=combine)
             .mutate(mutate_function=mutate, rate=0.1)
             .evaluate())


def run():
    population = Population.generate(initialise, evaluate, size=20, maximize=True)
    population = population.evolve(evolution)
    print(population.individuals)
    print(select(population.individuals))
    #for x in population:
        #print(x.chromosome)

    for i in range(1):
        draw(population[0].chromosome).save("solution" + str(i) + ".png")
        population = population.evolve(evolution)
        print("i =", i, " best =", population.current_best.fitness,
              " worst =", population.current_worst.fitness)


run()
