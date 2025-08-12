from ._base import SarvModule
from ._mixins import UrlMixin

class Competitor(SarvModule, UrlMixin):
    _module_name = 'sc_competitor'
    _label_en = 'Competitor'
    _label_pr = 'رقبا'