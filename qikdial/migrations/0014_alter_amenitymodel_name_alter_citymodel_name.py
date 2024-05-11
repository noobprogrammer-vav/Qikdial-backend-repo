# Generated by Django 5.0.4 on 2024-05-02 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qikdial', '0013_remove_servicemodel_listing_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amenitymodel',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='citymodel',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
