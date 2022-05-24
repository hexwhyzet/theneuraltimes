from datetime import datetime

from django.db.models import QuerySet

from theneuraltimes_app.models import NFT, PictureGenerationSuggestion, NewsSuggestion


def get_unpublished_nfts() -> QuerySet[NFT]:
    return NFT.objects.filter(pictureGenerationSuggestion=None)


def get_published_nfts() -> QuerySet[NFT]:
    return NFT.objects.filter(pictureGenerationSuggestion__isnull=False)


def does_nft_exist(date):
    return NFT.objects.filter(date=date).exists()


def does_unpublished_nfts_exist() -> bool:
    return get_unpublished_nfts().exists()


def create_NFT(date: datetime.date):
    return NFT.objects.get_or_create(date=date)[0]


def reboot_NFT(nft: NFT):
    NewsSuggestion.objects.filter(date=nft.date).delete()
    # for newsSuggestion in NewsSuggestion.objects.filter(date=nft.date):
    #     newsSuggestion.isSelected = False
    #     newsSuggestion.save()
    PictureGenerationSuggestion.objects.filter(newsSuggestion__date=nft.date).delete()
