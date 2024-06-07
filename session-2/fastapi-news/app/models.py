from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    datetime = Column(DateTime, index=True)
    body = Column(Text, index=True)
    link = Column(String, unique=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    reporter_id = Column(Integer, ForeignKey('reporters.id'))
    publisher_id = Column(Integer, ForeignKey('publishers.id'))
    category = relationship("Category")
    reporter = relationship("Reporter")
    publisher = relationship("Publisher")
    images = relationship("Image", back_populates="news")

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

class Reporter(Base):
    __tablename__ = 'reporters'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True)

class Publisher(Base):
    __tablename__ = 'publishers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    website = Column(String, unique=True)
    email = Column(String, unique=True, index=True)

class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey('news.id'))
    url = Column(String)
    news = relationship("News", back_populates="images")
