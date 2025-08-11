import os
import subprocess
import psutil
import time

from kabaret import flow
from libreflow.baseflow.file import GenericRunAction,OpenTrackedFileAction,OpenWithAction,TrackedFile
from libreflow.baseflow.task import Task


class CreateTvPaintFile(flow.Action):
    ICON = ('icons.libreflow', 'tvpaint')

    _task = flow.Parent()
    _tasks = flow.Parent(2)
    _shot = flow.Parent(3)
    _sequence = flow.Parent(5)
    _layout_source_path = flow.Computed(cached=True)
    _color_source_path = flow.Computed(cached=True)
    _antc_path = flow.Computed(cached=True)
    _audio_path = flow.Computed(cached=True)

    sources_versions = flow.Param()

    def allow_context(self, context):
        return context

    def needs_dialog(self):
        self._color_source_path.touch()
        self._antc_path.touch()

        if self._color_source_path.get() is None:
            self.message.set(
                "<font color=orange>BG Color layer folder not found</font>"
            )
            return True
        
        if self._antc_path.get() is None:
            self.message.set(
                "<font color=orange>Animatic not found</font>"
            )
            return True

        return False

    def get_buttons(self):
        self._layout_source_path.touch()

        if self._layout_source_path.get() is None:
            self.message.set(
                "<font color=orange>BG Layout layer folder not found</font>"
            )
            return ["Close"]
        
        if self._antc_path.get() is None:
            return ["Close"]


        return ["Build Anyway", "Close"]

    def check_tvpaint_running(self):
        # Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if "tvpaint animation" in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        return False

    def compute_child_value(self, child_value):
        if child_value is self._layout_source_path:
            self._layout_source_path.set(self.get_source_path("bg_layout"))
        elif child_value is self._color_source_path:
            self._color_source_path.set(self.get_source_path("bg_color"))
        elif child_value is self._antc_path:
            self._antc_path.set(self.get_source_path("storyboard"))
        elif child_value is self._audio_path:
            self._audio_path.set(self.get_audio_path())

    def start_tvpaint(self, path):
        start_action = self._task.start_tvpaint
        start_action.file_path.set(path)
        start_action.run(None)

    def execute_create_tvpaint_script(
        self, antc_path, layout_path, color_path, audio_path, width=None, height=None
    ):
        exec_script = self._task.execute_create_tvpaint_script
        exec_script._antc_path.set(antc_path)
        exec_script._layout_source_path.set(layout_path)
        exec_script._color_source_path.set(color_path)
        exec_script._audio_source_path.set(audio_path)
        exec_script.width.set(width)
        exec_script.height.set(height)
        exec_script.run(None)

    def get_default_file(self, task_name, file_name):
        file_mapped_name = file_name.replace(".", "_")
        mng = self.root().project().get_task_manager()

        dft_task = mng.default_tasks[task_name]
        if not dft_task.files.has_mapped_name(file_mapped_name):  # check default file
            # print(f'Scene Builder - default task {task_name} has no default file {filename} -> use default template')
            return None

        dft_file = dft_task.files[file_mapped_name]
        return dft_file
    
    def get_audio_path(self):
        self.source_task = self._shot.tasks['storyboard']

        if not self.source_task.files.has_file('animatic', 'wav'):
            return None
        f = self.source_task.files['animatic_wav']

        rev = f.get_head_revision(sync_status="Available")
        if rev is None:
            return None

        path = rev.get_path()
        return path if os.path.isfile(path) else None


    def get_source_path(self, task_name):
        if not self._shot.tasks.has_mapped_name(task_name):
            return None
        self.source_task = self._shot.tasks[task_name]

        if task_name == "bg_color" :
            if not self.source_task.files.has_file('bg_color', 'png'):
                return None
            f = self.source_task.files['bg_color_png']

            rev = f.get_head_revision(sync_status="Available")
            if rev is None:
                return None
            
            path = rev.get_path()
            return path if os.path.isfile(path) else None

        if task_name == "storyboard" :
            if not self.source_task.files.has_file('animatic', 'mp4'):
                return None
            f = self.source_task.files['animatic_mp4']

            rev = f.get_head_revision(sync_status="Available")
            if rev is None:
                return None

            path = rev.get_path()
            return path if os.path.isfile(path) else None

        if task_name == "bg_layout" : 
            if not self.source_task.files.has_folder(task_name + "_render"):
                return None
            f = self.source_task.files[f"{task_name}_render"]

            rev = f.get_head_revision(sync_status="Available")
            if rev is None:
                return None

            path = rev.get_path()
            return path if os.path.isdir(path) else None


    def get_first_image_resolution(self, path):
        if not os.path.exists(path):
            return None

        img_path = None

        if os.path.isdir(path): 
            folder_content = os.listdir(path)

            for file in folder_content:
                img_path = os.path.join(path, file)
                if os.path.splitext(img_path)[1] == ".png":
                    break
                    
        elif os.path.isfile(path):
            img_path = path

        else: return None

        check_res = subprocess.check_output(
            f'magick identify -ping -format "%wx%h" "{img_path}"', shell=True
        ).decode()

        res = check_res.split("x")

        return res

    def _ensure_file(self, name, format, path_format):
        files = self._task.files
        file_name = "%s_%s" % (name, format)

        if files.has_file(name, format):
            file = files[file_name]
        else:
            file = files.add_file(
                name=name,
                extension=format,
                tracked=True,
                default_path_format=path_format,
            )

        revision = file.create_working_copy()

        file.file_type.set("Works")

        return revision.get_path()

    def run(self, button):
        if button == "Close":
            return

        path_format = None
        task_name = self._task.name()
        default_file = self.get_default_file(task_name, f"{task_name}.tvpp")
        if default_file is not None:
            path_format = default_file.path_format.get()
        anim_path = self._ensure_file(
            name=task_name, format="tvpp", path_format=path_format
        )

        self.start_tvpaint(anim_path)

        layout_source_path = self._layout_source_path.get()
        color_source_path = self._color_source_path.get()
        animatic_source_path = self._antc_path.get()

        layout_res = self.get_first_image_resolution(layout_source_path)

        layout_source_name = os.path.split(layout_source_path)[1]

        animatic_source_name = os.path.split(animatic_source_path)[1]

        color_source_name = None

        if color_source_path is not None:
            color_res = self.get_first_image_resolution(color_source_path)

            color_source_name = os.path.split(color_source_path)[1]

            if color_res != layout_res:
                self.root().session().log_warning(
                    "Layout BG and Color BG are not corresponding, TvPaint Project will inherit Layout BG image size"
                )

        sources_ver = self.sources_versions.get()
        if sources_ver is None :
            sources_ver = {}
        sources_ver.update({default_file.name() : [layout_source_name, color_source_name,animatic_source_name]})
        self.sources_versions.set(sources_ver)

        print (self.sources_versions.get())


        self.execute_create_tvpaint_script(
            animatic_source_path,
            layout_source_path,
            color_source_path,
            self._audio_path.get(),
            layout_res[0],
            layout_res[1],
        )


class TvpaintSourceCheck(OpenWithAction):

    ICON = ("icons.libreflow", "tvpaint")

    _task = flow.Parent(3)
    _tasks = flow.Parent(4)
   
    def run(self, button):
        print(button)
        if button == 'Cancel':
            return
        

        self.root().session().log_info(
            "Checking for layout and background updates"
        )

        sources_ver = self._task.create_tv_paint_file.sources_versions.get()

        # Get sources versions from previous tasks if None
        if not sources_ver :
            tasks_list = self._tasks.mapped_items()
            tasks_list.reverse()
            taskindex = tasks_list.index(self._task)
            for task in tasks_list[taskindex+1:]:
                prev_sources_ver = task.create_tv_paint_file.sources_versions.get()
                if prev_sources_ver:
                    sources_ver = prev_sources_ver
                    keys = [*prev_sources_ver]
                    old_key = keys[0]
                    sources_ver[self._file.name()] = prev_sources_ver.pop(old_key)
                    print(sources_ver)
                    self._task.create_tv_paint_file.sources_versions.set(sources_ver)
                    break


        layout_source_path = self._task.create_tv_paint_file.get_source_path("bg_layout")
        color_source_path = self._task.create_tv_paint_file.get_source_path("bg_color")
        animatic_source_path = self._task.create_tv_paint_file.get_source_path("storyboard")

        to_update = {"bg_layout" : None, "bg_color" : None, "animatic" : None}

        if layout_source_path :
            up_to_date = True
            layout_source_name =  os.path.split(layout_source_path)[1]

            if sources_ver :
                if layout_source_name != sources_ver[self._file.name()][0]:
                    up_to_date = False
                    to_update["bg_layout"] = layout_source_path
                    self._file.open_tvpaint.message.set(f'<font color = orange>Layout BG is not up to date (current version: {sources_ver[self._file.name()][0]} - last version: {layout_source_name})</font>')

                if color_source_path is not None:
                    color_source_name = os.path.split(color_source_path)[1]
                    if color_source_name!= sources_ver[self._file.name()][1]:
                        up_to_date = False
                        to_update["bg_color"] = color_source_path
                        self._file.open_tvpaint.message.set(f'<font color = orange>Color BG is not up to date (current version: {sources_ver[self._file.name()][1]} - last version: {color_source_name})</font>')

                if animatic_source_path is not None:
                    animatic_source_name = os.path.split(animatic_source_path)[1]
                    try :
                        if animatic_source_name!= sources_ver[self._file.name()][2] :
                            up_to_date = False
                            to_update["animatic"] = animatic_source_path
                            self._file.open_tvpaint.message.set(f'<font color = orange>Animatic is not up to date (current version: {sources_ver[self._file.name()][2]} - last version: {animatic_source_name})</font>')
                    except IndexError :
                        if len(sources_ver[self._file.name()]) < 3 :
                            up_to_date = False
                            to_update["animatic"] = animatic_source_path
                            self._file.open_tvpaint.message.set(f'<font color = orange>Animatic is not up to date (current version: None - last version: {animatic_source_name})</font>')

            else :
                up_to_date = False
                to_update["bg_layout"] = layout_source_path
                to_update["bg_color"] = color_source_path
                to_update["animatic"] = animatic_source_path
                self._file.open_tvpaint.message.set(f'<font color = orange>Source versions data undetected, a conformity update is required</font>')
        

            if not up_to_date :

                print(f'{to_update=}')

                if button == 'Open revision':
                    self._file.open_tvpaint._buttons.set(['Update', 'Open Anyway', 'Cancel'])
                    self._file.open_tvpaint.mode.set(button)

                elif button == 'Create a working copy':
                    self._file.open_tvpaint._buttons.set(['Update','Cancel'])
                    self._file.open_tvpaint.mode.set(button)
                
                else: 
                    self._file.open_tvpaint._buttons.set(['Update','Open Anyway','Cancel'])
                    self._file.open_tvpaint.mode.set("Open Working Copy")

                self._file.open_tvpaint.to_update.set(to_update)

                if self._to_open.get():
                    self._file.open_tvpaint._to_open.set(self._to_open.get())
                else: self._file.open_tvpaint._to_open.set(self.revision_name.get())
                return self.get_result(next_action=self._file.open_tvpaint.oid())
            
            else : super(TvpaintSourceCheck,self).run(button)
        
        else:
            self.root().session().log_info("No source file to check")
            super(TvpaintSourceCheck,self).run(button)

    def runner_name_and_tags(self):
        return "TvPaint", []

    @classmethod
    def supported_extensions(cls):
        return ["tvpp"]


class OpenWithTvPaintAction(OpenWithAction):

    _task = flow.Parent(3)

    mode = flow.Param().ui(hidden=True)
    to_update = flow.Param().ui(hidden=True)

    def allow_context(self, context):
        return context and context.endswith('.details')
    
    def start_tvpaint(self, path):
        start_action = self._task.start_tvpaint
        start_action.file_path.set(path)
        start_action.run(None)

    def execute_update_tvpaint_script(self, layout_path, color_path, animatic_path):
        exec_script = self._task.execute_update_tvpaint_script
        exec_script._layout_source_path.set(layout_path)
        exec_script._color_source_path.set(color_path)
        exec_script._animatic_source_path.set(animatic_path)
        exec_script.run(None)


    def run(self, button):
        if button == 'Cancel':
            return self.get_result(next_action=self._task.oid())

        rev = self._file.get_revision(self._to_open.get())

        if button == 'Update':
            print('Updating file :', self._to_open.get())

            mode = self.mode.get()
            to_update = self.to_update.get()

            
            if not rev.is_working_copy() :
                rev = self._file.create_working_copy(from_revision=self._to_open.get())
            

            self.start_tvpaint(rev.get_path())

            self.execute_update_tvpaint_script(
                to_update['bg_layout'],
                to_update['bg_color'],
                to_update['animatic'],
            )


            # Wait for TVPaint script to finish
            for sp in (
                self.root()
                .session()
                .cmds.SubprocessManager.list_runner_infos()
            ):
                if (
                    sp["is_running"]
                    and sp["label"] == "TvPaint"
                ):
                    while sp["is_running"]:
                        time.sleep(1)
                        sp = self.root().session().cmds.SubprocessManager.get_runner_info(sp["id"])
                    break

            print("Update finished")

            layers = [k for k, v in to_update.items() if v is not None]
            
            f = self._file

            if f.get_working_copy() is not None:
                # Publish and upload
                f.publish_action.comment.set(f"updated layers : {layers}")
                if mode == "Open revision" :
                    f.publish_action.upload_after_publish.set(False)
                else : 
                    f.publish_action.upload_after_publish.set(True)
                print("Publish")
                f.publish_action.run("Publish")

                sources_ver = self._task.create_tv_paint_file.sources_versions.get()

                if to_update["bg_layout"]:
                    layout_source_name = os.path.split(to_update["bg_layout"])[1]
                    sources_ver[self._file.name()][0] = layout_source_name
                
                if to_update["bg_color"]:
                    color_source_name = os.path.split(to_update["bg_color"])[1]
                    sources_ver[self._file.name()][1] = color_source_name
                
                if to_update["animatic"]:
                    animatic_source_name = os.path.split(to_update["animatic"])[1]
                    sources_ver[self._file.name()][2] = animatic_source_name       

                self._task.create_tv_paint_file.sources_versions.set(sources_ver)

        elif button =='Open Anyway':
            if rev.is_working_copy():
                super(OpenWithTvPaintAction,self).run('open working copy')
            else :
                super(OpenWithTvPaintAction,self).run('Open revision')

        return self.get_result(next_action=self._task.oid())

    
    def runner_name_and_tags(self):
        return "TvPaint", []

    @classmethod
    def supported_extensions(cls):
        return ["tvpp"]


class ReloadAudio(flow.Action):
    ICON = ('icons.libreflow', 'tvpaint')

    _task = flow.Parent()
    _tasks = flow.Parent(2)
    _shot = flow.Parent(3)

    def allow_context(self, context):
        return self._task.files.has_file(self._task.name(), "tvpp")

    def needs_dialog(self):
        return False

    def get_file(self, task_name, file_name):
        if not self._tasks.has_mapped_name(task_name):
            return None
        task = self._tasks[task_name]

        name, ext = os.path.splitext(file_name)
        if task.files.has_file(name, ext[1:]):
            file_name = "%s_%s" % (name, ext[1:])
            return task.files[file_name]

        return None

    def execute_reload_audio_script(self, file_path, audio_path):
        exec_script = self._task.reload_audio_script
        exec_script.file_path.set(file_path)
        exec_script.audio_path.set(audio_path)
        exec_script.run(None)

    def _export_audio(self, tvpaint_file):
        export_audio = tvpaint_file.export_ae_audio
        ret = export_audio.run("Export")
        return ret

    def check_tvpaint_running(self):
        # Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if "tvpaint animation" in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        return False

    def start_tvpaint(self):
        start_action = self._task.start_tvpaint
        start_action.file_path.set("")
        start_action.run(None)

    def run(self, button):
        if button == "Close":
            return

        # Get TVPaint file
        tvpaint_file = self.get_file(self._task.name(), f"{self._task.name()}.tvpp")

        # Create or get working copy
        working_copy = tvpaint_file.get_working_copy()
        if working_copy is None:
            if tvpaint_file.get_head_revision(sync_status="Available") :
                working_copy = tvpaint_file.create_working_copy(
                    tvpaint_file.get_head_revision(sync_status="Available").name()
                )
            else :
                self.root().session().log_info('Revision not available locally') 
                return

        file_path = working_copy.get_path()

        # Get or export audio file
        audio_file = self.get_file("storyboard", "animatic.wav")
        if (audio_file is None) or (
            audio_file.get_head_revision(sync_status="Available")
        ) is None:
            self._export_audio(tvpaint_file)
            audio_path = tvpaint_file.export_ae_audio._audio_path.get()
        else:
            audio_path = audio_file.get_head_revision().get_path()

        if audio_path is not None:
            # Start TVPaint if it's not running
            if self.check_tvpaint_running() is False:
                self.start_tvpaint()

            # Start pytvpaint script
            self.execute_reload_audio_script(file_path, audio_path)


class ReloadAudioScript(GenericRunAction):
    file_path = flow.Param()
    audio_path = flow.Param()

    def allow_context(self, context):
        return context

    def runner_name_and_tags(self):
        return "PythonRunner", []

    def get_version(self, button):
        return None

    def get_run_label(self):
        return "Reload Audio"

    def extra_argv(self):
        current_dir = os.path.split(__file__)[0]
        script_path = os.path.normpath(
            os.path.join(current_dir, "scripts/reload_audio.py")
        )
        return [
            script_path,
            "--file-path",
            self.file_path.get(),
            "--audio-path",
            self.audio_path.get(),
        ]


class ReloadAudioBatch(flow.Action):
    ICON = ('icons.libreflow', 'tvpaint')

    sequences = flow.Param()

    def allow_context(self, context):
        user = self.root().project().get_user()
        return user.status.get() == "Admin"

    def get_buttons(self):
        return ["Reload", "Close"]

    def needs_dialog(self):
        self.message.set('Enter sequences to batch in a list format "["s000", "s000"]"')
        return True

    def run(self, button):
        if button == "Close":
            return

        sequences_list = list(self.sequences.get())

        for seq in sequences_list:
            sequence_oid = f"/sk/films/sk/sequences/{seq}"

            seq_obj = self.root().get_object(sequence_oid)

            for shot in seq_obj.shots.mapped_items():
                for task in shot.tasks.mapped_items():
                    for f in task.files.mapped_items():
                        # Fetch only TVPaint files
                        if "tvpp" in f.name():
                            head = f.get_head_revision()

                            if head.comment.get() == "fix audio dependency":
                                continue
                            if head is not None:
                                print(
                                    seq_obj.name(),
                                    shot.name(),
                                    task.name(),
                                    f.name(),
                                    head.name(),
                                    "Reload start",
                                )

                                f._task.reload_audio.run("None")

                                time.sleep(3)

                                # Wait for TVPaint script to finish
                                for sp in (
                                    self.root()
                                    .session()
                                    .cmds.SubprocessManager.list_runner_infos()
                                ):
                                    if (
                                        sp["is_running"]
                                        and sp["label"] == "Reload Audio"
                                    ):
                                        while sp["is_running"]:
                                            time.sleep(1)
                                            sp = self.root().session().cmds.SubprocessManager.get_runner_info(sp["id"])
                                        break

                                print(
                                    seq_obj.name(),
                                    shot.name(),
                                    task.name(),
                                    f.name(),
                                    head.name(),
                                    "Reload finish",
                                )

                                if f.get_working_copy() is not None:
                                    # Publish and upload
                                    f.publish_action.comment.set("fix audio dependency")
                                    f.publish_action.keep_editing.set(False)
                                    f.publish_action.upload_after_publish.set(True)
                                    print(
                                        seq_obj.name(),
                                        shot.name(),
                                        task.name(),
                                        f.name(),
                                        head.name(),
                                        "Publish",
                                    )
                                    f.publish_action.run("Publish")
                                break


class StartTvPaint(GenericRunAction):
    file_path = flow.Param()

    def allow_context(self, context):
        return context

    def runner_name_and_tags(self):
        return "TvPaint", []

    def target_file_extension(self):
        return "tvpp"

    def extra_argv(self):
        return [self.file_path.get()]


class ExecuteCreateTvPaintScript(GenericRunAction):
    _antc_path = flow.Param()
    _layout_source_path = flow.Param()
    _color_source_path = flow.Param()
    _audio_source_path = flow.Param()
    width = flow.Param()
    height = flow.Param()

    def allow_context(self, context):
        return context

    def runner_name_and_tags(self):
        return "PythonRunner", []

    def get_version(self, button):
        return None

    def get_run_label(self):
        return "Create TvPaint Project"

    def extra_argv(self):
        current_dir = os.path.split(__file__)[0]
        script_path = os.path.normpath(
            os.path.join(current_dir, "scripts/import_layers.py")
        )
        return [
            script_path,
            "--animatic-path",
            self._antc_path.get(),
            "--layoutbg-path",
            self._layout_source_path.get(),
            "--colorbg-path",
            self._color_source_path.get(),
            "--audio-path",
            self._audio_source_path.get(),
            "--width",
            self.width.get(),
            "--height",
            self.height.get(),
        ]

class ExecuteUpdateTvPaintScript(GenericRunAction):
    _layout_source_path = flow.Param()
    _color_source_path = flow.Param()
    _animatic_source_path = flow.Param()

    def allow_context(self, context):
        return context

    def runner_name_and_tags(self):
        return "PythonRunner", []

    def get_version(self, button):
        return None

    def get_run_label(self):
        return "Update TvPaint Project"

    def extra_argv(self):
        current_dir = os.path.split(__file__)[0]
        script_path = os.path.normpath(
            os.path.join(current_dir, "scripts/update_layers.py")
        )
        return [
            script_path,
            "--layoutbg-path",
            self._layout_source_path.get(),
            "--colorbg-path",
            self._color_source_path.get(),
            "--animatic-path",
            self._animatic_source_path.get(),
        ]

def source_check(parent):
    if isinstance(parent, TrackedFile) and parent.format.get() == 'tvpp':
        r = flow.Child(TvpaintSourceCheck)
        r.name = "open"
        r.index = None
        return r

def open_with_tvpaint(parent):
    if isinstance(parent, TrackedFile) and parent.format.get() == 'tvpp':
        r = flow.Child(OpenWithTvPaintAction)
        r.name = "open_tvpaint"
        r.index = None
        r.ui(hidden=True)
        return r


def create_from_layers(parent):
    if isinstance(parent, Task):
        r = flow.Child(CreateTvPaintFile)
        r.name = "create_tv_paint_file"
        r.index = None
        if parent.name() != 'posing':
            r.ui(hidden=True)
        return r


def start_tvpaint(parent):
    if isinstance(parent, Task):
        r = flow.Child(StartTvPaint)
        r.name = "start_tvpaint"
        r.index = None
        r.ui(hidden=True)
        return r


def execute_create_tvpaint_script(parent):
    if isinstance(parent, Task):
        r = flow.Child(ExecuteCreateTvPaintScript)
        r.name = "execute_create_tvpaint_script"
        r.index = None
        r.ui(hidden=True)
        return r

def execute_update_tvpaint_script(parent):
    if isinstance(parent, Task):
        r = flow.Child(ExecuteUpdateTvPaintScript)
        r.name = "execute_update_tvpaint_script"
        r.index = None
        r.ui(hidden=True)
        return r


def reload_audio(parent):
    if isinstance(parent, Task):
        r = flow.Child(ReloadAudio)
        r.name = "reload_audio"
        r.index = None
        return r


def reload_audio_batch(parent):
    if isinstance(parent, Task):
        r = flow.Child(ReloadAudioBatch)
        r.name = "reload_audio_batch"
        r.index = None
        return r


def reload_audio_script(parent):
    if isinstance(parent, Task):
        r = flow.Child(ReloadAudioScript)
        r.name = "reload_audio_script"
        r.index = None
        r.ui(hidden=True)
        return r


def install_extensions(session):
    return {
        "tvpaint_scene_builder": [
            create_from_layers,
            start_tvpaint,
            execute_create_tvpaint_script,
            execute_update_tvpaint_script,
            reload_audio,
            reload_audio_batch,
            reload_audio_script,
            open_with_tvpaint,
            source_check,
        ]
    }
