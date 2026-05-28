from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from zipfile import BadZipFile, ZipFile


LANG_PATTERN = re.compile(r"^assets/([^/]+)/lang/zh_cn\.json$", re.IGNORECASE)
ARCHIVE_SUFFIXES = {".jar", ".zip"}


def sanitize_segment(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", value.strip())
    return cleaned or "unknown"


def iter_archives(root: Path) -> list[Path]:
    archives: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in ARCHIVE_SUFFIXES:
            continue
        archives.append(path)
    return sorted(archives)


def extract_zh_cn_files(root: Path, output_dir: Path) -> tuple[int, int]:
    extracted = 0
    archives_scanned = 0

    for archive_path in iter_archives(root):
        archives_scanned += 1
        try:
            with ZipFile(archive_path) as archive:
                archive_tag = sanitize_segment(archive_path.relative_to(root).as_posix().replace("/", "__"))
                matched = False

                for member in archive.namelist():
                    match = LANG_PATTERN.match(member)
                    if not match:
                        continue

                    modid = sanitize_segment(match.group(1))
                    target_path = output_dir / modid / f"{archive_tag}.json"
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    with archive.open(member) as source, target_path.open("wb") as target:
                        shutil.copyfileobj(source, target)

                    extracted += 1
                    matched = True

                if matched:
                    print(f"[OK] {archive_path.relative_to(root).as_posix()}")
        except BadZipFile:
            print(f"[SKIP] {archive_path.relative_to(root).as_posix()} is not a valid archive")

    return archives_scanned, extracted


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="从整合包的 mod / resourcepack 压缩包中提取 assets/*/lang/zh_cn.json。"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="要扫描的根目录，默认是当前工作目录。",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="输出目录，默认在根目录下创建 zh_cn 文件夹。",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root directory does not exist: {root}")

    output_dir = args.output.resolve() if args.output else (root / "zh_cn").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    archives_scanned, extracted = extract_zh_cn_files(root, output_dir)

    print()
    print(f"Scanned archives: {archives_scanned}")
    print(f"Extracted zh_cn files: {extracted}")
    print(f"Output directory: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
