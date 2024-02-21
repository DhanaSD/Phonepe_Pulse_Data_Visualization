#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pymysql
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import requests
import subprocess
import os
import json
# ==============================================         /   /   DASHBOARD   /   /         ================================================== #

# ==============   /  CONNECT SQL SERVER  /   ACCESS DATA BASE    /   EXECUTE SQL QUERIES      /    ACCESS DATA   /   ========================= #

myconnection=pymysql.connect(host='127.0.0.1',user='root',passwd='Geethu!20D',database='phonepe_pulse')
cur=myconnection.cursor()

# ============================================       /     STREAMLIT DASHBOARD      /       ================================================= #
# Comfiguring Streamlit GUI 
st.set_page_config(layout='wide')

# Title
st.header(':violet[Phonepe Pulse Data Visualization ]')
st.write(':green[**(Note)**:-This data between  **2018**  to  **Q2 of 2023** in **INDIA**]')

# Selection option
option = st.radio(':violet[**Select your option**]',('All India', 'State wise','Top Ten categories'),horizontal=True)

if option=='All India':
    tab1,tab2=st.tabs(['Transaction','User'])

# ---------   /   All India Transaction Analysis   /  ----- #      
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            trans_yr = st.selectbox(':blue[**Select Year**]', ('select','2018','2019','2020','2021','2022','2023'),key='trans_yr')
        with col2:
            trans_qtr = st.selectbox(':blue[**Select Quarter**]', ('select','1','2','3','4'),key='trans_qtr')
        with col3:
            trans_type = st.selectbox(':blue[**Select Transaction type**]', ('select','Recharge & bill payments','Peer-to-peer payments',
            'Merchant payments','Financial Services','Others'),key='trans_type')
             
        cur.execute(f"SELECT State, Transaction_amount FROM aggregated_transaction WHERE Year = '{trans_yr}' AND Quarter = '{trans_qtr}' AND Transaction_type = '{trans_type}' order by Transaction_amount desc;")
        result1 = cur.fetchall()
        df1 = pd.DataFrame(result1, columns=['State', 'Transaction_amount']) 
               
    
        cur.execute(f"SELECT distinct(State), Transaction_count, Transaction_amount FROM aggregated_transaction WHERE Year = '{trans_yr}' AND Quarter = '{trans_qtr}' AND Transaction_type = '{trans_type}'order by Transaction_amount desc;")
        result2 = cur.fetchall()
        df2 = pd.DataFrame(result2, columns=['State','Transaction_count','Transaction_amount'])        
        
        cur.execute(f"SELECT SUM(Transaction_amount), AVG(Transaction_amount) FROM aggregated_transaction WHERE Year = '{trans_yr}' AND Quarter = '{trans_qtr}' AND Transaction_type = '{trans_type}';")
        result3 = cur.fetchall()
        df3= pd.DataFrame(result3, columns=['Total','Average'])        
        
        cur.execute(f"SELECT SUM(Transaction_count), AVG(Transaction_count) FROM aggregated_transaction WHERE Year = '{trans_yr}' AND Quarter = '{trans_qtr}' AND Transaction_type = '{trans_type}';")
        result4= cur.fetchall()
        df4 = pd.DataFrame(result4, columns=['Total','Average'])

         # ------    /  Geo visualization dashboard for Transaction /   ---- #
        # Drop a State column from df_in_tr_tab_qry_rslt
        df1.drop(columns=['State'], inplace=True)
        # Clone the gio data
        url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(url)
        data1 = json.loads(response.content)
        # Extract state names and sort them in alphabetical order
        state_names_tra = [feature['properties']['ST_NM'] for feature in data1['features']]
        state_names_tra.sort()
        # Create a DataFrame with the state names column
        df_state_names_tra = pd.DataFrame({'State': state_names_tra})
        # Combine the Gio State name with df1
        df_state_names_tra['Transaction_amount']=df1
        # convert dataframe to csv file
        df_state_names_tra.to_csv('State_trans.csv', index=False)
        # Read csv
        df_tra = pd.read_csv('State_trans.csv')
        # Geo plot
        fig_tra = px.choropleth(
            df_tra,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',locations='State',color='Transaction_amount',color_continuous_scale='thermal',title = 'Transaction Analysis')
        fig_tra.update_geos(fitbounds="locations", visible=False)
        fig_tra.update_layout(title_font=dict(size=33),title_font_color='#6739b7', height=800)
        st.plotly_chart(fig_tra,use_container_width=True)
        
        cur.execute(f"SELECT State, Transaction_amount FROM aggregated_transaction WHERE Year = '{trans_yr}' AND Quarter = '{trans_qtr}' AND Transaction_type = '{trans_type}' order by Transaction_amount desc;")
        result1 = cur.fetchall()
        df1 = pd.DataFrame(result1, columns=['State', 'Transaction_amount']) 
        df1_fig = px.bar(df1 , x = 'State', y ='Transaction_amount', color ='Transaction_amount', color_continuous_scale = 'thermal', title = 'All India Transaction Analysis Chart', height = 700,)
        df1_fig.update_layout(title_font=dict(size=25),title_font_color='#6739b7')
        st.plotly_chart(df1_fig,use_container_width=True)    
            
        st.markdown(
        f"<h1 style='color:#6739b7; font-size: 20px;'>TOTAL CALCULATION</h1>",
        unsafe_allow_html=True,)
        col4, col5 = st.columns(2)
        with col4:
            st.markdown(
        f"<h1 style='color:#6739b7; font-size: 20px;'>Transaction Analysis</h1>",
         unsafe_allow_html=True,)
            st.dataframe(df2)
        with col5:
            st.markdown(
    f"<h1 style='color:#6739b7; font-size: 20px;'>Transaction Amount</h1>",
    unsafe_allow_html=True,)
            st.dataframe(df3)
            st.markdown(
    f"<h1 style='color:#6739b7; font-size: 20px;'>Transaction Count</h1>",
    unsafe_allow_html=True,)
            st.dataframe(df4)

 # ----   /   All India User Analysis    /     -------- #    
         
    with tab2:  
        col1, col2 = st.columns(2)
        with col1:
            user_yr = st.selectbox(':blue[**Select Year**]', ('select','2018','2019','2020','2021','2022'),key='user_yr')
        with col2:
            user_qtr = st.selectbox(':blue[**Select Quarter**]', ('select','1','2','3','4'),key='user_qtr')
        
        cur.execute(f"SELECT State,SUM(User_Count), AVG(User_Count) FROM aggregated_user WHERE Year = '{user_yr}' AND Quarter = '{user_qtr}'group by State order by sum(User_Count) desc;")
        result5 = cur.fetchall()
        df5 = pd.DataFrame(result5, columns=['State','Total_User_Count','Average_User_Count'])   

        # ------    /  Geo visualization dashboard for User  /   ---- #
        # Drop a State column from df_in_us_tab_qry_rslt
        df5.drop(columns=['State'], inplace=True)
        # Clone the gio data
        url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(url)
        data2 = json.loads(response.content)
        # Extract state names and sort them in alphabetical order
        state_names_use = [feature['properties']['ST_NM'] for feature in data2['features']]
        state_names_use.sort()
        # Create a DataFrame with the state names column
        df_state_names_use = pd.DataFrame({'State': state_names_use})
        # Combine the Gio State name with df_in_tr_tab_qry_rslt
        df_state_names_use['User Count']=df5["Total_User_Count"]
        # convert dataframe to csv file
        df_state_names_use.to_csv('State_user.csv', index=False)
        # Read csv
        df_use = pd.read_csv('State_user.csv')
        # Geo plot
        fig_use = px.choropleth(
            df_use,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',locations='State',color='User Count',color_continuous_scale='thermal',title = 'User Analysis')
        fig_use.update_geos(fitbounds="locations", visible=False)
        fig_use.update_layout(title_font=dict(size=33),title_font_color='#6739b7', height=800)
        st.plotly_chart(fig_use,use_container_width=True)

        
        col1,col2=st.columns(2)
        with col1:
          cur.execute(f"SELECT State,SUM(User_Count), AVG(User_Count) FROM aggregated_user WHERE Year = '{user_yr}' AND Quarter = '{user_qtr}'group by State order by sum(User_Count) desc;")
          result5 = cur.fetchall()
          df5 = pd.DataFrame(result5, columns=['State','Total_User_Count','Average_User_Count'])  

          df5_fig = px.bar(df5 , x = 'State', y ='Total_User_Count', color ='Total_User_Count', color_continuous_scale = 'thermal', title = 'All India User Analysis Chart', height = 700,)
          df5_fig.update_layout(title_font=dict(size=25),title_font_color='#6739b7')
          st.plotly_chart(df5_fig,use_container_width=True)  
        with col2:   
          
          st.markdown(
    f"<h1 style='color:#6739b7; font-size: 20px;'>TOTAL CALCULATION</h1>",
    unsafe_allow_html=True,)    
          st.dataframe(df5)
        
# ---------------------------------       /     State wise Transaction        /        ------------------------------- #   

elif option =='State wise':    
    tab3, tab4 = st.tabs(['Transaction','User'])
   
    with tab3:
        col1, col2,col3 = st.columns(3)
        with col1:
            st_tr_st = st.selectbox(':blue[**Select State**]',('select','andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh','assam', 'bihar', 
            'chandigarh', 'chhattisgarh','dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat', 'haryana', 'himachal-pradesh', 
            'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh','maharashtra', 'manipur', 
            'meghalaya', 'mizoram', 'nagaland','odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim', 'tamil-nadu', 'telangana', 
            'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'),key='st_tr_st')
        with col2:
            st_tr_yr = st.selectbox(':blue[**Select Year**]', ('select','2018','2019','2020','2021','2022','2023'),key='st_tr_yr')
        with col3:
            st_tr_qtr = st.selectbox(':blue[**Select Quarter**]', ('select','1','2','3','4'),key='st_tr_qtr')
        
        cur.execute(f"SELECT Transaction_type, Transaction_amount FROM aggregated_transaction WHERE State = '{st_tr_st}' AND Year = '{st_tr_yr}' AND Quarter = '{st_tr_qtr}';")
        result6 = cur.fetchall()
        df6= pd.DataFrame(result6, columns=['Transaction_type', 'Transaction_amount'])
        
        cur.execute(f"SELECT Transaction_type, Transaction_count, Transaction_amount FROM aggregated_transaction WHERE State = '{st_tr_st}' AND Year = '{st_tr_yr}' AND Quarter = '{st_tr_qtr}';")
        result7= cur.fetchall()
        df7 = pd.DataFrame(result7, columns=['Transaction_type','Transaction_count','Transaction_amount'])
        
        cur.execute(f"SELECT SUM(Transaction_amount), AVG(Transaction_amount) FROM aggregated_transaction WHERE State = '{st_tr_st}' AND Year = '{st_tr_yr}' AND Quarter = '{st_tr_qtr}';")
        result8 = cur.fetchall()
        df8= pd.DataFrame(result8, columns=['Total','Average'])
                
        cur.execute(f"SELECT SUM(Transaction_count), AVG(Transaction_count) FROM aggregated_transaction WHERE State = '{st_tr_st}' AND Year ='{st_tr_yr}' AND Quarter = '{st_tr_qtr}';")
        result9 = cur.fetchall()
        df9 = pd.DataFrame(result9, columns=['Total','Average'])
        df6['Transaction_type'] = df6['Transaction_type'].astype(str)
        df6['Transaction_amount'] = df6['Transaction_amount'].astype(float)
        df6_fig = px.bar(df6 , x = 'Transaction_type', y ='Transaction_amount', color ='Transaction_amount', color_continuous_scale = 'thermal', title = 'Statewise Transaction Analysis Chart', height = 500,)
        df6_fig.update_layout(title_font=dict(size=25),title_font_color='#6739b7')
        st.plotly_chart(df6_fig,use_container_width=True)

        st.markdown(
    f"<h1 style='color:#6739b7; font-size: 20px;'>TOTAL CALCULATION</h1>",
    unsafe_allow_html=True,) 
        col4, col5 = st.columns(2)
        with col4:
            st.markdown(
    f"<h1 style='color:#6739b7; font-size: 20px;'>Transaction Analysis</h1>",
    unsafe_allow_html=True,) 
            st.dataframe(df7)
        with col5:
            st.markdown(
    f"<h1 style='color:#6739b7; font-size: 20px;'>Transaction Amount</h1>",
    unsafe_allow_html=True,) 
            st.dataframe(df8)
            st.markdown(
    f"<h1 style='color:#6739b7; font-size: 20px;'>Transaction Count</h1>",
    unsafe_allow_html=True,)            
            st.dataframe(df9)

 # -----------------------------------------       /     State wise User        /        ---------------------------------- # 
         
    with tab4:      
        col5, col6 = st.columns(2)
        with col5:
            st_us_st = st.selectbox(':blue[**Select State**]',('select','andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh','assam', 'bihar', 
            'chandigarh', 'chhattisgarh','dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat', 'haryana', 'himachal-pradesh', 
            'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh','maharashtra', 'manipur', 
            'meghalaya', 'mizoram', 'nagaland','odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim', 'tamil-nadu', 'telangana', 
            'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'),key='st_us_st')
        with col6:
            st_us_yr = st.selectbox(':blue[**Select Year**]', ('select','2018','2019','2020','2021','2022','2023'),key='st_us_yr')
        
        cur.execute(f"SELECT Quarter, SUM(User_Count) FROM aggregated_user WHERE State = '{st_us_st}' AND Year = '{st_us_yr}' GROUP BY Quarter;")
        result10 = cur.fetchall()
        df10 = pd.DataFrame(result10, columns=['Quarter', 'User Count'])
        df10['Quarter'] = df10['Quarter'].astype(int)
        df10['User Count'] = df10['User Count'].astype(int)
        df10_fig = px.bar(df10 , x = 'Quarter', y ='User Count', color ='User Count', color_continuous_scale = 'thermal', title = 'Statewise User Analysis Chart', height = 500,)
        df10_fig.update_layout(title_font=dict(size=25),title_font_color='#6739b7')
        st.plotly_chart(df10_fig,use_container_width=True)
        
        cur.execute(f"SELECT SUM(User_Count), AVG(User_Count) FROM aggregated_user WHERE State = '{st_us_st}' AND Year = '{st_us_yr}';")
        result11= cur.fetchall()
        df11 = pd.DataFrame(result11, columns=['Total','Average'])
        st.markdown(
    f"<h1 style='color:#6739b7; font-size: 20px;'>TOTAL CALCULATION</h1>",
    unsafe_allow_html=True,) 
        col3, col4 = st.columns(2)
        with col3:
            st.markdown(
    f"<h1 style='color:#6739b7; font-size: 20px;'>User Analysis</h1>",
    unsafe_allow_html=True,) 
            st.dataframe(df10)
        with col4:
            st.markdown(
    f"<h1 style='color:#6739b7; font-size: 20px;'>User Count</h1>",
    unsafe_allow_html=True,) 
            st.dataframe(df11)
else:
   
    tab5, tab6 = st.tabs(['Transaction','User'])

# ---------------------------------------       /     All India Top Transaction        /        ---------------------------- #    
    with tab5:
        top_tr_yr = st.selectbox(':blue[**Select Year**]', ('select','2018','2019','2020','2021','2022','2023'),key='top_tr_yr')
        cur.execute(f"SELECT State, SUM(Transaction_amount) As Transaction_amount FROM top_transaction WHERE Year = '{top_tr_yr}' GROUP BY State ORDER BY Transaction_amount DESC LIMIT 10;")
        result12= cur.fetchall()
        df12 = pd.DataFrame(result12, columns=['State', 'Top Transaction amount'])
        df12['State'] = df12['State'].astype(str)
        df12['Top Transaction amount'] = df12['Top Transaction amount'].astype(float)
        df12_fig = px.bar(df12 , x = 'State', y ='Top Transaction amount', color ='Top Transaction amount', color_continuous_scale = 'thermal', title = 'Top Transaction Analysis Chart', height = 600,)
        df12_fig.update_layout(title_font=dict(size=25),title_font_color='#6739b7')
        st.plotly_chart(df12_fig,use_container_width=True)
       
        
        cur.execute(f"SELECT State, SUM(Transaction_amount) as Transaction_amount, SUM(Transaction_count) as Transaction_count FROM top_transaction WHERE Year = '{top_tr_yr}' GROUP BY State ORDER BY Transaction_amount DESC LIMIT 10;")
        result13= cur.fetchall()
        df13= pd.DataFrame(result13, columns=['State', 'Top Transaction amount','Total Transaction count'])

        st.markdown(
    f"<h1 style='color:#6739b7; font-size: 20px;'>TOTAL CALCULATION</h1>",
    unsafe_allow_html=True,) 
        st.markdown(
    f"<h1 style='color:#6739b7; font-size: 20px;'>Top Transaction Analysis</h1>",
    unsafe_allow_html=True,) 
        st.dataframe(df13)

# -------------------------       /     All India Top User        /        ------------------ #        
    with tab6:

        top_us_yr = st.selectbox(':blue[**Select Year**]', ('select','2018','2019','2020','2021','2022','2023'),key='top_us_yr')
        # Top User Analysis bar chart query
        cur.execute(f"SELECT State, SUM(Registered_User) AS Top_user FROM top_user WHERE Year='{top_us_yr}' GROUP BY State ORDER BY Top_user DESC LIMIT 10;")
        result14 = cur.fetchall()
        df14= pd.DataFrame(result14, columns=['State', 'Total User count'])
        df14['State'] = df14['State'].astype(str)
        df14['Total User count'] = df14['Total User count'].astype(float)
        df14_fig = px.bar(df14 , x = 'State', y ='Total User count', color ='Total User count', color_continuous_scale = 'thermal', title = 'Top User Analysis Chart', height = 600,)
        df14_fig.update_layout(title_font=dict(size=25),title_font_color='#6739b7')
        st.plotly_chart(df14_fig,use_container_width=True)
        
        st.markdown(
    f"<h1 style='color:#6739b7; font-size: 20px;'>TOTAL CALCULATION</h1>",
    unsafe_allow_html=True,) 
        st.markdown(
    f"<h1 style='color:#6739b7; font-size: 20px;'>Top User Analysis</h1>",
    unsafe_allow_html=True,) 
        st.dataframe(df14)



        

