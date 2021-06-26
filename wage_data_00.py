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
#import numpy as np
import pandas as pd
# data from 2008-2020
#df=pd.read_csv(r"C:\Users\sxiao\OneDrive - Indiana University\FromBox\0CurrentResearch\wage_emp_data\cps_00026.csv")
# data from 1982-2020
df=pd.read_csv(r"C:\Users\sxiao\OneDrive - Indiana University\FromBox\0CurrentResearch\wage_emp_data\cps_00030.csv")
cpi=pd.read_csv(r"C:\Users\sxiao\OneDrive - Indiana University\FromBox\0CurrentResearch\wage_emp_data\CPI99.csv")
#print(df.head(10))

#%%
#keep only the observations eligible for earner study
# UNIVERSE for 'ELIGORG'
#1983+: Employed persons who are in outgoing rotation groups.
#1982: Employed persons.
df=df[df['ELIGORG']==1]# save a raw copy
df=df[1987<df['YEAR']>=1989]# data starts from year 1989
#%%
# Missing values
# missing_data=df.isnull()
# for column in missing_data.columns:
#     print(column)
#     print(missing_data[column].value_counts())
#     print("")  
#hourwage and earnweek are not available in march 2021
# remove the data with missing hourwage
df=df.dropna()
#%%
#keep only civilians age 15 and older who are currently employed as a wage or salaried worker (that is, not self-employed).af
df=df.drop(df[df['EARNWEEK']==9999.99].index)# need the index to drop these rows
#%%
# we will use AHRSWORKT to get the hourly wage for non-hourly workers 
# since it is available from 1989, while UHRSWORKORG is only available after 1994
# firt drop the NIU for AHRSWORKT
# universe: 1989+: Civilians age 15+, at work last week.
df=df.drop((df[df['AHRSWORKT']==999].index)&(df[df['PAIDHOUR']==1].index))# non-hourly workers who are not at work last week

#%%
# Convert to 1999/2000 dollars (https://cps.ipums.org/cps/cpi99.shtml)
# merge dataframe
df = pd.merge(df, cpi, how='left', on='YEAR')

#%% 
#save the current dataframe
df.to_pickle("./wage_data.pkl")
