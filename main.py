from pygame.examples.cursors import image
from pygame.transform import scale

from GUI import TextBox
from assets import division_scale, division_border_size
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
            nations[nameMap[color]].states[x, y] = grid[x, y]

    return grid, nations, nameMap, {v: k for k, v in nameMap.items()}, image.get_size()


class Country:
    def __init__(self, name):
        self.name = name
        self.states = {}

class Unit:
    def __init__(self, variety):
        self.attack = 1
        self.health = 100
        self.type = variety

    def display(self, window: pg.Surface, x_offset: int, y_offset: int, x:int, y:int):
        window.blit(assets[self.type], (x-x_offset, y-y_offset))

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
        if self.unit is not None:
            self.unit.display(window, x_offset, y_offset, self.rect.x, self.rect.y)


class Simulator(Game):
    def __init__(self, resolution: tuple[int, int], name: str, mapName="Map1", fps: int = 60,
                 background: tuple[int, int, int] = (255, 255, 255), ):
        super().__init__(resolution, name, fps, background)
        self.mapName = mapName
        self.mapImage = assets[mapName]
        self.countryNames = ["Harfang", "Narnia", "Achenland", "Calorman", "Argon", "Sicily", "Eteinsmoor"]
        self.stateSize = 64
        self.grid, self.nations, self.nameMap, self.colorMap, self.gridSize = createGrid(self.mapImage, self.countryNames,
                                                                                         [(255, 255, 255)], self.stateSize)
        self.x_offset, self.y_offset = 0, 0
        self.nations["Harfang"].states[0, 14].unit = Unit("Infantry")
        self.playerNation = "Narnia"
        self.selectedState: State | None = None
        self.selectedStatePos : tuple[int, int] | None = None

    def display(self) -> None:
        for x in range(self.gridSize[0]):
            for y in range(self.gridSize[1]):
                try:
                    self.grid[x, y].display(self.window, self.x_offset, self.y_offset)
                except KeyError:
                    continue
        blit_text(self.window, round(self.clock.get_fps()), (0, 0), colour=(0, 0, 0), size=30)

    def event(self, event: pg.event.Event) -> None:
        super().event(event)
        if event.type == pg.MOUSEBUTTONDOWN:
            mouseX, mouseY = pg.mouse.get_pos()
            try:
                newStatePos = (mouseX + self.x_offset) // self.stateSize, (mouseY + self.y_offset) // self.stateSize
                newState = self.grid[newStatePos]
                if self.selectedState is not None and self.selectedState.unit is not None and self.selectedState.country == newState.country and self.selectedState.rect.topleft != newState.rect.topleft:
                    newState.unit = self.selectedState.unit
                    self.selectedState.unit = None
                    self.selectedState = None
                elif self.selectedState is not None and self.selectedState.unit is not None and self.selectedState.rect.topleft != newState.rect.topleft:
                    newState.unit = self.selectedState.unit
                    self.selectedState.unit = None
                    self.nations[newState.country].states.pop(newStatePos)
                    self.nations[self.selectedState.country].states[newStatePos] = newState
                    newState.image.fill(self.colorMap[self.selectedState.country])
                    newState.country = self.selectedState.country
                    self.selectedState = None
                else:
                    self.selectedState = newState
                    self.selectedStatePos = newStatePos
            except KeyError:
                pass

    def tick(self) -> None:
        super().tick()
        relX, relY = pg.mouse.get_rel()
        mouseDown = pg.mouse.get_pressed()
        if True in mouseDown:
            self.x_offset -= relX
            self.y_offset -= relY


instance = Simulator((900, 500), "World War Simulator", fps=60)
instance.start()
