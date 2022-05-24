import datetime
from json import loads
from typing import List

from decouple import config
from requests import get

from theneuraltimes_app.news_grabber.news_sorter import ArticleHeadline


def articles_by_date(date: datetime.date) -> List[ArticleHeadline]:
    date_string = date.strftime('%Y-%m-%d')
    params = {'api-key': config('GUARDIAN_SECRET'), 'from_date': date_string, 'to_date': date_string, 'page-size': 50}
    response = get(f"https://content.guardianapis.com/search", params=params)
    articles = loads(response.content)['response']['results']
    answer = []
    for article in articles:
        if "webTitle" in article:
            answer.append(ArticleHeadline(article["webTitle"], article["webUrl"]))
    return answer
