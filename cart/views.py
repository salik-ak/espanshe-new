from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variations
from cart.models import CartItem, Cart
from django.core.exceptions import ObjectDoesNotExist
from order.models import Address
from accounts.forms import AddressForm
from order.models import Coupon,UserCoupon
from django.http import JsonResponse,HttpResponse

from django.contrib.auth.decorators import login_required

# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user = request.user
    if current_user.is_authenticated:

        product = Product.objects.get(id=product_id)
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variations.objects.get(
                        product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)

                except:
                    pass
        is_cart_item_exists = CartItem.objects.filter(product=product,user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,user=current_user)

            ex_var_list=[]
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            
   
    


            if product_variation in ex_var_list:
                # increase the cart_item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:   #create a new cart item
                item = CartItem.objects.create(
                    product=product, quantity=1,user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
            
        return redirect('my_cart')
    #if the user is not authenticated
    else:
        product=Product.objects.get(id=product_id) #get the product
        product_variation=[]
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variations.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        try:
            #get the cart using the cart_id present in the session
            cart= Cart.objects.get(cart_id=_cart_id(request))
        except:
            cart= Cart.objects.create(cart_id=_cart_id(request))

        cart.save()
        is_cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,cart=cart)
            #existing_variation  -----database
            #current variation--------product variation
            #item_id   ------database

            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation=item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)



            if product_variation in ex_var_list:
                #increase the cart_item quantity
                index = ex_var_list.index(product_variation)
                item_id=id[index]
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity += 1
                item.save()
            else:   # create a new cart item
                cart_item = CartItem.objects.create(product=product,quantity=1,cart=cart)
                if len (product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len (product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('my_cart')


def my_cart(request, total=0, quantity=0, cart_items=0):
    tax = 0
    grand_total = 0
    try:

        if request.user.is_authenticated:
            cart_items= CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        tax = (2 * total)/100
        grand_total = total+tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total':grand_total
    }
    return render(request, 'my_cart.html', context)




@login_required(login_url='user_login')
def checkout(request,total=0,quantity=0,cart_items=None):
    tax= 0
    grand_total =0
    address = Address.objects.filter(user= request.user)
    form = AddressForm()
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity += cart_item.quantity
        if quantity >= cart_item.product.stock:
            return redirect('my_cart')
        tax = (2* total)/100
        grand_total = total+tax
    except ObjectDoesNotExist:
        pass

    coupons = Coupon.objects.filter(active = True)

    for item in coupons:
        try:
            coupon = UserCoupon.objects.get(user = request.user,coupon = item)
        except:
            coupon = UserCoupon()
            coupon.user = request.user
            coupon.coupon = item
            coupon.save() 

    coupons = UserCoupon.objects.filter(user = request.user, used=False)   
    
    
    context = {
            'total': total,
            'quantity': quantity,
            'cart_items': cart_items,
            'tax': tax,
            'grand_total': grand_total,
            'address':address,
            'form':form,
            'coupons':coupons,
        

        }

    return render(request, 'user_checkout_address.html',context)



   
def incqnty(request):
  if request.method == 'POST':
    product_id = request.POST['pid']
    cart_item_id = request.POST['cid']
  product = get_object_or_404(Product, id=product_id)
  tax= 0
  grand_total = 0
  cart_count = 0
  out_of_stock = False
  try:
    print('1 try')
    if request.user.is_authenticated:
      cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

    if cart_item.quantity == cart_item.product.stock:
      out_of_stock = True
    
    if cart_item.quantity < cart_item.product.stock:
      cart_item.quantity  += 1
      cart_item.save()
    
    total = 0 
    sub_total = cart_item.sub_total()
    print('halo error')
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    print(cart_item.quantity)
    print('hai error')
    for cart_ite in cart_items:
        total += int(cart_ite.product.price)*int(cart_ite.quantity)
    
    tax = (5 * total)/100
    grand_total = total + tax
    grand_total = format(grand_total, '.2f')
  except:
    pass
  return JsonResponse(
          {'success': True,
           'qnty':cart_item.quantity,
           'sub_total':sub_total,
           'cart_count':cart_count,
           'total':total,
           'tax':tax,
           'grand_total':grand_total,
           'out_of_stock':out_of_stock
           },
          safe=False
        )

def decqnty(request):
  print('1 try')
  if request.method == 'POST':
    product_id = request.POST['pid']
    cart_item_id = request.POST['cid']
  product = get_object_or_404(Product, id=product_id)
  print('2 try')
  tax= 0
  grand_total = 0
  cart_count = 0
  try:
    print('3 try')
    if request.user.is_authenticated:
      cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    
    
    if cart_item.quantity > 1: 
      cart_item.quantity  -= 1
      cart_item.save()
    total = 0 
    sub_total = cart_item.sub_total()
    print('halo error')
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    print(cart_item.quantity)
    print('hai error')
    for cart_ite in cart_items:
        total += int(cart_ite.product.price)*int(cart_ite.quantity)
    
    tax = (5 * total)/100
    grand_total = total + tax
    grand_total = format(grand_total, '.2f')
  except:
    pass
  return JsonResponse(
          {'success': True,
           'qnty':cart_item.quantity,
           'sub_total':sub_total,
           'cart_count':cart_count,
           'total':total,
           'tax':tax,
           'grand_total':grand_total,
           },
          safe=False
        )

def remove_cart_item(request):
  if request.method == 'POST':
    product_id = request.POST['pid']
    cart_item_id = request.POST['cid']
  product = get_object_or_404(Product, id=product_id)
  tax= 0
  grand_total = 0
  cart_count = 0
  try:
    print('1 try')
    if request.user.is_authenticated:
      cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
      cart = Cart.objects.get(cart_id=_cart_id(request))
      cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

    total = 0 
    sub_total = cart_item.sub_total()
    print('halo error')
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    print(cart_item.quantity)
    print('hai sub')
    print(sub_total)
    print(total)
    for cart_ite in cart_items:
        total += int(cart_ite.product.price)*int(cart_ite.quantity)
        cart_count += cart_ite.quantity
    print(cart_count)
    total = total - sub_total
    tax = (5 * total)/100
    grand_total = total + tax
    grand_total = format(grand_total, '.2f')
    cart_item.delete()
  except:
    pass
  return JsonResponse(
          {'success': True,
           'qnty':cart_item.quantity,
           'sub_total':sub_total,
           'cart_count':cart_count,
           'total':total,
           'tax':tax,
           'grand_total':grand_total,
           },
          safe=False
        )


