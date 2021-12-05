from django.db import models
import hashlib
from django.db.models.signals import post_save
from django.dispatch import receiver

from datetime import datetime

from django.db.models.fields import TimeField
from django.contrib.auth.models import User


# Create your models here.
MY_CHOICES = [('Algorithms', 'Algorithms'),
              ('Artificial Intelligence', 'Artificial Intelligence'),
              ('Networking', 'Networking'),
              ('Wireless Communication', 'Wireless Communication'),
              ('Data Science', 'Data Science')]


class reader(models.Model):

    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=150)
    hashId = models.CharField(max_length=300)
    confirmation = models.BooleanField(default=False)
    date = models.DateField(default=datetime.now)
    # keywords = models.CharField(max_length=150, choices=MY_CHOICES)
    keywords = models.CharField(max_length=300)
    # keywords = models.ForeignKey('Keyword', on_delete=models.DO_NOTHING)
    state = models.CharField(max_length=150)
    token = models.CharField(max_length=300)

    # def __str__(self):
    #     return str(self.hashId)
    class Meta:
        db_table = "reader"


# class Keyword(models.Model):
#     keywords = models.CharField(max_length=100, choices=MY_CHOICES)

#     class Meta:
#         db_table = "keyword"

    # class reader(models.Model):
    #     id = models.AutoField(primary_key=True)
    #     HashId = hashlib.sha256(str(string_to_hash).encode('utf-8'))
    #     email = models.EmailField(max_length=150)
    #     confirmation = models.BooleanField(default=False)
    #     date = models.DateField(default=datetime.now)
    #     keywords = models.CharField(max_length=150)
    #     state = models.CharField(max_length=150)

    #     def __str__(self):
    #         return str(self.HashId)

    # @receiver(post_save, sender=User)
    # def update_profile_signal(sender, instance, created, **kwargs):
    #     if created:
    #         Profile.objects.create(user=instance)
    #     instance.profile.save()

    # def __str__(self):
    #     # Built-in attribute of django user
    #     return self.user.email

    # class subscriber(models.Model):
    #     user = models.OneToOneField(User, on_delete=models.CASCADE)
    #     # HashId = hashlib.sha256(str(string_to_hash).encode('utf-8'))
    #     # # email = models.CharField(max_length=200, null=True)
    #     # keywords = models.CharField(max_length=200, null=True)
    #     # date = models.DateField(default=datetime.now)
    #     # event_time = models.TimeField(auto_now=False, auto_now_add=False, null=True,
    #     #                               blank=True)

    #     def __str__(self):
    #         return str(self.user)

    # class subscriber(models.Model):
    #     user = models.OneToOneField(User, on_delete=models.CASCADE)
    #     HashId = hashlib.sha256(str(string_to_hash).encode('utf-8'))
    #     # email = models.CharField(max_length=200, null=True)
    #     keywords = models.CharField(max_length=200, null=True)
    #     date = models.DateField(default=datetime.now)
    #     event_time = models.TimeField(auto_now=False, auto_now_add=False, null=True,
    #                                   blank=True)

    #     def __str__(self):
    #         return str(self.HashId)

    # def __str__(self):
    #     # Built-in attribute of django user
    #     return self.user.email

    # class subscriber(models.Model):
    #     HashId = hashlib.sha256(str(string_to_hash).encode('utf-8'))
    #     email = models.CharField(max_length=200, null=True)
    #     keywords = models.CharField(max_length=200, null=True)
    #     date = models.DateField(default=datetime.now)
    #     event_time = models.TimeField(auto_now=False, auto_now_add=False, null=True,
    #                                   blank=True)

    #     def __str__(self):
    #         return str(self.HashId)


class topicname(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)
