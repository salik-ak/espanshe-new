from django.shortcuts import render
from store.models import Product

# Create your views here.

def index(request):

    products = Product.objects.all( )

    context ={
        'products':products
    }


    
    return render(request,'index.html',context)


def error_404(request,exception):


    
    return render(request,'404_error_page.html')

