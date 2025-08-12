import os

from niklibrary.helper.Cmd import Cmd


class Overlay:

    def __init__(self, overlay_path):
        self.path = overlay_path
        self.valid = False
        if str(overlay_path).lower().__contains__(os.sep + "overlay") and str(overlay_path).lower().endswith(".apk"):
            self.valid = True

    def extract_overlay(self, extract_dir_path=None, override_validity=False):
        if not override_validity and not self.valid:
            print(f"Overlay {self.path} does not seem valid")
            return False
        cmd = Cmd()
        if extract_dir_path is None:
            extract_dir_path = str(self.path).replace(".apk","") + "_extracted"
        if cmd.decompile_apk(self.path, extract_dir_path):
            return True
        return False
