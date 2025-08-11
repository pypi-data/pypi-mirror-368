from tesorotools.render.content.images import Image, Images
from tesorotools.render.content.section import Section
from tesorotools.render.content.subtitle import Subtitle
from tesorotools.render.content.table import Table
from tesorotools.render.content.text import Text
from tesorotools.render.content.title import Title
from tesorotools.render.report import Report
from tesorotools.utils.template import TemplateLoader

TemplateLoader.add_constructor("!report", Report.from_yaml)
TemplateLoader.add_constructor("!section", Section.from_yaml)
TemplateLoader.add_constructor("!image", Image.from_yaml)
TemplateLoader.add_constructor("!images", Images.from_yaml)
TemplateLoader.add_constructor("!table", Table.from_yaml)
TemplateLoader.add_constructor("!text", Text.from_yaml)
TemplateLoader.add_constructor("!title", Title.from_yaml)
TemplateLoader.add_constructor("!subtitle", Subtitle.from_yaml)
