#Implement all this concept by machine learning with flask

from time import sleep
from flask import Flask, escape, request, render_template,redirect,url_for,session
import pickle
from io import BytesIO
from flask import Flask, jsonify,g
import time
import os
from webdriver_manager.chrome import ChromeDriverManager
import tweepy
from dotenv import load_dotenv
from flask import request,jsonify
import snscrape.modules.twitter as snstwitter
import requests
from goose3 import Goose
from wordcloud import WordCloud, STOPWORDS
import plotly.graph_objs as go
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText
import json
import plotly
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import base64
import pandas as pd
from flask import send_file
import datetime
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
from nltk.corpus import stopwords
from textblob import TextBlob
from apify_client import ApifyClient
from email.message import EmailMessage
import smtplib
import pandas as pd
from selenium import webdriver
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import ast

# Download the NLTK stop words corpus
nltk.download('stopwords')
nltk.download('brown')

vector = pickle.load(open("vectorizer.pkl", 'rb'))
model = pickle.load(open("modeldecisiontree.pkl", 'rb'))

app = Flask(__name__)
app.config['SECRET'] = 'kavach'



API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": "Bearer " +  "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" }
API_URL_PROP = "https://api-inference.huggingface.co/models/valurank/distilroberta-propaganda-2class"
API_URL_HATE = "https://api-inference.huggingface.co/models/IMSyPP/hate_speech_en"

EMAIL_ADDRESS = 'cybersentinels2@gmail.com'
EMAIL_PASSWORD = 'cybersentinels@1234'
OTP_DB = {}

OTP_EXPIRATION_TIME_SECONDS = 30  # 30 sec


def generate_otp(expiration_time_seconds):
    otp = str(random.randint(1000, 9999))
    expiration_time = datetime.datetime.now() + timedelta(seconds=expiration_time_seconds)
    return otp, expiration_time


def send_otp(email, otp):
    message = f'Your OTP is {otp}.'
    msg = MIMEText(message)
    msg['Subject'] = 'OTP Verification'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('cybersentinels2@gmail.com', 'ucdywkafnzomexkz')
        smtp.send_message(msg)

@app.route('/verify', methods=['POST'])
def verify_otp():
    email = request.json['email']
    otp = request.json['otp']
    articles = request.json['rNews']
    print("verify",articles)
    print(f"Reached VERIFY {email} {otp}")
    if OTP_DB.get(email):
        # Get the OTP and expiration time from the OTP_DB
        db_otp = OTP_DB[email]['otp']
        db_expiration_time = OTP_DB[email]['expiration_time']

        # Check if the OTP is valid
        if db_otp == otp and datetime.datetime.now() < db_expiration_time:

            sendMail([email],articles)
            return jsonify({"Response": True})

    # The OTP is invalid or has expired
    return jsonify({"Response": False})

@app.route('/email', methods=['POST'])
def handle_data():
    email = request.json['email']
    print(f"Reached EMAIL {email}")
    # Generate and send the OTP to the user's email
    otp, otp_expiration_time = generate_otp(OTP_EXPIRATION_TIME_SECONDS)
    send_otp(email, otp)

    # Store the OTP and expiration time in the OTP_DB
    OTP_DB[email] = {'otp': otp, 'expiration_time': otp_expiration_time}

    return jsonify({"Response": True})

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

def queryprop(payload):
	response = requests.post(API_URL_PROP, headers=headers, json=payload)
	return response.json()

def query_hate(payload):
	response = requests.post(API_URL_HATE, headers=headers, json=payload)
	return response.json()

def buttonPage(givenLink):
    target_url = givenLink
    emails = []
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode
    driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
    driver.get(target_url)
    driver.implicitly_wait(3)    
    button_list = driver.find_elements(By.PARTIAL_LINK_TEXT,'Contact')
    try:
        if len(button_list)!=0:
            button_list[-1].click()
        else:
            pass
    except Exception as e:
        print(e)
    email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,4}"
    html = driver.page_source
    emails = re.findall(email_pattern, html)
    time.sleep(5)
    driver.close()
    return  emails

#def homePage(givenLink):
#    target_url = givenLink
#    emails = []
#    chrome_options = Options()
#    chrome_options.add_argument('--headless')  # Run Chrome in headless mode
#    driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
#    driver.get(target_url)
#    driver.implicitly_wait(3)
#    #driver.maximize_window()
#    email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,4}"
#    html = driver.page_source
#    emails = re.findall(email_pattern, html)
#    time.sleep(5)
#    driver.close()
#    return emails

def getEmail(url):
   
    email_list = buttonPage(url)
    #if len(email_list) == 0:
    #    email_list = homePage(url)
    #email_list.append('crce.9242.cs@gmail.com')
    return email_list

def sendMail(email_list,article):
    if len(email_list) != 0: 
        for email in email_list[:3]:
            msg = EmailMessage()
            body = ''

# add the links to the email body
            for article in article['articles'][:3]:
                 body += f'\n\nLink: {article["link"]}'
            msg.set_content('Hello! We have received a report of fake news. Please follow the given links to fact-check this story and help stop the spread of misinformation. '
                            f'\n{body}')
                            
            msg['Subject'] = 'Fake News Alert!'
            msg['From'] = 'cybersentinels2@gmail.com'
            msg['To'] = email

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('cybersentinels2@gmail.com', 'ucdywkafnzomexkz')
            server.send_message(msg)
            server.quit()

        print("Message sent successfully!")
    
    else:        
        print("Empty Email List")
    return

def summary(url):
    try:

        goose = Goose()
        articles = goose.extract(url)
        output = query({
        "inputs":  articles.cleaned_text
        })
        print(output)
    except:
        return "Please put the relevant text article"

    return jsonify({"result": output[0]['summary_text']})

def sentiment_intensity_analyzer(url):
    senti=[]
    goose = Goose()
    articles = goose.extract(url)
    sentence1 = articles.cleaned_text
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores([sentence1])
    #print(sentiment_dict['neg']*100, "% Negative")
    #print(sentiment_dict['pos']*100, "% Positive")
    #print("Review Overall Analysis", end = " ") 
    if sentiment_dict['compound'] >= 0.05 :
        senti.append("Positive")
    elif sentiment_dict['compound'] <= -0.05 :
        senti.append("Negative")
    else :
        senti.append("Neutral")
    return sentiment_dict

def articleSentiment(url):

    # url = 'https://blogs.jayeshvp24.dev/dive-into-web-design'
    goose = Goose()
    articles = goose.extract(url)
    sentence = articles.cleaned_text[0:500]
    #print(sentence)
    output=query_hate({
	"inputs": str(sentence)})
    print("ARTICLE SENTIMENT",output[0])
    result = {}
    for data in output[0]:
        if data['label'] == "LABEL_0":
            result["ACCEPTABLE"] = data['score']
        elif data['label'] == "LABEL_1":
            result["INAPPROAPRIATE"] = data['score']
        elif data['label'] == "LABEL_2":
            result["OFFENSIVE"] = data['score']
        elif data['label'] == "LABEL_3":
            result["VIOLENT"] = data['score']
    labels = list(result.keys())
    values = list(result.values())

    # # Use `hole` to create a donut-like pie chart
    # fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
    # # fig.show()
    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # print(graphJSON)
    # print(type(fig))
    # return graphJSON
    return {'labels': labels, 'values': values}

def propaganda(url):
    goose = Goose()
    articles = goose.extract(url)
    output = queryprop({
	"inputs":  articles.cleaned_text[0:600]
    })
    
    yes = output[0][0]['score']
    no = 1 - yes
    return {"yes": yes, "no": no}

def auth(url):
    tlis = []
    flis = []

    # Load the pickle file into a pandas dataframe
    with open('./blacklist.pkl', 'rb') as f:
        false = pickle.load(f)

    with open('./Trusted.pkl', 'rb') as g:
        true = pickle.load(g)

    for i in range(len(false)):
        flis.append(false.loc[i, "MBFC"])

    for l in flis:
        if(l in url):
            return {"authentic":'False'}
        
    for i in range(len(true)):
        tlis.append(true.loc[i, "url"])

    for l in tlis:
        if(l in url):
            return {"authentic":'True'}

    return {"authentic":'Unknown'}

@app.route('/plotly_wordcloud/<path:url>', methods=['GET'])
def plotly_wordcloud(url):
    goose = Goose()
    articles = goose.extract(url)
    text = articles.cleaned_text
    wordcloud = WordCloud(width=1280, height=853, margin=0,
                      colormap='Blues').generate(text)
    wordcloud.to_file("./wordcloud.png")
    #plt.imshow(wordcloud, interpolation='bilinear')
    #plt.axis('off')
    #plt.margins(x=0, y=0)
    #plt.show()
    #img = BytesIO()
    #plt.savefig("./wordcloud.png", format='png')
    #plt.imsave("./wordcloud.png", format='png')
    #img.seek(0)
    #nimg = Image.frombytes("RGBA", (128, 128), img, 'raw')
    #nimg = Image.frombuffer(img)
    #nimg.save("./wordcloud.png")
    #plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    
    return send_file("./wordcloud.png", mimetype='image/png')
    #return render_template('plot.html', plot_url=plot_url)

def getNews(url):
    goose = Goose()
    article = goose.extract(url)
    output = query({
        "inputs":  f"{article.title}"})

    text = output[0]['summary_text']

    # Create a TextBlob object
    blob = TextBlob(text)

    # Get the NLTK stop words
    stop_words = set(stopwords.words('english'))

    # Extract noun phrases from the text
    noun_phrases = blob.noun_phrases
    print("Noun Phrases",noun_phrases)

    # Extract words from the text
    words = blob.words

    # Filter out stop words from the words list
    filtered_words = [word.lower() for word in words if word.lower() not in stop_words]

    # Get the word frequencies
    word_freq = {}
    for word in filtered_words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1

    # Sort the words by frequency in descending order
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

    # Extract the keywords (top 5 in this case)
    keywords = [word for word, count in sorted_words[:3]]
    print("Keywords",keywords)

    result = " && ".join(keywords)
    #print("Result",result)

    apiurl = "https://api.newscatcherapi.com/v2/search"

    querystring = {"q":f"\"{result}\"","lang":"en","sort_by":"relevancy","page":"1"}

    headers = {
        "x-api-key": "frC22glVXGlEkor-uikhOhiDI6V5DKhdHbLrKZh7Zv8"
        }

    response = requests.request("GET", apiurl, headers=headers, params=querystring)
    json_response = json.loads(response.text)
    #print("Json Response",json_response)

    if(json_response['status'] == 'No matches for your search.'):
        sleep(1)
        result = " && ".join(noun_phrases[:3])
        #print(result)
        querystring = {"q":f"{result}","lang":"en","sort_by":"relevancy","page":"1"}
        response = requests.request("GET", apiurl, headers=headers, params=querystring)
        json_response = json.loads(response.text)
        #print("Json Response",json_response)
    
    return json_response

def getTwitterData(url):
    goose = Goose()
    article = goose.extract(url)

    output = query({
        "inputs":  f"{article.title}"})

    text = output[0]['summary_text']

    # Create a TextBlob object
    blob = TextBlob(text)

    # Extract noun phrases from the text
    noun_phrases = blob.noun_phrases

    result = " ".join(noun_phrases[:2])
    
    print("TWITTER RESULT",result)

        # To set your environment variables in your terminal run the following line:
    # export 'BEARER_TOKEN'='<your_bearer_token>'
    bearer_token = 'AAAAAAAAAAAAAAAAAAAAACMalQEAAAAApH0kWTpPY9NAtZxfaWoWkih5%2B7A%3DTZ19lQr1AU33BDe5ko9nldqrAtfjeMjKXiS8BmUW6LjuQujeeS'

    search_url = "https://api.twitter.com/2/tweets/search/recent"

    # Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
    # expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
    query_params = {'query': f"{result}",
                    'tweet.fields': 'public_metrics,entities,created_at,author_id',
                    'max_results': 100}


    def bearer_oauth(r):
        """
        Method required by bearer token authentication.
        """

        r.headers["Authorization"] = f"Bearer {bearer_token}"
        r.headers["User-Agent"] = "v2RecentSearchPython"
        return r

    def connect_to_endpoint(url, params):
        response = requests.get(url, auth=bearer_oauth, params=params)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()
    
    response_json = connect_to_endpoint(search_url, query_params)

    total_likes = 0
    total_retweets = 0
    unique_hashtags = set()
    finalusername = []
    flag = False
    i=0

    for tweet in response_json['data']:
        like_count = tweet['public_metrics']['like_count']
        retweet_count = tweet['public_metrics']['retweet_count']
        entities = tweet.get('entities', {})
        hashtags = [hashtag['tag'] for hashtag in entities.get('hashtags', [])]
        total_likes += like_count
        total_retweets += retweet_count
        unique_hashtags.update(hashtags)
        i+=1

        author_id = tweet['author_id']
        includes = response_json.get('includes', {})
        users = includes.get('users', [])
        user_dict = next((user for user in users if user['id'] == author_id), None)
        if user_dict:
            username = user_dict['username']
            created_at_str = tweet['created_at']
            created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            if i > 0:
                prev_tweet = response_json['data'][i-1]
                prev_created_at_str = prev_tweet['created_at']
                prev_created_at = datetime.strptime(prev_created_at_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                time_diff = created_at - prev_created_at
                if time_diff.seconds <= 60:
                    finalusername.append(username)

        if len(finalusername) > 3:
            flag = True

    tweet_data = {"likecount":total_likes,"retweet":total_retweets,"hashtags":list(unique_hashtags),"count":i}
    
    bot_activity = {"bots":list(set(finalusername)),"flag":flag}

    print("TOTAL TWEET COUNT",i)
    
    return tweet_data,bot_activity


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        url = str(request.form['url'])
        
        # Redirect to sentiment route with url in the request body
        return redirect(url_for('prediction', url=url))
    
    return render_template("search.html")

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == "POST":
        url = request.form.get('url')
        predict = model.predict(vector.transform([url]))[0]
        rNews = getNews(url)
        print("rNews!!!!!!!!!!!!!!!!!!!!!!!!!!!!",rNews)
        #print(type(rNews))
        authenticity = auth(url)
        #if authenticity['authentic'] == 'False' or authenticity['authentic'] == 'Unknown':
            #sendMail(getEmail(url),rNews)
        
        # Redirect to sentiment route with url in the request body
        return render_template('prediction.html',
                               predict = predict,
                               authenticity=authenticity,
                               url=url,
                                rNews=rNews)
    
    return render_template("prediction.html")

@app.route('/sentiment', methods=['GET', 'POST'])
def sentiment():
    print('Reached this route!!!!!!!!!!!!!!!!!!!!!!!!')
    if request.method == "POST":
        url = request.form.get('url')
        print(url)
        article_summary = summary(url)
        article_sentiment = articleSentiment(url)
        prop = propaganda(url)
        print(prop)
        
        print(url,'text')
        print('article_summary')
        return render_template('sentiment.html', 
                               url=url, 
                               article_summary=article_summary.json['result'], 
                               article_sentiment=article_sentiment, 
                               prop=prop)
    
    return render_template("sentiment.html")

    
@app.route('/news',methods = ['GET', 'POST'])
def news():
    if request.method == "POST":
        print("Reached this route!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        url = request.form.get('url')
        rNews = request.form.get('rNews')
        #print(rNews)
        rNews = ast.literal_eval(rNews)

        #print("/news",type(rNews))
        return render_template("news.html",
                               rNews = rNews)

    return render_template("news.html")


@app.route('/twitter',methods=['GET','POST'])
def twitter():
    if request.method == "POST":
        url = request.form.get('url')
        tweet,bot = getTwitterData(url)
        sia = sentiment_intensity_analyzer(url)

        return render_template('twitter.html', 
                               tweet=tweet,
                               bot=bot,
                               sia=sia)
    
    return render_template('twitter.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
