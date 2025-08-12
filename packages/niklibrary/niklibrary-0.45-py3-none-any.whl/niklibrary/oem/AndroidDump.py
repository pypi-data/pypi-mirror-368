import math
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
from niklibrary.build.Overlay import Overlay
from niklibrary.configuration import Config
from niklibrary.git.Git import Git
from niklibrary.git.GitlabManager import GitLabManager
from niklibrary.helper.F import F
from niklibrary.helper.Statics import Statics
from niklibrary.json.Json import Json


class AndroidDump:
    def __init__(self, android_version, oem, branch=None):
        self.host = "https://dumps.tadiphone.dev/dumps/google/"
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        self.android_version = android_version
        self.oem = oem
        self.branch = branch
        project = self.get_host_project()
        self.repo_dir = Statics.pwd + Statics.dir_sep + project.path
        self.url = project.ssh_url_to_repo if project is not None else None
        self.gapps_dict = {}
        self.repo = None

    def get_host_project(self):
        gitlab_manager = GitLabManager(private_token=Config.GITLAB_TOKEN)
        release_type = "stable" if self.oem == "nikgapps" else self.oem
        project_details_list = []
        for project in gitlab_manager.list_projects_with_ids():
            if str(project.name).__contains__(f"{self.android_version}_") and str(project.name).__contains__(
                    f"{release_type}") and not str(project.name).__contains__("cached"):
                project_details = gitlab_manager.gl.projects.get(project.id, statistics=True)
                storage_size = math.ceil(project_details.statistics["storage_size"] / (1024 ** 2) * 100) / 100
                created_at = datetime.strptime(project_details.created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                project_details_list.append((project, storage_size, created_at))
        project_details_list.sort(key=lambda x: x[2], reverse=True)
        for project, storage_size, created_at in project_details_list:
            if str(project.name).__contains__(self.android_version) and str(project.name).__contains__(release_type):
                print(f'Project Name: {project.name}, '
                      f'Project Path: {project.path}, '
                      f'Project ID: {project.id}, '
                      f'Namespace: {project.namespace["path"]}, '
                      f'Creation Date: {created_at}, '
                      f'Storage Size: {storage_size} MB')
                return project
        return None

    def get_repo(self):
        return self.repo

    def get_repo_dir(self):
        return self.repo_dir

    def get_host(self):
        return self.host

    def write_gapps_dict(self, gapps_dict=None, file_path=None):
        if gapps_dict is None:
            self.gapps_dict = self.get_gapps_dict()
            gapps_dict = self.gapps_dict
        if file_path is None or gapps_dict is None:
            return False
        Json.write_dict_to_file(gapps_dict, file_path)
        return True

    def get_gapps_dict(self):
        print(f"Getting {self.oem} GApps Dict")
        repo = self.clone_gapps_image()
        if repo is not None:
            return self.get_android_dump_dict()
        else:
            print(f"Failed to clone {self.oem} GApps Image")
            return None

    @abstractmethod
    def get_android_dump_dict(self):
        pass

    def clone_gapps_image(self):
        print(f"Cloning {self.oem} GApps Image")
        repo_url = self.url + ".git" if not self.url.endswith(".git") else self.url
        self.repo = Git(self.repo_dir)
        result = self.repo.clone_repo(repo_url, branch=self.branch, fresh_clone=False)
        return self.repo if result else None

    def extract_overlay(self, extract_dir_path):
        print(f"Extract {self.oem} overlays")
        if self.clone_gapps_image() is not None:
            print(f"Extracting {self.oem} overlays")
            for file in Path(self.repo_dir).rglob("*.apk"):
                file_path = str(file)
                if file_path.lower().__contains__("overlay"):
                    o = Overlay(file_path)
                    overlay_folder = extract_dir_path + Statics.dir_sep + file.stem
                    F.remove_dir(overlay_folder)
                    o.extract_overlay(overlay_folder)
            print(" ")
            return True
        else:
            print(f"Failed to extract {self.oem} overlays")
            return None
