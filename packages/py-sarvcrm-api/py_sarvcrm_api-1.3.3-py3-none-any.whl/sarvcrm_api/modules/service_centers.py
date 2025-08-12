from ._base import SarvModule
from ._mixins import UrlMixin

class ServiceCenters(SarvModule, UrlMixin):
    _module_name = 'Service_Centers'
    _label_en = 'Service Centers'
    _label_pr = 'مراکز سرویس'