from django.db import models

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    read_date = models.DateField()
    cover_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.author}"