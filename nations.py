from assets import *
from game import *

class Country:
    def __init__(self, name):
        self.name = name
        self.states: dict[tuple[int, int], State] = {}
        self.buildQue = []
        self.money = 0
        self.estimatedProduction = 0

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
        self.estimatedProduction = 0
        for state in self.states:
            self.estimatedProduction += self.states[state].production
            self.money += self.states[state].production * productionValue

        for buildPos in self.buildQue:
            for _ in range(3):
                if self.money > buildCost and self.states[buildPos].buildProgress < buildTime:
                    self.money -= buildCost
                    self.states[buildPos].buildProgress += 1
                    print(self.states[buildPos].buildProgress)
                elif self.states[buildPos].buildProgress >= buildTime:
                    self.states[buildPos].production += 3
                    self.states[buildPos].buildProgress = 0
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