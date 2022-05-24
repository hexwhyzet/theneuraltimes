from django.urls import path

from theneuraltimes_app.blockchain.smart_contract import metadata
from theneuraltimes_app.views import generate_picture, show_nfts

urlpatterns = [
    path('generated/<int:pic_id>', generate_picture),
    path('metadata/<int:nft_id>', metadata),
    path('', show_nfts)
]
