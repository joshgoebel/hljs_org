from django.contrib import admin

from hljs_org import models


admin.site.register(models.Snippet)
admin.site.register(models.News, list_display=['__str__', 'created'])
admin.site.register(models.Update, list_display=['version', 'started', 'finished', 'status'])
