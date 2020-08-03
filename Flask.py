from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import pickle
import clean
import Get_clean_tweets
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
    predict = pipeline.predict(df['cleaned_text'])
    cv = 0
    sub = 0
    pol = 0
    for i in range(len(predict)):
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
    txt = pd.DataFrame(df[['text','cleaned_text']])
    return render_template('home.html', hashtag = '<h3>The hashtags in tweet are:</h3> &emsp;<b>{hsh}</b><br>'.format(hsh = hsh),text = '<h3>The tweets are:</h3> &emsp;<br>',  tables = [txt.to_html(classes = 'data', header = "true", justify = "center")], sentiment = '<h3>The Overall Sentiment is: &emsp;{sent}</h3>'.format(sent = sent), val = '<h3>The Predicted Compound value is: &emsp;{cv}</h3><h3>The Predicted Polarity is: &emsp;{pol}</h3><h3>The Predicted Subjectivity is: &emsp;{sub}</h3>'.format( cv = cv, pol = pol, sub = sub), Bar = 'BAR PLOT',  plot = plotgraph)
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