from django.shortcuts import render



# Create your views here.
def user_category(request):
    return render(request,'user_category.html')