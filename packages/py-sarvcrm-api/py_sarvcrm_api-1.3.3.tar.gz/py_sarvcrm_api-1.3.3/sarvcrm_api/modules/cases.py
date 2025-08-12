from ._base import SarvModule
from ._mixins import UrlMixin

class Cases(SarvModule, UrlMixin):
    _module_name = 'Cases'
    _label_en = 'Cases'
    _label_pr = 'سرویس ها'