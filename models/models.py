from datetime import  date as _date, time
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Boolean, Float, Integer, Text, Date, Time
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    pass


class EventDB(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    source = Column(String, nullable=False)
    url = Column(String, nullable=False)
    other_urls = Column(PG_ARRAY(String), nullable=True)
    categories = Column(PG_ARRAY(String), nullable=True)
    date_from = Column(Date, nullable=True)
    time_from = Column(Time, nullable=True)  
    date_to = Column(String, nullable=True)
    time_to = Column(String, nullable=True)
    location = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    is_registration_necessary = Column(Boolean, nullable=True)
    location_url = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=True)


class EventExtract(BaseModel):
    """Information about events"""

    name: str = Field(description='The name of the event')
    urls: list[str] | None = Field( default=None, description='A list of URLs related to the event')
    categories: list[str] | None = Field(default=None, description='A list of categories the event falls in. Each category is one element in the list.')
    date_from: _date | None = Field(default=None, description='The date or the start date of the event')
    time_from: time | None = Field(default=None, description='Start time of the event')
    date_to: _date | None = Field(default=None, description='The end date of the event')
    time_to: time | None = Field(default=None, description='The ending time of the event')
    location: str | None = Field(default=None, description='The location of the event')
    price: float | None = Field(default=None, description='The price of the event')
    is_registration_necessary: bool | None = Field(default=None, description='If the event requires registration or not')
    # imageUrl: str | None = None
    location_url: str | None = Field(default=None, description='A url of the location. This can e.g. be a Google Maps Link or similar.')

    def isFreeOfCharge(self) -> bool | None:
        if self.price is None:
            return None
        return self.price == 0

class EventPublic(EventExtract):
    id: int
    source: str
    url: str

class EventCreate(EventExtract):
    source: str
    url: str
    description: str
    embedding: list[float]

class Event(EventCreate):
    id: int | None = Field(default=None)





class Events(BaseModel):
    """Extracted information about events"""
    events: list[Event]

