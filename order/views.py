from django.shortcuts import render, redirect
from cart.models import CartItem
from .forms import OrderForm
from django.http import JsonResponse
import json
from .models import Order, Address, Payment, OrderProduct,Coupon,UserCoupon
import datetime
from store.models import Product, Variations
from accounts.models import UserProfile
from django.contrib import messages
from store.models import Product,Variations
# Create your views here.


def place_order(request, total=0, quantity=0):

    current_user = request.user

# if the cart count is less than or equal to 0, then redirect back to  products
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('user_products')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    coupon_discount = 0
    grand_total = total + tax
    grand_total = format(grand_total, '.2f')

    if request.method == 'POST':
        coupon_code = request.POST['coupon']
        id = request.POST['flexRadioDefault']
        address = Address.objects.get(user=request.user, id=id)
        data = Order()
        data.user = current_user
        data.first_name = address.first_name
        data.last_name = address.last_name
        data.phone = address.phone
        data.email = address.email
        data.address_line_1 = address.address_line_1
        data.address_line_2 = address.address_line_2
        data.state = address.state
        data.country = address.country
        data.city = address.city
        data.order_note = address.order_note
        data.order_total = grand_total
        data.tax = tax
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()
        #  Generate order number
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d")  # like 20230305
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()

        try:
            instance = UserCoupon.objects.get(user=request.user, coupon__code=coupon_code)

            if float(grand_total) >= float(instance.coupon.min_value):
                coupon_discount = (
                    (float(grand_total) * float(instance.coupon.discount))/100)
                grand_total = float(grand_total) - coupon_discount
                grand_total = format(grand_total, '.2f')
                coupon_discount = format(coupon_discount, '.2f')

            data.order_total = grand_total
            data.order_discount = coupon_discount
            data.save()

        except:
            pass

        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        profile = UserProfile.objects.get(user=request.user)
        context = {
            'order': order,
            'cart_items': cart_items,
            'total': total,
            'tax': tax,
            'coupon_discount': coupon_discount,
            'grand_total': grand_total,
            'order_number': order_number,
            'profile':profile


        }

        return render(request, 'checkout_payment.html', context)

    else:
        return redirect('checkout')


def cash_on_delivery(request, id):
    # Move cart item to ordered product table
    try:

        order = Order.objects.get(user=request.user, is_ordered=False, order_number=id)
        cart_items = CartItem.objects.filter(user=request.user)
        order.is_ordered = True
        total = 0
        
        for i in cart_items:
            total += i.product.price * i.quantity
        tax = (2*total)/100
        shipping = (2*total)/100
        grand_total = order.order_total
        order.order_total = grand_total
        order.save()
        
        payment = Payment(
            user=request.user,
            payment_id=order.order_number,
            order_id=order.order_number,
            payment_method='Cash on Delivery',
            amount_paid=order.order_total,
            status='False'
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()
        
        for cart_item in cart_items:
            order_product = OrderProduct()
            order_product.order_id = order.id
            order_product.payment = payment
            order_product.user_id = request.user.id
            order_product.product_id = cart_item.product_id
            order_product.quantity = cart_item.quantity
            order_product.product_price = cart_item.product.price
            order_product.ordered = True
            order_product.save()

            cart_item = CartItem.objects.get(id=cart_item.id)
            product_variation = cart_item.variations.all()
            
            order_product = OrderProduct.objects.get(id=order_product.id)

            order_product.variations.set(product_variation)

            order_product.save()

            # Reduce quantity of product
            product = Product.objects.get(id=cart_item.product_id)
            product.stock -= cart_item.quantity
            product.save()

            # # Reduce quantity of variation

            print(cart_item.id)
            print(type(cart_item.variations))
            print(cart_item.variations.all())
            test = cart_item.variations.all()[0]
            print(test)
            variation = Variations.objects.filter(
                id__in=cart_item.variations.all())
            for var in variation:
                var.stock -= cart_item.quantity
                var.save()

            # clear cart
            
        CartItem.objects.filter(user=request.user).delete()

        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'payment': payment,
            'total': total,
            'tax': tax,
            'shipping': shipping,


        }
        
        return render(request, 'cod_success.html', context)
    
    except Exception as e:
        return redirect('home')


def payments(request):
    body = json.loads(request.body)
    # Store transaction details in Payment model

    order = Order.objects.get(
        user=request.user, is_ordered=False, order_number=body['orderID'])

    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        order_id=order.order_number,
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status='True'

    )

    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to order Product table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()
    # reduce the quantity of the sold products
        product = Product.objects.get(id=cart_item.product_id)
        product.stock -= cart_item.quantity
        product.save()
    # clear the cart
    CartItem.objects.filter(user=request.user).delete()
    # send order received to the customer

    # send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        total = 0
        for i in ordered_products:
            total += i.product_price * i.quantity
        tax = (2*total)/100
        grand_total = total + tax
        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'total': total,
            'tax': tax,
            'grand_total': grand_total

        }

        return render(request, 'order_complete.html', context)
    except Exception as e:
        print(e)
        return redirect('home')
    
def cancel_order(request, id):
    if request.user.is_superuser:
        order = Order.objects.get(order_number=id)
    else:
        order = Order.objects.get(order_number=id, user=request.user)
    order.status = "Cancelled"
    order.save()
    payment = Payment.objects.get(order_id=order.order_number)

    order_products = OrderProduct.objects.filter(
        user=request.user, order=order)
    for order_product in order_products:
        # increase quantity of product
        product = Product.objects.get(id=order_product.product_id)
        product.stock += order_product.quantity
        product.save()

        # increase quantity of product variation

        print(order_product.variations)
        variation = Variations.objects.filter(
            id__in=order_product.variations.all())
        print(variation)

        for var in variation:
            var.stock += order_product.quantity
            var.save()
            

    profile = UserProfile.objects.get(user=request.user)

    print(profile)
    if payment.status == 'True':
        print('hlo')
        print(payment.amount_paid)
        profile.wallet += payment.amount_paid
        print(profile.wallet)
        profile.save()

    payment.delete()
    if request.user.is_superuser:
        print(type(profile.user))
        print(type(profile.user.first_name))
        messages.success(request, profile.user.first_name +
                         'cancelled' + str(order.order_number))
        return redirect('my_orders')
    else:
        messages.success(request, 'item cancelled successfully')
        return redirect('my_orders')
    

def return_order(request, id):
    
    if request.method == 'POST':
        
        return_reason = request.POST['return_reason']
    print(return_reason)
    order = Order.objects.get(order_number=id, user=request.user)
    order.status = "Returned"
    order.is_returned = True
    order.return_reason = return_reason
    order.save()
    payment = Payment.objects.get(order_id=order.order_number)
    print("order get")

    order_products = OrderProduct.objects.filter(
        user=request.user, order=order)
    for order_product in order_products:
        # increase quantity of product
        product = Product.objects.get(id=order_product.product_id)
        product.stock += order_product.quantity
        product.save()

        # increase quantity of product variation
        print(order_product.variations)
        variation = Variations.objects.filter(
            id__in=order_product.variations.all())
        print(variation)
        for var in variation:
            var.stock += order_product.quantity
            var.save()
            

    profile = UserProfile.objects.get(user=request.user)
    if payment.status == 'True':
        print('hlo')
        print(payment.amount_paid)
        profile.wallet += payment.amount_paid

        print(profile.wallet)
        profile.save()

    payment.delete()
    messages.success(request, 'item returned successfully')
    return redirect('my_orders')

def coupons(request):
    if request.method == 'POST':
        coupon_code = request.POST['coupon']
        grand_total = request.POST['grand_total']
        coupon_discount = 0
        try:
            instance = UserCoupon.objects.get(
                user=request.user, coupon__code=coupon_code)

            if float(grand_total) >= float(instance.coupon.min_value):
                coupon_discount = (
                    (float(grand_total) * float(instance.coupon.discount))/100)
                grand_total = float(grand_total) - coupon_discount
                grand_total = format(grand_total, '.2f')
                coupon_discount = format(coupon_discount, '.2f')
                msg = 'Coupon Applied successfully'
                instance.used = True
                instance.save()
            else:
                msg = 'This coupon is only applicable for orders more than ₹' + \
                    str(instance.coupon.min_value) + '\- only!'
        except:
            msg = 'Coupon is not valid'
        response = {
            'grand_total': grand_total,
            'msg': msg,
            'coupon_discount': coupon_discount,
            'coupon_code': coupon_code,
        }

    return JsonResponse(response)

def wallet(request,id):
   print('hlo')
   try:
      print('hoi')
      order = Order.objects.get(user=request.user,is_ordered=False,order_number=id)
      cart_items = CartItem.objects.filter(user=request.user)
      order.is_ordered = True
      payment = Payment(
               user = request.user,
               payment_id = order.order_number,
               order_id = order.order_number,
               payment_method = 'Wallet payment',
               
               amount_paid = order.order_total,
               status = 'True'
      )
      payment.save()
      order.payment = payment
      order.is_ordered = True
      order.save()

      # Move cart item to ordered product table
      for item in cart_items:
         order_product = OrderProduct()
         order_product.order_id = order.id
         order_product.payment = payment
         order_product.user_id = request.user.id
         order_product.product_id = item.product_id
         order_product.quantity = item.quantity
         order_product.product_price = item.product.price
         order_product.ordered = True
         order_product.save()

         cart_item = CartItem.objects.get(id=item.id)
         print(cart_item)
         product_variation = cart_item.variations.all()
         order_product = OrderProduct.objects.get(id=order_product.id)
         order_product.variations.set(product_variation)
         order_product.save()

         # Reduce quantity of product
         product = Product.objects.get( id = cart_item.product_id)
         product.stock -= cart_item.quantity
         product.save()

         variation = Variations.objects.filter(id__in= cart_item.variations.all())
         
         for var in variation:
               var.stock -= cart_item.quantity
               var.save()
               print('ann')

      CartItem.objects.filter(user= request.user).delete()       
      ordered_products = OrderProduct.objects.filter(order_id = order.id)  
      total = 0
      for i in ordered_products:
           total += i.product_price * i.quantity
      tax = (2*total)/100  
      profile = UserProfile.objects.get(user=request.user)  
      profile.wallet -= order.order_total
      profile.save() 
      print('ann')
      
      context ={
            'order':order,
            'ordered_products':ordered_products,
            'payment':payment,
            'total':total,
            'tax':tax, 
            'profile':profile,     
         }  
      return render(request,'order_complete.html',context)   


   except Exception as e:
     print(e)
       
 
     print('potti')
   return redirect('home')
