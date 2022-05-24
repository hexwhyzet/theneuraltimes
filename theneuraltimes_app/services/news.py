from datetime import datetime

from django.db.models import QuerySet

from theneuraltimes_app.models import NewsSource
from theneuraltimes_app.models import NewsSuggestion
from theneuraltimes_app.news_grabber import new_york_times, guardian
from theneuraltimes_app.news_grabber.news_sorter import extract_interesting


def do_news_suggestions_exist(date):
    return NewsSuggestion.objects.filter(date=date).exists()


def get_news_suggestions(date) -> QuerySet[NewsSuggestion]:
    return NewsSuggestion.objects.filter(date=date)


def select_news_suggestion(news_suggestion: NewsSuggestion) -> None:
    news_suggestion.isSelected = True
    news_suggestion.save()


def get_selected_news_suggestions_not_edited(date) -> QuerySet[NewsSuggestion]:
    return NewsSuggestion.objects.filter(picture_generation_suggestion__isnull=True,
                                         isSelected=True,
                                         date=date)


def do_selected_news_suggestions_not_edited_exist(date) -> bool:
    return get_selected_news_suggestions_not_edited(date).exists()


def add_edited_header(news_suggestion: NewsSuggestion, edited_header: str):
    news_suggestion.editedHeader = edited_header
    news_suggestion.save()


def create_news_suggestion(source_type: NewsSource.NewsSourceType, headline: str, url: str,
                           date: datetime.date) -> NewsSuggestion:
    news_source: NewsSource
    if not NewsSource.objects.filter(sourceType=source_type).exists():
        news_source = NewsSource.objects.create(sourceType=source_type)
    else:
        news_source = NewsSource.objects.get(sourceType=source_type)

    return NewsSuggestion.objects.get_or_create(newsSource=news_source,
                                                url=url,
                                                headline=headline,
                                                date=date)


def export_news(date: datetime.date):
    all_headlines = {
        NewsSource.NewsSourceType.NEW_YORK_TIMES: extract_interesting(new_york_times.articles_by_date(date)),
        NewsSource.NewsSourceType.GUARDIAN: extract_interesting(guardian.articles_by_date(date)),
    }
    for source_type, headlines in all_headlines.items():
        for headline in headlines:
            create_news_suggestion(source_type=source_type, headline=headline.headline, url=headline.url, date=date)
