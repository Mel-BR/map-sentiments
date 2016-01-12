from django.db import models

class State(models.Model):
    abbrev = models.CharField(max_length=5, primary_key=True)
    full_name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.abbrev+" : "+self.full_name


class Tweet(models.Model):
    text = models.CharField(max_length=150, primary_key=True)
    hashtag = models.CharField(max_length=150, default="")
    state = models.ForeignKey(State)
    score = models.DecimalField(max_digits=5, decimal_places=3)

    def __unicode__(self):
        return self.text