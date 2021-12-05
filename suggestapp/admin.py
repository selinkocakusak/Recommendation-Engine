from django.contrib import admin
from .models import topicname, reader


# Register your models here.
# admin.site.register(UserInfo)
admin.site.register(topicname)


class readers(admin.ModelAdmin):

    list_display = ('hashId', 'email', 'confirmation', 'date', 'state')


admin.site.register(reader, readers)
# admin.site.register(Keyword)

# admin.site.register(subscriber)

# class contents(admin.ModelAdmin):
#     # def has_add_permission(self, request):
#     #     return False

#     list_display = ('no', 'doc_id', 'title', 'authors',
#                     'keywords', 'date')
#     list_filter = ('date', 'doc_id')


# admin.site.register(content, contents)
