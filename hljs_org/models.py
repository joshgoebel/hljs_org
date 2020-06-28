from django.db import models
from django.utils.html import mark_safe
import commonmark


class News(models.Model):
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    for_version = models.CharField(max_length=255, default='', blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'News'
        verbose_name_plural = 'News'

    def __str__(self):
        return self.text.split('\n', 1)[0]

    def html(self):
        return mark_safe(commonmark.commonmark(self.text))

class Update(models.Model):
    version = models.CharField(max_length=255)
    started = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True, blank=True)
    error = models.TextField(blank=True)

    def status(self):
        return 'in-progress' if self.finished is None else 'failed' if self.error else 'succeess'

    def __str__(self):
        return 'Update to {} at {}: {}'.format(
            self.version,
            self.started.strftime('%Y-%m-%d %H:%M:%S'),
            self.status(),
        )
