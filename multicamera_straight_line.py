import omni.replicator.core as rep
import random
import numpy as np
import os
import time
import math

BASE_ASSET_PATH = "/home/dplaskowski/agriverse/assets"

# Asset paths
ground_texture_paths = [
    f"{BASE_ASSET_PATH}/ground_textures/486590016_2143743766076614_2329454132937694831_n.png",
    f"{BASE_ASSET_PATH}/ground_textures/486978910_512422181731889_3381190367532928363_n.png",
    f"{BASE_ASSET_PATH}/ground_textures/488056794_642492435307013_1374426906719078429_n.png",
    f"{BASE_ASSET_PATH}/ground_textures/486725803_564571109371053_7183455364924371124_n.png",
    f"{BASE_ASSET_PATH}/ground_textures/487167218_9229572443837596_8958125524851478214_n.png",
    f"{BASE_ASSET_PATH}/ground_textures/488263029_1302147840883122_3978944319888097400_n.png",
    f"{BASE_ASSET_PATH}/ground_textures/486729343_676780248081594_7178959974179628579_n.png",
    f"{BASE_ASSET_PATH}/ground_textures/487746900_1686458001949542_7826165021854998275_n.png",
    f"{BASE_ASSET_PATH}/ground_textures/488459592_1589242651784029_6466095666272622201_n.png",
    f"{BASE_ASSET_PATH}/ground_textures/486748942_1387703095721247_2957283942765703619_n.png",
    f"{BASE_ASSET_PATH}/ground_textures/487845587_1036671345004830_4547011872904205828_n.png",
    f"{BASE_ASSET_PATH}/ground_textures/ground1.png",
    f"{BASE_ASSET_PATH}/ground_textures/486755080_1866743813864935_2219864280417093259_n.png",
    f"{BASE_ASSET_PATH}/ground_textures/488039696_1175115740791319_3247926840392435978_n.png"
]

maize_usd_paths = [
    f"{BASE_ASSET_PATH}/Cropcraft/plants/maize/maize_medium.usd",
    f"{BASE_ASSET_PATH}/Cropcraft/plants/maize/maize_small.usd",
]

weed_usd_with_weights = [
    (f"{BASE_ASSET_PATH}/Cropcraft/plants/taraxacum/taraxacum_01.usd", 0.4),
    (f"{BASE_ASSET_PATH}/Cropcraft/plants/taraxacum/taraxacum_02.usd", 0.3),
    (f"{BASE_ASSET_PATH}/Cropcraft/plants/taraxacum/taraxacum_03.usd", 0.2),
    (f"{BASE_ASSET_PATH}/Cropcraft/plants/taraxacum/taraxacum_04.usd", 0.1),
    (f"{BASE_ASSET_PATH}/Cropcraft/plants/taraxacum/taraxacum_05.usd", 0.0),
    (f"{BASE_ASSET_PATH}/Cropcraft/plants/taraxacum/taraxacum_06.usd", 0.0),
    (f"{BASE_ASSET_PATH}/Cropcraft/plants/taraxacum/taraxacum_07.usd", 0.0),
]

# Separate lists for convenience if needed elsewhere, though not used directly for weighted sampling
weed_usd_paths = [path for path, weight in weed_usd_with_weights]
weed_sampling_weights = [weight for path, weight in weed_usd_with_weights]

# assert sum(weed_sampling_weights) == 1.0

class SceneConfig:
    """Global parameters for the field and capture pipeline."""

    # Plant layout
    NUM_PLANTS_PER_COLUMN = 8
    NUM_COLUMNS = 3
    COLUMN_DELTA = 19.0  # spacing between columns
    PLANT_SPACING = 10.0  # spacing between plants inside a column
    NUM_WEEDS = 35
    SCALE = 20.0
    COLUMN_ORIENTATION = "horizontal"  # or "vertical"

    # Vehicle‑like camera sweep parameters (all relative 0‑1 inside field bounds)
    LINE_START_REL = (0.05, 0.10)   # near bottom‑left
    LINE_END_REL   = (0.95, 0.10)   # move straight along +X (sim vehicle)
    NUM_CAMERAS = 12                 # how many snapshots along the line
    CAMERA_JITTER_REL = 0.015       # sideways jitter relative to field size

    # Camera intrinsics / extrinsics
    CAMERA_HEIGHT = 75.0
    CAMERA_ANGLE = -90.0  # nadir view; change for oblique
    CAMERA_FOCAL_LENGTH = 35.0
    CAMERA_FOCUS_DISTANCE = 75.0
    CAMERA_F_STOP = 4.0

    # Lighting
    LIGHT_INTENSITY = 1000.0

    # Output
    OUTPUT_DIR = "/home/dplaskowski/agriverse/data_output"
    RESOLUTION = (640, 640)

    @classmethod
    def field_dims(cls):
        if cls.COLUMN_ORIENTATION == "horizontal":
            length = cls.NUM_COLUMNS * cls.COLUMN_DELTA
            width = cls.NUM_PLANTS_PER_COLUMN * cls.PLANT_SPACING
        else:
            length = cls.NUM_PLANTS_PER_COLUMN * cls.PLANT_SPACING
            width = cls.NUM_COLUMNS * cls.COLUMN_DELTA
        start_x = -width / 2.0
        start_y = -length / 2.0
        return dict(width=width, length=length, start_x=start_x, start_y=start_y)


def create_plants(field):
    maize, weeds = [], []

    # maize grid
    for c in range(SceneConfig.NUM_COLUMNS):
        for r in range(SceneConfig.NUM_PLANTS_PER_COLUMN):
            if SceneConfig.COLUMN_ORIENTATION == "horizontal":
                x = field["start_x"] + r * SceneConfig.PLANT_SPACING
                y = field["start_y"] + c * SceneConfig.COLUMN_DELTA
            else:
                x = field["start_x"] + c * SceneConfig.COLUMN_DELTA
                y = field["start_y"] + r * SceneConfig.PLANT_SPACING
            
            z_rotation = np.random.uniform(0, 360)
            m = rep.create.from_usd(random.choice(maize_usd_paths), semantics=[("class", "maize")])
            with m:
                rep.modify.pose(position=(x, y, 0),
                                scale=SceneConfig.SCALE,
                                rotation=(0, 0, z_rotation))
                
                
            maize.append(m)

    # weeds random
    rx_min = field["start_x"] - SceneConfig.PLANT_SPACING / 2
    rx_max = field["start_x"] + field["width"] - SceneConfig.PLANT_SPACING / 2
    ry_min = field["start_y"] - SceneConfig.COLUMN_DELTA / 2
    ry_max = field["start_y"] + field["length"] - SceneConfig.COLUMN_DELTA / 2

    for _ in range(SceneConfig.NUM_WEEDS):
        wx = np.random.uniform(rx_min, rx_max)
        wy = np.random.uniform(ry_min, ry_max)

        chosen_weed_usd = random.choices(weed_usd_paths, weights=weed_sampling_weights, k=1)[0]

        w = rep.create.from_usd(chosen_weed_usd,
                                semantics=[("class", "weed")])
        
        z_rotation = np.random.uniform(0, 360)
        with w:
            rep.modify.pose(position=(wx, wy, 0),
                            scale=SceneConfig.SCALE,
                            rotation=(0, 0, z_rotation))


        weeds.append(w)

    return maize, weeds


def compute_camera_positions(field):
    # absolute start / end
    sx = field["start_x"] + field["width"]  * SceneConfig.LINE_START_REL[0]
    sy = field["start_y"] + field["length"] * SceneConfig.LINE_START_REL[1]
    ex = field["start_x"] + field["width"]  * SceneConfig.LINE_END_REL[0]
    ey = field["start_y"] + field["length"] * SceneConfig.LINE_END_REL[1]

    dx, dy = ex - sx, ey - sy
    # perpendicular (normalized)
    perp_len = math.hypot(dx, dy)
    if perp_len == 0:
        perp = (0.0, 0.0)
    else:
        perp = (-dy / perp_len, dx / perp_len)
    jitter_abs = SceneConfig.CAMERA_JITTER_REL * min(field["width"], field["length"])  # metres

    positions = []
    for i in range(SceneConfig.NUM_CAMERAS):
        t = i / (SceneConfig.NUM_CAMERAS - 1)
        cx = sx + t * dx
        cy = sy + t * dy
        j = random.uniform(-jitter_abs, jitter_abs)
        cx += perp[0] * j
        cy += perp[1] * j
        positions.append((cx, cy, SceneConfig.CAMERA_HEIGHT))
    return positions


def main():
    print("Synthetic dataset generation – straight‑line camera sweep")
    field = SceneConfig.field_dims()
    print("Field dims:", field)

    with rep.new_layer():
        # ground
        g = rep.create.plane(scale=1000,position=(0, 0, 0))
        with g:
            rep.randomizer.texture(textures=[random.choice(ground_texture_paths)])

        # vegetation
        create_plants(field)

        # cameras
        cam_positions = compute_camera_positions(field)
        render_products = []
        for idx, pos in enumerate(cam_positions):
            cam = rep.create.camera(
                position=pos,
                rotation=(0, SceneConfig.CAMERA_ANGLE, 0),
                focal_length=SceneConfig.CAMERA_FOCAL_LENGTH,
                focus_distance=SceneConfig.CAMERA_FOCUS_DISTANCE,
                f_stop=SceneConfig.CAMERA_F_STOP,
                name=f"Cam_{idx:02d}",
            )
            rp = rep.create.render_product(cam, SceneConfig.RESOLUTION)
            render_products.append(rp)
        print(f"Created {len(render_products)} cameras along path")

        # lighting (simple dome)
        rep.create.light(light_type="Dome", intensity=SceneConfig.LIGHT_INTENSITY)

        # writer
        run_id = time.strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(SceneConfig.OUTPUT_DIR, run_id)
        os.makedirs(out_path, exist_ok=True)
        writer = rep.WriterRegistry.get("BasicWriter")
        writer.initialize(output_dir=out_path, rgb=True, bounding_box_2d_tight=True, semantic_segmentation=True)
        writer.attach(render_products)
        print("Output dir:", out_path)

        rep.orchestrator.run(num_frames=1)
        print("Done: cameras capture")


if __name__ == "__main__":
    main()