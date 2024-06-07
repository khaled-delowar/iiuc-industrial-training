from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas, dependencies, scraper

router = APIRouter(
    prefix="/news",
    tags=["news"],
)

@router.post("/", response_model=schemas.News)
def create_news(news: schemas.NewsCreate, db: Session = Depends(dependencies.get_db)):
    return crud.create_news(db=db, news=news)

@router.get("/", response_model=List[schemas.News])
def read_news_list(skip: int = 0, limit: int = 10, db: Session = Depends(dependencies.get_db)):
    """
    Return all news from the database.
    """

    news_list = crud.get_news_list(db=db, skip=skip, limit=limit)
    if news_list is None:
        raise HTTPException(status_code=404, detail="News not found")
    return news_list
    
    # return [
    #     schemas.News(
    #         id=news.id,
    #         title=news.title,
    #         body=news.body,
    #         link=news.link,
    #         datetime=news.datetime,
    #         category=news.category_name,  # Use computed property
    #         reporter=news.reporter_name,  # Use computed property
    #         publisher=news.publisher_name,  # Use computed property
    #     )
    #     for news in news_list
    # ]


@router.get("/{news_id}", response_model=schemas.News)
def read_news(news_id: int, db: Session = Depends(dependencies.get_db)):
    news = crud.get_news(db, news_id=news_id)

    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return news
    # return schemas.News(
    #     id=news.id,
    #     title=news.title,
    #     body=news.body,
    #     link=news.link,
    #     datetime=news.datetime,
    #     category=news.category_name,  # Use computed property
    #     reporter=news.reporter_name,  # Use computed property
    #     publisher=news.publisher_name,  # Use computed property
    # )



@router.post("/scrape/", response_model=List[schemas.News])
def scrape_news(urls: List[str], db: Session = Depends(dependencies.get_db)):
    all_inserted_news = []
    for url in urls:
        inserted_news = scraper.scrape_and_store_news(url, db)
        all_inserted_news.append(inserted_news)
    return all_inserted_news
    # return {"message": "News scraping initiated"}
from pydantic import BaseModel
from app.database import SessionLocal
class NewsBase(BaseModel):
    pass

class NewsUrl(NewsBase):
    news_link: str
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
class NewsCreate(NewsBase):
    title: str
    reporter: str
    publisher: str
    news_datetime: str
    category: str
    news_content: str
    news_link: str
@router.post("/new_news", response_model=NewsCreate)
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

        print(html_content)

        # find title from html content
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.find('title').text
        print(title)

        # find .contributor-name from html content
        reporter = soup.find('span', class_='contributor-name').text
        print(reporter)

        # print(response.html.html)
        publisher_website = url.split('/')[2]       
        publisher = publisher_website.split('.')[-2]  
        print(publisher)
        crud.get_or_create_publisher(db,reporter,publisher)
        print("hello")
        # find datetime from html content
        datetime_element = soup.find('time')
        news_datetime = datetime_element['datetime']
        print(news_datetime)
        print(type(news_datetime))

        # find category from .print-entity-section-wrapper
        category = soup.find(class_='print-entity-section-wrapper').text
        print(category)

        # find news body from p tags
        news_content = soup.find('div')
        news_body = news_content.find_all('p')
        news_body = '\n'.join([p.text for p in news_body])
        print(news_body)

       
        # Extract image URL
        session = HTMLSession()
        response = session.get(url)
        img_tags = response.html.find('img')
        print(img_tags)
        images = '\n'.join([img.attrs['src'] for img in img_tags if 'src' in img.attrs])
        print(images)
        images = []
        for img_tag in img_tags:
            if img_tag:
                img_url = img_tag.attrs['src']
                images.append(img_url)
                print(f"Image URL: {img_url}")
            else:
                print("No image tag found.")
        # insert into news_scrapper_crud if not exists
        # does_news_exist = news_scrapper_crud.get_news_by_link(db, news_link=url)
        # if does_news_exist:
        #     return does_news_exist
        # else:\
        #     return news_scrapper_crud.create_news(db, NewsCreate(title=title, reporter=reporter, news_datetime=news_datetime, news_content=news_body, news_link=url, category=category, publisher=publisher))

        # return NewsCreate(title=title, reporter=reporter, news_datetime=news_datetime, news_content=news_body, news_link=url, category=category, publisher=publisher)
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the news article")
 
    finally:
        # Close the session if any
        pass
