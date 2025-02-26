from fastcrud import FastCRUD

from ..models.user import Users
from ..schemas.user import UsersCreateInternal, UsersDelete, UsersUpdate, UsersUpdateInternal


CRUDUser = FastCRUD[Users, UsersCreateInternal, UsersUpdate, UsersUpdateInternal, UsersDelete, None]
crud_users = CRUDUser(Users)
