#!/usr/bin/env python3

import argparse
import inspect
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
import contenttypes

def copy_and_normalize_image(image: str) -> str:
    feature_image_new = Path(f"{args.type}/{image}")
    target_dir = Path(temp_dir) / Path(feature_image_new).parent
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"{record["slug"]}>>>{record['feature_image']}<<<")
    shutil.copy(
        f"{run_dir}/exported_typo3/media/{record['feature_image']}",
        f"{temp_dir}/{feature_image_new}"
    )
    return str(feature_image_new)

run_dir = os.path.realpath(os.path.dirname(os.path.realpath(__file__)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert TYPO3 export JSON to Ghost import JSON"
    )
    parser.add_argument('-l', '--limit',
                        default=0,
                        type=int,
                        help="Maximum number of posts"
                        )

    parser.add_argument('-t', '--type',
                        type=str,
                        required=True,
                        help="Type of conversion"
                        )
    parser.add_argument('-f', '--slug-filter',
                        default = ".*",
                        type = str,
                        help = "Slug Filter"
                        )

    args = parser.parse_args()

    class_name = args.type
    try:
        cls = getattr(contenttypes, class_name)
    except AttributeError:
        print(f"There is no such class {class_name}")
        classes = inspect.getmembers(contenttypes, inspect.isclass)
        for name, cls in classes:
            if issubclass(cls, contenttypes.Post) and cls is not contenttypes.Post:
                print(name, "→", cls)
        sys.exit(1)

    post_instance = cls(run_dir)
    post_instance.load_import_data()
    post_instance.load_export_data()

    ghost_data = post_instance.convert_typo3_to_ghost(
        args.slug_filter,
        args.limit
    )

    output_file = f"{run_dir}/import_ghost/{args.type}-import.zip"


    with tempfile.TemporaryDirectory() as temp_dir:
        count_extra_images = 0
        for record in ghost_data["data"]["posts"]:
            if "feature_image" in record:
                record["feature_image"] = copy_and_normalize_image(record["feature_image"])
            if len(record["extra_images"]) > 0:
                count_extra_images += 1
                print(f"More than one image '{record["title"]}' ----> '{record['slug']}' : {record['extra_images']}")

        print(f"We have {count_extra_images} record with more than one image")
        export_data_file = Path(temp_dir) / Path("import.json")
        print(f"Exporting Ghost JSON to {export_data_file}")
        with open(str(export_data_file), "w", encoding="utf-8") as f:
           json.dump(ghost_data, f, indent=2, ensure_ascii=False)

        zip_file = run_dir + f"/import_ghost/{args.type}.zip"
        print(f"Zipping Ghost data to {zip_file}")
        with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in Path(temp_dir).rglob("*"):
                if file_path.is_file():
                    zipf.write(
                        file_path,
                        arcname=file_path.relative_to(temp_dir),
                    )
