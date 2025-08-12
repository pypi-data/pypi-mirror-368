from ._base import SarvModule
from ._mixins import UrlMixin

class Vendors(SarvModule, UrlMixin):
    _module_name = 'Vendors'
    _label_en = 'Vendors'
    _label_pr = 'تامین کنندگان'