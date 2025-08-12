from ._base import SarvModule
from ._mixins import UrlMixin

class Contacts(SarvModule, UrlMixin):
    _module_name = 'Contacts'
    _label_en = 'Contacts'
    _label_pr = 'افراد'