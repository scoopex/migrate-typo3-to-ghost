import json
import re
from datetime import datetime, timezone
from pprint import pformat


class Post:
    tags = ["notimplemented"]
    slug_prefix = "noop"

    def __init__(self, run_dir: str) -> None:
        self.run_dir = run_dir
        self.data = {}
        self.tagdata = []

    def load_import_data(self) -> dict:
        import_data_file = f"{self.run_dir}/exported_typo3/{self.slug_prefix}-export.json"
        with open(import_data_file, "r", encoding="utf-8") as f:
            typo3_data = json.load(f)
            self.data = typo3_data
            print(f"data loaded from {import_data_file}")

    def load_export_data(self) -> dict:
        ghost_export_file = f"{self.run_dir}/exported_ghost/exported-ghost.json"
        with open(ghost_export_file, "r", encoding="utf-8") as f:
            ghost_export_data = json.load(f)

            taglist = {}
            for record in ghost_export_data["db"][0]["data"]["tags"]:
                if record["slug"].startswith("hash"):
                    continue
                taglist[record["slug"]] = record["id"]

            for tag in self.tags:
                if tag not in taglist:
                    raise RuntimeError(f"Unknown tag: >>>{tag}<<<\nAvailable Tags: \n{pformat(taglist, indent=2)}")
                self.tagdata.append(
                    {"id": str(taglist[tag])}
                )

    def typo3_to_german_date(self, timestamp: str) -> str:
        dt = datetime.strptime(timestamp, "%d-%m-%y %H:%M")
        date_str = dt.strftime("%d.%m.%Y")
        return date_str

    def typo3_to_ghost_datetime(self, timestamp: str) -> str:
        """
        Konvertiert Unix-Timestamp (Sekunden) in Ghost-kompatibles ISO-8601-Format
        """
        if not timestamp or timestamp == 0:
            raise RuntimeError(f"Error: timestamp not valid: {timestamp}")
        dt = datetime.strptime(timestamp, "%d-%m-%y %H:%M")
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    def convert_bodytext(self, record: dict) -> str:
        raise NotImplementedError()

    def check_empty(self, text: str) -> str:
        if len(text) == 0:
            raise RuntimeError(f"Unable to convert content: {text}")
        return text

    def convert_typo3_to_ghost(self,
                               slug_filter: str,
                               limit: int = 0) -> dict:

        ghost_posts = {}
        for record in self.data.get("records", []):
            crdate = record.get("crdate", 0)
            slug = self.check_empty(record.get("path_segment", ""))
            title =  self.check_empty(record.get("title", ""))
            if not re.fullmatch(slug_filter, slug):
                print(f"Skipping slug : {title} : {slug}")
                continue

            post = {
                "title": self.check_empty(record.get("title", "")).strip(),
                "slug": f"{self.slug_prefix}-{slug}",
                "html": self.convert_bodytext(record),
                "status": "published",
                "created_at": self.typo3_to_ghost_datetime(crdate),
                "updated_at": self.typo3_to_ghost_datetime(crdate),
                "published_at": self.typo3_to_ghost_datetime(crdate),
                "tags": self.tagdata
            }

            if "fal_media" in record and record["fal_media"] != "":
                post["feature_image"] = record["fal_media"]

            ghost_posts[f"{self.typo3_to_ghost_datetime(crdate)}-{slug}"] = post

            print("x" * 100)
            print("xxx")
            print(json.dumps(record, indent=2, ensure_ascii=False))
            print()
            print(json.dumps(post, indent=2, ensure_ascii=False))
            print("xxx")
            print("x" * 100)

        ghost_posts_sorted = []
        ghost_posts_count = 0
        for key in sorted(ghost_posts, reverse=True):
            if limit != 0 and ghost_posts_count >= limit:
                print(f"Reached specified limit of {limit} posts")
                break
            elif limit == 0:
                ghost_posts_sorted.append(ghost_posts[key])
            else:
                ghost_posts_sorted.append(ghost_posts[key])
            ghost_posts_count += 1

        ghost_export = {
            "meta": {
                "exported_on": int(datetime.now(tz=timezone.utc).timestamp() * 1000),
                "version": "5.0.0"
            },
            "data": {
                "posts": ghost_posts_sorted
            }
        }
        print(f"Exported {ghost_posts_count} posts of {len(self.data['records'])}")

        return ghost_export

class Antrag(Post):
    tags = ["news", "antraege", "gemeinderat"]
    slug_prefix = "antrag"

    def convert_bodytext(self, record: dict) -> str:
        text = record["bodytext"]
        result = text.replace("\r\n", "")
        result = result.replace("\t", "")
        result = result.replace("\n", "")
        if len(result) == 0:
            raise RuntimeError(f"Unable to convert content: {text}")

        g_date = self.typo3_to_german_date(record["crdate"])
        result = f"<p>Publikationsdatum {g_date}</p><p>{record["teaser"]}</p><p>{result}</p>"

        return result

class Stellungnahme(Post):
    tags = ["news", "stellungnahmen", "gemeinderat"]
    slug_prefix = "stellungnahme"

    def convert_bodytext(self, record: dict) -> str:
        text = record["bodytext"]
        result = text.replace("\r\n", "")
        result = result.replace("\t", "")
        result = result.replace("\n", "")
        if len(result) == 0:
            raise RuntimeError(f"Unable to convert content: {text}")

        g_date = self.typo3_to_german_date(record["crdate"])
        result = f"<p>Publikationsdatum {g_date}</p><p>{record["teaser"]}</p><p>{result}</p>"

        return result