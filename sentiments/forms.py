from django import forms
from models import Tweet

class HashtagForm(forms.Form):
    hashtag = forms.CharField(max_length=150)
    class Meta:
        model = Tweet
        fields = ('hashtag',)