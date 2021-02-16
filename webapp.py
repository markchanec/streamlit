#!/usr/bin/env python
# coding: utf-8

# In[34]:


import streamlit as st
import dbBroker1 as DB #use dbBroker for production
import requests
import plotly.figure_factory as ff
import numpy as np
#under the hood of ff, not auto included in streamlit sharing
#import so that pipreqsnb can pick up
import scipy 

#Initial record
INIT_ID = 82267


# In[35]:


#run next line if re-creating fresh schema in MySQL so that streamlit can use the latest data
#alternative is use main in dbBroker
# exec(open("dbBroker.py").read())

#otherwise we'll be using it as micro service to read data for the web app
# test = dbBroker.test_service("Test micro service: Success!")
# print(test)


# In[36]:


st.sidebar.title("Axie Infinity Valuation")
st.sidebar.header("Virtual market prices")
selected = st.sidebar.selectbox("Display prices in", ["ETH","USD"])
slot = st.sidebar.empty()
buttonID = st.sidebar.button("Random Token ID", key="RID")


# In[37]:


if buttonID:
    randomID = DB.getRandomID()
    tokenID = slot.number_input("Enter a number", value = randomID[0], key="ID") 
else:
    tokenID = slot.number_input("Enter a number", value = INIT_ID, key="ID")


# In[38]:


# import SessionState

# ss = SessionState.get(x=1)
# if st.button("Increment x"):
#     ss.x = ss.x + 1
#     st.text(ss.x)


# In[46]:


print("ID =", tokenID)
Iqr, Kde = DB.init_webapp(tokenID)
print("Record IQR =", Iqr)
print("Record KDE =", Kde)


# In[40]:


token_address = '<a href="https://opensea.io/assets/0xF5b0A3eFB8e8E4c201e2A935F110eAaF3FFEcb8d/' + str(tokenID) + '" target="_blank">[Token Description]</a>' 

st.sidebar.write(token_address, unsafe_allow_html = True)
st.sidebar.write(
    """<a href="https://www.virtualmarkets.org/post/find-the-value-of-non-fungible-tokens-automatically-and-in-real-time-with-machine-learning" target="_blank">[About this project]</a>""",
    unsafe_allow_html = True
)


# In[41]:


def getUSD():
    req = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd')
    usd = req.json()
    print("ETH/USD = ", usd["ethereum"]["usd"])
    return usd["ethereum"]["usd"]


# In[42]:


def drawKDE(data, LB, UB):
#     fig = ff.create_distplot([data], ['KDE curve'], colors=["darkred"], show_hist=False, show_rug=False)
#     fig.add_shape(type="line",
#         yref= 'paper', y0= 0, y1= 1,
#         xref= 'x', x0= LB, x1= LB,
#         opacity=0.7, line=dict(color="green",width=3)
#     )
#     fig.add_shape(type="line",
#         yref= 'paper', y0= 0, y1= 1,
#         xref= 'x', x0= UB, x1= UB,
#         opacity=0.7, line=dict(color="green",width=3)
#     )
    import plotly.graph_objs as go
    from plotly.subplots import make_subplots

    trace1 = go.Indicator(mode="gauge+number", value=LB, domain={'row' : 1, 'column' : 1}, title={'text': "5% quantile"})
    trace2 = go.Indicator(mode="gauge+number", value=Kde, domain={'row' : 1, 'column' : 1}, title={'text': "median"})
    trace3 = go.Indicator(mode="gauge+number", value=UB, domain={'row' : 1, 'column' : 2}, title={'text': "95% quantile"})

    fig = make_subplots(
        rows=1,
        cols=3,
        specs=[[{'type' : 'indicator'}, {'type' : 'indicator'}, {'type' : 'indicator'}]],
        )

    fig.append_trace(trace1, row=1, col=1)
    fig.append_trace(trace2, row=1, col=2)
    fig.append_trace(trace3, row=1, col=3)

    st.plotly_chart(fig, use_container_width=True)


# In[43]:


data = np.asarray(Kde)
lowerBound = Iqr[0]
upperBound = Iqr[1]

if selected == "ETH":
    st.subheader("Valuation Range: {0:.4f} to {1:.4f} ".format(Iqr[0], Iqr[1]) + selected)
    drawKDE(data, lowerBound, upperBound)
else:
    exchange = getUSD()
    st.subheader("Valuation Range: {0:.2f} to {1:.2f} ".format(Iqr[0]*exchange, Iqr[1]*exchange) + selected)
    
    data = data * exchange
    lowerBound = Iqr[0] * exchange
    upperBound = Iqr[1] * exchange
    drawKDE(data, lowerBound, upperBound)


# In[44]:


st.write(
        """Notes: This plot produces a valuation range for the entered token ID and shows the distribution of possible valuations with their likelihood represented by the shaded density.
        Use it to value any token and assess if a token on sale is listed for a reasonable price.
        The range is a 90% confidence interval.
        The token ID can be found as the string after the last '/' on the asset's page on OpenSea or the Axie Marketplace.
        Valuations are generated from multiple machine learning models trained on historical transaction data, incorporating token metadata, cryptocurrency exchange rates, and overall market trends.
        This app is for informational purposes only and does not constitute financial advice. Last Update: Nov. 18, 2020 
        """
)

