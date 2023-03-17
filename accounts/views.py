from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import auth
from .models import CustomUser,UserProfile
from django.contrib import messages
from .forms import AddressForm, UserProfileForm,CustomUserForm
from order.models import Order,OrderProduct,Address
from django.contrib.auth.decorators import login_required
from datetime import date,timedelta
from cart.models import Cart, CartItem
from cart.views import _cart_id
import requests




# Create your views here.

def user_login(request):
    if 'email' in request.session:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            if user.is_active:
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(
                        cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart=cart)

                        # getting the product variations by cart id
                        product_variation = []
                        for item in cart_item:
                            variation = item.variations.all()
                            product_variation.append(list(variation))

                        # get the cart items from the user to access his product variations
                        cart_item = CartItem.objects.filter(user=user)

                        ex_var_list = []
                        id = []
                        for item in cart_item:
                            existing_variation = item.variations.all()
                            ex_var_list.append(list(existing_variation))
                            id.append(item.id)
                        # product_variation=[1,2,3,4,6]
                        # ex_var_list=[4,6,3,5]

                        for pr in product_variation:
                            if pr in ex_var_list:
                                index = ex_var_list.index(pr)
                                item_id = id[index]
                                item = CartItem.objects.get(id=item_id)
                                item.quantity += 1
                                item.user = user
                                item.save()
                            else:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user
                                    item.save()

                except:
                    pass
                request.session['email'] = email

                auth.login(request, user)
                messages.success(request, 'Successfully logged in!')
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query

                    # next=/cart/checkout/
                    params = dict(x.split('=')for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)

                except:
                    return redirect('home')
            else:

                messages.error(request, 'You are Blocked !!')
                return redirect('user_login')
        else:
            messages.error(request, 'Invalid login')
            return redirect('user_login')
    else:

        return render(request, 'userlogin.html')




def user_signup(request):
    if 'email' in request.session:
        return redirect('home')
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        phone = request.POST['phone']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if CustomUser.objects.filter(email=email).exists():
                print('email allready taken')
                return redirect('user_signup')
            elif CustomUser.objects.filter(phone=phone).exists():
                print('phone number allready taken')
                return redirect('user_signup')
            else:
                user = CustomUser.objects.create_user(
                    phone=phone, password=password1, email=email, first_name=firstname, last_name=lastname
                )
                user.save()

                print('user created')

            return redirect('user_login')
        else:
            print('password not matching')
            return redirect('user_signup')

    else:
        return render(request, 'usersignup.html')
    
def logout(request):
    if 'email' in request.session:
        request.session.flush()
    auth.logout(request)
    messages.success(request,'successfully loged out')

    return redirect('/')
    
def AddCheckoutAddress(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            print('form is valid')
            detail = Address()
            detail.user = request.user
            detail.first_name = form.cleaned_data['first_name']
            detail.last_name = form.cleaned_data['last_name']
            detail.phone = form.cleaned_data['phone']
            detail.email = form.cleaned_data['email']
            detail.address_line_1 = form.cleaned_data['address_line_1']
            detail.address_line_2 = form.cleaned_data['address_line_2']
            detail.state = form.cleaned_data['state']
            detail.country = form.cleaned_data['country']
            detail.city = form.cleaned_data['city']
            detail.save()
            messages.success(request, 'Address added Successfully')
            return redirect('checkout')
        else:
            messages.success(request, 'Form is Not valid')
            return redirect('checkout')
        
def deleteCheckoutAddress(request, id):
    address = Address.objects.get(id=id)
    messages.success(request, "Address Deleted")
    address.delete()
    return redirect('checkout')


@login_required(login_url='user_login')
def user_dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(
        user_id=request.user.id, is_ordered=True)
    user = request.user
    orders_count = orders.count()

    try:
        userprofile = UserProfile.objects.get(user_id=request.user.id)
    except UserProfile.DoesNotExist:
        userprofile = UserProfile.objects.create(user=user)

    context = {
        'orders_count': orders_count,
        'user': user,
        'userprofile': userprofile,
    }
    return render(request, 'user_dashboard.html', context)

@login_required(login_url='user_login')
def editAddress(request, id):
    address = Address.objects.get(id=id)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address Updated Successfully')
            return redirect('myAddress')
        else:
            messages.error(request, 'Invalid Inputs!!!')
            return redirect('myAddress')
    else:
        form = AddressForm(instance=address)

    context = {
        'form': form,
    }
    return render(request, 'editAddress.html', context)

def my_orders(request):
    orders = Order.objects.filter(
        user=request.user, is_ordered=True).order_by('-id')
    today = date.today()
    for order in orders:
        add = order.updated_at + timedelta(days=7)
    context = {
        'orders': orders,
        'today':today,
        'add':add,
    }
    return render(request, 'my_orders.html', context)


@login_required(login_url='user_login')
def user_dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(
        user_id=request.user.id, is_ordered=True)
    user = request.user
    orders_count = orders.count()

    try:
        userprofile = UserProfile.objects.get(user_id=request.user.id)
    except UserProfile.DoesNotExist:
        userprofile = UserProfile.objects.create(user=user)

    context = {
        'orders_count': orders_count,
        'user': user,
        'userprofile': userprofile,
    }
    return render(request, 'user_dashboard.html', context)


@login_required(login_url='user_login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = CustomUserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your Profile has been updated')
            return redirect('edit_profile')

        else:
            return redirect('edit_profile')
    else:
        user_form = CustomUserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'edit_profile.html', context)

@login_required(login_url='user_login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    total = 0
    for i in order_detail:
        total += i.product_price * i.quantity
        tax = (2*total)/100
    context = {
        'order_datail': order_detail,
        'order': order,
        'total': total,
        'tax': tax,
    }
    return render(request, 'order_detail.html', context)

@login_required(login_url='user_login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        user = CustomUser.objects.get(email__exact=request.user.email)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'change_password.html')

@login_required(login_url='user_login')
def myAddress(request):
    current_user = request.user
    address = Address.objects.filter(user=current_user)

    context = {
        'address': address,
    }
    return render(request, 'myAddress.html', context)


@login_required(login_url='user_login')
def addAddress(request):
    if request.method == 'POST':
        form = AddressForm(request.POST, request.FILES,)
        if form.is_valid():
            print('form is valid')
            detail = Address()
            detail.user = request.user
            detail.first_name = form.cleaned_data['first_name']
            detail.last_name = form.cleaned_data['last_name']
            detail.phone = form.cleaned_data['phone']
            detail.email = form.cleaned_data['email']
            detail.address_line_1 = form.cleaned_data['address_line_1']
            detail.address_line_2 = form.cleaned_data['address_line_2']
            detail.state = form.cleaned_data['state']
            detail.country = form.cleaned_data['country']
            detail.city = form.cleaned_data['city']
            detail.save()
            messages.success(request, 'Address added Successfully')
            return redirect('myAddress')
        else:
            messages.success(request, 'Form is Not valid')
            return redirect('myAddress')
    else:
        form = AddressForm()
        context = {
            'form': form
        }
    return render(request, 'addAddress.html', context)

@login_required(login_url='user_login')
def deleteAddress(request, id):
    address = Address.objects.get(id=id)
    messages.success(request, "Address Deleted")
    address.delete()
    return redirect('myAddress')




def add_amount(request):
    
    if request.method == 'POST':
        amount = float(request.POST['amount'])
        add_amount = UserProfile.objects.get(user=request.user)
       
        add_amount.wallet += amount
        add_amount.save()

    return redirect('user_dashboard')






