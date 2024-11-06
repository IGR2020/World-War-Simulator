from pygame.examples.cursors import image

from functions import blit_text
from game import *


def createGrid(image, names, blacklist=None, scale=1):
    """Returns grid of country's provinces , list of nation's, the color: name mappings, the name: color mappings and the grid size"""
    grid = {}
    nameMap = {}
    nameCount = 0
    nations = {name: Country(name) for name in names}
    if blacklist is None: blacklist = []

    for x in range(image.get_width()):
        for y in range(image.get_height()):
            color = image.get_at((x, y))
            color = color[0], color[1], color[2]
            if color in blacklist:
                continue
            try:
                nameMap[color]
            except KeyError:
                nameMap[color] = names[nameCount]
                nameCount += 1
            grid[x, y] = State(nameMap[color], pg.Rect(x*scale, y*scale, scale, scale), color)
            nations[names[nameCount]].states[x, y] = grid[x, y]

    return grid, nations, nameMap, {v: k for k, v in nameMap.items()}, image.get_size()


class Country:
    def __init__(self, name):
        self.name = name
        self.states = {}
        self.army = []

class Unit:
    def __init__(self):
        self.attack = 1
        self.health = 100

class State:
    def __init__(self, country: str, rect: pg.Rect, color: tuple[int, int, int]):
        self.country = country
        self.rect = rect
        self.color = color
        self.image = pg.Surface(self.rect.size)
        self.image.fill(color)
        self.unit = None

    def display(self, window: pg.Surface, x_offset: int, y_offset: int):
        window.blit(self.image, (self.rect.x - x_offset, self.rect.y - y_offset))


class Simulator(Game):
    def __init__(self, resolution: tuple[int, int], name: str, mapName="Map1", fps: int = 60,
                 background: tuple[int, int, int] = (255, 255, 255), ):
        super().__init__(resolution, name, fps, background)
        self.mapName = mapName
        self.mapImage = assets[mapName]
        self.countryNames = ["Harfang", "Narnia", "Achenland", "Calorman", "Argon", "Sicily", "Eteinsmoor"]
        self.grid, self.nations, self.nameMap, self.colorMap, self.gridSize = createGrid(self.mapImage, self.countryNames,
                                                                           [(255, 255, 255)], 10)
        self.x_offset, self.y_offset = 0, 0

    def display(self) -> None:
        for x in range(self.gridSize[0]):
            for y in range(self.gridSize[1]):
                try:
                    self.grid[x, y].display(self.window, self.x_offset, self.y_offset)
                except KeyError:
                    continue
        blit_text(self.window, round(self.clock.get_fps()), (0, 0), colour=(0, 0, 0), size=30)


instance = Simulator((900, 500), "World War Simulator", fps=60)
instance.start()
