import os
import re
import sys
import json
import shutil
import zipfile
import requests
import tempfile
import contextlib
from django.core.management.base import BaseCommand

from warehouse.models import Project, Release

DATEREGEX = re.compile("\d{4}-\d{2}-\d{2}")
PEP440REGEX = re.compile(r"(\d+!)?\d+(\.\d+)*((?:a|b|rc)\d+)?(\.post\d+)?(\.dev\d+)?(\+[a-zA-Z0-9]+)?")
GITHUB_TOKEN = "3315dc7cd6bfec214c4e6ce50014d3ffa3ac8269"
UA_HEADERS = {
    "User-Agent": "vs-warehouse/0.1.0 https://github.com/stuxcrystal https://github.com/Irrational-Encoding-Wizardry",
    "From": "stuxcrystal@encode.moe"
}


@contextlib.contextmanager
def chdir(dir):
    current = os.getcwd()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(current)


class Command(BaseCommand):
    help = "Updates the entries inside the warehouse."

    def get_newest_version(self):
        session = requests.Session()
        session.headers.update(UA_HEADERS)

        print("Downloading https://github.com/vapoursynth/vsrepo/archive/master.zip")
        with tempfile.NamedTemporaryFile(delete=False) as f, \
                session.get("https://github.com/vapoursynth/vsrepo/archive/master.zip", stream=True) as r:
            f.write(r.raw.read())
            f.close()

            print("Extracting master.zip")
            with tempfile.TemporaryDirectory() as td:
                zf = zipfile.ZipFile(file=f.name)
                zf.extractall(td)
                zf.close()

                print("Updating the repository")
                path = os.path.join(td, "vsrepo-master")
                with chdir(path):
                    try:
                        import winreg
                    except ImportError:
                        with open("winreg.py", "w") as f:
                            f.write("")
                            f.close()

                    print(f"{sys.executable} vsrupdate.py update-local -o -g [HIDDEN]")
                    os.system(f"{sys.executable} vsrupdate.py update-local -o -g {GITHUB_TOKEN}")

                    # There will be an error. Ignore it, we only care about vspackages.json
                    print(f"{sys.executable} vsrupdate.py compile")
                    os.system(f"{sys.executable} vsrupdate.py compile")

                print("Reading repository")
                with open(os.path.join(path, "vspackages.json"), "r") as data_file:
                    repo = json.loads(data_file.read())

                shutil.rmtree(path)
                return repo

    def make_pyversion(self, version, date, index):
        version = version.lower().replace("-", ".")

        if DATEREGEX.match(version):
            return version.replace("-", ".")

        elif version.startswith("rev"):
            return self.make_pyversion(version[3:], date, index)

        elif version.startswith("release_"):
            return self.make_pyversion(version[len("release_"):], date, index)

        elif version.startswith("r") or version.startswith("v"):
            return self.make_pyversion(version[1:], date, index)

        elif version.startswith("test"):
            return self.make_pyversion(version[4:], date, index)

        elif version.startswith("git:"):
            version = version[4:]
            if date:
                datever = self.make_pyversion("%", date, index)
                return f"{datever}+{version}"
            else:
                return f"{index+1}+{version}"

        elif PEP440REGEX.match(version):
            return version

        elif not date:
            return str(index+1)

        else:
            return f"{date[:10].replace('-','.')}"

    def compile_to_database(self, repository):
        for package in repository:
            print("Updating project:", package["name"])
            project, created = Project.objects.get_or_create(identifier=package["identifier"])
            project.type = package["type"]
            project.identifier = package["identifier"]
            project.category = package["category"]
            project.website = package.get("website", "https://github.com/vapoursynth/vsrepo")
            project.name = package["name"]
            project.description = package["description"]
            project.dependencies = json.dumps(package.get("dependencies", []))
            project.save()

            for v, release in enumerate(reversed(package["releases"])):
                r, create = Release.objects.get_or_create(
                    project=project,
                    release_version=release["version"]
                )

                r.project = project
                r.r_version = release["version"]
                r.pypa_version = self.make_pyversion(release["version"], release.get("published", None), v)
                r.configuration = json.dumps(release)
                r.release_url = "-"
                r.save()

    def handle(self, *args, **kwargs):
        repository = self.get_newest_version()
        self.compile_to_database(repository["packages"])
