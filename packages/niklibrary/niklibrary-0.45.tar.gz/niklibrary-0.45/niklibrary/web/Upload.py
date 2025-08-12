import os
import platform
from pathlib import Path
import paramiko

from niklibrary.helper.F import F
from niklibrary.helper.P import P
from niklibrary.helper.Statics import Statics
from niklibrary.helper.T import T
from niklibrary.web.TelegramApi import TelegramApi


class Upload:
    def __init__(self, android_version, release_type, upload_files, password=None):
        self.android_version = android_version
        self.android_version_code = Statics.get_android_code(android_version)
        self.upload_files = upload_files
        self.host = "frs.sourceforge.net"
        self.username = "nikhilmenghani"
        self.password = os.environ.get('SF_PWD') if password is None else password
        self.release_dir = Statics.get_sourceforge_release_directory(release_type)
        self.release_date = T.get_london_date_time("%d-%b-%Y")
        self.cmd_method = False
        self.upload_obj = None
        self.sftp = None
        self.transport = None
        if not self.password:
            return
        try:
            self.transport = paramiko.Transport((self.host, 22))
            self.transport.connect(username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        except Exception as e:
            P.red("Exception while connecting to SFTP: " + str(e))
            self.sftp = None

    def set_release_dir(self, release_dir):
        self.release_dir = release_dir

    def get_cd(self, file_type):
        folder_name = f"{self.release_dir}/Test/{self.release_date}"
        match file_type:
            case "gapps" | "config":
                folder_name = f"{self.release_dir}/Android-{self.android_version}/{self.release_date}"
            case "addons":
                folder_name = f"{self.release_dir}/Android-{self.android_version}/{self.release_date}/Addons"
            case "debloater":
                tools_dir = Statics.get_sourceforge_release_directory("NikGappsTools/Debloater")
                folder_name = f"{tools_dir}/{self.release_date}"
            case "removeotascripts":
                tools_dir = Statics.get_sourceforge_release_directory("NikGappsTools/RemoveOtaScripts")
                folder_name = f"{tools_dir}/{self.release_date}"
            case "nikgappsconfig":
                folder_name = f"{self.release_dir}/Android-{self.android_version}"
            case _:
                print(file_type)
        print("Upload Dir: " + folder_name)
        return folder_name

    def ensure_remote_dir(self, path):
        """ Recursively create remote directory if it doesn't exist """
        dirs = path.strip("/").split("/")
        current = ""
        for directory in dirs:
            current += f"/{directory}"
            try:
                self.sftp.stat(current)
            except IOError:
                try:
                    self.sftp.mkdir(current)
                    P.magenta(f"Created remote directory: {current}")
                except Exception as e:
                    P.red("Exception while creating directory: " + str(e))
                    raise

    def upload(self, file_name, telegram: TelegramApi = None, remote_directory=None):
        if self.sftp is None:
            P.red("Connection failed!")
            return False, None, None
        system_name = platform.system()
        execution_status = False
        download_link = None
        file_size_kb = round(F.get_file_size(file_name, "KB"), 2)
        file_size_mb = round(F.get_file_size(file_name), 2)

        if telegram is not None:
            telegram.message(f"- The zip {file_size_mb} MB is uploading...")

        if system_name != "Windows" and self.upload_files:
            t = T()
            file_type = "gapps"
            base_name = os.path.basename(file_name).lower()
            if "-addon-" in base_name:
                file_type = "addons"
            elif "debloater" in base_name:
                file_type = "debloater"
            elif "removeotascripts" in base_name:
                file_type = "removeotascripts"
            if remote_directory is None:
                remote_directory = self.get_cd(file_type)

            remote_filename = Path(file_name).name
            try:
                self.ensure_remote_dir(remote_directory)
                remote_path = f"{remote_directory}/{remote_filename}"
                self.sftp.put(file_name, remote_path)
                P.green(f"File uploaded successfully to {remote_path}")
                download_link = Statics.get_download_link(file_name, remote_directory)
                P.magenta("Download Link: " + download_link)
                execution_status = True
                time_taken = t.taken(
                    f"Total time taken to upload file with size {file_size_mb} MB ({file_size_kb} KB)"
                )
                if telegram is not None:
                    telegram.message(
                        f"- The zip {file_size_mb} MB uploaded in {T.format_time(round(time_taken))}\n",
                        replace_last_message=True)
                    if download_link:
                        telegram.message(
                            f"*Note:* Download link should start working in 10 minutes",
                            escape_text=False,
                            ur_link={"Download": f"{download_link}"})
            except Exception as e:
                P.red("Exception while uploading file: " + str(e))
        else:
            P.red("System incompatible or upload disabled or connection failed!")
            P.red("system_name: " + system_name)
            P.red("self.sftp: " + str(self.sftp))
            P.red("self.upload_files: " + str(self.upload_files))
        return execution_status, download_link, file_size_mb

    def close_connection(self):
        if self.cmd_method:
            self.upload_obj.close_connection()
        elif self.sftp:
            self.sftp.close()
            if self.transport:
                self.transport.close()
            print("Connection closed")
