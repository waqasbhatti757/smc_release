# entities/user.py
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from uuid import uuid4
# from ..database.base import Base
from ..database.core import Base
class User(Base):
    __tablename__ = 'users'

    idusers = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)

    idoffice = Column(Integer, ForeignKey("support_office.idoffice"))
    usertype = Column(Integer, ForeignKey("user_roles.idrole"))
    is_admin = Column(Boolean, default=False)
    pmc = Column(Boolean, default=False)

    district_code = Column(String)
    tehsil_code = Column(String)
    uc_code = Column(String)

    ishide = Column(Boolean, default=False)
    status = Column(Boolean, default=True)

    role = relationship("UserRole", back_populates="users", lazy="joined")
    office = relationship("SupportOffice", back_populates="users", lazy="joined")


class UserRole(Base):
    __tablename__ = 'user_roles'
    idrole = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    users = relationship("User", back_populates="role")

class SupportOffice(Base):
    __tablename__ = 'support_office'
    idoffice = Column(Integer, primary_key=True)
    name = Column(String)
    users = relationship("User", back_populates="office")
