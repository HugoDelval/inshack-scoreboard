from django.db import models


class News(models.Model):
    text = models.TextField()
    updated_date = models.DateTimeField(auto_now=True)

