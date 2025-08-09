from pathlib import Path
import sys
import codecs
import re
import datetime
from simple_report.structure.html.templates import jinja2_env


class HtmlReport(object):
    
    def __init__(self, report_title, project_name='', author='',  pages='Home', background_color='#e4e4e4', display_timestamp=True) -> None:
        self.report_title = report_title
        self.project_name = project_name
        self.author = author
        self.pages = pages if isinstance(pages, list) else [pages]
        self.body = {page: "" for page in self.pages}
        self.background_color = background_color
        self.display_timestamp = display_timestamp
        self.plotly_js_included = False

    @property
    def get_str_timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def default_page(self):
        if len(self.pages):
            return self.pages[0]
        else:
            print("There's no page in the html.")
        
    @property
    def pages_id(self):
        return [self.convert_string_to_id(page) for page in self.pages]
        
    def convert_string_to_id(self, some_string):
        return re.sub('[^(a-z)(A-Z)(0-9)._-]', '', some_string)

    @property
    def timestamp(self):
        return datetime.datetime.now().strftime("%c")

    @property
    def get_timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    @property
    def author_html(self):
        if self.author_name is None:
            return ""
        else:
            return f"<p style='padding;0px; margin: 0px;'>Author: {str(self.author)}</p>"

    @property
    def nav_buttons(self):
        html = ''.join(
            [
                f"""<button {"id='defaultOpen'"*(i==0)} class="tablink" onclick="openPage('{page_id}', this, '{self.background_color}')">{page_name}</button>"""
                for i, (page_id, page_name) in enumerate(zip(self.pages_id, self.pages))
            ]
        )
        return html
    
    @property
    def header(self):
        content = {
            'report_title': self.report_title,
            'project_name': self.project_name,
            'author': self.author,
            'timestamp': self.timestamp,
        }
        template = jinja2_env.get_template('header.html')
        rendered_template = template.render(content)
        return rendered_template

    def to_html(self):
        content = {
            'project_name': self.project_name,
            'author': self.author,
            'timestamp': self.get_timestamp,
            'report_title': self.report_title,
            'background_color': self.background_color,
            'header': self.header,
            'nav_buttons': self.nav_buttons,
            'pages_id': self.pages_id,
            'pages': self.pages,
            'body': self.body,
            'display_timestamp': self.display_timestamp,
            'timestamp_str': self.get_str_timestamp,
            }
        template = jinja2_env.get_template('report.html')
        rendered_template = template.render(content, zip=zip, enumerate=enumerate)
        return rendered_template

    def add_new_page(self, page_name):
        self.pages.append(page_name)
        self.body[page_name] = ""

    def export(self, path):
        with codecs.open(f'{path}/html_report.html', 'w', "utf-8") as f:
            f.write(self.to_html())

    def add(self, element, page=None):
        if page is None:
            page = self.default_page
        self.body[page] += element.to_html(report=self)
