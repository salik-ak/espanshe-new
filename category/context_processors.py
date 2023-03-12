from .models import Sub_Category

def menu_links(request):
    links=Sub_Category.objects.all()
    return dict(links=links)
