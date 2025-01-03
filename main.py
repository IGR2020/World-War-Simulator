import time

from GUI import TextBox
from functions import blit_text
from game import *
from assets import *
from menu import NationStats
from nations import *


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

        # Temporary Testing
        self.nations["Harfang"].states[12, 14].unit = Unit("Infantry")
        self.nations["Harfang"].states[13, 14].unit = Unit("Tank")
        self.nations["Argon"].states[16, 10].unit = Unit("Tank")

        self.playerNation = "Harfang"
        self.selectedState: State | None = None
        self.selectedStatePos: tuple[int, int] | None = None
        self.playerNationStats = NationStats(0, 0, self.nations[self.playerNation])

    def display(self) -> None:
        for nation in self.nations:
            self.nations[nation].display(self.window, self.x_offset, self.y_offset)
        blit_text(self.window, round(self.clock.get_fps()), (0, 200), colour=(0, 0, 0), size=30)

        # GUI rendering
        self.playerNationStats.display(self.window)

    def event(self, event: pg.event.Event) -> None:
        super().event(event)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_F3:
                print("\n", self.nations[self.playerNation].money, sep="\n")
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

        # Division Movement
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

        # Nation scripts
        for nation in self.nations:
            self.nations[nation].script()

        self.playerNationStats.tick()


instance = Simulator((900, 500), "World War Simulator", fps=fps)
instance.start()
