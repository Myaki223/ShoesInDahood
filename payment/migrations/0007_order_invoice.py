# Generated by Django 5.1.4 on 2025-04-17 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_order_date_shipped'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='invoice',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
