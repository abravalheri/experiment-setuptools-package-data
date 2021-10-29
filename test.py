import io
import json
import shutil
import subprocess
import sys
from configparser import ConfigParser
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

import logicmin
from tabulate import tabulate

EXPERIMENT = Path(__file__).parent
BASE = EXPERIMENT / "base"

INPUTS = ("include_package_data", "exclude_package_data", "package_data", "MANIFEST.in")
OUTPUTS = ("wheel", "sdist")

PKGDATA = {"example_package": "*.txt, sub-dir/*.txt"}


MANIFEST = """\
global-include *.py *.txt
global-exclude *.py[cod]
"""


def main():
    results = []
    truth_table = logicmin.TT(len(INPUTS), len(OUTPUTS))

    with TemporaryDirectory() as tmpdir:
        for i, (cfg, opts) in enumerate(setupcfg()):
            project = Path(tmpdir, f"example-{i}")
            shutil.copytree(BASE, project)
            (project / "setup.cfg").write_text(cfg)
            for manifest in (None, MANIFEST):
                opts = {**opts, "MANIFEST.in": manifest}
                if manifest:
                    (project / "MANIFEST.in").write_text(manifest)
                    print("  ----> add MANIFEST.in")
                else:
                    assert not (project / "MANIFEST.in").exists()
                    print("  ----> no MANIFEST.in")

                run([sys.executable, "-m", "build", "--wheel", str(project)])
                list_zip = ["unzip", "-l", str(next(project.glob("dist/*.whl")))]
                p = run(list_zip, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                files = str(p.stdout, "utf-8")
                print(files, flush=True)
                out = {"wheel": are_datafiles_included(files)}
                print("~" * 60, flush=True)

                run([sys.executable, "-m", "build", "--sdist", str(project)])
                list_tar = ["tar", "tf", str(next(project.glob("dist/*.tar.gz")))]
                p = run(list_tar, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                files = str(p.stdout, "utf-8")
                print(files, flush=True)
                out["sdist"] = are_datafiles_included(files)
                print("~" * 60, flush=True)

                results.append({**opts, **out})
                inputs = dict2bitstring(opts, INPUTS)
                outputs = dict2bitstring(out, OUTPUTS)
                truth_table.add(inputs, outputs)

            print("\n\n\n\n", flush=True)

        (EXPERIMENT / "results.json").write_text(json.dumps(results, indent=2))
        table = [
            {k: table_cell(v, k in OUTPUTS) for k, v in row.items()}
            for row in results
        ]
        print(tabulate(table, headers="keys", tablefmt="grid"))
        logicexp = truth_table.solve()
        short_in = [x[0].lower() for x in INPUTS]
        short_out = [x[0].lower() for x in OUTPUTS]
        print("\n\n\n\n")
        print(logicexp.printN(xnames=short_in, ynames=short_out))
        print("\n")
        print(logicexp.printN(xnames=INPUTS, ynames=OUTPUTS, syntax="VHDL"))


def setupcfg():
    cfg_text = (BASE / "setup.cfg").read_text()
    for include_package_data in (False, True):
        for exclude_package_data in (None, PKGDATA):
            for package_data in (None, PKGDATA):
                opts = {
                    "include_package_data": include_package_data,
                    "exclude_package_data": exclude_package_data,
                    "package_data": package_data,
                }

                print("*" + 60 * "=*", flush=True)
                print(opts, "\n", flush=True)

                cfg = ConfigParser()
                cfg.read_string(cfg_text)
                cfg["options"]["include_package_data"] = str(include_package_data)
                for section in ("exclude_package_data", "package_data"):
                    if opts[section] is None:
                        assert not cfg.has_section(f"options.{section}")
                    else:
                        cfg.add_section(f"options.{section}")
                        cfg[f"options.{section}"].update(opts[section])

                with io.StringIO() as sio:
                    cfg.write(sio)
                    yield (sio.getvalue(), opts)


def run(cmd, **kwargs):
    print("\n$", " ".join(cmd), flush=True)
    return subprocess.run(cmd, **kwargs)


def are_datafiles_included(text):
    return "data.txt" in text and "sub-dir/other.txt" in text


def dict2bitstring(adict, fields):
    return "".join("0" if adict[f] in (None, False) else "1" for f in fields)


def table_cell(value, force_yes_no=False):
    if force_yes_no:
        return "Yes" if value else "No"
    if value is True:
        return True
    return "Yes" if value else None


if __name__ == "__main__":
    main()
