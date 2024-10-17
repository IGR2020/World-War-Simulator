import pygame as pg

def load(path: str, scale: int = 1) -> pg.Surface:
    return pg.transform.scale_by(pg.image.load(path), scale).convert_alpha()

def copy(image: pg.Surface) -> pg.Surface:
    return pg.transform.scale_by(image, 1)

width, height = 900, 500
window = pg.display.set_mode((width, height))
pg.display.set_caption("War Simulator")

fps = 60
clock = pg.time.Clock()
run = True

class Country:
    def __init__(self, mask, rect) -> None:
        self.mask = mask
        self.rect = rect
        self.army = []
        self.factories = 1
        self.factoryJobs = {"Building": 1}
        self.buildProgress = []
        self.buildTime = 100

    def script(self):
        if sum(list(self.factoryJobs.values())) > self.factories:
            for job in self.factryJobs:
                if self.factoryJobs[job] > 0:
                    self.factoryJobs[job] -= 1
                    break
        for i in range(self.factoryJobs["Building"]):
            try:
                self.buildProgress[i] += 0.01
            except:
                self.buildProgress.append(0)
            if self.buildProgress[i] > self.buildTime:
                self.factories += 1
                self.buildProgress.pop(i)

    def select(self):
        print("Total Factories")
        print(self.factories)
        print("Empolyment Status")
        print(self.factoryJobs)
        print("Build Status")
        print(self.buildProgress)
        print()



def getColors(image: pg.Surface) -> set[tuple[int, int, int]]:
    colors = set()
    for i in range(image.get_width()):
        for j in range(image.get_height()):
            colors.add(tuple(image.get_at((i, j))))
    return colors

def createMasks(image: pg.Surface, colors: set[tuple[int, int, int]]) -> dict[tuple[int, int, int], Country]:
    countries = {}
    for color in colors:
        temp = copy(image)
        temp.set_colorkey(color)
        mask = pg.mask.from_surface(temp)
        mask.invert()
        rect = pg.Rect(0, 0, image.get_width(), image.get_height())
        countries[color] = Country(mask, rect)
    return countries

def collideMask(mask1, mask2, rect1, rect2) -> bool:
    xof = rect1[0] - rect2[0]
    yof = rect1[1] - rect2[1]
    if mask2.overlap_area(mask1, (xof, yof)) > 0:
        return True
    return False

world_map = load("fantasy.png", 4)
countries = createMasks(world_map, getColors(world_map))
temp = pg.Surface((1, 1))
temp.fill((255, 255, 255))
point = Country(pg.mask.from_surface(temp), pg.Rect(0, 0, 1, 1))

while run:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

        if event.type == pg.MOUSEBUTTONDOWN:
            for country in countries:
                point.rect.topleft = pg.mouse.get_pos()
                if collideMask(countries[country].mask, point.mask, countries[country].rect, point.rect):
                    print("Country", country)
                    countries[country].select()

    for country in countries:
        countries[country].script()

    window.fill((255, 255, 255))

    window.blit(world_map, (0, 0))

    pg.display.update()