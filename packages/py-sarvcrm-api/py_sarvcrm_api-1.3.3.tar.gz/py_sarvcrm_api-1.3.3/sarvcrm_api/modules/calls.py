from ._base import SarvModule
from ._mixins import UrlMixin

class Calls(SarvModule, UrlMixin):
    _module_name = 'Calls'
    _label_en = 'Calls'
    _label_pr = 'تماس ها'