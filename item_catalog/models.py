from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    #username = Column(String(32), unique=True, index=True, nullable=False)
    #picture = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String(32), nullable=False)

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def serialize(self):
        return {"id": self.id,
                #"username": self.username,
                "picture": self.picture,
                "email": self.email}


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, index=True)
    created_date = Column(DateTime, default=datetime.datetime.now)

    # the creator
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created_date
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, index=True)
    description = Column(String(250))
    created_date = Column(DateTime, default=datetime.datetime.now)

    # parent category
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    # the creator
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            "name": self.name,
            "description": self.description,
            "created": self.created_date
        }


engine = create_engine('sqlite:///cat2.db')
Base.metadata.create_all(engine)
