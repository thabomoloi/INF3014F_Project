from flask import Blueprint

main = Blueprint('main', __name__)

from .views import *
from .errors import *
from ..models import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
