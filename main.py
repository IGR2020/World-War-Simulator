from functions import blit_text
from game import *


def createGrid(image, names, blacklist=None, scale=1):
    """Returns grid of country's provinces ,the color: name mappings, the name: color mappings and the grid size"""
    grid = {}
    nameMap = {}
    nameCount = 0
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
            grid[x, y] = {"Country": nameMap[color], "Rect": pg.Rect(x * scale, y * scale, scale, scale)}

    return grid, nameMap, {v: k for k, v in nameMap.items()}, image.get_size()


class State:
    def __init__(self, country: str, rect: pg.Rect):
        self.country = country
        self.rect = rect

class Simulator(Game):
    def __init__(self, resolution: tuple[int, int], name: str, mapName="Map1", fps: int = 60,
                 background: tuple[int, int, int] = (255, 255, 255), ):
        super().__init__(resolution, name, fps, background)
        self.mapName = mapName
        self.mapImage = assets[mapName]
        self.countryNames = ["Harfang", "Narnia", "Achenland", "Calorman", "Argon", "Sicily", "Eteinsmoor"]
        self.grid, self.nameMap, self.colorMap, self.gridSize = createGrid(self.mapImage, self.countryNames,
                                                                           [(255, 255, 255)], 10)

    def display(self) -> None:
        for x in range(self.gridSize[0]):
            for y in range(self.gridSize[1]):
                try:
                    pg.draw.rect(self.window, self.colorMap[self.grid[x, y]["Country"]], self.grid[x, y]["Rect"])
                except KeyError:
                    continue
        blit_text(self.window, round(self.clock.get_fps()), (0, 0), colour=(0, 0, 0), size=30)


instance = Simulator((900, 500), "World War Simulator", fps=60)
instance.start()
