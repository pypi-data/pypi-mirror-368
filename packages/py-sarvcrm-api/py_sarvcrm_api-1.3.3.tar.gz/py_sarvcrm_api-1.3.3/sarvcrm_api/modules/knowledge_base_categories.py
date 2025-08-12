from ._base import SarvModule
from ._mixins import UrlMixin

class KnowledgeBaseCategories(SarvModule, UrlMixin):
    _module_name = 'Knowledge_Base_Categories'
    _label_en = 'Knowledge Base Categories'
    _label_pr = 'دسته پایگاه دانش'