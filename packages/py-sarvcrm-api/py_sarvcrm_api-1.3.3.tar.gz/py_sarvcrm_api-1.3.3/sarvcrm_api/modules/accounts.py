from ._base import SarvModule
from ._mixins import UrlMixin

class Accounts(SarvModule, UrlMixin):
    _module_name = 'Accounts'
    _label_en = 'Accounts'
    _label_pr = 'حساب ها'