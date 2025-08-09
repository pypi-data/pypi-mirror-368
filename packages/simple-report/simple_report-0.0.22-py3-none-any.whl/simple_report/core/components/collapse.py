import uuid
from simple_report.core.components.base import BaseElement
from simple_report.structure.html.templates import jinja2_env


class Collapse(BaseElement):
    def __init__(self, use_panel, toggle_text, content, **kwargs):
        self.use_panel = use_panel
        self.toggle_text = toggle_text
        self.content = content if isinstance(content, list) else [content]

    def to_html(self, **kwargs):
        toggle_btn_id = uuid.uuid4().hex[:10].upper()
        content = {
            'use_panel': self.use_panel,
            'anchor_id': toggle_btn_id,
            'toggle_text': self.toggle_text,
            'content': self.content
            }
        template = jinja2_env.get_template('collapse.html')
        rendered_template = template.render(content)
        return rendered_template