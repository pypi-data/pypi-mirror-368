import os
import json
import sys
import argparse

from pytvpaint import george
from pytvpaint.project import Project

project = Project.current_project()
clip = project.current_clip

# --------------------------------------#
# ------ Creating Groups Function ------#
# --------------------------------------#


def create_group(layer_color_index, group_name, rgb):
    color_group = clip.get_layer_color(layer_color_index)
    if group_name:
        color_group.name = group_name
    if rgb:
        rgb_color = george.RGBColor
        rgb_color.r = rgb[0]
        rgb_color.g = rgb[1]
        rgb_color.b = rgb[2]
        color_group.color = rgb_color

    return color_group


# --------------------------------------#
# ------- Import Layers Function -------#
# --------------------------------------#


def import_layers(folder_path, layer_color_index, group_name=None, rgb=None):
    folder_content = os.listdir(folder_path)

    for file in folder_content:
        file_path = os.path.join(folder_path, file)
        if os.path.splitext(file_path)[1] == ".json":
            with open(file_path) as f:
                data = json.load(f)
                layers = data["layers"]
                hidden_layers = data["hidden_layers"]
            break

    color_group = create_group(layer_color_index, group_name, rgb)

    for l in layers:
        folder_name = os.path.split(folder_path)
        file = folder_name[1] + "-" + l + ".png" #l.replace(" ", "-")
        file_path = os.path.join(folder_path, file)
        if os.path.exists(file_path):
            layer_name = group_name + "_" + l

            print(f"[SCENE BUILDER] - Importing : {file}")

            layer = clip.add_layer(layer_name)
            layer.color = color_group
            layer.load_image(file_path, frame=0)
            layer.post_behavior= george.LayerBehavior.HOLD

            if layers.index(l) == 0:
                layer.position = 0

            if l == "characters":
                layer.position = start_layer.position

            if l in hidden_layers:
                layer.is_visible = False


# ------------------------------------------------#
# -- Get layers folders from LayoutBG & ColorBG --#
# ------------------------------------------------#


def process_remaining_args(args):
    parser = argparse.ArgumentParser(description="TVPaint Project Template Arguments")
    parser.add_argument("--animatic-path", dest="animatic_path")
    parser.add_argument("--layoutbg-path", dest="layoutbg_path")
    parser.add_argument("--colorbg-path", dest="colorbg_path")
    parser.add_argument("--audio-path", dest="audio_path")
    parser.add_argument("--width", dest="width")
    parser.add_argument("--height", dest="height")

    values, _ = parser.parse_known_args(args)

    return (values.animatic_path, values.layoutbg_path, values.colorbg_path, values.audio_path, values.width, values.height)


ANIMATIC_PATH, LAYOUTBG_PATH, COLORBG_PATH, AUDIO_PATH, PROJECT_WIDTH, PROJECT_HEIGHT = process_remaining_args(
    sys.argv
)

# ----------------------------#
# -------- Set Camera --------#
# ----------------------------#

# TODO : SET PROJECT SIZE TO PSD FILE SIZE THEN CAMERA TO PROJECT SIZE
# centrer le cadre et laisser le graphise aligner la caméra sur le background

project_width = 2048 if PROJECT_WIDTH == "None" else float(PROJECT_WIDTH)

project_height = 858 if PROJECT_HEIGHT == "None" else float(PROJECT_HEIGHT)

project = Project.current_project()
clip = project.current_clip
camera = clip.camera
print("[SCENE BUILDER] Set camera resolution to 2048x858")
george.tv_camera_info_set(width=2048, height=858)


# ---------------------------------#
# -------- Import animatic --------#
# ---------------------------------#

project = project.resize(2048, 872, overwrite=True)
project = Project.current_project()
clip = project.current_clip

filename = os.path.split(os.path.splitext(ANIMATIC_PATH)[0])[1]

img_seq = clip.load_media(media_path=ANIMATIC_PATH, with_name=f"Animatic_{filename}", preload=True)
img_seq.color = clip.get_layer_color(by_index=11)

print(f"[SCENE BUILDER] Resize project to {project_width}x{project_height}")
project = project.resize(project.width*2, project.height*2, overwrite=True)
project = Project.current_project()
clip = project.current_clip


# --------------------------------#
# -------- Resize Project --------#
# --------------------------------#


project = project.resize(project_width, project_height, overwrite=True, resize_opt= george.ResizeOption.CROP)

project = Project.current_project()
clip = project.current_clip
camera = clip.camera

print("[SCENE BUILDER] Set camera position to center")
camera.get_point_data_at(0)
george.tv_camera_set_point(0, project_width / 2, project_height / 2, 0, scale=1)


# ----------------------------------#
# -------- Creating Groups ---------#
# ----------------------------------#

print("[SCENE BUILDER] Create Color group")
create_group(1, "Color", [255, 255, 0])
print("[SCENE BUILDER] Create Clean & Inbetween group")
create_group(2, "Clean & Inbetween", [0, 87, 234])
print("[SCENE BUILDER] Create FX_RA & TD group")
create_group(3, "FX_RA & TD", [0, 146, 0])
print("[SCENE BUILDER] Create RA & TD characters group")
create_group(4, "RA & TD characters", [0, 255, 255])
print("[SCENE BUILDER] Create Posing & FX Posing group")
create_group(5, "Posing & FX Posing", [214, 124, 171])
print("[SCENE BUILDER] Create BG group")
create_group(7, "BG", [205, 33, 33])
print("[SCENE BUILDER] Create Notes & Corrections group")
create_group(8, "Notes & Corrections", [240, 128, 20])
print("[SCENE BUILDER] Create Director's Notes and Corrections group")
create_group(9, "Director's Notes and Corrections", [0, 0, 0])
print("[SCENE BUILDER] Create Guides & References group")
create_group(10, "Guides & References", [255,255,255])
print("[SCENE BUILDER] Create Animatic group")
create_group(11, "Animatic", [167, 63, 239])


# ----------------------------------#
# -------- Importing Layers --------#
# ----------------------------------#

start_layer = clip.get_layer(by_name='Anim_01')

print("[SCENE BUILDER] Import BG_Layout layers")
import_layers(LAYOUTBG_PATH, 6, "OL & UL", [205, 33, 33])
if COLORBG_PATH != "None":
    print("[SCENE BUILDER] Import BG_Color layers")
    *_, last = clip.layers
    list_bottom = last.position

    filename = os.path.split(os.path.splitext(COLORBG_PATH)[1])

    layer = clip.add_layer(f"BG_{filename}")
    layer.color = clip.get_layer_color(by_index=7)
    layer.load_image(COLORBG_PATH, frame=0)
    layer.post_behavior= george.LayerBehavior.HOLD
    layer.position = list_bottom


# ----------------------------------#
# -------- Importing Audio ---------#
# ----------------------------------#

print('[SCENE BUILDER] Import audio')
if os.path.exists(AUDIO_PATH):
    audio = clip.add_sound(AUDIO_PATH)
    print('[SCENE BUILDER] Audio imported')
else : print('[SCENE BUILDER] Audio not found')


# ----------------------------------#
# --------- Saving Project ---------#
# ----------------------------------#


project.save_video_dependencies()
project.save_audio_dependencies()
print("[SCENE BUILDER] Save project")
project.save()

print("[SCENE BUILDER] Build complete")
