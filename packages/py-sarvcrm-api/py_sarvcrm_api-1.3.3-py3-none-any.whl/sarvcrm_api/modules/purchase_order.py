from ._base import SarvModule
from ._mixins import UrlMixin

class PurchaseOrders(SarvModule, UrlMixin):
    _module_name = 'Purchase_Order'
    _label_en = 'Purchase Order'
    _label_pr = 'سفارش خرید'