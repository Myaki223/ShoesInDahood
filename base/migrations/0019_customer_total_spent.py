# Generated by Django 4.1.7 on 2023-05-06 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0018_shoppingcart'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='total_spent',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
