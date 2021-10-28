import io
import sys
import shutil
from configparser import ConfigParser
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable
import subprocess


BASE = Path(__file__).parent / "base"

PKGDATA = {"example_package": "*.txt, sub-dir/*.txt"}


def setupcfg():
    cfg_text = (BASE / "setup.cfg").read_text()
    for include_package_data in (False, True):
        for package_data in (None, PKGDATA):
            print(f":::: {include_package_data=} :::: {package_data=} ::::", flush=True)
            cfg = ConfigParser()
            cfg.read_string(cfg_text)
            cfg["options"]["include_package_data"] = str(include_package_data)
            if package_data is None:
                assert not cfg.has_section("options.package_data")
            else:
                cfg.add_section("options.package_data")
                cfg["options.package_data"].update(package_data)

            with io.StringIO() as sio:
                cfg.write(sio)
                yield sio.getvalue()


def run(cmd):
    print("$", ' '.join(cmd), flush=True)
    subprocess.run(cmd)


MANIFEST = """\
global-include *.py *.txt
global-exclude *.py[cod]
"""



with TemporaryDirectory() as tmpdir:
    for i, cfg in enumerate(setupcfg()):
        print("*" + 60 * "=*", flush=True)
        project = Path(tmpdir, f"example-{i}")
        shutil.copytree(BASE, project)
        (project / "setup.cfg").write_text(cfg)
        for include_manifest in (False, True):
            if include_manifest:
                (project / "MANIFEST.in").write_text(MANIFEST)
                print("  ----> add MANIFEST.in")
            else:
                assert not (project / "MANIFEST.in").exists()
                print("  ----> no MANIFEST.in")

            run([sys.executable, "-m", "build", "--wheel", str(project)])
            run(["unzip", "-l", str(next(project.glob("dist/*.whl")))])
            print("~" * 60, flush=True)
            run([sys.executable, "-m", "build", "--sdist", str(project)])
            run(["tar", "tf", str(next(project.glob("dist/*.tar.gz")))])
            print("~" * 60, flush=True)
        print("\n\n\n\n", flush=True)
