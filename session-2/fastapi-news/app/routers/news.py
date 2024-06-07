from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas, dependencies
from pydantic import BaseModel
from app.database import SessionLocal

router = APIRouter(
    prefix="/news",
    tags=["news"],
)

@router.get("/", response_model=List[schemas.News])
def read_news_list(skip: int = 0, limit: int = 10, db: Session = Depends(dependencies.get_db)):
    """
    Return all news from the database.
    """
    news_list = crud.get_news_list(db=db, skip=skip, limit=limit)
    if news_list is None:
        raise HTTPException(status_code=404, detail="News not found")
    return news_list

@router.get("/{news_id}", response_model=schemas.News)
def read_news(news_id: int, db: Session = Depends(dependencies.get_db)):
    news = crud.get_news(db, news_id=news_id)
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return news

@router.post("/scrape/", response_model=List[schemas.News])
def scrape_news(urls: List[str], db: Session = Depends(dependencies.get_db)):
    all_inserted_news = []
    for url in urls:
        inserted_news = scraper.scrape_and_store_news(url, db)
        all_inserted_news.append(inserted_news)
    return all_inserted_news

class NewsUrl(BaseModel):
    news_link: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/new_news", response_model=schemas.NewsCreate)
async def create_news(news: NewsUrl, db: Session = Depends(get_db)):
    from requests_html import HTMLSession
    from bs4 import BeautifulSoup
    import httpx

    try:
        url = news.news_link

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')

        title = soup.find('title').text
        reporter = soup.find('span', class_='contributor-name').text
        publisher_website = url.split('/')[2]
        publisher = publisher_website.split('.')[-2]
        publisher_email = "info@publisher.com"

        datetime_element = soup.find('time')
        news_datetime = datetime_element['datetime']
        category = soup.find(class_='print-entity-section-wrapper').text
        news_content = soup.find('div')
        news_body = news_content.find_all('p')
        news_body = '\n'.join([p.text for p in news_body])

        session = HTMLSession()
        response = session.get(url)
        img_tags = response.html.find('img')
        images = [img.attrs['src'] for img in img_tags if 'src' in img.attrs]

        news_data = schemas.NewsCreate(
            title=title,
            datetime=news_datetime,
            body=news_body,
            link=url,
            news_category=category,
            news_reporter=reporter,
            news_publisher=publisher,
            publisher_website=publisher_website,
            images=images
        )
        created_news = crud.create_news(db=db, news=news_data)
        return created_news

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the news article")
    finally:
        pass
