from pygame.transform import scale

from functions import load_assets, loadJson

assets = load_assets("assets")
division_scale = 4
assets.update(load_assets("assets/units", scale=division_scale))
division_border_size = division_scale*3
fontLocation = "assets/fonts/"
stateSize = 64
unitData = loadJson("data/units.json")
