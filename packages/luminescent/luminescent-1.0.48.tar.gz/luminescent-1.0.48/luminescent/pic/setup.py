import platform
import subprocess
from ..constants import *
from ..layers import *
from ..utils import *
from ..materials import *
import json
import gdsfactory as gf
from copy import deepcopy

# from time import time
import datetime
from math import cos, pi, sin
import os
import numpy as np

from sortedcontainers import SortedDict, SortedSet
from gdsfactory.generic_tech import LAYER_STACK, LAYER


def setup(
    path,
    study,
    wavelength,
    wavelengths,
    wl_1_f=None,
    bbox=None,
    boundaries=["PML", "PML", "PML"],
    nres=4,
    dx=None,
    dy=None,
    dz=None,
    component=None,
    z=None,
    # zmargin=None,
    zmin=None,
    zmax=None,
    zmargin_mode=None,
    xmargin_mode=None,
    inset=0,
    port_margin="auto",
    runs=[],
    sources=[],
    layer_stack=SOI220,
    materials=dict(),
    core="core",
    exclude_layers=[],
    Courant=None,
    gpu=None,
    dtype=np.float32,
    saveat=10,
    magic="",
    name=None,
    source_port_margin=0.1,
    modes=None,
    ports=None,
    approx_2D_mode=False,
    show_field="Hz",
    T=None,
    field_decay_threshold=None,
    path_length_multiple=None,
    relative_pml_depths=1,
    relcourant=0.9,
    hasPEC=None,
    keys=None,
    ordering="frequency",
    #
    field_slices=None,
    geometry_slices=None,
    force=False,
    verbose=False,
    pixel_size=0.01,
    secret=None,
    info=None,
):
    # if force:
    #     shutil.rmtree(path, ignore_errors=True)
    # elif os.path.exists(path):
    #     raise FileExistsError(
    #         f"Path {path} already exists. Use force=True to overwrite."
    #     )

    os.makedirs(path, exist_ok=True)
    if info is None:
        info = {}
    json.dump(info, open(os.path.join(path, "info.json"), "w"), indent=4)
    if approx_2D_mode:
        N = 2
    else:
        N = 3
        approx_2D_mode = None

    if inset is None:
        inset = [0] * N

    prob = {
        "nres": nres,
        "wavelength": wavelength,
        "wavelengths": wavelengths,
        "name": name,
        "path": path,
        "keys": keys,
        "show_field": show_field,
        "dx": dx,
        "dy": dy,
        "dz": dz,
        "z": z,
        "T": T,
        "field_decay_threshold": field_decay_threshold,
        "path_length_multiple": path_length_multiple,
        "saveat": saveat,
        "verbose": verbose,
        "field_slices": field_slices,
        "geometry_slices": geometry_slices,
        "boundaries": boundaries[0:N],
        "approx_2D_mode": approx_2D_mode,
        "relative_pml_depths": relative_pml_depths,
        "relcourant": relcourant,
        "hasPEC": hasPEC,
        "ordering": ordering,
        "pixel_size": pixel_size,
        "secret": secret,
    }

    prob["class"] = "pic"
    prob["dtype"] = str(dtype)
    prob["timestamp"] = (
        datetime.datetime.now().isoformat(timespec="seconds").replace(":", "-")
    )
    prob["magic"] = magic

    gpu_backend = gpu
    # if gpu_backend:s
    prob["gpu_backend"] = gpu_backend

    if component is None:
        0
    else:
        c = component
        if ports is None:
            ports = []

        if bbox is None:
            bbox = c.bbox_np()
        l, w = bbox[1] - bbox[0]
        for v in ports:
            if "layer" in v:
                0
            else:
                if "z" in v:
                    v["center"] = (sum(bbox) / 2).tolist() + [v["z"]]
                x, y = v["center"][:2]
                if "length" not in v:
                    v["length"] = l
                if "width" not in v:
                    v["width"] = w
                v["start"] = [-v["length"] / 2, -v["width"] / 2]
                v["stop"] = [+v["length"] / 2, +v["width"] / 2]
                if v["direction"] == "+z":
                    frame = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
                elif v["direction"] == "-z":
                    frame = [[-1, 0, 0], [0, 1, 0], [0, 0, -1]]
                v["frame"] = frame
                v["normal"] = frame[2]
                v["tangent"] = frame[0]

        for p in c.get_ports_list(prefix="o"):
            v = {
                "name": p.name,
                "center": (np.array(p.center) / 1e0).tolist(),
                "normal": [
                    cos(p.orientation / 180 * pi),
                    sin(p.orientation / 180 * pi),
                ],
                "tangent": [
                    -sin(p.orientation / 180 * pi),
                    cos(p.orientation / 180 * pi),
                ],
                "width": p.width / 1e0,
            }
            z, n = [0, 0, 1], [*v["normal"], 0]
            t = np.cross(z, n).tolist()
            v["frame"] = [t, z, n]
            ports.append(v)

        prob["ports"] = ports

        bbox = bbox.tolist()
        bbox[0].append(zmin)
        bbox[1].append(zmax)
        print(f"bbox: {bbox}")
        prob["bbox"] = bbox

        if c and c.get_ports_list():
            d = layer_stack.layers[core]
            hcore = d.thickness
            zcore = d.zmin

            if zmargin_mode is None:
                zmargin_mode = 3 * hcore
            if type(zmargin_mode) in [int, float]:
                zmargin_mode = [zmargin_mode, zmargin_mode]
            # if zmargin is None:
            #     zmargin = [zmargin_mode[0], zmargin_mode[1]]
            # if type(zmargin) in [int, float]:
            #     zmargin = [zmargin, zmargin]

            port_width = max([p.width / 1e0 for p in c.ports])
            if xmargin_mode is None:
                xmargin_mode = port_width
            if type(xmargin_mode) in [int, float]:
                xmargin_mode = [xmargin_mode, xmargin_mode]
            print(f"xmargin_mode: {xmargin_mode}")

            if zmin is None:
                zmin = zcore - 3 * hcore
            if zmax is None:
                zmax = zcore + 4 * hcore

            # h = hcore + zmargin[0] + zmargin[1]
            # zmin = zcore - zmargin[0]
            # zmax = zmin + h
            #
            # xmargin = ymargin = 2*port_width

            wmode = port_width + xmargin_mode[0] + xmargin_mode[1]
            hmode = hcore + zmargin_mode[0] + zmargin_mode[1]
            zmode = zcore - zmargin_mode[0]
            zcenter = zmode + hmode / 2

        layers = set(c.layers) - set(exclude_layers)

        if modes is None:
            modes = [
                {
                    "wavelength_range": [wavelengths[0], wavelengths[-1]],
                    "nmodes": 1,
                }
            ]
        for mode in modes:
            # if "wavelength" in mode:
            #     assert "frequency" not in mode
            #     mode["frequency"] = wl_1_f / mode["wavelength"]
            #     if "bandwidth" in mode:
            #         mode["bandwidth"] *= mode["frequency"] / mode["wavelength"]
            # if "frequency" in mode:
            #     assert "wavelength" not in mode
            #     mode["wavelength"] = wl_1_f / mode["frequency"]
            #     if "bandwidth" in mode:
            #         mode["bandwidth"] *= mode["wavelength"] / mode["frequency"]
            if "frequency_range" in mode:
                mode["wavelength_range"] = [
                    wl_1_f / mode["frequency_range"][1],
                    wl_1_f / mode["frequency_range"][0],
                ]
            if "wavelength_range" not in mode:
                mode["wavelength_range"] = [wavelengths[0], wavelengths[-1]]
            if "ports" not in mode:
                mode["ports"] = None

        MODES = os.path.join(path, "modes")
        os.makedirs(MODES, exist_ok=True)
        GEOMETRY = os.path.join(path, "geometry")
        os.makedirs(GEOMETRY, exist_ok=True)

        layer_stack_info = material_voxelate(
            c, zmin, zmax, layers, layer_stack, materials, GEOMETRY
        )

        dir = os.path.dirname(os.path.realpath(__file__))

        for f in ["solvemodes.py"]:
            fn = os.path.join(dir, f)
            if platform.system() == "Windows":
                os.system(f"copy /Y {fn} {MODES}")
            else:
                subprocess.run(["cp", fn, MODES])
        prob["layer_stack"] = layer_stack_info
        prob["study"] = study
        prob["materials"] = materials

        prob["N"] = N

        for run in runs:
            for k, v in run["sources"].items():
                # p = ports[k]
                p = next((p for p in ports if p["name"] == k), None)
                ct = np.array(p["center"])
                n = np.array(p["normal"])
                v["center"] = (ct + n * source_port_margin).tolist()

                # modes = solve_modes(polys, eps, bbox)
            for k, v in run["monitors"].items():
                p = next((p for p in ports if p["name"] == k), None)
                v["center"] = copy.deepcopy(p["center"])
            for k, v in list(run["sources"].items()) + list(run["monitors"].items()):
                p = next((p for p in ports if p["name"] == k), None)
                v["frame"] = p["frame"]
                if len(v["center"]) == 2:
                    v["center"] += [zcenter]
                    v["start"] = [-wmode / 2, zmode - zcenter]
                    v["stop"] = [wmode / 2, zmode + hmode - zcenter]
                else:
                    v["start"] = p["start"]
                    v["stop"] = p["stop"]
        bg = materials["background"]["epsilon"]
        ime = []
        hasPEC = False
        for f in os.listdir(GEOMETRY):
            i, mat, _ = f[:-4].split("_")
            if mat != "design" and mat != "None":
                if mat != "PEC":
                    eps = materials[mat]["epsilon"]
                else:
                    hasPEC = True
                    eps = "PEC"
                ime.append((int(i), trimesh.load(os.path.join(GEOMETRY, f)), eps))
        mesheps = [x[1:] for x in sorted(ime, key=lambda x: x[0])]
        l = []
        for mode in modes:
            if not mode["ports"]:
                v = runs[0]["monitors"].values()[0]
            else:
                v = runs[0]["monitors"][mode["ports"][0]]
            start = v["start"]
            stop = v["stop"]

            L = stop[0] - start[0]
            W = stop[1] - start[1]
            dl = mode.get("dx", L / 50)
            dx = L / round(L / dl)
            dy = W / round(W / dl)

            if "frequency" not in mode and "wavelength" not in mode:
                mode["wavelength"] = wavelength
            elif "frequency" in mode:
                mode["wavelength"] = wl_1_f / mode["frequency"]

            if "modes" in mode:
                mode["dl"] = [dx, dy]
                for _mode in mode["modes"]:
                    for k, v in _mode.items():
                        if type(v) is np.ndarray:
                            _mode[k] = v.tolist()
                l.append(mode)
            else:
                polyeps = section_mesh(
                    mesheps,
                    v["center"],
                    v["frame"],
                    start,
                    stop,
                    bg,
                )
                # print(f"polyeps: {polyeps}")
                if "PEC_boundaries" in mode:
                    hasPEC = True
                    PEC_boundaries = mode["PEC_boundaries"]
                else:
                    PEC_boundaries = []
                nmodes = mode.get("nmodes", 1)

                wavelength = mode["wavelength"]
                eps = epsilon_from_polyeps(polyeps, bg, start, stop, dx, dy).tolist()
                if hasPEC:
                    _modes = solvemodes_femwell(
                        polyeps,
                        bg,
                        start,
                        stop,
                        wavelength,
                        nmodes,
                        dx,
                        dy,
                        PEC_boundaries,
                    )
                else:
                    _modes = solvemodes(
                        polyeps, bg, start, stop, wavelength, nmodes, dx, dy
                    )
                l.append(
                    {
                        "wavelength_range": mode["wavelength_range"],
                        "modes": _modes,
                        "ports": mode["ports"],
                        "dl": [dx, dy],
                        "epsilon": eps,
                    }
                )
        prob["modes"] = l
        prob["runs"] = runs

    if not os.path.exists(path):
        os.makedirs(path)
    return prob


def port_name(port):
    s = str(port).split("@")[0]
    if s[0] == "o":
        return s
    return f"o{s}"


def port_number(port):
    s = str(port).split("@")[0]
    if s[0] == "o":
        s = s[1:]
    return int(s)


def mode_number(port):
    l = str(port).split("@")
    return 0 if len(l) == 1 else int(l[1])


def unpack_sparam_key(k):
    o, i = k.split(",")
    po, pi = port_name(o), port_name(i)
    mo, mi = mode_number(o), mode_number(i)
    return po, mo, pi, mi


def long_sparam_key(k):
    po, mo, pi, mi = unpack_sparam_key(k)
    return f"{po}@{mo},{pi}@{mi}"
