# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
db = SQLAlchemy()

crsf = CSRFProtect()

limiter = Limiter(
    key_func=get_remote_address
)