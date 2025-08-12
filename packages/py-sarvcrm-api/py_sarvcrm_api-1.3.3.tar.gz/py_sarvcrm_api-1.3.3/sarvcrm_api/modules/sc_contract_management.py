from ._base import SarvModule
from ._mixins import UrlMixin

class Services(SarvModule, UrlMixin):
    _module_name = 'sc_contract_management'
    _label_en = 'Services'
    _label_pr = 'خدمات'