# Generated by Django 3.2.16 on 2023-02-05 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='phone',
            field=models.CharField(default='', help_text='enter 10 digit phone number', max_length=20, unique=True, verbose_name='phone number'),
            preserve_default=False,
        ),
    ]