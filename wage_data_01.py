# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 10:06:04 2021

@author: sxiao
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np
import pandas as pd
# data from 2008-2020
#df=pd.read_csv(r"C:\Users\sxiao\OneDrive - Indiana University\FromBox\0CurrentResearch\wage_emp_data\cps_00026.csv")
# data from 1989-2020
df=pd.read_pickle(r"C:\Users\sxiao\OneDrive - Indiana University\FromBox\0CurrentResearch\spyder\wage_data_1989.pkl")

#%%
# Below I tried to compute the 1/35 quantile with only top-coded weekly earnings.

# hourly wages exceeding 1/35th the top-coded value of weekly earnings will be dropped
# first let us get the 1/35 thershhold
# Top codes:
#1982-1988: 999 (Weekly earnings of $999 or more).
#1989-1997: 1923 (Weekly earnings of $1923 or more).
#1998-onward: 2884.61 for non-ASEC samples.
# Follow Autor (2010), we will times the top coded weekly earning by 1.5
df['TEMP']=df['EARNWEEK']*df['CPI']*1.5/df['AHRSWORKT']# use earning in 2000 dollars
def get_pct(df):
    if (df['EARNWEEK'] ==  2884.61)&(df['PAIDHOUR'] ==1): #some 'PAIDHOUR'==2 and 'EARNWEEK'==  2884.61 are not top coded 
        return df['TEMP']
    else:
        return np.nan

df['PCT'] = df.apply(get_pct, axis = 1)

# need to change it 1982 dollars first
df_pct=df['PCT'].dropna()

a=np.percentile(df_pct, 1/35)# if do not adjust in 2000 dollars, it returns 36.057625
# if adjusted in 2000 dollars, it returns 24.48 for years 2008-2020
# returns 28.43 for data from 1989-2020
#%%
df['temp_top_0']=np.around(1923/df['UHRSWORKORG'],decimals=2)
df['temp_top_1']=np.around(2884.61/df['UHRSWORKORG'],decimals=2)
# Construct the topp coding indicator for the hourly workers
def get_i(df):
    if (df['YEAR']<=2002)&(df['UHRSWORKORG']>=20)&(df['HOURWAGE']==df['temp_top_0']):
        return 1
    if (df['YEAR']>2002)&(df['UHRSWORKORG']>=29)&(df['HOURWAGE']==df['temp_top_1']):
        return 1
    #elif (df['UHRSWORKORG']<29)&(df['HOURWAGE']==99.99):
    elif df['HOURWAGE']==99.99:
        return 1
    else: 
        return 0
df['TOPHWAGE']=df.apply(get_i,axis=1)
df=df.sort_values(by=['TOPHWAGE'], ascending=False)
df=df.sort_values(by=['PAIDHOUR','HOURWAGE'], ascending=False)

#%%
def get_wage(df):
    if (df['PAIDHOUR']==2)&(df['TOPHWAGE']==1):# paid hourly and top coded
        return df['HOURWAGE']*1.5*df['CPI']
    elif (df['PAIDHOUR']==2)&(df['TOPHWAGE']==0):# paid hourly and not top coded
        return df['HOURWAGE']*df['CPI']
    elif (df['PAIDHOUR']==1)&(df['EARNWEEK']==2884.61):# not paid hourly and top coded after 1998
        return df['TEMP']
    elif (df['PAIDHOUR']==1)&(df['EARNWEEK']==1923):# not paid hourly and top coded for year before 1998
        return df['TEMP']
    elif (df['PAIDHOUR']==1)&(df['EARNWEEK']!=2884.61)&(df['EARNWEEK']!=1923):# not paid hourly and not top coded
        return df['EARNWEEK']*df['CPI']/df['AHRSWORKT']
df['WAGE']=df.apply(get_wage,axis=1)   
# Missing values
missing_data=df['WAGE'].isnull()
missing_data.value_counts()
#%%
# Folowing Autor(2008),
# Top-coded earnings observations are multiplied by 1.5. Hourly earners
# of below $1.675/hour in 1982 dollars ($2.80/hour in 2000 dollars) are dropped, 
# as are hourly wages exceeding 1/35th the top-coded value of weekly earnings. 
df=df[(df['WAGE']>2.80)&(df['WAGE']<28.43)]
#fff=df[['YEAR','MONTH','WTFINL','WAGE','AHRSWORKT','EARNWT','HOURWAGE', 'PAIDHOUR', 'EARNWEEK', 'UHRSWORKORG']]
# if only want to keep the least variables
dff=df[['YEAR','MONTH','WTFINL','WAGE']]
#%%
dfg=dff.groupby(['YEAR','MONTH'],as_index=False)
# use transform to transform the data directly
dff['SHARE']=dfg['WTFINL'].transform(lambda x:x/x.sum()*100 )
grouped = dff.groupby(['YEAR', 'MONTH','WAGE'], as_index=False)
gdf=grouped.aggregate(np.sum)# employment share of same wage are summed
#%%
gdf['CAT']=pd.cut(gdf['WAGE'], [2,4,5,6, 7,8, 9,10, 11,12, 13,14, 15,16, 17,18,19,20,21,22,23,24,25,26,27,29])
grouped = gdf.groupby(by=['YEAR','MONTH','CAT'], as_index=False)
gdf=grouped['SHARE'].aggregate(np.sum)# employment share of same wage are summed

gdf['DATE']=pd.to_datetime(gdf['YEAR'].astype(str)+gdf['MONTH'].astype(str), format='%Y%m')
gdf=gdf[['DATE','CAT','SHARE']]
#%%
df_done=gdf.pivot(index='DATE',columns='CAT',values='SHARE')
# #%%
# import matplotlib.pyplot as plt
# # time series plot
# plt.plot(df_done)
# %%
df_done.to_csv('data1989.csv')
