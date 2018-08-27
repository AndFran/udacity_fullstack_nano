from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()


class Restaurant(Base):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    restaurant_name = Column(String(255))
    restaurant_address = Column(String(255))
    restaurant_image = Column(String(255))

    @property
    def serialize(self):
        return {
            "id": self.id,
            "restaurant_name": self.restaurant_name,
            "restaurant_address": self.restaurant_address,
            "restaurant_image": self.restaurant_image
        }



engine = create_engine('sqlite:///restaruants.db')
Base.metadata.create_all(engine)
