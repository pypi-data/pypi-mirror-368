import os
from pathlib import Path

from niklibrary.helper.Cmd import Cmd
from niklibrary.helper.Statics import Statics
from niklibrary.oem.AndroidDump import AndroidDump


class GoogleOem(AndroidDump):
    def __init__(self, oem, android_version, gapps_dict=None, clone_repo=False):
        self.oem = oem
        super().__init__(android_version, self.oem)
        self.branch = "main"
        # self.repo_dir = Statics.pwd + Statics.dir_sep + f"{self.oem}_" + str(android_version)
        self.gapps_dict = {} if gapps_dict is None else gapps_dict
        self.repo = self.clone_gapps_image() if clone_repo else None

    def get_android_dump_dict(self):
        supported_partitions = ["system_ext", "product"]
        self.gapps_dict = {"branch": self.branch}
        cmd = Cmd()
        for partition in supported_partitions:
            supported_types = {"priv-app": "priv-app", "app": "app"}
            for supported_type in supported_types:
                partition_dir = self.repo_dir + Statics.dir_sep + partition + Statics.dir_sep + \
                                supported_type + Statics.dir_sep
                for path in Path(partition_dir).rglob("*.apk"):
                    if path.is_file():
                        path = str(path)
                        path = path.replace("\\", "/")
                        file_size = os.stat(path).st_size
                        file_path = str(path)
                        file_location = file_path[len(self.repo_dir) + 1:]
                        file_path = file_path[len(partition_dir):]
                        folder_name = file_path.split("/")[0]
                        isstub = True if folder_name.__contains__("-Stub") else False
                        package_name = cmd.get_package_name(path)
                        package_version = cmd.get_package_version(path)
                        version_code = cmd.get_package_version_code(path)
                        version = ''.join([i for i in package_version if i.isdigit()])
                        gapps_list = self.gapps_dict[package_name] if package_name in self.gapps_dict else []
                        g_dict = {"partition": partition, "type": supported_types[supported_type],
                                  "folder": folder_name, "version_code": version_code, "v_code": version,
                                  "file": file_path, "package": package_name, "version": package_version,
                                  "location": file_location, "isstub": isstub, "size": file_size}
                        gapps_list.append(g_dict)
                        if isstub:
                            apk_gz_folder = folder_name.replace("-Stub", "")
                            for apk_gz_path in Path(str(partition_dir) + apk_gz_folder).rglob("*.apk.gz"):
                                if apk_gz_path.is_file():
                                    apk_gz_file_path = str(apk_gz_path).replace("\\", "/")
                                    file_size = Statics.get_file_bytes(apk_gz_file_path)
                                    apk_gz_file_path = apk_gz_file_path[len(partition_dir):]
                                    apk_gz_file_location = str(apk_gz_path)[len(self.repo_dir) + 1:].replace("\\", "/")
                                    gz_dict = {"partition": partition, "type": supported_types[supported_type],
                                               "folder": apk_gz_folder, "version_code": version_code, "v_code": version,
                                               "file": apk_gz_file_path, "package": package_name,
                                               "version": package_version, "location": apk_gz_file_location,
                                               "isstub": isstub, "size": file_size}
                                    gapps_list.append(gz_dict)
                        if package_name not in self.gapps_dict:
                            self.gapps_dict[package_name] = gapps_list
        return self.gapps_dict

    def get_file_list_dict(self, pkg):
        oem_file_list_dict = {}
        folder = None
        file_list = []
        # get the folder from the package as pkg is of primary apk, so that folder counts
        for oem_pkg in self.gapps_dict:
            if str(pkg).__eq__(str(oem_pkg)) and folder is None:
                for oem_file in self.gapps_dict[oem_pkg]:
                    folder = str(oem_file["folder"])
                    break
        if folder is not None:
            for oem_pkg in self.gapps_dict:
                if str(oem_pkg).__eq__("branch"):
                    continue
                for oem_file in self.gapps_dict[oem_pkg]:
                    if str(folder).__eq__(str(oem_file["folder"])):
                        f_dict = {"partition": oem_file["partition"], "type": oem_file["type"],
                                  "folder": folder, "package": oem_file["package"],
                                  "file": oem_file["file"], "version_code": oem_file["version_code"],
                                  "version": oem_file["version"], "location": oem_file["location"]}
                        file_list.append(f_dict)
        if len(file_list) > 0:
            oem_file_list_dict[pkg] = file_list
        return oem_file_list_dict
