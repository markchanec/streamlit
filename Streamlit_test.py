#!/usr/bin/env python
# coding: utf-8

# In[57]:


import streamlit as st
import plotly.figure_factory as ff
import numpy as np


# In[26]:


st.sidebar.title("Axie Infinity Valuation")
st.sidebar.header("Virtual market prices")
selected = st.sidebar.selectbox("Display prices in", ["ETH","USD"])
tokenID = st.sidebar.number_input("Enter a number", value=82267)
st.sidebar.button("Random Token ID")
st.sidebar.write(
        """<a href="https://www.google.com">[Token Description]</a>""",
        unsafe_allow_html = True
)
st.sidebar.write(
        """<a href="https://www.insead.edu">[About this project]</a>""",
        unsafe_allow_html = True
)


# In[27]:


st.subheader("Valuation Range: xx to xx " + selected)


# In[71]:


np.random.seed(1)
fig = ff.create_distplot([np.random.randn(1000)], ['KDE curve'], colors=["darkred"], show_hist=False, show_rug=False)

fig.add_shape(type="line",
    yref= 'paper', y0= 0, y1= 1,
    xref= 'x', x0= -2, x1= -2,
    opacity=0.7, line=dict(color="darkred",width=3)
)

fig.add_shape(type="line",
    yref= 'paper', y0= 0, y1= 1,
    xref= 'x', x0= 2, x1= 2,
    opacity=0.7, line=dict(color="darkred",width=3)
)

st.plotly_chart(fig, use_container_width=True)


# In[29]:


st.write(
        """Notes: This plot produces a valuation range for the entered token ID and shows the distribution of possible valuations with their likelihood represented by the shaded density.
        Use it to value any token and assess if a token on sale is listed for a reasonable price.
        The range is a 90% confidence interval.
        The token ID can be found as the string after the last '/' on the asset's page on OpenSea or the Axie Marketplace.
        Valuations are generated from multiple machine learning models trained on historical transaction data, incorporating token metadata, cryptocurrency exchange rates, and overall market trends.
        This app is for informational purposes only and does not constitute financial advice. Last Uptade: Nov. 18, 2020 
        """
)

