from .setup import *
from ..constants import *
from ..layers import *
from ..utils import *
import gdsfactory as gf
from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np
import math

from gdsfactory.cross_section import Section
from gdsfactory.generic_tech import LAYER_STACK, LAYER


def make_prob(
    path,
    component=None,
    wavelengths=None,
    wavelength=None,
    entries=None,
    keys=["2,1"],
    study="sparams",
    nres=4,
    sources=None,
    monitors=None,
    frequencies=None,
    wl_1_f=None,
    modes=None,
    #
    layer_stack={},
    materials=MATERIALS,
    verbose=True,
    #
    targets=None,
    symmetries=[],
    # design_layer=DESIGN,
    init_pattern_level=None,
    init_pattern_spacing=None,
    init_pattern_diameter=None,
    init_grayscale=True,
    area_change=0.01,
    fill_material=None,
    void_material=None,
    iters=None,
    lmin=None,
    stoploss=None,
    design_ports=None,
    #
    path_length_multiple=0.85,
    approx_2D_mode=None,
    pixel_size=0.01,
    info=None,
    **kwargs
):
    if approx_2D_mode:
        N = 2
    else:
        N = 3

    if wl_1_f is None:
        ordering = "wavelength"
    else:
        ordering = "frequency"

    if targets is not None:
        study = "inverse_design"
        design_layer = layer_stack["design"].layer.layer
        if "relative_mesh_density" not in materials["design"]:
            materials["design"]["relative_mesh_density"] = math.sqrt(
                materials[fill_material]["epsilon"]
            )

        keys = SortedSet()
        b = wavelengths is None
        if b:
            wavelengths = SortedSet()
        for d in targets:
            if b:
                wavelengths.add(d["wavelength"])
            keys.add(d["key"])
        keys = list(keys)

    if frequencies is not None:
        assert wl_1_f is not None
        assert wavelengths is None
        wavelengths = [wl_1_f / f for f in frequencies]

    if type(wavelengths) in [int, float]:
        wavelengths = [wavelengths]
    wavelengths = sorted(wavelengths)
    if wavelength is None:
        wavelength = median(wavelengths)
    # nres *= wavelength / min(map(min, wavelengths))

    if not entries:
        entries = []

        for w in wavelengths:
            for k in keys:
                try:
                    entries.append([w, *unpack_sparam_key(k)])
                except Exception as e:
                    0
    l = []
    for w, po, mo, pi, mi in entries:
        k = [w, pi, mi, pi, mi]
        if k not in entries:
            l.append(k)
    entries.extend(l)

    imow = {}
    for w, po, mo, pi, mi in entries:
        if pi not in imow:
            imow[pi] = {}
        if mi not in imow[pi]:
            imow[pi][mi] = {}

        if po not in imow[pi][mi]:
            imow[pi][mi][po] = mo
        else:
            imow[pi][mi][po] = max(imow[pi][mi][po], mo)

    runs = []
    for _w in [1]:
        for i in imow:
            for mi in imow[i]:
                d = {
                    "sources": {
                        i: {
                            "wavelength_mode_numbers": [[w, [mi]] for w in wavelengths],
                        }
                    },
                    "monitors": {
                        o: {
                            "wavelength_mode_numbers": [
                                [w, list(range(imow[i][mi][o] + 1))]
                                for w in wavelengths
                            ],
                        }
                        for o in imow[i][mi]
                    },
                }
                d["sources"] = SortedDict(d["sources"])
                d["monitors"] = SortedDict(d["monitors"])
                if component is None:
                    0
                else:
                    runs.append(d)

    prob = setup(
        path,
        component=component,
        study=study,
        wavelength=wavelength,
        wl_1_f=wl_1_f,
        wavelengths=wavelengths,
        runs=runs,
        layer_stack=layer_stack,
        materials=materials,
        modes=modes,
        verbose=verbose,
        keys=keys,
        ordering=ordering,
        nres=nres,
        approx_2D_mode=approx_2D_mode,
        pixel_size=pixel_size,
        info=info,
        #  sources=sources, monitors=monitors,
        **kwargs
    )

    if targets:
        polys = component.extract([design_layer]).get_polygons()
        if not symmetries:
            symmetries = [[]] * len(polys)
        else:
            if type(symmetries[0]) is not list:
                symmetries = [symmetries] * len(polys)

        def _bbox(b):
            return [[b.left / 1e3, b.bottom / 1e3], [b.right / 1e3, b.top / 1e3]]

        ks = set(materials[fill_material].keys()).intersection(
            set(materials[void_material].keys())
        )
        swaps = {
            k: (materials[void_material][k], materials[fill_material][k]) for k in ks
        }
        designs = []
        for p, s in zip(list(polys.values())[0], symmetries):
            bbox = _bbox(p.bbox())
            if N == 3:
                l = get_layers(layer_stack, design_layer)[0]
                bbox[0].append(l.zmin)
                bbox[1].append(l.zmin + l.thickness)
            designs.append(
                {
                    "bbox": bbox,
                    "swaps": swaps,
                    "symmetries": s,
                }
            )
        prob = {
            **prob,
            **{
                "targets": targets,
                "designs": designs,
                "init_pattern_level": init_pattern_level,
                "init_pattern_spacing": init_pattern_spacing,
                "init_pattern_diameter": init_pattern_diameter,
                "init_grayscale": init_grayscale,
                "area_change": area_change,
                "iters": iters,
                "lmin": lmin,
                "stoploss": stoploss,
                "path_length_multiple": path_length_multiple,
                "design_ports": design_ports,
            },
        }
    save_problem(prob, path)
    return prob

    # l = [k for k in imow if port_number(k) == pi]
    # if not l:
    #     imow[f"o{pi}@{mi}"] = []
    # else:
    #     k = l[0]
    #     mn = max(mode_number(k), mi)
    #     if mn != mode_number(k):
    #         imow[i] = imow[k]
    #         del imow[k]

    # l = [k for k in imow[i] if port_number(k) == po]
    # if not l:
    #     imow[f"o{pi}@{mi}"]
    # else:
    #     k = l[0]
    #     mn = max(mode_number(k), mi)
    #     if mn != mode_number(k):
    #         imow[f"o{pi}@{mn}"] = imow[k]
    #         del imow[k]

    # if po not in imow[pi]:
    #     imow[pi]["o"][po] = mo
    # else:
    #     imow[pi]["o"][po] = max(imow[pi]["o"][po], mo)
