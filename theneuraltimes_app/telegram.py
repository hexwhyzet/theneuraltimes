import warnings
from dataclasses import dataclass

import telebot
from decouple import config
from telebot import StateMemoryStorage, custom_filters
from telebot.handler_backends import StatesGroup, State

from theneuraltimes_app.blockchain.smart_contract import mint_nft
from theneuraltimes_app.models import NFT, NewsSuggestion, PictureGenerationSuggestion
from theneuraltimes_app.services.news import do_news_suggestions_exist, get_news_suggestions, \
    select_news_suggestion, do_selected_news_suggestions_not_edited_exist, \
    get_selected_news_suggestions_not_edited, add_edited_header
from theneuraltimes_app.services.picture_generation_suggestion import create_picture_generation_suggestion, \
    get_picture_generation_suggestions
from theneuraltimes_app.services.telegram_user import does_admin_exist, get_chat_id, get_user_id, \
    create_telegram_admin_user

API_TOKEN = config("TELEGRAM_TOKEN")

state_storage = StateMemoryStorage()

bot = telebot.TeleBot(API_TOKEN, state_storage=state_storage)


class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_admin'

    def check(self, message: telebot.types.Message):
        if not does_admin_exist():
            return True
        return message.from_user.id == get_user_id()


@dataclass
class DataLabels:
    NFT = "NFT"
    NEWS_SUGGESTIONS = "NEWS_SUGGESTIONS"
    NEWS_SUGGESTION_EDITING = "NEWS_SUGGESTION_EDITING"
    PICTURE_GENERATION_SUGGESTION = "PICTURE_GENERATION_SUGGESTION"


class MyStates(StatesGroup):
    no_pending_nfts = State()
    news_selection = State()
    news_editing = State()
    pictures_generation_waiting = State()
    generated_pictures_selection = State()


bot.add_custom_filter(IsAdmin())
bot.add_custom_filter(custom_filters.StateFilter(bot))


def initialize_admin_state():
    if does_admin_exist():
        bot.set_state(get_user_id(), MyStates.no_pending_nfts.name, get_chat_id())


def is_no_pending_nfts_status():
    return bot.get_state(get_user_id()) in [None, MyStates.no_pending_nfts.name]


def is_pictures_generation_waiting_status():
    return bot.get_state(get_user_id()) == MyStates.pictures_generation_waiting.name


def pending_nft():
    with bot.retrieve_data(get_user_id(), get_chat_id()) as data:
        return NFT.objects.get(pk=data[DataLabels.NFT])


@bot.message_handler(commands=['register'], is_admin=True)
def send_welcome(message: telebot.types.Message):
    if does_admin_exist():
        bot.send_message(get_chat_id(), "The admin user is already registered")
        return
    create_telegram_admin_user(user_id=message.from_user.id, chat_id=message.chat.id)
    initialize_admin_state()
    bot.send_message(get_chat_id(), "The admin user is successfully registered")


def initiate_news_selection(nft: NFT):
    if not does_admin_exist():
        warnings.warn("TelegramAdminUser does not exist")
        return

    if not do_news_suggestions_exist(nft.date):
        warnings.warn(f"News suggestions for specified date: {nft.date} do not exist")
        return

    news_suggestions = get_news_suggestions(nft.date)

    with bot.retrieve_data(get_user_id(), get_chat_id()) as data:
        data[DataLabels.NFT] = nft.pk

        answer = ""
        news_suggestions_data = dict()
        for news_id, news_suggestion in enumerate(news_suggestions):
            news_id += 1
            answer += f"{news_id} - {news_suggestion.headline}\n"
            news_suggestions_data[news_id] = news_suggestion.pk
        data[DataLabels.NEWS_SUGGESTIONS] = news_suggestions_data

    bot.send_message(get_chat_id(),
                     "Enter list of numbers of selected headers:\n"
                     f"{answer}")
    bot.set_state(get_user_id(), MyStates.news_selection.name, get_chat_id())


@bot.message_handler(state=MyStates.news_selection, is_admin=True)
def receive_news_selection(message):
    if not does_admin_exist():
        warnings.warn("TelegramAdminUser does not exist")
        return
    numbers = [int(s) for s in message.text.split() if s.isdigit()]

    if not len(numbers):
        bot.send_message(get_chat_id(), "No numbers specified, try again")
        return

    with bot.retrieve_data(get_user_id(), get_chat_id()) as data:
        existing_numbers = list(data[DataLabels.NEWS_SUGGESTIONS].keys())

        if any([number not in existing_numbers for number in numbers]):
            bot.send_message(get_chat_id(),
                             f"Unknown numbers: {' '.join([str(number) for number in numbers if number not in existing_numbers])},"
                             "try again")
            return

        bot.send_message(get_chat_id(),
                         f"Headers specified: {' '.join(map(str, numbers))}.\nLet's start editing")

        for number in numbers:
            select_news_suggestion(NewsSuggestion.objects.get(pk=data[DataLabels.NEWS_SUGGESTIONS][number]))

        nft = NFT.objects.get(pk=data[DataLabels.NFT])

    initiate_news_editing(nft)


def initiate_news_editing(nft: NFT):
    bot.set_state(get_user_id(), MyStates.news_editing.name, get_chat_id())

    with bot.retrieve_data(get_user_id(), get_chat_id()) as data:
        data[DataLabels.NFT] = nft.pk

        if not do_selected_news_suggestions_not_edited_exist(nft.date):
            bot.send_message(get_chat_id(), "All headers edited.\nWait for generated pictures.")
            bot.set_state(get_user_id(), MyStates.pictures_generation_waiting.name, get_chat_id())
            return

        news_suggestion = get_selected_news_suggestions_not_edited(date=nft.date).first()
        bot.send_message(get_chat_id(), f"Header: {news_suggestion.headline}\n"
                                        "Write edited version, otherwise send '-' character")
        data[DataLabels.NEWS_SUGGESTION_EDITING] = news_suggestion.pk


@bot.message_handler(state=MyStates.news_editing, is_admin=True)
def receive_news_editing(message):
    with bot.retrieve_data(get_user_id(), get_chat_id()) as data:
        news_suggestion = NewsSuggestion.objects.get(pk=data[DataLabels.NEWS_SUGGESTION_EDITING])
        if message.text != "-":
            add_edited_header(news_suggestion, message.text)
        else:
            add_edited_header(news_suggestion, news_suggestion.headline)
        create_picture_generation_suggestion(news_suggestion)

        nft = NFT.objects.get(pk=data[DataLabels.NFT])
    initiate_news_editing(nft)


def initiate_generated_pictures_selection(nft: NFT):
    bot.set_state(get_user_id(), MyStates.generated_pictures_selection.name, get_chat_id())

    with bot.retrieve_data(get_user_id(), get_chat_id()) as data:
        data[DataLabels.NFT] = nft.pk

        picture_generation_suggestions = get_picture_generation_suggestions(nft.date).all()

        picture_generation_suggestions_data = dict()
        ctr = 1
        for header, edited_header in list(set(map(lambda x: (x.newsSuggestion.headline, x.newsSuggestion.editedHeader),
                                                  picture_generation_suggestions))):
            header_picture_generation_suggestions = filter(lambda x: x.newsSuggestion.headline == header,
                                                           picture_generation_suggestions)
            answer = f"{ctr} - Header: {header}"
            if edited_header is not None:
                answer += f"\nEdited header: {edited_header}"

            bot.send_message(get_chat_id(), answer)

            for picture_generation_suggestion in header_picture_generation_suggestions:
                if picture_generation_suggestion.picturePath is not None:
                    bot.send_photo(get_chat_id(),
                                   photo=picture_generation_suggestion.picturePath,
                                   caption=str(ctr))
                    picture_generation_suggestions_data[ctr] = picture_generation_suggestion.pk
                    ctr += 1
        data[DataLabels.PICTURE_GENERATION_SUGGESTION] = picture_generation_suggestions_data


@bot.message_handler(state=MyStates.generated_pictures_selection, is_admin=True)
def receive_news_editing(message):
    with bot.retrieve_data(get_user_id(), get_chat_id()) as data:
        nft = NFT.objects.get(pk=data[DataLabels.NFT])

        if not message.text.isdigit():
            bot.send_message(get_chat_id(), "Please enter number of selected photo, try again")
            return
        number = int(message.text)

        if number not in data[DataLabels.PICTURE_GENERATION_SUGGESTION].keys():
            bot.send_message(get_chat_id(), "Specified number is not found, try again")
            return

        picture_pk = data[DataLabels.PICTURE_GENERATION_SUGGESTION][number]
        picture = PictureGenerationSuggestion.objects.get(pk=picture_pk)
        nft.pictureGenerationSuggestion = picture
        nft.save()
        mint_nft(nft)
        bot.set_state(get_user_id(), MyStates.no_pending_nfts.name, get_chat_id())
        bot.send_message(get_chat_id(), "Success!")


def start_bot():
    bot.infinity_polling()


def first_fake_poll():
    bot.get_updates(offset=-1)


def single_poll():
    updates = bot.get_updates(offset=(bot.last_update_id + 1), long_polling_timeout=5)
    bot.process_new_updates(updates)
