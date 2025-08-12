from ._base import SarvModule
from ._mixins import UrlMixin

class Timesheets(SarvModule, UrlMixin):
    _module_name = 'Timesheet'
    _label_en = 'Timesheet'
    _label_pr = 'تایم شیت'