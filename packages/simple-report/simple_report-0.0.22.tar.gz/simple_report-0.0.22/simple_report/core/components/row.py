from simple_report.structure.html.templates import jinja2_env
from simple_report.core.components.base import BaseElement


class Row(BaseElement):
    def __init__(self, *children, show_border=False, **kwargs):
        super().__init__(**kwargs)
        self.children = [value if isinstance(value, list) else [value] for value in children]
        self.show_border = show_border

    def to_html(self, **kwargs):
        content = {
            'children': self.children,
            'show_border': self.show_border
        }
        template = jinja2_env.get_template('row.html')
        rendered_template = template.render(content)
        return rendered_template
