from django.contrib import admin
from .models import reader, reader_keyword, keyword, article, reader_like


class readers(admin.ModelAdmin):

    list_display = ('hashId', 'email', 'confirmation', 'date', 'state')


class readerLikes(admin.ModelAdmin):

    list_display = ('reader', 'doi', 'term', 'date', 'state')


class articleAll(admin.ModelAdmin):

    list_display = ('no', 'doi', 'title')


admin.site.register(reader, readers)
admin.site.register(keyword)
admin.site.register(reader_keyword)
admin.site.register(article, articleAll)
admin.site.register(reader_like, readerLikes)
