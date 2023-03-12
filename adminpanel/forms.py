# from .models import AdminLogin
from store.models import Product
from django import forms
from category.models import Category, Sub_Category
from order.models import Coupon


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'slug', 'price', 'image', 'image1', 'image2',
                  'image3', 'stock', 'category', 'sub_category', 'description']
        labels = {

            'product_name': 'product_name',
            'slug': 'slug',
            'price': 'price',
            'image': 'image',
            'image1': 'image1',
            'image2': 'image2',
            'image3': 'image3',
            'stock': 'stock',
            'category': 'category',
            'sub_category': 'sub_category',
            'description': 'description'

        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'slug', 'description']
        labels = {
            'category_name': 'category_name',
            'slug': 'slug',
            'description': 'description'
        }


class Sub_CategoryForm(forms.ModelForm):
    class Meta:
        model = Sub_Category
        fields = ['sub_category_name', 'slug', 'category']
        labels = {
            'sub_category_name': 'sub_category_name',
            'slug': 'slug',
            'category': 'category'
        }

class Update_CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'slug', 'description']
        labels = {
            'category_name': 'category_name',
            'slug': 'slug',
            'description': 'description'
        }


class Update_ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name','slug', 'price', 'image','image1','image2','image3', 'stock', 'category','sub_category',]
        labels = {
            'product_name': 'product_name',
                   'slug' :'slug' ,
                   'price': 'price',
                   'image': 'image',
                  'image1':'image1',
                  'image2':'image2',
                  'image3':'image3',
                   'stock': 'stock',
                'category': 'category',
            'sub_category':'sub_category'
           
        }
class DateInput(forms.DateInput):
    input_type = 'date'

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount','min_value','valid_at','active']
        widgets = {
                    'valid_at': DateInput(),
                    }
        labels ={
            'code':'Coupon Code',
            'discount':'Discount in percentage',
            'min_value':'Minimum Value',
            'valid_at':'Expiry Date',
            'active':'Available',
            
        }
