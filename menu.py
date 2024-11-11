from game import *
from nations import *
from GUI import *
from time import time


class NationStats(GUIHolder):
    def __init__(self, x: int, y: int, playerNation: Country):
        self.nation = playerNation
        self.GUIHeader = [
            Text(playerNation.name, x, y, (0, 0, 0), 35, "Arialblack"),
            TextBox("Cog", "Cog", (32, 0), x, y, (0, 0, 0), 35, "Arialblack", "0"),
            TextBox("Coins", "Coins", (32, 0), x, y, (0, 0, 0), 35, "Arialblack", "0"),
        ]
        self.GUI = table(self.GUIHeader, GUISpacing)
        self.updateTime = 0
        self.updateSpeed = 0.4

    def tick(self) -> None:
        if time() - self.updateTime < self.updateSpeed:
            return

        self.GUI[1].text = self.nation.estimatedProduction
        self.GUI[2].text = round(self.nation.money)

        self.GUI[1].reload()
        self.GUI[2].reload()

        self.updateTime = time()