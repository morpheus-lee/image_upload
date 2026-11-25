from datetime import datetime
from functools import wraps
from pathlib import Path
from uuid import UUID
from zoneinfo import ZoneInfo

from flask import (
    Response, abort, current_app, redirect, render_template_string, request, url_for,
)
from flask_appbuilder.api import expose, permission_name, protect
from flask_login import current_user
from flask_login.utils import login_url
from flask_wtf.csrf import generate_csrf, validate_csrf
from superset_core.rest_api.api import RestApi
from superset_core.rest_api.decorators import api
from wtforms.validators import ValidationError

from .storage import MAX_BYTES, list_images, read_image, save_image
from .ui import CSS, PAGE

RESOURCE = "ImageLibrary"
MENU = "圖片管理"
PRIVATE_HEADERS = {"Cache-Control": "private, no-store"}


def database_path():
    return current_app.config.get("IMAGE_LIBRARY_DB_PATH") or (
        Path(current_app.config["DATA_DIR"]) / "image-library" / "images.sqlite3"
    )


def can_read():
    return current_user.is_authenticated and current_app.appbuilder.sm.has_access(
        "can_read", RESOURCE
    )


def session_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(login_url(current_app.appbuilder.get_url_for_login, request.url))
        return view(*args, **kwargs)

    return wrapper


@api(id="image_library", name="Image Library")
class ImageLibraryApi(RestApi):
    class_permission_name = RESOURCE
    csrf_exempt = False

    def render_library(self, status=200, error=None):
        page = max(1, request.args.get("page", 1, type=int))
        rows, page, last_page, count = list_images(database_path(), page)
        taipei = ZoneInfo("Asia/Taipei")
        rows = [
            dict(
                row,
                id=UUID(row["id"]),
                display_time=datetime.fromisoformat(row["created_at"])
                .astimezone(taipei)
                .strftime("%Y-%m-%d %H:%M"),
            )
            for row in rows
        ]
        html = render_template_string(
            PAGE, endpoint=self.endpoint, rows=rows, page=page,
            last_page=last_page, count=count, error=error,
            uploaded=request.args.get("uploaded") == "1" and status == 200,
            can_upload=self.appbuilder.sm.has_access("can_write", RESOURCE),
            csrf_token=generate_csrf(),
        )
        return Response(html, status=status, headers=PRIVATE_HEADERS)

    @expose("/")
    @session_required
    @protect()
    @permission_name("read")
    def library(self):
        return self.render_library()

    @expose("/upload", methods=["POST"])
    @session_required
    @protect()
    @permission_name("write")
    def upload(self):
        if not can_read():
            abort(403)
        if request.content_length is not None and request.content_length > MAX_BYTES + 65_536:
            return self.render_library(413, "請選擇一張 10 MiB 以內的圖片。")
        try:
            validate_csrf(request.form.get("csrf_token"))
        except ValidationError:
            abort(400)
        files = request.files.getlist("image")
        if len(files) != 1 or not files[0].filename:
            return self.render_library(400, "請選擇一張圖片。")
        image = files[0]
        try:
            save_image(database_path(), image.filename, image.stream.read(MAX_BYTES + 1))
        except ValueError as error:
            return self.render_library(400, str(error))
        return redirect(url_for(f"{self.endpoint}.library", uploaded=1), code=303)

    @expose("/image/<uuid:image_id>")
    @session_required
    @protect()
    @permission_name("read")
    def image(self, image_id):
        return self.image_response(image_id, thumbnail=False)

    @expose("/thumbnail/<uuid:image_id>")
    @session_required
    @protect()
    @permission_name("read")
    def thumbnail(self, image_id):
        return self.image_response(image_id, thumbnail=True)

    def image_response(self, image_id, thumbnail):
        row = read_image(database_path(), image_id.hex, thumbnail)
        if row is None:
            abort(404)
        return Response(
            row["data"], mimetype="image/png" if thumbnail else row["mime"],
            headers={**PRIVATE_HEADERS, "X-Content-Type-Options": "nosniff"},
        )

    @expose("/style.css")
    @session_required
    @protect()
    @permission_name("read")
    def stylesheet(self):
        return Response(CSS, mimetype="text/css", headers=PRIVATE_HEADERS)


current_app.appbuilder.add_link(
    name=MENU, href="ImageLibraryApi.library", cond=can_read,
)
