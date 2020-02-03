from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    imdb = soup.find('div', attrs={'class':'lister list detail sub-list'}) 
    film = imdb.find_all('div', attrs={'class':'lister-item-content'})

    temp = [] #initiating a tuple
    
    for i in range(0, len(film)):
        film = imdb.find_all('div', attrs={'class':'lister-item-content'})[i]
        
        #get title
        title = film.find_all('h3')[0].find_all('a')[0].text
        title = title.strip() #for removing the excess whitespace 
        
        #get rating
        rating = film.find_all('strong')[0].text
        rating = rating.strip() #for removing the excess whitespace
        
        #get metascore
        try: metascore =  film.find_all('div','inline-block ratings-metascore')[0].find_all('span')[0].text.strip()
        except IndexError: metascore = 0
        
        #get rating
        vote = film.find_all('p', 'sort-num_votes-visible')[0].find_all('span')[1].text
        vote = vote.strip() #for removing the excess whitespace
        
        temp.append((title, rating, metascore, vote))
    
    temp
    
    datafilm = pd.DataFrame(temp, columns = ('title', 'rating', 'metascore', 'vote')).set_index('title') #creating the dataframe
    #data wranggling -  try to change the data type to right data type
    datafilm['vote'] = datafilm['vote'].str.replace(",", "")
    datafilm[['rating', 'metascore', 'vote']] = datafilm[['rating', 'metascore', 'vote']].astype('float64')
    datafilm = datafilm.sort_values('vote').tail(7)
    datafilm = datafilm[['vote']].sort_values('vote')
    #end of data wranggling             

    return datafilm

@app.route("/")
def index():
    df = scrap('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.plot(kind='barh')
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
