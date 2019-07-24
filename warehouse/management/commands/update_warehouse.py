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
from django.utils import dateparse

from warehouse.models import Project, Release, Distribution

DATEREGEX = re.compile("\d{4}-\d{2}-\d{2}")
PEP440REGEX = re.compile(r"(\d+!)?\d+(\.\d+)*((?:a|b|rc)\d+)?(\.post\d+)?(\.dev\d+)?(\+[a-zA-Z0-9]+)?")
GITHUB_TOKEN = os.environ["WAREHOUSE_GITHUB_TOKEN"]
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
                            f.write("""
import contextlib
import shutil
HKEY_LOCAL_MACHINE = None
KEY_READ = None
@contextlib.contextmanager
def OpenKeyEx(*args, **kwargs):
    yield None
    
def QueryValueEx(*args, **kwargs):
    import __main__
    e7z = shutil.which("7z")
    if e7z is not None:
        __main__.cmd7zip_path = e7z
    return None
                            """)

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
            project.github = package.get("github", "")
            project.doom9 = package.get("doom9", "")

            project.name = package["name"]
            project.description = package["description"]
            project.dependencies = json.dumps(package.get("dependencies", []))

            if created:
                project.from_vsutil = True

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
                dt_publish = release.get("published", "")
                if dt_publish:
                    r.published = dateparse.parse_datetime(release["published"])
                r.save()

                for format in ("script", "win32", "win64"):
                    if format not in release:
                        continue

                    dist = release[format]

                    d, create = Distribution.objects.get_or_create(
                        release=r,
                        platform=format
                    )

                    d.format = format
                    d.release = r
                    d.url = dist["url"]
                    d.save()

    def handle(self, *args, **kwargs):
        repository = self.get_newest_version()
        self.compile_to_database(repository["packages"])
