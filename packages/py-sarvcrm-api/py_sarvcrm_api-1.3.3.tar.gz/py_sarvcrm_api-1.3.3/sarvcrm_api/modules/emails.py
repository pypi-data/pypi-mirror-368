from ._base import SarvModule
from ._mixins import UrlMixin

class Emails(SarvModule, UrlMixin):
    _module_name = 'Emails'
    _label_en = 'Emails'
    _label_pr = 'ایمیل ها'