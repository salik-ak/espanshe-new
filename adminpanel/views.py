from django.shortcuts import redirect, render,get_object_or_404
from django.contrib.auth.models import auth
from django.contrib import messages
from store.models import Product
from .forms import ProductForm, CategoryForm, Sub_CategoryForm, Update_CategoryForm, Update_ProductForm,CouponForm
from category.models import Category, Sub_Category
from accounts.models import CustomUser
from order.models import Order,Payment
from django.core.paginator import  Paginator
from order.models import Coupon


# Create your views here.


def adminlogin(request):

    if 'email' in request.session:
        return redirect('adminhome')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)

        if user is not None and user.is_superuser:
            request.session['email'] = email
            auth.login(request, user)
            print('admin logged in ')
            messages.success(request, 'successfully signed up!')
            return redirect('adminhome')
        else:
            print('Not autherised')
            messages.error(request, 'Not autherised')
            return redirect('adminlogin')
    return render(request, 'adminlogin.html')


def adminhome(request):
    if 'email' in request.session:
        return render(request, 'adminhome.html')
    return redirect('adminlogin')


def adminproduct(request):
    if 'email' in request.session:
        products = Product.objects.all()
        context = {
            'products': products
        }

        return render(request, 'adminproduct.html', context)
    else:
        return redirect('adminlogin')


def admin_addproducts(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('adminproduct')
        else:

            return redirect('admin_addproducts')
    else:
        form = ProductForm()
        context = {
            'form': form
        }

    return render(request, 'admin_addproduct.html', context)


def admin_category(request):
    if 'email' in request.session:
        categories = Category.objects.all()

        context = {
            'categories': categories
        }
        return render(request, 'admin_category.html', context)
    else:
        return redirect('adminlogin')


def admin_addcategory(request):

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            # messages.sucess(request, 'category added successfully.')
            return redirect('admin_category')
        else:
            # messages.error(request, 'category allready exisist!!!')
            return redirect('admin_addcategory')
    return render(request, 'admin_addcategory.html')


def admin_subcategory(request):

    sub_categories = Sub_Category.objects.all()

    context = {
        'sub_categories': sub_categories
    }
    return render(request, 'admin_subcategory.html', context)


def admin_addsubcategory(request):

    if request.method == 'POST':
        form = Sub_CategoryForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('admin_subcategory')
        else:

            return redirect('admin_addsubcategory')

    form = Sub_CategoryForm()
    context = {
        'form': form
    }

    return render(request, 'admin_addsubcategory.html', context)


def admin_deletesubcategory(request, id):
    dlt = Sub_Category.objects.get(pk=id)
    dlt.delete()
    return redirect('admin_subcategory')


def admin_deletecategory(request, id):
    dlt = Category.objects.get(pk=id)
    dlt.delete()
    return redirect('admin_category')


def update_category(request, id):
    if request.method == 'POST':
        update = Category.objects.get(pk=id)
        form = Update_CategoryForm(request.POST, instance=update)
        if form.is_valid():
            form.save()
            return redirect('admin_category')
        else:
            return redirect('update_category', id)

    else:
        update = Category.objects.get(pk=id)
        form = Update_CategoryForm(instance=update)
        context = {
            'form': form
        }
        return render(request, 'update_category.html', context)


def admin_userlist(request):
    users = CustomUser.objects.all()
    context = {
        'users': users

    }

    return render(request, 'admin_userlist.html', context)


def blockuser(request,id):
    user = CustomUser.objects.get(id=id)
    if user.is_active:
        user.is_active = False
        user.save()
        messages.success(request,'user successfully blocked')
    else:
        user.is_active = True
        user.save()
        messages.success(request,'user successfully unblocked')
    return redirect('admin_userlist')



def update_products(request,id):
    if request.method == 'POST':
        update = Product.objects.get(pk=id)
        form = ProductForm(request.POST,request.FILES,instance=update)
        if form.is_valid():
            form.save()
            return redirect('adminproduct')
        else:
            return redirect('update_product',id)
    else:
        update = Product.objects.get(pk=id)
        form = ProductForm(instance=update)
        context = {
            'form':form
        }
    return render(request,'admin_updateproduct.html',context)




def delete_products(request, id):
    dlt = Product.objects.get(pk=id)
    dlt.delete()
    return redirect('admin_products')


def admin_orders(request):
    orders = Order.objects.filter(is_ordered=True).order_by('-id')
    context ={
        'orders':orders
    }
    return render (request,'admin_orders_list.html',context)

def update_order(request, id):
  if request.method == 'POST':
    order = get_object_or_404(Order, id=id)
    status = request.POST.get('status')
    order.status = status 
    order.save()
    if status  == "Delivered":
      try:
          payment = Payment.objects.get(payment_id = order.order_number, status = False)
          print(payment)
          if payment.payment_method == 'Cash on Delivery':
              payment.status = True
              payment.save()
      except:
          pass
    order.save()
    
  return redirect('admin_orders')

def coupon(request):
    coupons = Coupon.objects.all()
    paginator = Paginator(coupons,7)
    page= request.GET.get('page')
    paged_coupon = paginator.get_page(page) 
    context = {
        'coupons':paged_coupon
    }
    return render(request,'coupon.html',context)

def addCoupon(request):
    if request.method == 'POST':
      form = CouponForm(request.POST)
      if form.is_valid() :
         
         form.save()
         messages.success(request, 'Coupon added successfully.')
         return redirect('coupon')
      else:
         messages.error(request, 'Coupon already exisist!!!')
         return redirect('addCoupon')
      
    form = CouponForm()
    context={
        'form':form
    }
    return render(request,'add_coupon.html',context)

def deleteCoupon(request,id):
    dlt = Coupon.objects.get(pk=id)
    dlt.delete()
    return redirect('coupon')

def updateCoupon(request,id):
    if request.method == 'POST':
        update = Coupon.objects.get(pk=id)
        form = CouponForm(request.POST,instance=update)
        if form.is_valid():
          form.save()
          return redirect('coupon')
        else:
            messages.error(request, 'Coupon already exsist!!!')
            return redirect('updateCoupon',id)
    else:
        update = Coupon.objects.get(pk=id)
        form = CouponForm(instance=update)
        context={
            'form':form
        }
    return render(request,'update_coupon.html',context)
  


def adminlogout(request):
    if 'email' in request.session:
        request.session.flush()
    auth.logout(request)
    return redirect('adminlogin')


