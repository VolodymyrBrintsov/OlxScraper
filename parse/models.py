from django.db import models
import datetime

class JobAdds(models.Model):
    title = models.TextField(default='')
    phone = models.CharField(max_length=150)
    heading = models.CharField(max_length=150)
    name = models.CharField(max_length=50)
    user_since = models.CharField(max_length=150)
    price = models.CharField(max_length=150)
    link = models.SlugField(max_length=255)
    time = models.CharField(default=datetime.datetime.now().strftime("%m/%d/%Y"), max_length=20)

    def __str__(self):
        return self.title