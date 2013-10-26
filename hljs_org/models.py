from django.db import models


class Snippet(models.Model):
    code = models.TextField()

    def __str__(self):
        return self.code.replace('\n', ' ')[:100]
