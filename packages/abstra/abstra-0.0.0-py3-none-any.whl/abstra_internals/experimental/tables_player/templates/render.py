from pathlib import Path

from ...common.render import make_render

templates_path = Path(__file__).parent
url_prefix = "/_experimental/tables_player"

render = make_render(templates_path=templates_path, url_prefix=url_prefix)