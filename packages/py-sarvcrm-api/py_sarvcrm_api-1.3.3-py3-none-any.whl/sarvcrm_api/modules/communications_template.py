from ._base import SarvModule
from ._mixins import UrlMixin

class CommunicationTemplates(SarvModule, UrlMixin):
    _module_name = 'Communications_Template'
    _label_en = 'Communications Template'
    _label_pr = 'قالب ارتباطات'