from ..materials import *
from .sparams import *
from .setup import *
from ..constants import *
from ..layers import *
from ..utils import *
import gdsfactory as gf
from copy import deepcopy
from functools import partial
from math import cos, pi, sin
import os
from gdsfactory.generic_tech import LAYER_STACK, LAYER
import json


def make_design_prob(
    path,
    component,
    targets,
    lmin,
    iters=10,
    # lvoid=None,
    # lsolid=None,
    symmetries=[],
    weights=dict(),
    eta=0.4,
    init=1,
    stoploss=None,
    layer=DESIGN,
    fill_material=None,
    void_material=None,
    materials={},
    #  fill_layer=LAYER.WG,
    #  void_layer=None,
    layer_stack=SOI220,
    restart=True,
    save_memory=False,
    **kwargs,
):
    assert (
        "field_decay_threshold" not in kwargs
    ), "field_decay_threshold is not supported in inverse design"
    materials = {**MATERIALS, **materials}
    c = component
    # if not N:
    #     raise NotImplementedError(
    #         "3D inverse design feature must be requested from Luminescent AI info@luminescentai.com")

    c.flatten()
    prob = make_prob(
        path,
        component=c,
        layer_stack=layer_stack,
        materials=materials,
        wavelengths=wavelengths,
        study="inverse_design",
        keys=keys,
        path_length_multiple=path_length_multiple,
        **kwargs,
    )

    prob["restart"] = restart
    prob["weights"] = {
        **{
            "tparams": 1,
            "sparams": 1,
            "phasediff": 1,
        },
        **weights,
    }
    prob["save_memory"] = save_memory

    # prob["lvoid"] = lvoid
    # prob["lsolid"] = lsolid
    prob["lmin"] = lmin
    prob["stoploss"] = stoploss
    prob["design_config"] = dict()
    # l = get_layers(layer_stack, fill_layer)[0]
    # d = {"thickness": l.thickness,
    #      "material": matname(l.material), "zmin": l.zmin}
    # d["layer"] = fill_layer
    # prob["design_config"]["fill"] = d

    # if void_layer is not None:
    #     l = get_layers(layer_stack, void_layer)[0]
    #     d = {"thickness": l.thickness, "material": l.material, "zmin": l.zmin}
    #     d["layer"] = void_layer
    #     d["epsilon"] = materials[d["material"]]["epsilon"]
    #     d["epsilon"] = d["epsilon"]
    # else:
    #     d = copy.deepcopy(d)
    #     d["epsilon"] = epsmin
    #     d["epsilon"] = d["epsilon"]
    # prob["design_config"]["void"] = d

    prob["iters"] = iters
    save_problem(prob, path)
    return prob


def Target(
    key,
    target,
    weight,
    param="T",
    frequency=None,
    wl_1_f=None,
    wavelength=None,
    func="abs",
):
    if frequency is not None:
        wavelength = wl_1_f / frequency
    return {
        "param": param,
        "key": str(key),
        "wavelength": wavelength,
        "target": target,
        "weight": weight,
        "func": func,
    }


def apply_design(c0, sol):
    path = sol["path"]
    a = gf.Component()
    a.add_ref(c0)
    fill = sol["design_config"]["fill"]["layer"]
    dl = sol["design_config"]["DESIGN"]
    for i, d in enumerate(sol["designs"]):
        x0, y0 = d["bbox"][0]
        x1, y1 = d["bbox"][1]
        b = gf.Component()
        b.add_polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer=fill)
        a = gf.boolean(a, b, "not", layer=fill)
    c = gf.Component()
    c << a
    # for layer in c0.layers:
    #     if layer != dl:
    #         c.add_ref(c0.extract([layer]))
    # c.show()
    # raise ValueError()
    g = gf.import_gds(os.path.join(path, f"optimized_design_{i+1}.gds"))
    polygons = g.get_polygons(merge=True)
    g = gf.Component()
    for p in polygons[1]:
        g.add_polygon(p, layer=fill)
    g = c << g
    g.xmin = x0
    g.ymin = y0
    return c
