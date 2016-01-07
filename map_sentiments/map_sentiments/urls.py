from django.conf.urls import patterns, include, url
from sentiments import views


urlpatterns = patterns('',
	url(r'^d3States/$', views.d3States),
	url(r'^getUsStates/$', views.getUsStates),
	url(r'^loadStates/$', views.loadStates),
	url(r'^loadTweets/$', views.loadTweets),
	url(r'^getScoresByStates/$', views.getScoresByStates),
	url(r'^streamTweets/$', views.streamTweets),
)

