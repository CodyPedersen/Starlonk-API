from .admin import adm_router, get_process, purge_old
from .base import base_router, get_home
from .satellite import (
    sat_router,
    get_satellites,
    get_bulk_satellites,
    predict_satellites
)

__all__ = [
    'adm_router',
    'base_router',
    'get_bulk_satellites',
    'get_home',
    'get_process',
    'get_satellites',
    'predict_satellites',
    'purge_old',
    'sat_router'
]
