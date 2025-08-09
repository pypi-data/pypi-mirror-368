from abc import ABC
from simple_report.structure.html.templates import jinja2_env
from simple_report.core.components.base import BaseElement


class TextElement(BaseElement, ABC):
    def __init__(
        self,
        element,
        text,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.element = element
        self.text = text

    def to_html(self, **kwargs):
        content = {
            'element': self.element,
            'id': self.id,
            'class_name':self.class_name,
            'text':self.text
            }
        template = jinja2_env.get_template('text.html')
        rendered_template = template.render(content)
        return rendered_template


class H1(TextElement):
    def __init__(self, text, **kwargs):
        super().__init__(element='h1', text=text, **kwargs)


class H2(TextElement):
    def __init__(self, text):
        super().__init__(element='h2', text=text)


class H3(TextElement):
    def __init__(self, text):
        super().__init__(element='h3', text=text)


class H4(TextElement):
    def __init__(self, text):
        super().__init__(element='h4', text=text)


class H5(TextElement):
    def __init__(self, text):
        super().__init__(element='h5', text=text)


class H6(TextElement):
    def __init__(self, text):
        super().__init__(element='h6', text=text)


class P(TextElement):
    def __init__(self, text):
        super().__init__(element='p', text=text)


class List(object):
    def __init__(self, text_list):
        self.text_list = text_list if isinstance(text_list, list) else [text_list]

    def to_html(self, **kwargs):
        return f"""<ul>{''.join(f'<li>{str(text)}</li>' for text in self.text_list)}</ul>"""
