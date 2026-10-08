"""Empacota fontes locais sem conservar entradas obsoletas nos ZIPs .skill."""
from pathlib import Path
import argparse
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("whoiam", "pesquisa-seres", "postagem")


def entries(name):
    folder = ROOT / name
    return {p.relative_to(folder).as_posix(): p.read_bytes()
            for p in sorted(folder.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    failed = []
    for name in NAMES:
        expected = entries(name)
        target = ROOT / f"{name}.skill"
        if args.check:
            try:
                with zipfile.ZipFile(target) as archive:
                    actual = {n: archive.read(n) for n in archive.namelist() if not n.endswith("/")}
                if actual != expected:
                    failed.append(name)
            except (OSError, zipfile.BadZipFile):
                failed.append(name)
        else:
            temporary = target.with_suffix(".skill.tmp")
            with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
                for name_in_zip, data in expected.items():
                    info = zipfile.ZipInfo(name_in_zip, date_time=(2026, 10, 8, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(info, data)
            temporary.replace(target)
    if failed:
        raise SystemExit("Pacotes divergentes: " + ", ".join(failed))
    print("Pacotes conferidos." if args.check else "Pacotes atualizados a partir das fontes locais.")


if __name__ == "__main__":
    main()
