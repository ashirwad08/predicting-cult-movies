from bs4 import BeautifulSoup
import pandas as pd
import re
from pprint import pprint


#==============================================================================
#not run
def scrape_wiki_movies(urlConst = 'https://en.wikipedia.org/wiki/List_of_American_films_of_', yr_lb = 1970, yr_ub = 2012):
  """for a list of given URL structures of years, get their corresponding wiki pages that contain movie lists for that year; return a dictionary with year as key and soup object of wiki pages as values"""
  
  #get pages
  urlList = [urlConst+str(i) for i in range(yr_lb, yr_ub+1)]
  soupObjects={}
  
  for url in urlList:
    try:
        resp = requests.get(url)
        soupObjects[str(re.search('\d+$',url).group())] = BeautifulSoup(resp.text,'lxml')
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
  
  #soupObjects is a dictionary of "<year>":"beautifulSoup object" (of wiki page that has movie list for that year)
  return soupObjects



#==============================================================================
#not run
def get_wiki_movieList(soupObjects, yr_lb=1970,ur_ub=2012):

  """use BeautifulSoup to parse a dictionary of Soup pages and return a pandas dataframe of movie title, director, cast, genre, studios, releaseDate, releaseYear"""
  
  #parse these pages into a pandas df
  
  title=pd.Series([],name='title')
  director=pd.Series([],name='director')
  cast=pd.Series([],name='cast')
  genre=pd.Series([],name='genre')
  studios=pd.Series([],name='studios')
  releaseDate=pd.Series([],name='releaseDate')
  releaseYear=pd.Series([],name='releaseYear')
  
  yearRange = [str(i) for i in range(yr_lb,yr_ub+1)]
  
  
  for year in yearRange:
    for table in soupObjects[year].find_all(class_='wikitable'):
      for row in table.find_all('tr'):
        r = row.find_all('td')
        if not(r):
          continue
            
        try:
          title=title.append(pd.Series(r[0].text))
        except IndexError:
          title=title.append(pd.Series('NA'))

        try:
          director=director.append(pd.Series(r[1].text))
        except IndexError:
          director=director.append(pd.Series('NA'))

        try:
          cast=cast.append(pd.Series(r[2].text))
        except IndexError:
          cast=cast.append(pd.Series('NA'))

        try:
          genre=genre.append(pd.Series(r[3].text))
        except IndexError:
          genre=genre.append(pd.Series('NA'))

        try:
          studios=studios.append(pd.Series(r[4].text))
        except IndexError:
          studios=studios.append(pd.Series('NA'))

        try:
          releaseDate=releaseDate.append(pd.Series(r[5].text))
        except IndexError:
          releaseDate=releaseDate.append(pd.Series('NA'))
        
        releaseYear=releaseYear.append(year)
  
  #concat all these series into a df
  dat = pd.concat([title,director,cast,genre,studios,releaseDate,releaseYear], axis=1)
  dat.columns = ['title','director','cast','genre','studios','releaseDate','releaseYear']
  dat.index = dat['title']
  
  return dat



  
  
  

