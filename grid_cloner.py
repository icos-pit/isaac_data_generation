# field_scene.py  – 400 maize + weighted taraxacum weeds + semantics

from isaacsim.core.utils.stage import add_reference_to_stage, get_current_stage
from isaacsim.core.cloner      import Cloner
from omni.isaac.core.prims     import XFormPrimView
import omni.replicator.core as rep
import numpy as np, random

BASE = "/home/dplaskowski/agriverse/assets"

# ─────────────────── parameters ───────────────────
weed_usd_with_weights = [
    (f"{BASE}/Cropcraft/plants/taraxacum/taraxacum_05.usd", 0.4),
    (f"{BASE}/Cropcraft/plants/taraxacum/taraxacum_07.usd", 0.3),
    (f"{BASE}/Cropcraft/plants/taraxacum/taraxacum_06.usd", 0.2),
    (f"{BASE}/Cropcraft/plants/taraxacum/taraxacum_04.usd", 0.1),
]
N_WEEDS          = 3_000
WEED_SCALE_RANGE = (2.0, 4.0)

# ─────────────────── maize grid ───────────────────
SRC_MAIZE = "/World/Maize_0"
add_reference_to_stage(f"{BASE}/Cropcraft/plants/maize/maize_small.usd", SRC_MAIZE)

rows, cols, step = 20, 20, 14
tot = rows * cols
xs  = np.linspace(-(cols-1)*step/2, (cols-1)*step/2, cols)
ys  = np.linspace(-(rows-1)*step/2, (rows-1)*step/2, rows)
xx, yy = np.meshgrid(xs, ys)
maize_pos = np.stack([xx.ravel(), yy.ravel(), np.zeros(tot)], -1).astype(np.float32)

cloner = Cloner()
maize_paths = cloner.generate_paths("/World/Maize", tot)
cloner.clone(SRC_MAIZE, maize_paths, positions=maize_pos)
XFormPrimView("/World/Maize_*").set_local_scales(
    np.repeat(np.random.uniform(10, 20, (tot, 1)), 3, 1)
)

# ─────────────────── weeds – same cloning pattern as maize ───────────────────
variants, weights = zip(*weed_usd_with_weights)
counts = np.round(np.array(weights) * N_WEEDS).astype(int)
counts[-1] += N_WEEDS - counts.sum()          # fix rounding drift

bbox_x = (-step*(cols-1)/2,  step*(cols-1)/2)
bbox_y = (-step*(rows-1)/2,  step*(rows-1)/2)

weed_paths = []
for v, (usd, n_clones) in enumerate(zip(variants, counts)):
    if n_clones == 0:
        continue

    # source prim for this variant
    src = f"/World/_WeedSrc_{v}"
    add_reference_to_stage(usd, src)

    # random positions for this variant
    pos = np.column_stack([
        np.random.uniform(*bbox_x, n_clones),
        np.random.uniform(*bbox_y, n_clones),
        np.zeros(n_clones, dtype=np.float32)
    ])

    # clone exactly like maize
    paths = cloner.generate_paths(f"/World/Weed{v}", n_clones)
    cloner.clone(src, paths, positions=pos)
    weed_paths.extend(paths)

# scale all weeds at once
XFormPrimView("/World/Weed_*").set_local_scales(
    np.repeat(np.random.uniform(*WEED_SCALE_RANGE, (N_WEEDS, 1)), 3, 1)
)

# ─────────────────── semantic labels ───────────────────
stage = get_current_stage()
rep.modify.semantics([("class", "maize")], input_prims=[stage.GetPrimAtPath(p) for p in maize_paths])
rep.modify.semantics([("class", "weed")],  input_prims=[stage.GetPrimAtPath(p) for p in weed_paths])

# ─────────────────── ground plane with random texture each frame ───────────────────
ground_texture_paths = [
    f"{BASE}/ground_textures/{name}" for name in (
        "ground1.png",
        "486748942_1387703095721247_2957283942765703619_n.png",
        "487845587_1036671345004830_4547011872904205828_n.png",
        "488039696_1175115740791319_3247926840392435978_n.png",
    )
]

with rep.new_layer():
    plane = rep.create.plane(scale=1000, position=(0, 0, 0))
    with plane:
        rep.randomizer.texture(textures=rep.distribution.choice(ground_texture_paths))

