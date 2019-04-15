{% load fullurl %}
import os
import json
import shutil
import platform
import tempfile
import subprocess
from distutils.command.build import build
from urllib.request import urlopen
from setuptools import setup
from setuptools.command.build_py import build_py

class Extract7z:

    @staticmethod
    def find_7z_binary():
        if shutil.which("7z") is not None: return shutil.which("7z")

        try:
            import winreg
            with winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\7-Zip', reserved=0,
                                  access=winreg.KEY_READ) as regkey:
                return os.path.join(winreg.QueryValueEx(regkey, 'Path')[0], '7z.exe')
        except:
            pass

        target = os.path.join(os.getenv("TEMP"), "7za.exe")
        if os.path.exists(target): return target

        return None

    @classmethod
    def prepare(cls, announce):
        if cls.find_7z_binary() is not None: return
        source = "{% fullstatic "7za.exe" %}"
        target = os.path.join(os.getenv("TEMP"), "7za.exe")

        announce("Downloading 7za.exe to extract the archive...")
        with urlopen(source) as f, \
                open(target, "wb") as t:
            t.write(f.read())
            t.close()

    def __init__(self, file):
        file.close()
        self.archive = file.name

    def close(self):
        pass

    def extract(self, filename) -> bytes:
        return subprocess.check_output(
            [self.find_7z_binary(), "e", self.archive, f"-so", filename, "-t7z"],
            universal_newlines=False
        )


class ExtractZip:

    @staticmethod
    def prepare(announce):
        pass

    def __init__(self, file):
        import zipfile
        self.archive = zipfile.ZipFile(file)

    def close(self):
        self.archive.close()

    def extract(self, filename) -> bytes:
        with self.archive.open(filename, "r") as f:
            return f.read()


class ForceBuildVSPlugin(build):

    def run(self):
        self.run_command("build_vs")
        super().run()


try:
    import vapoursynth
except ImportError:
    REQUIRES_VAPOURSYNTH = True
else:
    REQUIRES_VAPOURSYNTH = False

{% autoescape off %}
VSREPO_CONFIGURATION = json.loads("""{{ release.configuration }}""")
DEPENDENCIES = json.loads("""{{ project.dependencies }}""")
{% endautoescape %}
DEPENDENCIES = [s.lower() for s in DEPENDENCIES]

if REQUIRES_VAPOURSYNTH:
    DEPENDENCIES += ["vapoursynth"]

if REQUIRES_VAPOURSYNTH and platform.system() == "Windows":
    DEPENDENCIES += ["vapoursynth-portable"]


{% if project.type == "PyScript" %}
class PyScript(build_py):

    def run(self):
        target: str = VSREPO_CONFIGURATION["script"]["url"]
        script: str = next(iter(VSREPO_CONFIGURATION["script"]["files"].keys()))
        self.announce(f"Downloading {target} to {script}")
        with urlopen(target) as f, \
             tempfile.TemporaryFile("wb", delete=False) as t:
            t.write(f.read())
            t.close()

            if "/zipball/" in target or target.endswith(".zip"):
                with open(t.name, "rb") as zf:
                    extractor = ExtractZip(zf)
                    for filename, (path, _) in VSREPO_CONFIGURATION["script"]["files"].items():
                        with tempfile.TemporaryFile("w+b", delete=False) as a:
                            self.announce(f"Extracting {filename}")
                            a.write(extractor.extract(path))
                            a.close()
                            self.copy_file(a.name, filename)

            else:
                self.announce(f"Packaging {script}")
                self.copy_file(t.name, script)

        super().run()

setup(
    name='{{ project.identifier }}',
    version='{{ release.sanitized_pypa_version }}',
    description="{{ project.description }}",
    url='{{ project.website }}',
    py_modules = [next(iter(VSREPO_CONFIGURATION["script"]["files"].keys()))[:-3]],
    install_requires = DEPENDENCIES,
    cmdclass={
        'build_vs': PyScript,
        'build': ForceBuildVSPlugin
    }
)
{% else %}
if platform.architecture()[0] == "64bit":
    key = "win64"
else:
    key = "win32"

VSREPO_ARCHITECTURE = VSREPO_CONFIGURATION.get(key)
if VSREPO_ARCHITECTURE is None:
    raise EnvironmentError("Your architecture is not supported by this plugin.")


def portable_target():
    if key == "win64":
        plugin_dir = "vapoursynth64"
    else:
        plugin_dir = "vapoursynth32"

    return f"Lib\\site-packages\\{plugin_dir}\\plugins"


if REQUIRES_VAPOURSYNTH:
    target = portable_target()

else:
    vsm_parent = os.path.dirname(vapoursynth.__file__)
    if os.path.exists(os.path.join(vsm_parent, "portable.vs")):
        target = portable_target()

    else:
        root = os.path.join(os.getenv("APPDATA"), "VapourSynth")
        if key == "win64":
            target = os.path.join(root, "plugins64")
        else:
            target = os.path.join(root, "plugins32")




if VSREPO_ARCHITECTURE["url"].endswith("7z"):
    UNPACKER = Extract7z
    SETUP_DEPENDENCIES = []
else:
    UNPACKER = ExtractZip
    SETUP_DEPENDENCIES = []


class VSPlugin(build_py):

    def run(self):
        UNPACKER.prepare(self.announce)

        target = VSREPO_ARCHITECTURE["url"]
        self.announce(f"Downloading {target}")
        with urlopen(target) as f, \
             tempfile.TemporaryFile("w+b", delete=False) as t:
            t.write(f.read())
            t.flush()
            t.seek(0)

            extractor = UNPACKER(t)
            try:
                for filename, (path, _) in VSREPO_ARCHITECTURE["files"].items():
                    with tempfile.TemporaryFile("w+b", delete=False) as a:
                        self.announce(f"Extracting {filename}")
                        a.write(extractor.extract(path))
                        a.close()
                        self.copy_file(a.name, filename)
            finally:
                extractor.close()




setup(
    name='{{ project.identifier }}',
    version='{{ release.sanitized_pypa_version }}',
    description="{{ project.description }}",
    url='{{ project.website }}',
    install_requires = DEPENDENCIES,
    setup_requires = SETUP_DEPENDENCIES,
    cmdclass={
        'build_vs': VSPlugin,
        'build': ForceBuildVSPlugin
    },
    data_files=[
        (target, list(VSREPO_ARCHITECTURE["files"].keys()))
    ]
)
{% endif %}