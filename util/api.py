from urllib import request, parse
from urllib.error import HTTPError # error handling for bad api calls
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def getkey(k_file):
    '''retrives api keys based on file name'''
    try:
        f = open(k_file, 'r')
        l = f.read().split('\n')
        f.close()
        return l[0]
    except FileNotFoundError:
        print("Missing key file, HALP!")
        return None

newskey = getkey("keys/newsApi.txt") #gets API key
nytimeskey = getkey("keys/nytApi.txt")
googlekey = getkey("keys/googleCivic.txt") #gets API key

def civic(zip_code):
    '''info on all politician in a zip_code'''
    try:
        url = "https://www.googleapis.com/civicinfo/v2/representatives?key=" + googlekey
        url += "&address=" + str(zip_code)
        cri = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        stuff = request.urlopen(url) # GETS STUFF

        js = stuff.read() # gets info from urlopen
        jason = json.loads(js)
        jason["officials"].reverse()
        return jason["officials"]
    except HTTPError:
        return "error"
    return None

def news_api(query):
    '''news articles from News API after given a query'''
    # try:
    url = "https://newsapi.org/v2/everything?apiKey=" + newskey
    url += "&q=" + query.replace(" ", "+")
    # url += 'domains=nytimes.com'
    #print(url)
    cri = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    stuff = request.urlopen(url) # GETS STUFF

    js = stuff.read() # gets info from urlopen
    jason = json.loads(js)
    return jason["articles"]
    # except HTTPError:
    #     return "error"

def nyt_news(query):
    '''news articles from NY Times after given a query'''
    try:
        url = "https://api.nytimes.com/svc/search/v2/articlesearch.json?api-key=" + nytimeskey
        url += "&q=" + query.replace(" ", "+")
        # url += 'facet_field=day_of_week'
        print(url)
        cri = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        stuff = request.urlopen(url) # GETS STUFF

        js = stuff.read() # gets info from urlopen
        jason = json.loads(js)
        jason = jason["response"]["docs"]
        articles = []
        for article in jason:
            if article["headline"]["print_headline"]:
                d = dict()
                d["headline"] = article["headline"]["print_headline"]
                d["snippet"] = article["snippet"]
                d["web_url"] = article["web_url"]
                articles.append(d)
        return articles # In the form: [{'headline': 'STUFF', 'snippet': 'STUFF', 'web_url': 'STUFF'}]

    except HTTPError:
        return "error"
    return None