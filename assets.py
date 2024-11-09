from pygame.transform import scale

from functions import load_assets, loadJson

fps = 60
assets = load_assets("assets")
division_scale = 4
assets.update(load_assets("assets/units", scale=division_scale))
division_border_size = division_scale*3
fontLocation = "assets/fonts/"
stateSize = 64
unitData = loadJson("data/units.json")
buildTime = 100*fps
buildCost = 155
buildEffectSpacing = 8
buildEffectThickness = 2
productionValue = 7/fps