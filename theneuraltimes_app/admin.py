from django.contrib import admin

# Register your models here.
from theneuraltimes_app.models import NewsSource, NewsSuggestion, PictureGenerationSuggestion, NFT, TelegramAdminUser

admin.site.register(NewsSource)
admin.site.register(NewsSuggestion)
admin.site.register(PictureGenerationSuggestion)
admin.site.register(NFT)
admin.site.register(TelegramAdminUser)
