import os, time
from shutil import copyfile
import subprocess

class BackupData:
    def __init__(self, path, lookups, editBox):
        self.path = path
        self.base = path
        self.lookups = [dir.strip().replace("\\", "/") for dir in lookups if os.path.exists(dir.strip())]
        self.sync_services = {'Google Drive': 'C:/Program Files (x86)/Google\Drive/googledrivesync.exe',
                            'Dropbox': 'C:/Program Files (x86)/Dropbox/Client/Dropbox.exe'}

        self.path_content = set()
        self.parse_log()
        self.parse_dir(path)
        self.content_to_delete = sorted(self.log_content - self.path_content, reverse=True)
        self.content_to_add = sorted(self.path_content - self.log_content)

        # self.console_output = editBox
        self.backup()



    def parse_log(self):
        if not os.path.exists('log.txt'):
            open('log.txt', 'w')
        self.log_content = {row.strip() for row in open('log.txt', 'r')}

    def backup(self):
        self.add_content()
        self.delete_content()
        f = open('log.txt', 'w')
        f.write("\n".join((path for path in self.path_content)))
        f.close()
        # self.console_output.append("Finished backing up ...\n\n")


    def add_content(self):
        for path in self.content_to_add:
            for dest in self.lookups:
                if not os.path.exists(dest + path):
                    if os.path.isdir(self.base + path):
                        os.makedirs(dest+path)
                    else:
                        copyfile(self.base + path, dest+path)
                    print("+", dest+path)
                    # self.console_output.append("+ {}\n".format(dest+path))

    def delete_content(self):
        for path in self.content_to_delete:
            for dest in self.lookups:
                if os.path.exists(dest+path):
                    if os.path.isfile(dest + path):
                        os.remove(dest + path)
                    else:
                        os.removedirs(dest+path)
                    print('-', dest + path)
                    # self.console_output.append("- {}\n".format(dest + path))


    def parse_dir(self, path):
        self.path_content.add(path.replace(self.base, ""))
        if os.path.isdir(path):
            for f in os.listdir(path):
                self.parse_dir(path + "/" + f)

    # def parse_dir(self, path):
    #     if not os.path.isdir(path):
    #         for dir in self.lookups:
    #             dir = path.replace(self.base, dir)
    #             if not os.path.isfile(dir):
    #                 print("Doesnt exist, creating file", dir)
    #                 copyfile(path, dir)
    #     else:
    #         for dir in self.lookups:
    #             dir = path.replace(self.base, dir)
    #             if not os.path.exists(dir):
    #                 print("Directory doesnt exists, creating it", dir)
    #                 os.makedirs(dir)
    #         for f in os.listdir(path):
    #             self.parse_dir(path + "/" + f)

    def sync_data(self):
        for service in self.sync_services:
            self.console_output.append("\nSyncing with {} ...".format(service))
            subprocess.call([self.sync_services[service]])
            self.console_output.append("Sync completed.\n")
            self.console_output.append("Syncing has finished.\n")