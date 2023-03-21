from evol import Population, Evolution
from PIL import Image, ImageDraw, ImageChops
import random

MAX = 255 * 200 * 200
TARGET = Image.open("darwin.png")
TARGET.load()  # read image and close the file


def mutate(solution, rate):
    # print("-"* 30)
    maximum = 10
    polygon_count = len(solution)
    mutation_choice = []
    mutation_choice += [1] * 10
    mutation_choice += [2] * 10
    mutation_choice += [3] * 10
    mutation_choice += [4] * 10
    if len(solution) < 100:
        mutation_choice += [6] * 1
    if len(solution) > 3:
        mutation_choice += [5] * 1
    i = mutation_choice[random.randint(1,len(mutation_choice))-1]
    if i == 1:
        # print("Random point change")
        polygon_index = random.randint(0, len(solution) - 1)
        polygon = solution[polygon_index]
        coords = [x for x in polygon]
        #print("-" * 20)
        #print(coords)
        point_index = random.randint(1, len(coords) - 1)
        random_point = coords[point_index]
        #print(random_point)
        new_point = tuple([int(x + random.gauss(0, 10)) for x in random_point])
        coords[point_index] = new_point
        solution[polygon_index] = coords
    elif i == 2:
        # print("Change colour")
        polygon_index = random.randint(0, len(solution) - 1)
        polygon = solution[polygon_index]
        colors = [x for x in polygon[0]]

        for x in range(3):
            colors[x] = max(0, min(256, int(colors[x] + random.gauss(0, 10))))
        polygon[0] = tuple(colors)
    elif i == 3:
        # print("shuffling polygons")
        random.shuffle(solution)
    elif i == 4:
        # print("New alpha value")
        polygon_index = random.randint(0, len(solution) - 1)
        polygon = solution[polygon_index]
        colors = [x for x in polygon[0]]
        new_alpha = max(30, min(60, int(colors[3] + random.gauss(0, 10))))
        colors[3] = new_alpha
        polygon[0] = tuple(colors)
    elif i == 5:
        # print("Delete a random polygon")
        solution.pop(random.randrange(len(solution)))
    elif i == 6:
        # print("Add new polygon")
        solution.append(make_polygon(random.randint(3, 5)))

    return solution
    pass


def combine(*parents):
    return parents[0]



def select(population):
    groupA = random.sample(population, 5)
    #groupB = random.sample(population, 10)
    return [max(groupA, key=lambda x: x.fitness)]



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





def run():
    evolution = (Evolution().survive(fraction=0.5)

                 .mutate(mutate_function=mutate, rate=0.1)
                 .evaluate())
    evolution = (Evolution()
                 .survive(fraction=0.5, selector="tournament", tournament_size=2)
                 .mutate(mutate_function=mutate, rate=0.5)
                 .evaluate(evaluate_function=evaluate))

    population = Population.generate(initialise, evaluate, size=50, maximize=True)
    population = population.evolve(evolution)


    for i in range(2000):

        population = population.evolve(evolution)
        print("i =", i, " best =", population.current_best.fitness," polygons =",len(population.current_best.chromosome),
              " worst =", population.current_worst.fitness)
    draw(population.current_best.chromosome).save("solution.png")

run()
