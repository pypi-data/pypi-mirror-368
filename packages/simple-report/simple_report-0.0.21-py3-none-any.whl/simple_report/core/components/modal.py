import uuid
from simple_report.core.components.base import BaseElement
from simple_report.structure.html.templates import jinja2_env


class Modal(BaseElement):
    def __init__(self, toggle_text, content, **kwargs):
        super().__init__(**kwargs) # Code only works with this
        self.toggle_text = toggle_text
        self.content = [content] if not isinstance(content, list) else content
        # From Copilot
        # self.id = uuid.uuid4().hex[:10].upper()
        # self.title = kwargs.get('title', '')
        # self.body = kwargs.get('body', '')
        # self.footer = kwargs.get('footer', '')

    def to_html(self, **kwargs):
        anchor_id = uuid.uuid4().hex[:10].upper()
        content = {
            'anchor_id': anchor_id,
            'toggle_text': self.toggle_text,
            'content': self.content
            }
        template = jinja2_env.get_template('modal.html')
        rendered_template = template.render(content)
        return rendered_template