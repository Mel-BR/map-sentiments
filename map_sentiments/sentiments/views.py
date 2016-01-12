from django.http import HttpResponse
from sentiments.models import State, Tweet
from django.db.models import Avg
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from collections import defaultdict
from TwitterAPI import TwitterAPI
from alchemyapi import AlchemyAPI
from sentiments.forms import HashtagForm
import csv
import json
import os


def d3States(request):

    if request.method == 'POST':
        form = HashtagForm(request.POST)

        if form.is_valid():
            hashtag = form.cleaned_data['hashtag']
            #streamTweets(request, hashtag)

    else:
        hashtag = "0"
        form = HashtagForm()


    return render(request, "sentiments/d3-SentAna.html", locals())


def loadStates(request):
	path = (os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"\\files\\abbrev.csv").replace('\\','/')
	with open(path) as f:
		state = State
		reader = csv.reader(f)
		for row in reader:
			_, created = state.objects.get_or_create(abbrev=row[1],full_name=row[0],)
	return HttpResponse("Load successful")


def loadTweets(request):

    path = (os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"\\files\\access.json").replace('\\','/')
    #url = static('/sentiments/us-states.json')

    with open(path) as f:
        data = json.load(f)
        ACCESS_TOKEN_KEY = data['ACCESS_TOKEN_KEY']
        ACCESS_TOKEN_SECRET = data['ACCESS_TOKEN_SECRET']
        CONSUMER_KEY = data['CONSUMER_KEY']
        CONSUMER_SECRET = data['CONSUMER_SECRET']

    api = TwitterAPI(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN_KEY,ACCESS_TOKEN_SECRET)

    SEARCH_TERM = 'trump'
    count = 0
    lang = 'en'
    geocode = "37.6,-95.665,1400mi"

    r = api.request('search/tweets', {'lang': lang, 'q': SEARCH_TERM, 'count': count, 'geocode': geocode})
    for item in r:
        if item['place'] != None  :
            text = unicode(item['text']).encode('utf-8')
            state = unicode(item['place']['full_name'][-2:]).encode("utf-8")
            score = getScore(text)
            if score > -2:
                queryState = State.objects.filter(abbrev=state)
                queryTweet = Tweet.objects.filter(text=text)

                #Check if tweet not already in the Database & if state exists
                if queryState.count()>0 and queryTweet.count() == 0 :
                    state = queryState[0]
                    _, created = Tweet.objects.get_or_create(text=text,state=state,score=score,)
                    count +=1
    return HttpResponse("Load successful "+ str(count)+" tweets has been added to the DB")



def getScore(text):
	alchemyapi = AlchemyAPI()
	score = -10

	response = alchemyapi.sentiment('html', text)
	if 'docSentiment' in response:
		if 'score' in response['docSentiment']:
			score = float(response['docSentiment']['score'])
   	return score


def streamTweets(request, htag):

    path = (os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"\\files\\access.json").replace('\\','/')
    #url = static('/sentiments/us-states.json')

    with open(path) as f:
		data = json.load(f)
		ACCESS_TOKEN_KEY = data['ACCESS_TOKEN_KEY']
		ACCESS_TOKEN_SECRET = data['ACCESS_TOKEN_SECRET']
		CONSUMER_KEY = data['CONSUMER_KEY']
		CONSUMER_SECRET = data['CONSUMER_SECRET']

    api = TwitterAPI(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN_KEY,ACCESS_TOKEN_SECRET)

    SEARCH_TERM = htag
    lang = 'en'
    geocode = "37.6,-95.665,1400mi"
	
    while True:
        try:
            iterator = api.request('statuses/filter', {'lang': lang, 'track': SEARCH_TERM, 'geocode': geocode}). get_iterator()
            for item in iterator:
                if 'text' in item:
                    if item['place'] != None :
                        text = unicode(item['text']).encode('utf-8')
                        state = unicode(item['place']['full_name'][-2:]).encode("utf-8")
                        score = getScore(text)
                        if score > -2:
                            queryState = State.objects.filter(abbrev=state)
                            queryTweet = Tweet.objects.filter(text=text)

                            #Check if tweet not already in the Database & if state exists
                            if queryState.count()>0 and queryTweet.count() == 0 :
                                print "added"
                                print text
                                print state
                                print score
                                print htag
                                print "\n\n\n"
                                state = queryState[0]
                                _, created = Tweet.objects.get_or_create(text=text,state=state,score=score,hashtag=htag)


                elif ' disconnect' in item:
                    event = item[ ' disconnect' ]
                    if event[ ' code' ] in [ 2, 5, 6, 7]:
                        # something needs to be fixed before re-connecting
                        raise Exception(event[ ' reason' ])
                    else:
                        # temporary interruption, re-try request
                        break
        except Exception as e:
            pass


def getUsStates(request):
	path = (os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"\\files\\us-states.json").replace('\\','/')

	with open(path) as f:
		data = json.load(f)
	return HttpResponse(json.dumps(data), content_type='application/json')


def getScoresByStates(request, htag):
	jsonReturn=[]

	tweets = Tweet.objects.filter(hashtag=htag).values('state').annotate(av=Avg('score'))
	for tweet in tweets:
		state_abbrev = tweet['state']
		state_full_name = State.objects.get(abbrev=state_abbrev).full_name
		new = defaultdict(float)
		new['state']=state_full_name
		new['value']=tweet['av']
		jsonReturn.append(new)

	return HttpResponse(json.dumps(jsonReturn), content_type='application/json')
