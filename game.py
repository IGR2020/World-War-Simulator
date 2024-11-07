from collision import *

class Game:
    def __init__(
        self,
        resolution: tuple[int, int],
        name: str,
        fps: int = 60,
        background: tuple[int, int, int] = (255, 255, 255),
    ):
        self.width, self.height = resolution
        self.name = name
        self.window = pg.display.set_mode(resolution)
        self.fps = fps
        self.clock = pg.time.Clock()
        self.run = True
        self.background = background
        pg.display.set_caption(name)

        self.deltaTime = 0

    def tick(self) -> None:
        self.deltaTime = self.clock.tick(self.fps) / 16
        if self.deltaTime > 1.4:
            print("[Graphics] Low FPS")

    def display(self) -> None: ...

    def event(self, event: pg.event.Event) -> None:
        if event.type == pg.QUIT:
            self.run = False
        if event.type == pg.K_F3:
            print(self.deltaTime)

    def quit(self):
        return None

    def start(self):
        while self.run:
            for event in pg.event.get():
                self.event(event)
            self.tick()
            self.window.fill(self.background)
            self.display()
            pg.display.update()
        return self.quit()