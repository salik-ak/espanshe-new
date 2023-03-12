from django.db import models
from django.urls import reverse

# Create your models here.


class Category(models.Model):
    
    category_name = models.CharField(max_length=50)
    slug = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255)
    # cat_image = models.ImageField(upload_to='photos/categories',blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'


    

    def __str__(self):
        return self.category_name


class Sub_Category(models.Model):
    sub_category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'sub category'
        verbose_name_plural = 'sub categories'

    def get_url(self):
        return reverse('products_by_sub_category',args=[self.slug])

    def __str__(self):
        return self.sub_category_name
