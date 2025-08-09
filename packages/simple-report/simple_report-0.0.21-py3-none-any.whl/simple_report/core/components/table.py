import uuid
from simple_report.core.components.base import BaseElement
from simple_report.structure.html.templates import jinja2_env


class Table(object):

    def __init__(self, dataframe, title=None, height_limit=None, use_striped_style=True, use_jquery=False, caption=None):
        self.dataframe = dataframe
        self.title = title
        self.height = height_limit
        self.use_height_limit = height_limit is not None
        self.use_striped_style = use_striped_style
        self.use_jquery = use_jquery
        self.caption = caption

    def to_html(self, **kwargs):
        table_id = uuid.uuid4().hex[:10].upper()
        table = self.dataframe.to_html(
            table_id=table_id,
            classes=['table', 'table-striped'] if self.use_striped_style else ['table'],
            border=0,
            )

        content = {
            'title': self.title,
            'height': self.height,
            'use_height_limit': self.use_height_limit,
            'caption': self.caption,
            'table': table,
        }
        template = jinja2_env.get_template('table.html')
        rendered_template = template.render(content, none=None)
        return rendered_template
