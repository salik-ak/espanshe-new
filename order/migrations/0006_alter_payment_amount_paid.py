# Generated by Django 3.2.16 on 2023-03-03 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_coupon_usercoupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='amount_paid',
            field=models.FloatField(max_length=100),
        ),
    ]
