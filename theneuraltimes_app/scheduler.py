import datetime
import threading

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from decouple import config

from theneuraltimes_app.models import PictureGenerationSuggestion
from theneuraltimes_app.services.news import export_news
from theneuraltimes_app.services.nft import does_unpublished_nfts_exist, get_unpublished_nfts, create_NFT, reboot_NFT, \
    does_nft_exist
from theneuraltimes_app.services.picture_generation_suggestion import does_sent_picture_generation_suggestion_exist, \
    sent_picture_generation_suggestion, does_unsent_picture_generation_suggestion_exist, \
    unsent_picture_generation_suggestion
from theneuraltimes_app.telegram import is_no_pending_nfts_status, initiate_news_selection, single_poll, \
    is_pictures_generation_waiting_status, pending_nft, initiate_generated_pictures_selection


def send_picture_generation_suggestion(suggestion: PictureGenerationSuggestion):
    threading.Thread(target=lambda: requests.post(
        f"{config('PICTURE_GENERATOR_URL')}/{suggestion.pk}/{suggestion.newsSuggestion.editedHeader}")
                     ).start()
    suggestion.lastTimeSent = datetime.datetime.utcnow()
    suggestion.save()


NEWS_EXPORT_TIMEDELTA = datetime.timedelta(hours=36)


def job():
    if is_no_pending_nfts_status():
        maybe_unpublished_date = (datetime.datetime.utcnow() - NEWS_EXPORT_TIMEDELTA).date()
        if not does_nft_exist(maybe_unpublished_date):
            export_news(maybe_unpublished_date)
            initiate_news_selection(create_NFT(maybe_unpublished_date))
            return
        if does_unpublished_nfts_exist():
            nft = get_unpublished_nfts().order_by('date').first()
            reboot_NFT(nft)
            export_news(nft.date)
            initiate_news_selection(nft)
            return
    elif is_pictures_generation_waiting_status():
        nft = pending_nft()
        if does_sent_picture_generation_suggestion_exist(nft.date):
            pending_suggestion = sent_picture_generation_suggestion(nft.date).first()
            if datetime.datetime.utcnow() - pending_suggestion.lastTimeSent > datetime.timedelta(hours=2):
                send_picture_generation_suggestion(pending_suggestion)
        elif does_unsent_picture_generation_suggestion_exist(nft.date):
            unsent_suggestion = unsent_picture_generation_suggestion(nft.date).first()
            send_picture_generation_suggestion(unsent_suggestion)
        else:
            initiate_generated_pictures_selection(nft)
    single_poll()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job, 'interval', seconds=5)
    scheduler.start()
    print("Main scheduler started working in background!")
