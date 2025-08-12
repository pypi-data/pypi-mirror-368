from ._base import SarvModule
from ._mixins import UrlMixin

class Campaigns(SarvModule, UrlMixin):
    _module_name = 'Campaigns'
    _label_en = 'Campaigns'
    _label_pr = 'کمپین ها'