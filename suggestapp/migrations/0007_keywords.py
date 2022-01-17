# Generated by Django 3.2.8 on 2022-01-17 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('suggestapp', '0006_alter_keyword_keyword_name'),
    ]

    def insert_default_articles(apps, schema_editor):
        list = ['Algorithms', "Artificial Intelligence",
                "Networking", "Wireless Communication", "Data Science", "Molecular Communication", "Computer Science"]
        for item in list:
            element = item
            content = apps.get_model('suggestapp', 'keyword')
            content = content(keyword_name=element)
            content.save()

    operations = [
        migrations.RunPython(insert_default_articles),
    ]
