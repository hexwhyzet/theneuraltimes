from theneuraltimes_app.models import NFT, TelegramAdminUser


def create_telegram_admin_user(user_id: int, chat_id: int):
    if not TelegramAdminUser.objects.exists():
        TelegramAdminUser.objects.create(userId=user_id, chatId=chat_id)


def get_telegram_user(telegram_id: str) -> TelegramAdminUser:
    return TelegramAdminUser.objects.get(userId=telegram_id)


def update_target_nft(user: TelegramAdminUser, nft: NFT) -> None:
    user.targetNFT = nft
    user.save()


def update_last_command(user: TelegramAdminUser, command: str) -> None:
    user.lastCommand = command
    user.save()


def does_admin_exist():
    return TelegramAdminUser.objects.all().exists()


def get_chat_id():
    return TelegramAdminUser.objects.all().first().chatId


def get_user_id():
    return TelegramAdminUser.objects.all().first().userId
