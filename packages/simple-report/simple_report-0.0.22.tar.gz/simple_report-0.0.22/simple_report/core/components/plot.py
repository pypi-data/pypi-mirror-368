import io
import uuid
from simple_report.core.components.base import BaseElement
from matplotlib.figure import Axes, Figure
from seaborn.axisgrid import Grid
from plotly.graph_objs._figure import Figure as PFigure
import base64
from plotly.io import to_html as plotly_to_html
from simple_report.utils.utils import plot_360_n0sc0pe


class Image(BaseElement):
    def __init__(
        self,
        figure,
        image_format,
        **kwargs,
    ):
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return "Image"

    def render(self):
        raise NotImplementedError()


class Plot(BaseElement):
    def __init__(self, figure, page=None, **kwargs):
        super().__init__(**kwargs)
        self.figure = figure
        self.page = page

    def to_html(self, **kwargs):
        report = kwargs.get('report')
        if Axes in type(self.figure).__mro__:
            print('Adding Axes (axes) as plot')
            return self.add_matplotlib_axes(self.figure, self.page)
        elif Grid in type(self.figure).__mro__:
            print('Adding Grid (axes) as plot')
            return self.add_matplotlib_axes(self.figure, self.page)
        elif Figure in type(self.figure).__mro__:
            print('Adding Figure (figure) as plot')
            return self.add_matplotlib_figure(self.figure, self.page)
        elif PFigure in type(self.figure).__mro__:
            return self.add_plotly_figure(self.figure, report=report)
        else:
            raise NotImplementedError(f"Plot type '{type(self.figure).__name__}' not supported")

    def add_matplotlib_figure(self, figure: Figure, image_format='png', page=None):
        image_format = 'png'
        tmpfile = io.BytesIO()
        figure_type = type(figure).__name__
        if figure_type == 'FacetGrid':
            figure.savefig(tmpfile, format='png')
            result_string = plot_360_n0sc0pe(figure.figure, image_format)
        elif figure_type == 'AxesSubplot':
            figure.figure.savefig(tmpfile, format='png')
            result_string = plot_360_n0sc0pe(figure.figure, image_format)
        elif figure_type == 'Figure':
            figure.savefig(tmpfile, format='png')
            result_string = plot_360_n0sc0pe(figure.figure, image_format)

        return f"""<img class="img-fluid text-center" src=\'{result_string}\'>"""

    def add_matplotlib_axes(self, figure: Axes, page=None):
        image_format = 'png'
        figure_type = type(figure).__name__
        if figure_type == 'FacetGrid':
            print(".... Adding FacetGrid")
            result_string = plot_360_n0sc0pe(figure, image_format)
        elif figure_type == 'AxesSubplot':
            print(".... Adding AxesSubplot")
            result_string = plot_360_n0sc0pe(figure.figure, image_format)
        elif figure_type == 'Axes':
            print(".... Adding Axes")
            result_string = plot_360_n0sc0pe(figure.figure, image_format)
        else:
            raise NotImplementedError(f"Figure type '{figure_type}' not supported")

        if image_format == 'svg':
            return f"""<div class="text-center">
                {result_string.replace('<svg', '<svg class="img-fluid text-center"')}
            </div>"""
        else:
            return f"""<img class="img-fluid text-center" src=\'{result_string}\'>"""

    def add_plotly_figure(self, figure: PFigure, report=None):
        include_js = False
        
        if report and not report.plotly_js_included:
            include_js = 'cdn'
            report.plotly_js_included = True
        encoded_figure = plotly_to_html(figure, include_plotlyjs=include_js, full_html=False)
        
        return f"""<div class="container">{encoded_figure}</div>"""
