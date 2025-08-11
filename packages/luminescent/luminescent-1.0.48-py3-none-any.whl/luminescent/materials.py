from gdsfactory.technology import LogicalLayer, LayerLevel, LayerStack
from gdsfactory.generic_tech.layer_map import LAYER
import gdsfactory as gf
import copy


MATERIALS = {
    "air": {"epsilon": 1.0},
    "cSi": {"epsilon": 3.476**2},
    "SiO2": {"epsilon": 1.444**2},
    "SiN": {"epsilon": 2.0**2},
    "Ge": {"epsilon": 4.0**2},
    "Si": {"epsilon": 3.476**2},
    # "ZeSe": {"epsilon": 5.7},
    "FR4": {"epsilon": 4.3},
    # "Al2O3": {"epsilon": 9.9},
    # "PEC": {"epsilon": 133700, "sigma": 50},
    "PEC": {"epsilon": 133700},
    "design": {},
}

ks = copy.deepcopy(list(MATERIALS.keys()))
for k in ks:
    MATERIALS[k.lower()] = MATERIALS[k]

BBOX = (0, 0)
WG = (1, 0)
CLAD = (2, 0)
DESIGN = (1000, 0)
OVERRIDE = (2000, 0)

thickness_wg = 0.22
layers = {
    "core": LayerLevel(
        layer=LogicalLayer(layer=WG),
        thickness=thickness_wg,
        zmin=0.0,
        material="Si",
        mesh_order=1,
    ),
    "design": LayerLevel(
        layer=LogicalLayer(layer=DESIGN),
        thickness=thickness_wg,
        zmin=0.0,
        material="design",
        mesh_order=0,
    ),
}


SOI220 = LayerStack(layers=layers)

th_sub = 1.6
layers = {
    "top": LayerLevel(
        layer=LogicalLayer(layer=LAYER.WG),
        thickness=0.1,
        zmin=th_sub,
        material="PEC",
        mesh_order=1,
    ),
    "core": LayerLevel(
        layer=LogicalLayer(layer=(2, 0)),
        thickness=th_sub,
        zmin=0.0,
        material="FR4",
        mesh_order=2,
    ),
    "bot": LayerLevel(
        layer=LogicalLayer(layer=(2, 0)),
        thickness=5,
        zmin=-5,
        material="PEC",
        mesh_order=3,
    ),
}


MS = LayerStack(layers=layers)
MS.layers["background"] = {"material": "air"}


MATKEYS = {
    "si": "cSi",
    "Si": "cSi",
    "sio2": "SiO2",
    "sin": "SiN",
    "ge": "Ge",
}


def matname(k):
    if k in MATKEYS:
        return MATKEYS[k]
    return k.capitalize()
