#!/usr/bin/env python
# coding: utf-8

# In[81]:


#online sharing version for share.streamlit.io
import pandas as pd
import numpy as np
from scipy.stats import norm

#constants used apart from column names
#any function, variables with 0 or 1 suffix are to be used in conjunction
CSV0 = "csv/final_output_valuation_quantiles1.csv"
df0 = pd.read_csv(CSV0)
print("CSV0 size =", df0.shape) 

# CSV1 = "csv/final_output_valuation_all1.csv"
# df1 = pd.read_csv(CSV1)
# print("CSV1 size =", df1.shape)


# In[82]:


def init_webapp(id):
    print("ID = ",id)
    Iqr_df = df0.query("token_ids==@id")
    Iqr_list = Iqr_df.values.tolist()
    Iqr_list[0].pop(0) #drop id
    
#     Kde_df = df1.query("token_ids==@id")
#     Kde_list = Kde_df.values.tolist()
#     Kde_list[0].pop(0)

    # to infer values in CSV1 from CSV0, assume perfect normal distribution
    # The 5% and 95% quantiles are μ−1.645σ and μ+1.645σ
    q5 = Iqr_list[0][0]
    q95 = Iqr_list[0][1]
    mu = np.log(q95) - np.log(q5)
    sigma = (np.log(q95) - np.log(q5) ) / (1.645*2)
    x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)
    Kde_list = norm.pdf(x, mu, sigma)
    
    return Iqr_list[0], np.exp(Kde_list)


# In[83]:


def getRecord(id):
    init_webapp(id)


# In[84]:


def getRandomID():
    rand = df0.sample()

    return [rand['token_ids'].values[0]]


# In[85]:


if __name__ == "__main__":
    random = getRandomID()
    test1, test2 = init_webapp(random[0])

    print(test1)
    print(test2)

