import hashlib
import os.path
import shutil
import stat
from pathlib import Path


class F:
    @staticmethod
    def create_file_dir(file_path):
        parent_dir = str(Path(file_path).parent)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

    @staticmethod
    def get_immediate_subdirectories(path):
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    @staticmethod
    def make_dir(dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    @staticmethod
    def file_category(extension, path):
        """
        Determine the category of a file based on its extension.
        """
        document_extensions = ['.doc', '.docx', '.pdf', '.txt', '.xls', '.xlsx', '.ppt', '.pptx', '.enc']
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.dng']
        thumbnails_extensions = ['.thumb']
        video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.3gp', '.mkv', '.mpg', '.mpeg', '.m4v']
        audio_extensions = ['.mp3', '.wav', '.aac', '.flac', '.amr', '.m4a', 'com.oneplus.soundrecorder', '.opus', 'awb', '.m4b', '.ogg']
        code_extensions = ['.py', '.js', '.html', '.css', '.java', '.c', '.cpp']
        archive_extensions = ['.zip', '.rar', '.tar', '.gz', '.7z']
        android_extensions = ['.apk', '.apks']
        hidden_extensions = ['.nomedia', '.ace']
        backup_extensions = ['SwiftBackup', '.bak', '.backup', '.bck', 'app']
        tg_theme_extensions = ['.attheme', '.tdesktop-theme']
        kindle_extensions = ['.azw', '.azw3', '.mobi']
        bat_file_extensions = ['.bat']
        books_extensions = ['.epub', '.fb2', '.ibooks', '.lit', '.pdb', '.pdg', '.pml', '.rb', '.tcr', '.txtz', '.umd']
        img_extensions = ['.img']
        shell_extensions = ['.sh']
        library_extensions = ['.so']
        fonts_extensions = ['.ttf', '.otf', '.woff', '.woff2']

        if extension in document_extensions:
            return 'Document'
        elif extension in image_extensions:
            return 'Image'
        elif extension in video_extensions:
            return 'Video'
        elif any(extension in path for extension in audio_extensions):
            return 'Audio'
        elif extension in code_extensions:
            return 'Code'
        elif extension in archive_extensions:
            return 'Archive'
        elif extension in android_extensions:
            return 'Android'
        elif extension in thumbnails_extensions:
            return 'Thumbnail'
        elif extension in hidden_extensions:
            return 'Hidden'
        elif any(extension in path for extension in backup_extensions):
            return 'Backup'
        elif extension in tg_theme_extensions:
            return 'Telegram Theme'
        elif extension in kindle_extensions:
            return 'Kindle'
        elif extension in bat_file_extensions:
            return 'Batch File'
        elif extension in books_extensions:
            return 'Books'
        elif extension in img_extensions:
            return 'Partition Image'
        elif extension in shell_extensions:
            return 'Shell Script'
        elif extension in library_extensions:
            return 'Library Files'
        elif extension in fonts_extensions:
            return 'Fonts'
        else:
            return 'Other'

    @staticmethod
    def calculate_hash(file_path):
        """
        Calculate the MD5 hash of a file.
        """
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def convert_size(size_bytes):
        """
        Convert the size from bytes to a more readable format (KB, MB, GB).
        """
        if size_bytes < 1024:
            return f"{size_bytes} Bytes"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 ** 3:
            return f"{size_bytes / (1024 ** 2):.2f} MB"
        else:
            return f"{size_bytes / (1024 ** 3):.2f} GB"

    @staticmethod
    def copy_file(source, destination):
        F.create_file_dir(destination)
        shutil.copy2(source, destination)

    @staticmethod
    def move_file(source, destination):
        F.create_file_dir(destination)
        shutil.move(source, destination)

    @staticmethod
    def dir_exists(dir_path):
        if os.path.exists(dir_path):
            return True
        return False

    @staticmethod
    def file_exists(file_path):
        return os.path.exists(file_path)

    @staticmethod
    def remove_dir(dir_path):
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path, onerror=F.remove_readonly)
            return True
        return False

    @staticmethod
    def remove_readonly(func, path, exc_info):
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            raise exc_info[1]

    @staticmethod
    def remove_file(file_path):
        if F.file_exists(file_path):
            os.remove(file_path)
            return True
        return False

    @staticmethod
    def convert_unit(size_in_bytes, unit):
        """ Convert the size from bytes to other units like KB, MB or GB"""
        if unit == "KB":
            return size_in_bytes / 1024
        elif unit == "MB":
            return size_in_bytes / (1024 * 1024)
        elif unit == "GB":
            return size_in_bytes / (1024 * 1024 * 1024)
        else:
            return size_in_bytes

    @staticmethod
    def get_file_size(file_name, size_type="MB"):
        """ Get file in size in given unit like KB, MB or GB"""
        try:
            size = os.path.getsize(file_name)
        except Exception as e:
            size = 0
            print("Exception occurred while calculating file size: " + str(e))
        return F.convert_unit(size, size_type)

    @staticmethod
    def get_dir_list(file_path):
        return_list = []
        dir_list = ""
        file_path = str(file_path.replace("___", "/")).replace("\\", "/")
        for path in str(file_path).split("/"):
            dir_list = str(dir_list) + "/" + path
            if not str(dir_list).__eq__("/") \
                    and not str(dir_list).__contains__(".") \
                    and not str(dir_list).endswith("/system") \
                    and not str(dir_list).endswith("/product") \
                    and not str(dir_list).endswith("/etc") \
                    and not str(dir_list).endswith("/framework") \
                    and not str(dir_list).startswith("/usr/srec/en-US/") \
                    and not str(dir_list).endswith("system_ext_seapp_contexts") \
                    and not str(dir_list).endswith("/priv-app"):
                return_list.append(dir_list[1:])
        return return_list

    @staticmethod
    def read_priv_app_temp_file(file_path, encoding='cp437'):
        return_list = []
        if F.file_exists(file_path):
            file = open(file_path, encoding=encoding)
            text = file.readlines()
            for line in text:
                if line.startswith("uses-permission:"):
                    try:
                        permissions = line.split('\'')
                        if permissions.__len__() > 1:
                            return_list.append(permissions[1])
                    except Exception as e:
                        return_list = ["Exception: " + str(e)]
            file.close()
            F.remove_file(file_path)
        else:
            return_list.append("Exception: " + str(1001))
        return return_list

    @staticmethod
    def read_package_name(file_path, encoding='cp437'):
        if F.file_exists(file_path):
            file = open(file_path, encoding=encoding)
            text = file.readline()
            if text.startswith("package:"):
                index1 = text.find("'")
                if index1 == -1:
                    text = text.replace("package:", "").strip()
                else:
                    text = text[index1 + 1: -1]
                    index1 = text.find("'")
                    text = text[0: index1]
            file.close()
            F.remove_file(file_path)
        else:
            text = "Exception: " + str(1001)
        return text

    @staticmethod
    def read_package_version(file_path, encoding='cp437'):
        if F.file_exists(file_path):
            file = open(file_path, encoding=encoding)
            text = file.readline()
            if text.__contains__("versionName="):
                index1 = text.find("versionName='")
                text = text[index1 + 13: -1]
                index1 = text.find("'")
                text = text[0: index1]
            file.close()
            F.remove_file(file_path)
        else:
            text = "Exception: " + str(1001)
        return text

    @staticmethod
    def read_key(file_path, key, encoding='cp437'):
        if F.file_exists(file_path):
            file = open(file_path, encoding=encoding)
            text = file.readline()
            if text.__contains__(f"{key}="):
                index1 = text.find(f"{key}='")
                text = text[index1 + len(key) + 2: -1]
                index1 = text.find("'")
                text = text[0: index1]
            file.close()
            F.remove_file(file_path)
        else:
            text = "Exception: " + str(1001)
        return text

    @staticmethod
    def write_string_file(str_data, file_path):
        F.create_file_dir(file_path)
        if F.file_exists(file_path):
            os.remove(file_path)
        file = open(file_path, "w")
        file.write(str_data)
        file.close()

    @staticmethod
    def convert_to_lf(filename):
        with open(filename, 'r', newline='\n', encoding='utf-8') as file:
            content = file.read()
        content = content.replace('\r\n', '\n')
        with open(filename, 'w', newline='\n', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def write_string_in_lf_file(str_data, file_path):
        F.create_file_dir(file_path)
        if F.file_exists(file_path):
            os.remove(file_path)
        file = open(file_path, "w", newline='\n')
        file.write(str_data)
        file.close()

    @staticmethod
    def read_string_file(file_path):
        if F.file_exists(file_path):
            file = open(file_path, "r", encoding='cp437')
            lines = file.readlines()
            file.close()
            return lines
        else:
            print("File: " + file_path + " not found!")
            return ['File Not Found']

    @staticmethod
    def read_binary_file(file_path):
        if F.file_exists(file_path):
            file = open(file_path, "rb")
            lines = file.readlines()
            file.close()
            return lines
        else:
            print("File: " + file_path + " not found!")
            return ['File Not Found']

    @staticmethod
    def get_md5(file_path):
        if F.file_exists(file_path):
            md5_hash = hashlib.md5()
            a_file = open(file_path, "rb")
            content = a_file.read()
            md5_hash.update(content)
            digest = md5_hash.hexdigest()
            a_file.close()
            return digest
        else:
            return "File Not Found"
