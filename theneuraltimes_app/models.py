from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class NewsSource(models.Model):
    class NewsSourceType(models.TextChoices):
        NEW_YORK_TIMES = 'NYT', _('New York Times')
        GUARDIAN = 'GUARDIAN', _('GUARDIAN')
        CUSTOM = 'Custom', _('Custom')

    sourceType = models.CharField(max_length=100, choices=NewsSourceType.choices, default=NewsSourceType.CUSTOM,
                                  unique=True)

    def __str__(self):
        return self.sourceType


class NewsSuggestion(models.Model):
    newsSource = models.ForeignKey(NewsSource, on_delete=models.CASCADE, null=False, blank=False)
    url = models.CharField(max_length=1000, null=False, blank=False)
    headline = models.CharField(max_length=1000, null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    isSelected = models.BooleanField(default=False)
    editedHeader = models.CharField(max_length=1000, null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.newsSource.sourceType} - {self.headline}"


class PictureGenerationSuggestion(models.Model):
    newsSuggestion = models.ForeignKey(NewsSuggestion, on_delete=models.CASCADE, null=False, blank=False,
                                       related_name='picture_generation_suggestion')
    picturePath = models.CharField(max_length=1000, null=True, blank=True)

    lastTimeSent = models.DateTimeField(null=True, blank=True, default=None)


class NFT(models.Model):
    # newsSuggestion = models.ForeignKey(NewsSuggestion, on_delete=models.CASCADE, blank=True, null=True)
    pictureGenerationSuggestion = models.ForeignKey(PictureGenerationSuggestion,
                                                    on_delete=models.CASCADE,
                                                    blank=True,
                                                    null=True)
    date = models.DateField(unique=True, null=False, blank=False)

    blockchain_id = models.PositiveIntegerField(unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.date} - picture is{' not ' if self.pictureGenerationSuggestion is None else ' '}selected"


class TelegramAdminUser(models.Model):
    chatId = models.IntegerField(null=False, blank=False, unique=True)
    userId = models.IntegerField(null=False, blank=False, unique=True)

    def save(self, *args, **kwargs):
        if not self.pk and TelegramAdminUser.objects.exists():
            raise ValidationError('There is can be only one TelegramAdminUser instance')
        return super(TelegramAdminUser, self).save(*args, **kwargs)
