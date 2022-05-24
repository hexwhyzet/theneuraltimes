import datetime
from json import loads
from typing import List

from decouple import config
from requests import get

from theneuraltimes_app.news_grabber.news_sorter import ArticleHeadline


def articles_by_date(date: datetime.date) -> List[ArticleHeadline]:
    answer = []
    for page in range(5):
        params = {'api-key': config('NYT_SECRET'),
                  'fq': f"pub_date: ({date.strftime('%Y-%m-%d')})",
                  'page': page}
        response = get(f"https://api.nytimes.com/svc/search/v2/articlesearch.json", params=params)
        articles = loads(response.content)['response']['docs']
        for article in articles:
            if "headline" in article:
                answer.append(ArticleHeadline(article["headline"]["main"], article["web_url"]))
    return answer
