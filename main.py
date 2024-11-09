import time

from GUI import TextBox
from assets import division_scale, division_border_size, stateSize, unitData, buildEffectSpacing, buildEffectThickness, \
    productionValue, buildCost, buildTime
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
            grid[x, y] = State(nameMap[color], pg.Rect(x * scale, y * scale, scale, scale), color)
            nations[nameMap[color]].states[x, y] = grid[x, y]

    return grid, nations, nameMap, {v: k for k, v in nameMap.items()}, image.get_size()


class Country:
    def __init__(self, name):
        self.name = name
        self.states: dict[tuple[int, int], State] = {}
        self.buildQue = []
        self.money = 0

    def display(self, window: pg.Surface, x_offset: int, y_offset: int):
        for state in self.states:
            self.states[state].display(window, x_offset, y_offset)
        for buildPos in self.buildQue:
            startX, startY = buildPos[0] * stateSize, buildPos[1] * stateSize
            for x, y in zip(range(buildPos[0] * stateSize, buildPos[0] * stateSize + stateSize, buildEffectSpacing),
                            range(buildPos[1] * stateSize, buildPos[1] * stateSize + stateSize, buildEffectSpacing)):
                pg.draw.line(window, (0, 0, 0), (startX - x_offset, y - y_offset), (x - x_offset, startY - y_offset),
                             width=buildEffectThickness)
        for buildPos in self.buildQue:
            startX, startY = buildPos[0] * stateSize + stateSize, buildPos[1] * stateSize + stateSize
            for x, y in zip(range(buildPos[0] * stateSize, buildPos[0] * stateSize + stateSize, buildEffectSpacing),
                            range(buildPos[1] * stateSize, buildPos[1] * stateSize + stateSize, buildEffectSpacing)):
                pg.draw.line(window, (0, 0, 0), (x - x_offset, startY - y_offset), (startX - x_offset, y - y_offset),
                             width=buildEffectThickness)

    def script(self):
        for state in self.states:
            self.money += self.states[state].production * productionValue

        for buildPos in self.buildQue:
            for _ in range(15):
                if self.money > buildCost:
                    self.money -= buildCost
                    self.states[buildPos].buildProgress += 1
                elif self.states[buildPos].buildProgress > buildTime:
                    self.states[buildPos].production += 1
                    self.buildQue.remove(buildPos)
                    break
                else:
                    break


class Unit:
    def __init__(self, variety):
        self.attack = unitData[variety]["Attack"]
        self.health = unitData[variety]["Health"]
        self.maxHealth = unitData[variety]["Health"]
        self.type = variety
        self.target = None
        self.moveSpeed = unitData[variety]["Move Speed"]
        self.moveCoolDown = time.time()
        self.experience = 1
        self.healRate = unitData[variety]["Heal Rate"]
        self.defence = unitData[variety]["Defence"]

    def addExperience(self, experience):
        self.experience += experience
        self.moveSpeed = unitData[self.type]["Move Speed"] * self.experience
        self.attack = unitData[self.type]["Attack"] * self.experience
        self.maxHealth = unitData[self.type]["Health"] * self.experience
        self.healRate = unitData[self.type]["Heal Rate"] * self.experience
        self.defence = unitData[self.type]["Defence"] * self.experience

    def display(self, window: pg.Surface, x_offset: int, y_offset: int, x: int, y: int):
        window.blit(assets[self.type], (x - x_offset, y - y_offset))
        rect = pg.Rect(x - x_offset, y + stateSize - y_offset - 5, (self.health / self.maxHealth) * stateSize, 5)
        pg.draw.rect(window, (255, 0, 0), rect)


class State:
    def __init__(self, country: str, rect: pg.Rect, color: tuple[int, int, int]):
        self.country = country
        self.rect = rect
        self.color = color
        self.image = pg.Surface(self.rect.size)
        self.image.fill(color)
        self.unit = None
        self.production = 3
        self.buildProgress = 0

    def display(self, window: pg.Surface, x_offset: int, y_offset: int):
        window.blit(self.image, (self.rect.x - x_offset, self.rect.y - y_offset))
        if self.unit is not None:
            self.unit.display(window, x_offset, y_offset, self.rect.x, self.rect.y)


class Simulator(Game):
    def __init__(self, resolution: tuple[int, int], name: str, mapName="Map1", fps: int = 60,
                 background: tuple[int, int, int] = (255, 255, 255)):
        super().__init__(resolution, name, fps, background)
        self.mapName = mapName
        self.mapImage = assets[mapName]
        self.countryNames = ["Harfang", "Narnia", "Archenland", "Calorman", "Argon", "Sicily", "Eteinsmoor"]
        self.grid, self.nations, self.nameMap, self.colorMap, self.gridSize = createGrid(self.mapImage,
                                                                                         self.countryNames,
                                                                                         [(255, 255, 255)],
                                                                                         stateSize)
        self.x_offset, self.y_offset = 0, 500
        self.nations["Harfang"].states[12, 14].unit = Unit("Infantry")
        self.nations["Harfang"].states[13, 14].unit = Unit("Tank")
        self.nations["Argon"].states[16, 10].unit = Unit("Tank")
        self.playerNation = "Harfang"
        self.selectedState: State | None = None
        self.selectedStatePos: tuple[int, int] | None = None

    def display(self) -> None:
        for nation in self.nations:
            self.nations[nation].display(self.window, self.x_offset, self.y_offset)
        blit_text(self.window, round(self.clock.get_fps()), (0, 0), colour=(0, 0, 0), size=30)

    def event(self, event: pg.event.Event) -> None:
        super().event(event)
        if event.type == pg.MOUSEBUTTONDOWN:
            mouseX, mouseY = pg.mouse.get_pos()
            try:
                newStatePos = ((mouseX + self.x_offset) // stateSize, (mouseY + self.y_offset) // stateSize)
                self.grid[newStatePos]
            except KeyError:
                return
            if event.button == 1:
                if self.selectedState is not None and self.selectedState.unit is not None and self.selectedState.country == self.playerNation:
                    self.selectedState.unit.target = newStatePos
                    self.selectedState = None
                else:
                    self.selectedState = self.grid[newStatePos]
            elif event.button == 3 and self.grid[newStatePos].country == self.playerNation:
                self.nations[self.playerNation].buildQue.append(newStatePos)

    # movement of units should be through this function only
    def moveUnit(self, selectedStatePos: tuple[int, int], newStatePos: tuple[int, int]):
        newState = self.grid[newStatePos]
        selectedState = self.grid[selectedStatePos]
        # invalidates movement which is not adjacent
        if selectedState is None or (newStatePos[0] - selectedStatePos[0]) + abs(
                newStatePos[1] - selectedStatePos[1]) > 1:
            pass
        # movement withing same country
        elif selectedState.unit is not None and selectedState.country == newState.country and selectedState.rect.topleft != newState.rect.topleft:
            self.grid[selectedStatePos].unit.moveCoolDown = time.time()
            newState.unit, selectedState.unit = selectedState.unit, newState.unit
        # movement to different country
        elif selectedState.unit is not None and selectedState.rect.topleft != newState.rect.topleft:
            self.grid[selectedStatePos].unit.moveCoolDown = time.time()
            if selectedState.unit.health < 1:
                selectedState.unit = None
                if newState is not None and newState.unit.health < 1:
                    newState.unit = None
            elif newState.unit is not None and newState.unit.health > 1:
                newState.unit.health -= selectedState.unit.attack
                newState.unit.moveCoolDown = time.time()
                selectedState.unit.health -= newState.unit.defence
                selectedState.unit.addExperience(0.1)
                newState.unit.addExperience(0.03)
            else:
                newState.unit = None
                newState.unit = selectedState.unit
                selectedState.unit = None
                self.nations[newState.country].states.pop(newStatePos)
                self.nations[selectedState.country].states[newStatePos] = newState
                newState.image.fill(self.colorMap[selectedState.country])
                newState.country = selectedState.country

    def tick(self) -> None:
        super().tick()
        relX, relY = pg.mouse.get_rel()
        mouseDown = pg.mouse.get_pressed()
        if True in mouseDown:
            self.x_offset -= relX
            self.y_offset -= relY
        for x in range(self.gridSize[0]):
            for y in range(self.gridSize[1]):
                try:
                    if self.grid[x, y].unit is None:
                        continue
                    target = self.grid[x, y].unit.target
                    moveCoolDown = self.grid[x, y].unit.moveCoolDown
                    moveSpeed = self.grid[x, y].unit.moveSpeed
                    newStatePos = [0, 0]
                    if time.time() - moveCoolDown < moveSpeed:
                        continue
                    self.grid[x, y].unit.health += self.grid[x, y].unit.healRate
                    self.grid[x, y].unit.health = min(self.grid[x, y].unit.health, self.grid[x, y].unit.maxHealth)
                    if target is None:
                        continue
                    if target == (x, y):
                        self.grid[x, y].unit.target = None
                        continue
                    if x - target[0] < 0:
                        newStatePos[0] = + 1
                    elif x - target[0] > 0:
                        newStatePos[0] = -1
                    elif y - target[1] < 0:
                        newStatePos[1] = +1
                    elif y - target[1] > 0:
                        newStatePos[1] = -1
                    newStatePos[0] += x
                    newStatePos[1] += y
                    newStatePos = (newStatePos[0], newStatePos[1])
                    self.moveUnit((x, y), newStatePos)
                except KeyError:
                    continue
        for nation in self.nations:
            self.nations[nation].script()


instance = Simulator((900, 500), "World War Simulator", fps=60)
instance.start()
