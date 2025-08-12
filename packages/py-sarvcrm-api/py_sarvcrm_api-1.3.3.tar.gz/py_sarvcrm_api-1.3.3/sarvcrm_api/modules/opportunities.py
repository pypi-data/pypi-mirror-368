from ._base import SarvModule
from ._mixins import UrlMixin

class Opportunities(SarvModule, UrlMixin):
    _module_name = 'Opportunities'
    _label_en = 'Opportunities'
    _label_pr = 'فرصت ها'