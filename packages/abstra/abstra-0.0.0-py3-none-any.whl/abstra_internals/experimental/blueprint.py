from flask import Blueprint

from .login.blueprint import get_login_bp
from .tables_player.blueprint import get_tables_player_bp


def get_experimental_bp():
    bp = Blueprint("experimental", __name__)

    tables_player_bp = get_tables_player_bp()
    bp.register_blueprint(tables_player_bp, url_prefix="/tables_player")

    login_bp = get_login_bp()
    bp.register_blueprint(login_bp, url_prefix="/login")

    return bp