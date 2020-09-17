from django.db import models

class JobAdds(models.Model):
    title = models.TextField(default='')
    phone = models.CharField(max_length=50)
    heading = models.CharField(max_length=50)
    name = models.CharField(max_length=15)
    user_since = models.CharField(max_length=50)
    price = models.CharField(max_length=50)
    link = models.SlugField()

    def __str__(self):
        return self.title