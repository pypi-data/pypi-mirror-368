import sys
import argparse
import os

from pytvpaint import george
from pytvpaint.project import Project

def process_remaining_args(args):
    parser = argparse.ArgumentParser(
        description='TVPaint Project Template Arguments'
    )
    parser.add_argument('--file-path', dest='file_path')
    parser.add_argument('--audio-path', dest='audio_path')

    values, _ = parser.parse_known_args(args)

    return (
        values.audio_path,values.file_path
    )

AUDIO_PATH, FILE_PATH = process_remaining_args(sys.argv)


if os.path.exists(AUDIO_PATH):
    print(f"[RELOAD AUDIO] Audio file exists")

project = Project.current_project()

# Check if project is already open
project_name = os.path.split(os.path.splitext(FILE_PATH)[0])[1]

if project.get_project(by_name=project_name) is None:
    print('[RELOAD AUDIO] Load project (in silent mode, ignore warning popup dialog)')
    project.load(FILE_PATH, silent=True)
else:
    print('[RELOAD AUDIO] Select project as current') 
    project.get_project(by_name=project_name).make_current()


project = Project.current_project()
clip = project.current_clip
audio = clip.get_sound()

# Check if there is already a sound track
if audio is None :
    print('[RELOAD AUDIO] Import sound')
    audio = clip.add_sound(AUDIO_PATH)
else: 
    print('[RELOAD AUDIO] Reload sound')
    audio.reload()

# Enable save audio dependencies in project to avoid absolute path issue for audio
print('[RELOAD AUDIO] Enable save audio dependencies')
project.save_audio_dependencies()

print("[RELOAD AUDIO] Save project")
project.save()

print("[RELOAD AUDIO] Close TVPaint")
project.close()
