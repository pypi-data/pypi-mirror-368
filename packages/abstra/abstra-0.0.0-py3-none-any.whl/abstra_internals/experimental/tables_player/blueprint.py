import json

from flask import Blueprint, redirect, request

from abstra.tables import count, select, select_by_id
from abstra_internals.environment import IS_PRODUCTION
from abstra_internals.interface.sdk.tables.api import _dump
from abstra_internals.jwt_auth import USER_AUTH_COOKIE_KEY
from abstra_internals.repositories import users_repository
from abstra_internals.server.guards.role_guard import Guard

from ..common.render import make_url
from .models import TableModel
from .templates import render


def get_tables_player_bp():
    guard = Guard(users_repository, enabled=IS_PRODUCTION)
    bp = Blueprint("tables_player", __name__)
    login_url = make_url("/_experimental/login")

    def get_user():
        auth_cookies = request.cookies.get(USER_AUTH_COOKIE_KEY)
        if not auth_cookies:
            return None
        user = guard.auth_decoder(auth_cookies)
        if not user:
            return None
        return guard.repository.get_user(user.email)

    def auth_redirect():
        auth_cookies = request.cookies.get(USER_AUTH_COOKIE_KEY)
        allowed = guard.should_allow(id="tables", auth=auth_cookies)
        if allowed.status == "FORBIDEN" or allowed.status == "UNAUTHORIZED":
            url = login_url(redirect_url=request.url)
            return redirect(url)
        elif allowed.status != "ALLOWED":
            raise Exception("Unexpected status: " + allowed.status)

    @bp.get("/tables")
    def _tables():
        redirection = auth_redirect()
        if redirection:
            return redirection

        dump = _dump()
        tables = [
            TableModel.from_dto(dump, t["name"])
            for t in sorted(dump["tables"], key=lambda t: t["name"])
        ]
        return render(
            template=["page", "tables"],
            context=dict(logout_url=login_url(), user=get_user(), tables=tables),
        )

    @bp.get("/table/<table_name>")
    def _table(table_name: str):
        redirection = auth_redirect()
        if redirection:
            return redirection
        dump = _dump()
        table = TableModel.from_dto(dump, table_name)
        if "filter" in request.args:
            where = json.loads(request.args["filter"])
        else:
            where = {}

        return render(
            template=["page", "table"],
            context=dict(
                logout_url=login_url(),
                user=get_user(),
                table_name=table.name,
                columns=table.columns,
                rows=select(table.name, where=where),
            ),
        )

    @bp.get("/table/<table_name>/count")
    def _table_count(table_name: str):
        redirection = auth_redirect()
        if redirection:
            return redirection
        dump = _dump()
        table = TableModel.from_dto(dump, table_name)
        if "filter" in request.args:
            where = json.loads(request.args["filter"])
        else:
            where = {}

        return count(table.name, where=where)

    def row(table_name: str, row_id: int, layout):
        dump = _dump()
        table = TableModel.from_dto(dump, table_name)
        row = select_by_id(table.name, row_id)
        return render(
            template=[layout, "row"],
            context=dict(logout_url=login_url(), user=get_user(), table=table, row=row),
        )

    @bp.get("/table/<table_name>/row/<row_id>")
    def _row(table_name: str, row_id: int):
        redirection = auth_redirect()
        if redirection:
            return redirection
        return row(table_name, row_id, "page")

    @bp.get("/table/<table_name>/row/<row_id>/modal")
    def _row_modal(table_name: str, row_id: int):
        redirection = auth_redirect()
        if redirection:
            return redirection
        return row(table_name, row_id, "modal")

    return bp
