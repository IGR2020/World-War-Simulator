from game import *
from GUI import *
from nations import *


class NationStats(GUIHolder):
    def __init__(self, x: int, y: int, playerNation: Country):
        self.nation = playerNation
        self.GUIHeader = [
            Text(playerNation.name, x, y, (0, 0, 0), 35, "Arialblack"),
            Text("0", x, y, (0, 0, 0), 35, "Arialblack"),
            Text("0", x, y, (0, 0, 0), 35, "Arialblack"),
            Text("0", x, y, (0, 0, 0), 35, "Arialblack"),
        ]
        self.GUI = table(self.GUIHeader, GUISpacing)

