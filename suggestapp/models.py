from django.db import models
from datetime import datetime


# Create your models here.


class reader(models.Model):

    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=150)
    hashId = models.CharField(max_length=300)
    confirmation = models.BooleanField(default=False)
    date = models.DateField(default=datetime.now)
    state = models.CharField(max_length=150)
    token = models.CharField(max_length=300)

    def __str__(self):
        return str(self.email)


class keyword(models.Model):
    MY_CHOICES = [('Algorithms', 'Algorithms'),
                  ('Artificial Intelligence', 'Artificial Intelligence'),
                  ('Networking', 'Networking'),
                  ('Wireless Communication', 'Wireless Communication'),
                  ('Data Science', 'Data Science'),
                  ('Molecular Communication', 'Molecular Communication'),
                  ('Computer Science', 'Computer Science')]
    keyword_id = models.AutoField(primary_key=True)
    keyword_name = models.CharField(
        max_length=100, null=True, choices=MY_CHOICES)

    def __str__(self):
        return str(self.keyword_id)


class reader_keyword(models.Model):
    readers = models.EmailField(max_length=150)
    keywords = models.ManyToManyField(keyword, blank=True)

    def __str__(self):
        return str(self.readers)


class article(models.Model):
    no = models.AutoField(primary_key=True)
    doi = models.CharField(max_length=50)
    title = models.TextField(default='')
    authors = models.TextField(default='')
    abstract = models.TextField(default='')
    term = models.TextField()
    date = models.CharField(max_length=100)
    link = models.URLField(max_length=250)
    vectorized = models.TextField(default='')

    def __str__(self):
        return str(self.no)
