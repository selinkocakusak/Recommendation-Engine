from django.contrib import admin
from .models import reader, reader_keyword, keyword, article


class readers(admin.ModelAdmin):

    list_display = ('hashId', 'email', 'confirmation', 'date', 'state')


admin.site.register(reader, readers)
admin.site.register(keyword)
admin.site.register(reader_keyword)
admin.site.register(article)
