import pandas as pd
import numpy as np

def movie_clean_df(dat):
  """takes in a data frame of movies and scraped data points, then performs cleaning steps to create a data frame that's ready for EDA for objective: Analyze cult movie phenomenon. Returns ready data frame."""
  
  #Step 1: subset data frame. 
  # let's only use the data points for which BOMOJO returned matches
  dat_eda = dat.loc[dat.rev_totalGross.notnull(),:]
  
  #step 2: Create post_opening_rev feature
  #This is intended to be the revenue difference ebtween opening weekend and lifetime gross.

  
  dat_eda['rev_postOpening'] = dat_eda.apply(lambda row: row.rev_totalGross - row.rev_opening, axis=1)
  
  # Step 3: Coerce date entries
  dat_eda.releaseDate=pd.to_datetime(dat_eda.releaseDate, errors='coerce')
  
 # Step 4: Categorize columns director, genre, distributor, genre_bomojo, rating
dat_eda=pd.concat([ dat_eda[['director','cast','genre','studios','distributor','genre_bomojo','rating']].apply(lambda col: col.astype('category'), axis=0),
          dat_eda[['title','releaseDate','canontitle','rev_totalGross','rev_opening','num_theaters','runtime','prod_budget','rev_postOpening']] ], 
                  axis=1)
  
  # Step 5: Extract leading cast member
  dat_eda['leadActor']=dat_eda.cast.apply(lambda val: re.split(r',',val)[0]).astype('category')

 
  # Step 6: Remove wiki's "studio". use "distributor" as studio??
  # both "genre" and "genre_bomojo" suck! bmojo is better
  dat_eda.drop(['studios','cast','genre'], axis=1, inplace=True)
  
  
  # Step 7: convert "runtime" to minutes field
  dat_eda['runtime']=dat_eda.runtime.str.replace('N/A','0', case=False)
  dat_eda['runtime_mins']=(dat_eda.runtime.str.split(' ').str.get(0).astype('float'))*60 + (dat_eda.runtime.str.split(' ').str.get(2).astype('float'))

  
  # step 9: convert production budget to numeric, subout "million" word
  dat_eda['prod_budget']=dat_eda.prod_budget.str.replace('million','000000',case=False)
  dat_eda['prod_budget']=dat_eda.prod_budget.str.replace('N/A|NA','0',case=False)
  dat_eda['prod_budget']=dat_eda.prod_budget.astype('float')
  
  
  # step 10: read in a separate list of cult movies, merge on canonical names and label new
  cultdf = pd.read_csv('/Users/ash/Downloads/cult movie list.csv', header=0)
  cultdf = cultdf.set_index('title')
  
  
  
  
  #done with cleaning!!!!!!
  return dat_eda
  



#==============================================================================
#not run

def movie_eda(mov):
  """Exploratory steps and manipulations on the movie dataset before training. Returns a final, 
  training and test datasets"""
  
  
  # TO DO!!! ADJUST REVENUE NUMBERS OVER TIME!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  
  
  #MAIN HYPOTHESIS: The CULTINDEX is a somewhat significant gauge of a movie's cult status
  #Ideally, it takes into account post release variables
  
  #Cult Index Calculation - v0
  
  ##Penalize index for higher production budget (reward for lower): CI = constant * 1/prod_budget
  ##Penalize index heavily for high opening weekend (adhering to the "exclusive" definition of cult movies: CI = constant * 1/(rev_opening)^2 (consider polynomial in v0.1)
  ##Penalize index for higher number of opening theaters (reward for lower): CI = constant * 1/num_theaters
  ##Reward index somewhat for high post opening lifetime gross revenue, this is rev_postOpening as a fraction of the opening revenue; I want to reward the index if fraction gets very large: CI = constant * exp(rev_postOpening/rev_opening)
  
  #Cult Index v0 = [exp(rev_postOpening/rev_opening)] / [prod_budget * rev_opening^2 * num_theaters], scaled to 0:1
  
  mov['rev_fraction'] = mov.rev_postOpening/mov.rev_opening
  mov.ix[mov.prod_budget==0,'prod_budget'] = np.nan
  
  mov['CULT_INDEX'] = (mov.rev_postOpening**2)/((mov.prod_budget**4) * (mov.rev_opening**2) * mov.num_theaters**2)
  
  
  
  





  
