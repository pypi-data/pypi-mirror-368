from ._base import SarvModule
from ._mixins import UrlMixin

class ProductCategories(SarvModule, UrlMixin):
    _module_name = 'AOS_Product_Categories'
    _label_en = 'Product Categories'
    _label_pr = 'دسته های محصول'