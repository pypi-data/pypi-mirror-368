import json
from pathlib import Path
from typing import List, Union
from urllib.parse import quote

from flask import render_template_string


def quote_value(value):
    if isinstance(value, str):
        return quote(value)
    else:
        return quote(json.dumps(value))
    

def make_url(url_prefix: str = ''):
    def url(*parts, **query):
        pathpart = '/'.join(str(part) for part in [url_prefix, *parts])
        if query:
            querypart = '?' + '&'.join(
                f'{quote(str(k))}={quote_value(v)}'
                for k, v in query.items()
            )
        else:
            querypart = ''
        if querypart:
            return f'{pathpart}{querypart}'
        return pathpart
    return url



def make_render(templates_path: Path, url_prefix: str = ''):
    def render(template: Union[str, List[str]], context: dict):
        if isinstance(template, str):
            template_list = [template]
        else:
            template_list = template
        
        html = ''
        for template in reversed(template_list):
            template_content = (templates_path / f'{template}.html').read_text(encoding='utf-8')
            html = render_template_string(template_content, url=make_url(url_prefix=url_prefix), child_content=html, **context)
        return html
    return render