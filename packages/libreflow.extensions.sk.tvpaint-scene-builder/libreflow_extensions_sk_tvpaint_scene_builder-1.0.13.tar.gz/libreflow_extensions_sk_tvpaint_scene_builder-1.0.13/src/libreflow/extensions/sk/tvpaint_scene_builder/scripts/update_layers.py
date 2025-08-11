import os
import json
import sys
import argparse

from pytvpaint import george
from pytvpaint.project import Project

project = Project.current_project()
clip = project.current_clip

def process_remaining_args(args):
    parser = argparse.ArgumentParser(description="TVPaint Update Arguments")
    parser.add_argument("--layoutbg-path", dest="layoutbg_path")
    parser.add_argument("--colorbg-path", dest="colorbg_path")
    parser.add_argument("--animatic-path", dest="animatic_path")
    values, _ = parser.parse_known_args(args)

    return (values.layoutbg_path, values.colorbg_path,values.animatic_path)

LAYOUTBG_PATH, COLORBG_PATH, ANIMATIC_PATH = process_remaining_args(sys.argv)

print(LAYOUTBG_PATH)
print(COLORBG_PATH)
print(ANIMATIC_PATH)

if LAYOUTBG_PATH != 'None':

    print("[SCENE UPDATE] Updating Layout layers")

    clip.get_layer_color(by_index=6).select_layers(True)
    project_layers = clip.selected_layers

    folder_content = os.listdir(LAYOUTBG_PATH)
    folder_name = os.path.split(LAYOUTBG_PATH)[1]

    for file in folder_content:
        file_path = os.path.join(LAYOUTBG_PATH, file)
        if os.path.splitext(file_path)[1] == ".json":
            with open(file_path) as f:
                data = json.load(f)
                layers = data["layers"]
                hidden_layers = data["hidden_layers"]
            break
    
    #remove layers not in new list
    for pl in project_layers:
        pln = pl.name.replace("OL & UL_","")
        if pln not in layers:
            pl.remove()

    #replace layers with new list
    for l in layers:
        file = folder_name + "-" + l.replace(" ", "-") + ".png"
        file_path = os.path.join(LAYOUTBG_PATH, file)

        if os.path.exists(file_path):
            layer_name ="OL & UL_"+l
            
            layer = clip.get_layer(by_name=layer_name)
            if not layer:
                layer = clip.add_layer(layer_name)
                layer.color = clip.get_layer_color(by_index=6)
                layer.post_behavior= george.LayerBehavior.HOLD
            
            layer.load_image(file_path, frame=0)

            if l in hidden_layers:
                layer.opacity = 0

if COLORBG_PATH != 'None':
    print("[SCENE UPDATE] Updating BG Color layers")

    clip.get_layer_color(by_index=7).select_layers(True)

    if all(False for _ in clip.selected_layers):
        print('No BG Color found - creating the layer')

        *_, last = clip.layers
        list_bottom = last.position

        filename = os.path.split(os.path.splitext(COLORBG_PATH)[0])[1]

        layer = clip.add_layer(f"BG_{filename}")
        layer.color = clip.get_layer_color(by_index=7)
        layer.position = list_bottom
    else :
        clip.get_layer_color(by_index=7).select_layers(True)
        *_,layer = clip.selected_layers
        
    layer.load_image(COLORBG_PATH, frame=0)
    layer.post_behavior= george.LayerBehavior.HOLD

if ANIMATIC_PATH != 'None':
    print("[SCENE UPDATE] Updating Animatic Layer")

    filename = os.path.split(os.path.splitext(ANIMATIC_PATH)[0])[1]

    clip.get_layer_color(by_index=11).select_layers(True)

    if all(False for _ in clip.selected_layers):
        print('No Animatic found - creating the layer')

        new_layer = clip.load_media(media_path=ANIMATIC_PATH, with_name=f"Animatic_{filename}", preload=True)
        new_layer.color = clip.get_layer_color(by_index=11)

    else :
        clip.get_layer_color(by_index=11).select_layers(True)
        *_,layer = clip.selected_layers

        layer.make_current()

        new_layer = clip.load_media(media_path=ANIMATIC_PATH, with_name=filename, preload=True)
        new_layer.color = clip.get_layer_color(by_index=11)
        
        layer.remove()
    
    



project.save_video_dependencies()
project.save_audio_dependencies()
print("[SCENE UPDATE] Save project")
project.save()

print("[SCENE UPDATE] Update complete")
project.close_all(True)

