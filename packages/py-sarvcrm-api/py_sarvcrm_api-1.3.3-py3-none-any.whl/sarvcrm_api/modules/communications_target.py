from ._base import SarvModule
from ._mixins import UrlMixin

class CommunicationTargets(SarvModule, UrlMixin):
    _module_name = 'Communications_Target'
    _label_en = 'Communications Target'
    _label_pr = 'هدف ارتباطات'