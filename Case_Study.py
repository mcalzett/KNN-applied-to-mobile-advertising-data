"""
Created on Sat Jun 29 21:08:54 2019

@author: mattiacalzetta
"""

"""Data Sets:

‘Campaign Data’:
This contains the core performance data on the campaign, where each creative appeared, on which site and some basic performance metric counts.
●	Date - Day upon which the impressions were served.
●	CreativeID - Relates to the unique ID of the Creative shown (shown in 'Creative Metadata')
●	Impressions - Count of how many impressions were served. https://en.wikipedia.org/wiki/Impression_(online_media)
●	Clicks - The number of impressions where a click occurred.
●	VideoStarts - How many times the video was playing for longer than 1 second.
●	VideoCompletions - How many times the video was played to the end.
●	OperatingSystem - Mobile Operating System of the Device the Impressions were served on: iOS, Android, or Other
●	Day of Week - Numeric ID for the Weekday, 1=Monday, 7=Sunday
●	Site - The name of the specific site the creative appeared on.
●	Site Category - A high-level grouping based on the typical content on the site.


‘Creative Metadata’:
This contains additional categorical data about the Creatives that may help uncover other trends/factors.
●	CreativeID - Unique ID for the advert
●	CreativeName - Distinct title for the Creative.
●	MediaFormat - The type of media used: Static Display, or Vertical Video
●	CreativeCategory - The top-level category of the message/topic in the creative.
●	DominantColour - The dominant colour of Static Display creatives.
●	CreativeFormat - The mobile ad format the creative is placed into: MPU/Mobile Interscroller.

Note: 
●	All videos were the same length, 15 seconds.
●	Static Display creatives will have zero Video Starts/Completions.
"""

import os
import pandas as pd
from itertools import combinations
from sklearn import preprocessing
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import warnings
warnings.filterwarnings("ignore")

os.chdir("/Users/mattiacalzetta/Desktop")
camp_data=pd.read_csv("Jnr Analyst Task Data - Campaign Data.csv")
creat_data=pd.read_csv("Jnr Analyst Task Data - Creative Metadata.csv")

"""To explore the data:
    creat_data.head()
    camp_data.head()
    camp_data['CreativeID'].unique()
    etc.
"""

#to merge the two DFs
data=pd.merge(camp_data,creat_data, on='CreativeID')

#list of creative IDs. We have 70 Creative IDs - len(LIST_CREATIVE_ID)
LIST_CREATIVE_ID=data['CreativeID'].unique()

#--------------------------------------------------------------------------------------------------
#Build KPIs

#Create Click Through Rate - the % of impressions that become clicks
data['CTR']=(data.loc[:,'Clicks']/data.loc[:,'Impressions'])*100

#Create % of video started/completed per impression
data['VID_START_RATE']=(data.loc[:,'VideoStarts']/data.loc[:,'Impressions'])*100
data['VID_COMPLET_RATE']=(data.loc[:,'VideoCompletions']/data.loc[:,'Impressions'])*100

#--------------------------------------------------------------------------------------------------

"""#Create Heatmap

# Compute the correlation matrix
corr = data.corr()

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(11, 9))

# Generate a mask for the upper triangle
mask = np.zeros_like(corr, dtype=np.bool)
mask[np.triu_indices_from(mask)] = True

# Generate a custom diverging colormap
cmap = sns.diverging_palette(220, 10, as_cmap=True)


# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot=True)
"""

#--------------------------------------------------------------------------------------------------
print('QUESTION 1: What are the best performing segments in this campaign, what are the worst?')

for i in range(2):  
    print('---------------------------------------------------------------------------------------')

#Function for Weighted Average
def wavg(val_col_name, wt_col_name):
    def inner(group):
        return (group[val_col_name] * group[wt_col_name]).sum() / group[wt_col_name].sum()
    inner.__name__ = 'wtd_avg'
    return inner

LIST_CATEGORY=creat_data.columns.tolist() #MAIN SEGMENTS

ADDITIONAL_SEGMENTS=['DayofWeek','Date','OperatingSystem','Site','SiteCategory'] #LET'S ADD SOME MORE SEGMENTS

for ADDSEG in ADDITIONAL_SEGMENTS:
    LIST_CATEGORY.append(ADDSEG)

for CATEGORY in LIST_CATEGORY:
    
    PIVOT=data.groupby([CATEGORY]).apply(wavg('CTR', 'Impressions')).to_frame()
    PIVOT.columns = ['AVG CTR']
    PIVOT= PIVOT.sort_values(['AVG CTR'], ascending=False)
   
    print('For Category: "' + CATEGORY + '", please see below the 3 best/worst performing segments:')
    print('---------------------------------------------------------------------------------------')
    print(PIVOT.head(3))
    print(PIVOT.tail(3))
    for i in range(2):  
        print('---------------------------------------------------------------------------------------')


#--------------------------------------------------------------------------------------------------
#●	What are the best performing segments in this campaign, what are the worst?
print('QUESTION 2: Which combinations of segments lead to the overall highest and lowest performances?')
print('---------------------------------------------------------------------------------------')
print('To answer this question, first, let us find out what are the categories/segments that have the highest impact on the CTR. One logical way to do so is by computing the difference between the best and worst performing element for each segment. The higher the delta, the higher the chances that those features actually impact the CTR:')


DELTAS=[]

for CATEGORY in LIST_CATEGORY:

    PIVOT=data.groupby([CATEGORY]).apply(wavg('CTR', 'Impressions')).to_frame()
    PIVOT.columns = ['AVG CTR']
    DELTA=max(PIVOT['AVG CTR'])-min(PIVOT['AVG CTR'])
    DELTAS.append(DELTA)
    
DELTAS_CATEGORY=pd.DataFrame()    

DELTAS_CATEGORY['DELTA']=DELTAS
DELTAS_CATEGORY['CATEGORY']=LIST_CATEGORY
DELTAS_CATEGORY=DELTAS_CATEGORY.sort_values(['DELTA'], ascending=False)


print(DELTAS_CATEGORY)
print(' ')
print('It is clear that "Site", "CreativeName" and "Creative ID" can be deciding factors. Now let us analyze what combinations of the 3 segments are the best/worst performers.')

for i in range(2):  
        print('---------------------------------------------------------------------------------------')


comb=[]

for i in range(4):
    x=DELTAS_CATEGORY['CATEGORY'].iloc[i]
    comb.append(x)

for combo in combinations (comb, 3):
    
    PIVOT=data.groupby(combo).apply(wavg('CTR', 'Impressions')).to_frame()
    PIVOT.columns = ['AVG CTR']
    PIVOT= PIVOT.sort_values(['AVG CTR'], ascending=False)
    
    
    #The below is just to be able to convert a tuple into strings that we can print 
    combo_string=""

    for i in combo:
        x=str(i)
        combo_string=combo_string + ', ' + x
        
    combo_string=combo_string[2:]
    
    print("For Combination of Categories: " + combo_string + ", please see below the 3 best/worst performing combinations:")
    print(PIVOT.head(3))
    print(PIVOT.tail(3))
    for i in range(2):  
        print('---------------------------------------------------------------------------------------')
        
        
#--------------------------------------------------------------------------------------------------  
#●	What ideas, recommendations for future campaigns or further analysis can you make?
print('QUESTION 3: What ideas, recommendations for future campaigns or further analysis can you make?')
print('---------------------------------------------------------------------------------------')  
print('Thanks to Data Analysis, we are able to analyze the performance of different campaigns. We can see what the highest-performing sites, formats or even colors were. However, when it comes to brand new adverts/clients, “a posteriori” analyses do not yield benefits (as there is no data available). On the contrary, Data Science can help with “a priori” analyses. For example, let us apply a very popular but simple machine learning algorithm: K Nearest Neighbor (KNN). KNN has a variety of applications (e.g. face recognition) across multiple industries. In simple terms, KNN is mainly used when your task is some form of “find items similar to this one”. In this case, we are going to build a model able to find the closest CreativeID based on (1) the existing CreativeIDs and (2) the metadata (i.e. features) of the new CreativeID. The practical application of this model is the following: we want to launch a new campaign for a brand new creative. KNN will tell us what is the most similar (existing) creative. Since we know the segments where the existing creative performed the best, we know the segments we will have to focus on for the new campaign.')     
     
le = preprocessing.LabelEncoder()        
        
LIST_CATEGORY=creat_data.columns.tolist() #MAIN SEGMENTS/FEATURES
LIST_CATEGORY=LIST_CATEGORY[1:] #REMOVING "CREATIVE ID" AS IT IS ALREADY A NUMERICAL DIMENSION


#Encoding data columns in loop
creat_data_encoded=pd.DataFrame()

for i in LIST_CATEGORY:
    creat_data_encoded[i]=le.fit_transform(creat_data[i])

#creating a DF with the encoded dimensions
creat_data_encoded['CreativeID']=creat_data['CreativeID'] #Adding back the "Creative ID"

#list of features
#CreativeName_l= list(creat_data_encoded['CreativeName'])
MediaFormat_l= list(creat_data_encoded['MediaFormat'])
CreativeCategory_l= list(creat_data_encoded['CreativeCategory'])
DominantColour_l= list(creat_data_encoded['DominantColour'])
CreativeFormat_l= list(creat_data_encoded['CreativeFormat'])

features=list(zip(MediaFormat_l,CreativeCategory_l,DominantColour_l,CreativeFormat_l))

#our label, "Creative ID"
label= list(creat_data_encoded['CreativeID'])

#print('Please see below the details of the KNN model applied:')

#KNN Model
model = KNeighborsClassifier(n_neighbors=1)
model.fit(features,label)

print('Now, let us suppose that we want to launch a new campaign for a gaming creative with vertical display, MPU format and its dominant color is purple. The closest/most similar creative is indicated below:')

#Predict Output
predicted= model.predict([[1,3,1,1]]) # 1:vertical display, 3:gaming, 1:purple, 1:MPU
predicted =predicted[0] #to get the first value of the 1-value array that is the prediction

print('')
print(predicted)
print('')
print('Now, let us see where creative ' + str(predicted) + ' performed the best:')

best_perf= data[data['CreativeID']==predicted]
best_perf.sort_values(['CTR'], ascending=False)


print(best_perf.head(5))
