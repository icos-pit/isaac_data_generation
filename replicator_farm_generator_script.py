import omni.replicator.core as rep
import random
import numpy as np

# Asset paths
ground_texture_paths = [
    "omniverse://localhost/Library/Assets/Ground textures/486590016_2143743766076614_2329454132937694831_n.png",
    "omniverse://localhost/Library/Assets/Ground textures/486725803_564571109371053_7183455364924371124_n.png",
    "omniverse://localhost/Library/Assets/Ground textures/486729343_676780248081594_7178959974179628579_n.png",
    "omniverse://localhost/Library/Assets/Ground textures/487167218_9229572443837596_8958125524851478214_n.png",
    "omniverse://localhost/Library/Assets/Ground textures/486748942_1387703095721247_2957283942765703619_n.png",
]

maize_usd_paths = [
    "omniverse://localhost/Library/Assets/Vegetation/Cropcraft/plants/maize/maize_big_1.usd",
    "omniverse://localhost/Library/Assets/Vegetation/Cropcraft/plants/maize/maize_big_2.usd",
    "omniverse://localhost/Library/Assets/Vegetation/Cropcraft/plants/maize/maize_big_3.usd",
    "omniverse://localhost/Library/Assets/Vegetation/Cropcraft/plants/maize/maize_medium.usd",
    "omniverse://localhost/Library/Assets/Vegetation/Cropcraft/plants/maize/maize_small.usd"
]

weed_usd_paths = [
    "omniverse://localhost/Library/Assets/Vegetation/Cropcraft/plants/taraxacum/taraxacum_01.usd",
    "omniverse://localhost/Library/Assets/Vegetation/Cropcraft/plants/taraxacum/taraxacum_02.usd",
    "omniverse://localhost/Library/Assets/Vegetation/Cropcraft/plants/taraxacum/taraxacum_03.usd",
    "omniverse://localhost/Library/Assets/Vegetation/Cropcraft/plants/taraxacum/taraxacum_04.usd",
    "omniverse://localhost/Library/Assets/Vegetation/Cropcraft/plants/taraxacum/taraxacum_05.usd",
    "omniverse://localhost/Library/Assets/Vegetation/Cropcraft/plants/taraxacum/taraxacum_06.usd",
    "omniverse://localhost/Library/Assets/Vegetation/Cropcraft/plants/taraxacum/taraxacum_07.usd"
]

# Configuration parameters
class SceneConfig:
    NUM_SCENES = 2              # Number of unique scenes to generate
    NUM_PLANTS_PER_COLUMN = 3
    NUM_COLUMNS = 2
    COLUMN_DELTA = 15
    PLANT_SPACING = 15.0
    EPS_RANGE = 1.4              # Random position offset range
    NUM_WEEDS = 5
    COLUMN_ORIENTATION = "horizontal"  # "horizontal" or "vertical"
    
    # Camera settings
    CAMERA_HEIGHT = 150
    CAMERA_ANGLE = -90           # Degrees
    CAMERA_FOCAL_LENGTH = 35
    CAMERA_FOCUS_DISTANCE = 150
    CAMERA_F_STOP = 4.0
    
    # Light settings
    LIGHT_HEIGHT = 100
    LIGHT_INTENSITY = 1000
    LIGHT_ROTATION = (315, 0, 0)
    
    # Output settings
    OUTPUT_DIR = "_output/yolo_dataset"
    RESOLUTION = (640, 480)
    
    @classmethod
    def calculate_field_dimensions(cls):
        if cls.COLUMN_ORIENTATION == "horizontal":
            field_length = cls.NUM_COLUMNS * cls.COLUMN_DELTA
            field_width = cls.NUM_PLANTS_PER_COLUMN * cls.PLANT_SPACING
        else:  # vertical
            field_length = cls.NUM_PLANTS_PER_COLUMN * cls.PLANT_SPACING
            field_width = cls.NUM_COLUMNS * cls.COLUMN_DELTA
            
        field_start_x = -field_width / 2
        field_start_y = -field_length / 2
        
        return {
            "field_length": field_length,
            "field_width": field_width, 
            "field_start_x": field_start_x,
            "field_start_y": field_start_y
        }


def create_farm_scene():
    # Calculate field dimensions
    field_dims = SceneConfig.calculate_field_dimensions()
    
    with rep.new_layer():
        # Create ground plane
        ground_plane = rep.create.plane(scale=100, position=(0, 0, 0))
        
        # Create references to store our plants
        maize_plants = []
        weed_plants = []
        
        # Create maize plants in rows/columns
        for col in range(SceneConfig.NUM_COLUMNS):
            for row in range(SceneConfig.NUM_PLANTS_PER_COLUMN):
                if SceneConfig.COLUMN_ORIENTATION == "horizontal":
                    x = field_dims["field_start_x"] + row * SceneConfig.PLANT_SPACING
                    y = field_dims["field_start_y"] + col * SceneConfig.COLUMN_DELTA
                else:  # vertical
                    x = field_dims["field_start_x"] + col * SceneConfig.COLUMN_DELTA
                    y = field_dims["field_start_y"] + row * SceneConfig.PLANT_SPACING
                
                # Random position offset
                x_offset = 0  # Will be randomized in the randomization function
                y_offset = 0  # Will be randomized in the randomization function
                
                # Create a random maize plant
                maize_plant = rep.create.from_usd(
                    random.choice(maize_usd_paths)
                )
                # Set initial position
                maize_plant.set_position((x + x_offset, y + y_offset, 0))
                # Set initial scale
                maize_plant.set_scale(1.0)  # Will be randomized in the randomization function
                # Set initial rotation
                maize_plant.set_rotation((0, 0, 0))  # Will be randomized in the randomization function
                
                maize_plants.append(maize_plant)
        
        # Create random weeds
        for _ in range(SceneConfig.NUM_WEEDS):
            # Random position within field boundaries
            x = np.random.uniform(field_dims["field_start_x"], field_dims["field_start_x"] + field_dims["field_width"])
            y = np.random.uniform(field_dims["field_start_y"], field_dims["field_start_y"] + field_dims["field_length"])
            
            # Create a random weed plant
            weed_plant = rep.create.from_usd(
                random.choice(weed_usd_paths)
            )
            # Set initial position
            weed_plant.set_position((x, y, 0))
            # Set initial scale
            weed_plant.set_scale(1.0)  # Will be randomized in the randomization function
            # Set initial rotation
            weed_plant.set_rotation((0, 0, 0))  # Will be randomized in the randomization function
            
            weed_plants.append(weed_plant)
            
        # Create light
        light = rep.create.light(
            light_type="distant", 
            position=(0, 0, SceneConfig.LIGHT_HEIGHT), 
            intensity=SceneConfig.LIGHT_INTENSITY, 
            rotation=SceneConfig.LIGHT_ROTATION
        )
        
        # Create camera and render product
        camera = rep.create.camera(
            position=(0, 0, SceneConfig.CAMERA_HEIGHT),
            rotation=(0, SceneConfig.CAMERA_ANGLE, 0),
            focal_length=SceneConfig.CAMERA_FOCAL_LENGTH,
            focus_distance=SceneConfig.CAMERA_FOCUS_DISTANCE,
            f_stop=SceneConfig.CAMERA_F_STOP,
            name="MyCamera"
        )
        
        # Create render product
        render_product = rep.create.render_product(camera, resolution=SceneConfig.RESOLUTION)
        
        # Attach writer to save RGB images and bounding box annotations
        writer = rep.WriterRegistry.get("BasicWriter")
        writer.initialize(
            output_dir=SceneConfig.OUTPUT_DIR,
            rgb=True,
            bounding_box_2d_tight=True
        )
        
        # Define randomization function
        def randomize_scene():
            # Randomize ground texture
            with ground_plane:
                random_texture_path = random.choice(ground_texture_paths)
                rep.randomizer.texture(textures=[random_texture_path])
            
            # Randomize maize plants
            for plant in maize_plants:
                with plant:
                    # Randomize position slightly
                    original_pos = plant.get_attribute("xformOp:translate")
                    x_offset = np.random.uniform(-SceneConfig.EPS_RANGE, SceneConfig.EPS_RANGE)
                    y_offset = np.random.uniform(-SceneConfig.EPS_RANGE, SceneConfig.EPS_RANGE)
                    new_pos = (original_pos[0] + x_offset, original_pos[1] + y_offset, original_pos[2])
                    plant.set_position(new_pos)
                    
                    # Randomize scale slightly
                    scale_factor = np.random.uniform(0.8, 1.2)
                    plant.set_scale(scale_factor)
                    
                    # Randomize rotation (only around z-axis)
                    z_rotation = np.random.uniform(0, 360)
                    plant.set_rotation((0, 0, z_rotation))
                    
                    # Randomly select a different maize model
                    random_model = random.choice(maize_usd_paths)
                    # In Replicator, we can't easily change the USD path after creation
                    # We would need to destroy and recreate the object instead
            
            # Randomize weed plants
            for plant in weed_plants:
                with plant:
                    # Randomize position (more freedom for weeds)
                    x = np.random.uniform(field_dims["field_start_x"], field_dims["field_start_x"] + field_dims["field_width"])
                    y = np.random.uniform(field_dims["field_start_y"], field_dims["field_start_y"] + field_dims["field_length"])
                    plant.set_position((x, y, 0))
                    
                    # Randomize scale
                    scale_factor = np.random.uniform(0.6, 1.4)
                    plant.set_scale(scale_factor)
                    
                    # Randomize rotation
                    z_rotation = np.random.uniform(0, 360)
                    plant.set_rotation((0, 0, z_rotation))
                    
                    # Randomly select a different weed model
                    random_model = random.choice(weed_usd_paths)
                    # In Replicator, we can't easily change the USD path after creation
                    # We would need to destroy and recreate the object instead
            
            # Randomize camera parameters
            with camera:
                # Randomize camera height slightly
                height_offset = np.random.uniform(-10, 10)
                camera.set_position((0, 0, SceneConfig.CAMERA_HEIGHT + height_offset))
                
                # Randomize camera angle slightly
                angle_offset = np.random.uniform(-5, 5)
                camera.set_rotation((0, SceneConfig.CAMERA_ANGLE + angle_offset, 0))
            
            # Randomize light
            with light:
                # Randomize light intensity
                intensity = np.random.uniform(800, 1200)
                light.set_intensity(intensity)
                
                # Randomize light position slightly
                x_offset = np.random.uniform(-20, 20)
                y_offset = np.random.uniform(-20, 20)
                light.set_position((x_offset, y_offset, SceneConfig.LIGHT_HEIGHT))
        
        # Register randomizer
        rep.randomizer.register(randomize_scene)
        
        # Trigger randomization for multiple frames
        with rep.trigger.on_frame(max_execs=SceneConfig.NUM_SCENES):
            rep.randomizer.randomize_scene()


if _name_ == "_main_":
    create_farm_scene()