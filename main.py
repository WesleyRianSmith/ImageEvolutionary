from evol import Population, Evolution
from PIL import Image, ImageDraw, ImageChops
import random

MAX = 255 * 200 * 200
TARGET = Image.open("darwin.png")
TARGET.load()  # read image and close the file

def mutate(solution, indpb):
    print("-"* 30)
    if random.random() < 2:
        polygon_index = random.randint(0,len(solution)-1)
        polygon = solution[polygon_index]
        coords = [x for x in polygon]
        print(coords)
        if random.random() < indpb:
            point_index = random.randint(1, len(coords)-1)
            random_point = coords[point_index]
            print(random_point)
            new_point = tuple([x + random.randint(-5, 5) for x in random_point])
            print(new_point)
            coords[point_index] = new_point
            print(coords)
        solution[polygon_index] = coords


    else:
        if random.random() < indpb:
            pass
        pass

    return solution
    pass

def combine():
    pass

def select():
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
    color = [random.randint(0, 256) for _ in range(3)]
    color.append(random.randint(30,60))
    color = [tuple(color)]
    coordinates = [(random.randint(10, 190), random.randint(10, 190)) for _ in range(n)]
    return color + coordinates

def initialise():
    return [make_polygon(3) for i in range(3)]



def run():


    population = Population.generate(initialise, lambda x: 1, size=10, maximize=True)
    print(population[0].chromosome)
    mutate(population[0].chromosome,1)
    print("-"*30)
    population_piece = population[0].chromosome
    print(population_piece)
    #print(random.choice(population_piece))
    #draw(population[0].chromosome)
    #print(evaluate(population[0].chromosome))
run()