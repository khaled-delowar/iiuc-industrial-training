from pydantic import BaseModel
from typing import List
from datetime import datetime

class NewsBase(BaseModel):
    title: str
    datetime: datetime
    body: str
    link: str
    news_category: str
    news_reporter: str
    news_publisher: str
    publisher_website: str
    images: List[str] = []

class NewsCreate(NewsBase):
    pass

class News(NewsBase):
    id: int

    class Config:
        orm_mode = True
