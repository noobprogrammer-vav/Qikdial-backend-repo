# Generated by Django 5.0.4 on 2024-04-30 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qikdial', '0007_listingmodel_company_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='listingmodel',
            name='specific_city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='listingmodel',
            name='company_name',
            field=models.CharField(max_length=100),
        ),
    ]
