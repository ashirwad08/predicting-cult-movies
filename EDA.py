import pandas as pd
import numpy as np

def movie_clean_df(dat):
  """takes in a data frame of movies and scraped data points, then performs cleaning steps to create a data frame that's ready for EDA for objective: Analyze cult movie phenomenon. Returns ready data frame."""
  
  #Step 1: subset data frame. 
  # let's only use the data points for which BOMOJO returned matches
  dat_eda = dat.loc[dat.rev_totalGross.notnull(),:]
  # or just read in latest pickle!
  with open(r"Movie_DF_latest_apr24_10pm.p", "rb") as input_file:
    dat_eda = pickle.load(input_file)
  
  
  
  #Steps 1.x: Adjust revenue numbers for inflation!
  ##ADJUST for inflation the following columns: rev_totalGross, adjusted by CPI; rev_opening adjusted by BOMOJO ticket sales;
# prod_budget, adjusted by CPI; recalculate rev_postOpening!
  
  #read in BOMOJO ticket sales adjuster by year
  bomojo_adj = pd.read_csv('./bomojo_ticket_price_adjuster.csv',header=0)
  bomojo_adj.columns=bomojo_adj.columns.str.replace('\.\s','')
  #bomojo_adj.Year = bomojo_adj.Year.astype('str')
  bomojo_adj.AvgPrice = bomojo_adj.AvgPrice.str.replace('$','').astype('float')
  #bomojo_adj.Year = bomojo_adj.Year.astype('int')
  bomojo_adj.head()
  
  cpi = pd.read_csv("./cpi_by_year.csv", header=0)
  cpi.columns=cpi.columns.str.replace('\.\s','')
  cpi['CPI']=cpi.CPI.astype('float')
  cpi['year']=cpi.year.astype('int')
  
  
  mov['releaseYear'] = mov.releaseDate.apply(lambda val: val.year)
  
  mov['rev_opening_ADJ'] = (mov.rev_opening/mov.AvgPrice)*8.58
  
  mov['rev_totalGross'] = (mov.rev_totalGross/mov.AvgPrice)*8.58
  
  mov['prod_budget_ADJ'] = (mov.prod_budget/mov.CPI) * 238 #2016 CPI

  
  
  #step 2: Create post_opening_rev feature
  #This is intended to be the revenue difference ebtween opening weekend and lifetime gross.

  #dat_eda['rev_postOpening'] = dat_eda.apply(lambda row: row.rev_totalGross - row.rev_opening, axis=1)
  mov['rev_postOpening'] = mov.rev_totalGross_ADJ - mov.rev_opening_ADJ 
  
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
  cultlist = pd.read_csv('/Users/ash/Downloads/cult movie list.csv', header=0)
  cultlist = cultdf.set_index('title')
  mov = mov.merge(cultlist, how='left')
  
  
  
  #done with cleaning!!!!!!
  return dat_eda
  



#==============================================================================
#not run

def movie_eda(mov):
  """Exploratory steps and manipulations on the movie dataset before training. Returns a final, 
  training and test datasets"""
  
  #IMPUTE MISSING VALUES
  ##rev_totalGross_ADJ has only 10 missing datapoints, whack years! delete
  mov.rev_totalGross_ADJ.dropna(inplace=True) #IMPUTE (delete in this case, all gross revs missing)
  
  
  
  #Next, we'll look at rev_opening_ADJ
#first, impute by mean revenue of distributor and genre for that year,
  mov['rev_opening_ADJ'].fillna(mov.groupby(['year','distributor','genre_bomojo'])['rev_opening_ADJ'].transform('mean'), inplace=True)

#only catches a few because of the year constraint, now impute based on distributor and genre
  mov['rev_opening_ADJ'].fillna(mov.groupby(['distributor','genre_bomojo'])['rev_opening_ADJ'].transform('mean'), inplace=True)
#fills about a 2/3rds of Nas, drop the rest...

  mov['rev_opening_ADJ'].dropna(inplace=True)
  
  #Okay, next! prod_budget. There are 3610 missing values!!! Sensitive to imputing, but this could also be an important feature. Let's try the strategy we tried uptop.
  mov.prod_budget_ADJ[mov.prod_budget_ADJ==0]=np.nan
  mov.prod_budget_ADJ.fillna(mov.groupby(['year','distributor','genre_bomojo'])['prod_budget_ADJ'].transform('mean'), inplace=True)
  mov.prod_budget_ADJ.fillna(mov.groupby(['distributor','genre_bomojo'])['prod_budget_ADJ'].transform('median'), inplace=True)
  #these cut down nans to more than half. will drop the rest, too much noise at just the distributor level... fuck it ill try that
  mov.prod_budget_ADJ.fillna(mov.groupby(['distributor'])['prod_budget_ADJ'].transform('median'), inplace=True)
  # okay, down to 371 missing values. Imputed 90% of them! drop the rest
  mov.prod_budget_ADJ.dropna(inplace=True)
  
  
 
  
  
  
  
  # REMOVE OUTLIERS!!!!
  #look at hist. kernel density: 
  plt.figure(figsize=(20,10))
  sns.distplot(mov.rev_opening_ADJ, rug=True)
  
  
  
  
  
  
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
  
  
  
  


  





  
