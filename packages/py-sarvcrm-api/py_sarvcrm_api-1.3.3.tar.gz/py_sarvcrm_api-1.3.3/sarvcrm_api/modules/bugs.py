from ._base import SarvModule
from ._mixins import UrlMixin

class Bugs(SarvModule, UrlMixin):
    _module_name = 'Bugs'
    _label_en = 'Bug Tracker'
    _label_pr = 'پیگیری ایرادهای محصول'