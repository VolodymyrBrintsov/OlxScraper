from django.db import models
import datetime

class JobAdds(models.Model):
    title = models.TextField(default='')
    phone = models.CharField(max_length=150)
    heading = models.CharField(max_length=50)
    name = models.CharField(max_length=15)
    user_since = models.CharField(max_length=50)
    price = models.CharField(max_length=50)
    link = models.SlugField()
    time = models.CharField(default=datetime.datetime.now().strftime("%m/%d/%Y"), max_length=20)

    def __str__(self):
        return self.title