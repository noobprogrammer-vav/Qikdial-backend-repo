# Generated by Django 5.0.4 on 2024-05-03 06:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qikdial', '0015_remove_listingmodel_category_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listingmodel',
            name='category',
        ),
        migrations.RemoveField(
            model_name='listingmodel',
            name='user',
        ),
        migrations.AddField(
            model_name='listingmodel',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='qikdial.categorymodel'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='listingmodel',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
