from pathlib import Path, PurePosixPath

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.deps import settings
from app.services.recipe_service import import_recipes, merge_import_summaries
from app.services.translation_service import import_translation_paths, refresh_recipe_labels

router = APIRouter()


def safe_upload_path(upload_dir: Path, filename: str) -> Path:
    clean_parts = [
        part
        for part in PurePosixPath(filename.replace("\\", "/")).parts
        if part not in {"", ".", ".."}
    ]
    if not clean_parts:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    root = upload_dir.resolve()
    target_path = root.joinpath(*clean_parts).resolve()
    if root != target_path and root not in target_path.parents:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    return target_path


@router.post("/upload")
async def upload_recipe_files(files: list[UploadFile] = File(...)) -> dict:
    json_files = [file for file in files if file.filename and file.filename.lower().endswith(".json")]
    if not json_files:
        raise HTTPException(status_code=400, detail="请上传 .json 文件。")

    cfg = settings()
    upload_dir = Path(cfg.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    recipe_summaries = []
    recipe_filenames = []
    failed_files: list[str] = []
    translation_paths: list[Path] = []

    for file in json_files:
        filename = file.filename or f"{len(recipe_filenames)}.json"
        try:
            target_path = safe_upload_path(upload_dir, filename)
            target_path.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(target_path, "wb") as out_file:
                while chunk := await file.read(1024 * 1024):
                    await out_file.write(chunk)

            if "zh_cn.json" in filename.lower():
                translation_paths.append(target_path)
            else:
                recipe_summaries.append(await import_recipes(target_path, source_file=filename))
                recipe_filenames.append(filename)
        except Exception:
            failed_files.append(filename)

    translation_summary = {"entries": 0, "files": 0, "labels_refreshed": 0}
    if translation_paths:
        translation_summary = import_translation_paths(translation_paths)
        refreshed = await refresh_recipe_labels()
        translation_summary["labels_refreshed"] = int(refreshed.get("updated", 0))

    return {
        "filenames": recipe_filenames,
        "translation_files": [path.as_posix() for path in translation_paths],
        "failed_files": failed_files,
        "translation_summary": translation_summary,
        "summary": merge_import_summaries(recipe_summaries),
    }
