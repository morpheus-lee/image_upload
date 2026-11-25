import sqlite3
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 20_000_000
PAGE_SIZE = 20
FORMATS = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}


def prepare_image(data):
    if not data or len(data) > MAX_BYTES:
        raise ValueError("請選擇一張 10 MiB 以內的圖片。")
    try:
        with Image.open(BytesIO(data), formats=list(FORMATS)) as image:
            if image.width * image.height > MAX_PIXELS:
                raise ValueError("圖片最多可有 2,000 萬像素。")
            if getattr(image, "is_animated", False):
                raise ValueError("請上傳靜態圖片。")
            mime = FORMATS[image.format]
            image.load()
            thumbnail = ImageOps.exif_transpose(image).convert("RGBA")
            thumbnail.thumbnail((144, 108))
            output = BytesIO()
            thumbnail.save(output, "PNG")
            return mime, output.getvalue()
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError):
        raise ValueError("請上傳有效的 JPEG、PNG 或 WebP 圖片。") from None


@contextmanager
def connect(path):
    path = Path(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with closing(sqlite3.connect(path, timeout=10)) as db, db:
        db.row_factory = sqlite3.Row
        db.execute("""
            CREATE TABLE IF NOT EXISTS images (
                seq INTEGER PRIMARY KEY,
                id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                mime TEXT NOT NULL,
                original BLOB NOT NULL,
                thumbnail BLOB NOT NULL
            )
        """)
        yield db


def save_image(path, name, data):
    mime, thumbnail = prepare_image(data)
    name = name.replace(chr(92), "/").rsplit("/", 1)[-1]
    name = "".join(char for char in name if char.isprintable()).strip()[:255]
    with connect(path) as db:
        db.execute(
            "INSERT INTO images (id, name, created_at, mime, original, thumbnail) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (uuid4().hex, name or "圖片", datetime.now(timezone.utc).isoformat(),
             mime, data, thumbnail),
        )


def list_images(path, page):
    with connect(path) as db:
        db.execute("BEGIN")
        count = db.execute("SELECT count(*) FROM images").fetchone()[0]
        last_page = max(1, (count + PAGE_SIZE - 1) // PAGE_SIZE)
        page = min(page, last_page)
        rows = db.execute(
            "SELECT id, name, created_at FROM images "
            "ORDER BY seq DESC LIMIT ? OFFSET ?",
            (PAGE_SIZE, (page - 1) * PAGE_SIZE),
        ).fetchall()
    return rows, page, last_page, count


def read_image(path, image_id, thumbnail):
    column = "thumbnail" if thumbnail else "original"
    with connect(path) as db:
        return db.execute(
            f"SELECT {column} AS data, mime FROM images WHERE id = ?",
            (image_id,),
        ).fetchone()
