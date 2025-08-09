from abc import ABC
from simple_report.structure.html.templates import jinja2_env
from simple_report.core.components.base import BaseElement


class Code(BaseElement):
    def __init__(
        self,
        text,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.text = text

    def to_html(self, **kwargs):
        content = {
            'id': self.id,
            'class_name':self.class_name,
            'text':self.text
            }
        template = jinja2_env.get_template('code.html')
        rendered_template = template.render(content)
        return rendered_template
