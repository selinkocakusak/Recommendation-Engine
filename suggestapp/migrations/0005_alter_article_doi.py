# Generated by Django 3.2.8 on 2022-01-16 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suggestapp', '0004_alter_reader_like_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='doi',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]