from ._base import SarvModule
from ._mixins import UrlMixin

class Payments(SarvModule, UrlMixin):
    _module_name = 'Payments'
    _label_en = 'Payments'
    _label_pr = 'پرداخت ها'