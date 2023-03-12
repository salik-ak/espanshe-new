from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product
from category.models import Sub_Category, Category
from cart.models import CartItem
from cart.views import _cart_id
from django.core.paginator import Paginator
from django.db.models import Q



# Create your views here.
def products_by_sub_category(request, sub_category_slug=None):
    sub_category = None
    categories = None
    products = None

    if  sub_category_slug != None:
        sub_category = get_object_or_404(Sub_Category, slug=sub_category_slug)
        products = Product.objects.filter(
            sub_category=sub_category, is_available=True).order_by('-id')
        categories = Category.objects.all()
        sub = Sub_Category.objects.all()
        product_count = products.count()
        paginator = Paginator(products, 8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

    else:
        categories = Category.objects.all()
        sub = Sub_Category.objects.all()
        products = Product.objects.all().order_by('-id')
        product_count = products.count()
        paginator = Paginator(products, 8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'categories': categories,
        'sub': sub,
        'product_count': product_count
    }

    return render(request, 'user__shop.html', context)


def user_products(request, sub_category_slug=None):
    
    sub_category = None
    categories = None
    products = None

    if sub_category_slug != None:
        sub_category = get_object_or_404(Sub_Category, slug=sub_category_slug)
        products = Product.objects.filter(
            sub_category=sub_category, is_available=True).order_by('-id')
        categories = Category.objects.all()
        sub = Sub_Category.objects.all()
        product_count = products.count()
        paginator = Paginator(products, 8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

    else:
        categories = Category.objects.all()
        sub = Sub_Category.objects.all()
        products = Product.objects.all().order_by('-id')
        product_count = products.count()
        paginator = Paginator(products, 8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'categories': categories,
        'sub': sub,
        'product_count': product_count
    }
    return render(request, 'user__shop.html', context)






def search(request):
    categories = Category.objects.all()
    sub = Sub_Category.objects.all()
    products = None
       
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('is_available').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
        else:
           return redirect('user_products')    
            
    context = {
        'products': products,
        'categories':categories,
        'sub':sub,

        
    }
    return render(request, 'user__shop.html', context)



def user_productdetails(request,product_slug):

    
    
    single_product = Product.objects.get(slug=product_slug)
    
    

    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(
        request), product=single_product).exists()
    product_description = single_product.description

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'product_description': product_description,
    }

    return render(request, 'user_singleproduct.html', context)
