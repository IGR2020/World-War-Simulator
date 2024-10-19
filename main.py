import pygame as pg

def load(path: str, scale: int = 1) -> pg.Surface:
    return pg.transform.scale_by(pg.image.load(path), scale).convert_alpha()

def copy(image: pg.Surface) -> pg.Surface:
    return pg.transform.scale_by(image, 1)

def groupColors(colors: list[tuple[int, int, int]]) -> list[list[tuple[int, int, int]]]:
    groupedColors = []
    for color in colors:
        for gColors in groupedColors:
            if abs(color[0] - gColors[0][0]) + abs(color[1] - gColors[0][1]) + abs(color[2] - gColors[0][2]) < 10:
                gColors.append(color)
                break
        else:
            groupedColors.append([color])
    return groupedColors

width, height = 900, 500
window = pg.display.set_mode((width, height))
pg.display.set_caption("War Simulator")

fps = 60
clock = pg.time.Clock()
run = True

buildCost = 1800

class Country:
    def __init__(self, states) -> None:
        self.jobs = {"Building": [{"State": 0, "Count": 1}]}
        self.states: list[State] = states
        self.buildSpeed = 0.1

    def getTotalProduction(self):
        return sum([state.factories for state in self.states])
    
    def getTotalEmployment(self):
        return sum([build["Count"] for build in self.jobs["Building"]])
    
    def reduceJobs(self):
        for build in self.jobs["Building"]:
            if build["Count"] > 0: 
                build["Count"] -= 1
                return

    def script(self):
        if self.getTotalEmployment() > self.getTotalProduction():
            self.reduceJobs()      
        for build in self.jobs["Building"]:
            self.states[build["State"]].buildProgress += build["Count"]*self.buildSpeed
        for state in self.states:
            state.script()

class State:
    def __init__(self, mask, rect) -> None:
        self.factories = 1
        self.mask = mask
        self.rect = rect
        self.buildProgress = 0

    def script(self):
        if self.buildProgress > buildCost:
            self.factories += 1
            self.buildProgress = 0


def getColors(image: pg.Surface) -> set[tuple[int, int, int]]:
    colors = set()
    for i in range(image.get_width()):
        for j in range(image.get_height()):
            colors.add(tuple(image.get_at((i, j))))
    return colors

def createMasks(image: pg.Surface, colors: list[list[tuple[int, int, int]]], names: list[str]) -> dict[str, Country]:
    countries = {}
    for colorGroup, name in zip(colors, names):
        states = []
        for color in colorGroup:
            temp = copy(image)
            temp.set_colorkey(color)
            mask = pg.mask.from_surface(temp)
            mask.invert()
            rect = pg.Rect(0, 0, image.get_width(), image.get_height())
            states.append(State(mask, rect))
        countries[name] = Country(states)
    return countries

def collideMask(mask1, mask2, rect1, rect2) -> bool:
    xof = rect1[0] - rect2[0]
    yof = rect1[1] - rect2[1]
    if mask2.overlap_area(mask1, (xof, yof)) > 0:
        return True
    return False

world_map = load("fantasy.png", 4)
groupedColors = groupColors(getColors(world_map))
countryNames = ["India", "Russia", "Ameriaca", "Russia", "Germany", "Australia", "Argentina", "Brazil", "Denmark", "Italy", "Afghanistan", "South Africa"]
countries = createMasks(world_map, groupedColors, countryNames)
temp = pg.Surface((1, 1))
temp.fill((255, 255, 255))
point = State(pg.mask.from_surface(temp), pg.Rect(0, 0, 1, 1))

while run:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

        if event.type == pg.MOUSEBUTTONDOWN:
            point.rect.topleft = pg.mouse.get_pos()
            for country in countries:
                for state in countries[country].states:
                    if collideMask(state.mask, point.mask, state.rect, point.rect):
                        print("Country", country)

    for country in countries:
        countries[country].script()

    window.fill((255, 255, 255))

    window.blit(world_map, (0, 0))

    pg.display.update()