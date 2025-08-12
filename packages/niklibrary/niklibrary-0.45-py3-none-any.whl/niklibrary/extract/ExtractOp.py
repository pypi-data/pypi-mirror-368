import os

from niklibrary.build.Overlay import Overlay
from niklibrary.helper.F import F
from niklibrary.helper.Statics import Statics
from niklibrary.oem.GoogleOem import GoogleOem


class ExtractOp:

    @staticmethod
    def extract_overlays(android_version, oem, oem_overlays_directory):
        match oem:
            case 'cheetah' | 'husky':
                oem_overlays_dir = f"{oem_overlays_directory}{Statics.dir_sep}{android_version}{Statics.dir_sep}{oem}"
                F.make_dir(oem_overlays_dir)
                c = GoogleOem(android_version=android_version, oem=oem)
                c.extract_overlay(oem_overlays_dir)
            case _:
                print("default")

    @staticmethod
    def extract_all_overlays(overlay_dir):
        for root, _, files in os.walk(overlay_dir):
            if root.lower().__contains__(os.sep + "overlay"):
                for file in files:
                    file_path = str(os.path.join(root, file))
                    if file_path.lower().__contains__("overlay"):
                        ExtractOp.extract_overlay(file_path)

    @staticmethod
    def extract_overlay(file_path):
        o = Overlay(file_path)
        if not o.extract_overlay():
            print("Overlay extraction of " + file_path + " failed")
