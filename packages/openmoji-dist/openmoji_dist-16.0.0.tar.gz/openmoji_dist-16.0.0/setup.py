from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from warnings import filterwarnings

from openmoji_dist import VERSION, _get_openmoji_data_dir, SVG_SOURCE_URL, FONT_SOURCE_URL, LICENSE_TEXT_URL, BUILD
from setuptools import setup, find_packages

filterwarnings("ignore", "", UserWarning, "setuptools.dist")

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3 :: Only",
    "Typing :: Typed",
]

OPENMOJI_DIR = Path(_get_openmoji_data_dir())

if (Path(__file__).parent / ".git").exists():
    import shutil
    shutil.rmtree(OPENMOJI_DIR, ignore_errors=True)

if (not OPENMOJI_DIR.exists() or not tuple(OPENMOJI_DIR.iterdir())) and "egg_info" not in sys.argv[1:]:
    from tempfile import TemporaryDirectory
    from urllib.request import urlretrieve
    from zipfile import ZipFile

    SVG_DEST_DIR = OPENMOJI_DIR / "svg"
    SVG_DEST_DIR.mkdir(exist_ok=True, parents=True)
    FONT_DEST_DIR = OPENMOJI_DIR / "font"
    FONT_DEST_DIR.mkdir(exist_ok=True)

    urlretrieve(LICENSE_TEXT_URL, OPENMOJI_DIR / "LICENSE")

    with TemporaryDirectory() as download_dir:
        svg_file = Path(download_dir) / "svg.zip"
        urlretrieve(SVG_SOURCE_URL, svg_file)
        with ZipFile(svg_file) as zip_file:
            zip_file.namelist()
            zip_file.extractall(SVG_DEST_DIR)

    with TemporaryDirectory() as download_dir:
        font_file = Path(download_dir) / "font.zip"
        urlretrieve(FONT_SOURCE_URL, font_file)
        with ZipFile(font_file) as zip_file:
            font_files = defaultdict(set)
            unicode_ranges: set[str] = set()
            for member in zip_file.namelist():
                if "glyf_colr_" not in member:
                    continue
                type_ = ("glyf_colr1" if "glyf_colr_1" in member else "glyf_colr0")
                if not member.endswith((".woff2", ".ttf")):
                    if member.endswith(".css"):
                        zip_file.extract(member=member, path=Path(download_dir))
                        unicode_ranges.update(
                            line.strip()
                            for line in (Path(download_dir) / member).read_text("UTF-8").splitlines()
                            if "unicode-range" in line
                        )
                    continue
                # TODO: maybe `pyftsubset --flavor=woff2 --with-zopfli --output-file=... ... '*'`
                # In tests this decreaed file sizes by a few kb
                zip_file.extract(member=member, path=Path(download_dir))
                name = type_ + "." + member.split(".")[-1]
                (FONT_DEST_DIR / name).write_bytes((Path(download_dir) / member).read_bytes())
                font_files[type_].add(name)

            assert len(unicode_ranges) == 1
            unicode_range = unicode_ranges.pop()
            for type_ in font_files.keys():
                # maybe todo: https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/src#tech
                src = ",".join(
                    'url("{file}?v={version}") format("{format}")'.format(
                        version=VERSION,
                        file=file,
                        format={"ttf": "truetype", "woff2": "woff2"}[file.split(".")[-1]]
                    )
                    for file in sorted(font_files[type_], key=lambda file: {"ttf": 1, "woff2": 0}[file.split(".")[-1]])
                )
                (FONT_DEST_DIR / f"{type_}.css").write_text(
                    "@font-face {"
                    'font-family: "OpenMojiColor";'
                    f'src: {src};'
                    f"{unicode_range}"
                    "}\n",
                    "UTF-8"
                )
    from subprocess import run

    files_to_compress = tuple(
        path.relative_to(OPENMOJI_DIR).as_posix()
        for path in OPENMOJI_DIR.rglob("*")
        if path.is_file()
    )
    run(["zstd", "--zstd=wlog=23,clog=23,hlog=22,slog=6,mml=3,tlen=48,strat=9", "-k", "-T0", *files_to_compress], check=True, cwd=OPENMOJI_DIR)
    run(["pigz", "-11", "-fmk", *files_to_compress], check=True, cwd=OPENMOJI_DIR)
    for file in files_to_compress:
        size = (OPENMOJI_DIR / file).stat(follow_symlinks=False).st_size
        algs = ("gz", "zst")
        if file.rsplit(".", 1)[-1] in algs:
            continue
        for alg in algs:
            compressed = OPENMOJI_DIR / f"{file}.{alg}"
            if compressed.stat(follow_symlinks=False).st_size // 10 >= size // 10:
                compressed.unlink()
                print(compressed.as_posix(), "size increased while compressing")


package_data = {
    OPENMOJI_DIR.parent.relative_to(Path(__file__).parent).as_posix().replace("/", "."): [
        file.relative_to(OPENMOJI_DIR.parent).as_posix()
        for file in OPENMOJI_DIR.rglob("*")
        if file.is_file()
    ]
}

setup(
    name="openmoji-dist",
    license="CC-BY-SA-4.0",
    platforms="OS Independent",
    description="Openmoji files",
    long_description=(Path(__file__).parent / "README").read_text("UTF-8"),
    url="https://codeberg.org/Joshix/py-openmoji",
    version=VERSION if not BUILD else f"{VERSION}.{BUILD}",
    classifiers=classifiers,
    packages=find_packages(),
    package_data=package_data,
    include_package_data=True,
)
