from django.db.models import QuerySet

from theneuraltimes_app.models import NewsSuggestion, PictureGenerationSuggestion


def create_picture_generation_suggestion(news_suggestion: NewsSuggestion):
    return PictureGenerationSuggestion.objects.create(newsSuggestion=news_suggestion)


def get_picture_generation_suggestions(date) -> QuerySet[PictureGenerationSuggestion]:
    return PictureGenerationSuggestion.objects.filter(newsSuggestion__date=date)


def sent_picture_generation_suggestion(date) -> QuerySet[PictureGenerationSuggestion]:
    return PictureGenerationSuggestion.objects.filter(newsSuggestion__date=date,
                                                      newsSuggestion__isSelected=True,
                                                      picturePath__isnull=True,
                                                      lastTimeSent__isnull=False)


def does_sent_picture_generation_suggestion_exist(date) -> PictureGenerationSuggestion:
    return sent_picture_generation_suggestion(date).exists()


def unsent_picture_generation_suggestion(date) -> QuerySet[PictureGenerationSuggestion]:
    return PictureGenerationSuggestion.objects.filter(newsSuggestion__date=date,
                                                      newsSuggestion__isSelected=True,
                                                      lastTimeSent__isnull=True)


def does_unsent_picture_generation_suggestion_exist(date) -> PictureGenerationSuggestion:
    return unsent_picture_generation_suggestion(date).exists()
