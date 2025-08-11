from tesorotools.artists.line_plot import Format, Legend, LinePlot
from tesorotools.utils.config import TemplateLoader

TemplateLoader.add_constructor("!line_plot", LinePlot.from_yaml)
TemplateLoader.add_constructor("!format", Format.from_yaml)
TemplateLoader.add_constructor("!legend", Legend.from_yaml)
