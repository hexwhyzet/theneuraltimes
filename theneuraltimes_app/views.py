from django.http import Http404
from django.http.response import HttpResponse
from django.shortcuts import render

from theneuraltimes_app.models import PictureGenerationSuggestion
from theneuraltimes_app.services.nft import get_published_nfts


def generate_picture(request, pic_id):
    try:
        p = PictureGenerationSuggestion.objects.get(pk=pic_id)
        p.picturePath = request.GET['url']
        p.save()
    except PictureGenerationSuggestion.DoesNotExist:
        raise Http404("Poll does not exist")
    return HttpResponse('')


def show_nfts(request):
    nfts = get_published_nfts()
    return render(request, 'catalogue/index.html', {"nfts": nfts})
