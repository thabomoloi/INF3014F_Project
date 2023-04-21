from .role import Role
from .user import User, AnonymousUser
from .address import Address
from .. import login_manager
from .permissions import Permission
from .orders import *

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
