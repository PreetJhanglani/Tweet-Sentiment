import sys

from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import pickle
import clean
import Get_clean_tweets
from wordcloud import WordCloud,ImageColorGenerator
from PIL import Image
import urllib
import matplotlib
matplotlib.use('Agg')

import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import os, io, base64


pipeline = pickle.load(open('ridge_pipeline.model', 'rb'))


def clean_tweet(x):
    hshtg = clean.GetHshtg(str(x))
    twt = clean.RmUrl(x)
    twt = clean.RmHshtg(str(twt))
    twt = clean.RmRt(str(twt))
    twt = clean.RmAt(str(twt))
    twt = clean.RmNum(str(twt))
    twt = clean.RmScP(str(twt))
    # print ("The hashtags in tweet are{hshtg}. \n The clean tweet is: {twt}.".format(hshtg = hshtg[0], twt = str(twt)))
    return twt, hshtg;
    
def plot(cv, sub):
    x1 , y1 = [0,1],[0,0]
    plt.bar( 0.2, cv, color = 'r', width = 0.2, label = 'Compound Value')
    plt.bar( 0.4,sub, color = 'b', width = 0.2, label = 'Subjectivity')
    plt.plot(x1,y1, color = 'black')
    plt.ylim(-1,1)
    plt.xlim(0,1)
    plt.ylabel("Value")
    plt.grid()
    plt.legend(loc = "upper right")
    pngImage = io.BytesIO()
    FigureCanvas(plt.gcf()).print_png(pngImage)
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
    plt.clf()
    return pngImageB64String
    # return plt.show()
    # plt.savefig("templates/plot/new_plot.png")

def word_cloud(all_words_sent, color_map):
    # combining the image with the dataset
    Mask = np.array(Image.open(requests.get('http://clipart-library.com/image_gallery2/Twitter-PNG-Image.png', stream=True).raw))
    # We use the ImageColorGenerator library from Wordcloud 
    # Here we take the color of the image and impose it over our wordcloud
    image_colors = ImageColorGenerator(Mask)
    # Now we use the WordCloud function from the wordcloud library 
    wc = WordCloud(background_color= 'black', height= 1500, width= 4000, mask= Mask, colormap= color_map).generate(all_words_sent)
    # Size of the image generated 
    plt.figure(figsize=(8,8))
    # Here we recolor the words from the dataset to the image's color
    # recolor just recolors the default colors to the image's blue color
    # interpolation is used to smooth the image generated 
    plt.imshow(wc, interpolation= "kaiser")
    plt.axis('off')
    pngImage = io.BytesIO()
    FigureCanvas(plt.gcf()).print_png(pngImage)
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
    plt.clf()
    return pngImageB64String



app = Flask(__name__)
pic_folder = os.path.join('templates','plot')
app.config['UPLOAD_FOLDER'] = pic_folder

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/', methods = ['POST', 'GET'])
def get_data():
    if request.method == 'POST':
        keyword = request.form['keyword']
        count = request.form['count']

        # return redirect(url_for('success', x = text))
# @app.route('/<x>', methods = ['GET'])
# def success(x):
    x = str(keyword) 
    c = int(count)
    pic = os.path.join(app.config['UPLOAD_FOLDER'], 'new_plot.png')
    df,hsh = Get_clean_tweets.inputq(x,c)
    new_hsh = "The Hastags in the given tweets are:- "
    for i in hsh:
        if i != []:
            for j in i:
                new_hsh = new_hsh + j + ", "

    predict = pipeline.predict(df['cleaned_text'])
    cvl = []
    subl = []
    poll = []
    cv = 0
    pol = 0
    sub = 0
    for i in range(len(predict)):
        cvl.append(predict[i][0])
        poll.append(predict[i][1])
        subl.append(predict[i][2])
        cv += predict[i][0]
        pol += predict[i][1]
        sub += predict[i][2]
    cv = cv / (len(predict))
    sub = sub / (len(predict))
    pol = pol / (len(predict))
    plotgraph = plot(cv, sub)
    if cv >= 0.05:
        sent = "Positive"
    elif (cv > -0.05) and (cv < 0.05):
        sent = "Neutral"
    elif cv <= -0.05:
        sent = "Negative"
    # return "<img src= Static/img/new_plot.png>"
    df['cv'] = cvl
    cv_color = '#111'
    if sent == "Positive":
        all_words_positive = ' '.join(text for text in df['cleaned_text'][df['cv']>=0.05])
        cv_color = '#005220'
        cv_colo = '#005220'
        wc = word_cloud(all_words_positive , 'Greens_r')
    elif sent == "Negative":
        cv_color = '#E12D25'
        all_words_negative = ' '.join(text for text in df['cleaned_text'][df['cv']<=(-0.05)])
        wc = word_cloud(all_words_negative, 'Reds')
    elif sent == "Neutral":
        cv_color = '#074589'
        all_words_neutral = ' '.join(text for text in df['cleaned_text'][(df['cv'] < (0.05)) & (df['cv'] > (-0.05))])
        wc = word_cloud(all_words_neutral, 'Blues')
    txt = df['text']
    txt = '<table><thead><tr><th scope="col">Sr No.</th><th scope="col">Tweets</th></tr></thead><tbody>'
    c =1
    for i in df['text']:
        txt = txt + '<tr><td data-label="Sr No">'+ str(c) +'</td><td data-label="Due Date">'+i+'</td></tr>'
        c=c+1
    txt = txt + '</tbody></table>'
    # txt = pd.DataFrame(df['text'])
    return render_template('home.html', hashtag = '<h2 style=" text-align: center; color:#111;">Hashtags</h2> &emsp;<p style="text-align:center;">{hsh}</p><br>'.format(hsh = new_hsh),text = '<h2  style=" text-align: center; color:#111;">Tweets</h2> &emsp;<br>',  table = txt, sentiment = '<h3 style=" text-align: center;">The Overall Sentiment is: &emsp;{sent}</h3>'.format(sent = sent), val = '<h3  style=" text-align: center;">The Predicted Compound value is: &emsp;<span style="color: {cv_color}">{cv}</span></h3><h3  style=" text-align: center;">The Predicted Polarity is:  <span style="color: {cv_color}">{pol}</span></h3><h3  style=" text-align: center;">The Predicted Subjectivity is: &emsp;<span style="color: {cv_color}">{sub}</span></h3>'.format( cv = cv, pol = pol, sub = sub, cv_color = cv_color), Bar = '<b>BAR PLOT</b>',  plot = plotgraph, word_cloud = '<b>WORD CLOUD</b>', wc = wc)
# @app.route("/", methods=["GET"])
'''<h3>The tweets are:</h3> &emsp;{text}<br>'.format(text ='''
# def plotView():

#     # Generate plot
#     fig = Figure()
#     axis = fig.add_subplot(1, 1, 1)
#     axis.set_title("title")
#     axis.set_xlabel("x-axis")
#     axis.set_ylabel("y-axis")
#     axis.grid()
#     axis.plot(range(5), range(5), "ro-")
    
#     # Convert plot to PNG image
#     pngImage = io.BytesIO()
#     FigureCanvas(fig).print_png(pngImage)
    
#     # Encode PNG image to base64 string
#     pngImageB64String = "data:image/png;base64,"
#     pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
    
#     return render_template("test.html", image=pngImageB64String)

if __name__ == '__main__' :
    app.run(debug=True)