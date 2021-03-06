# -*- coding: utf-8 -*-

"""
Created on Fri Mar  8 21:31:53 2019
@author: Frederic
"""

# pip install geopy 
# pip install Nominatim
# import requests
# import lxml.html as lh
import pandas as pd
import numpy as np
import datetime as dt
# import urllib.request
# from bs4 import BeautifulSoup
import os
# from  geopy.geocoders import Nominatim
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import plotly.graph_objects as go
import altair as alt
import streamlit as st

# os.chdir('E:\Workarea\Python\Webcrawling')

date = "21/02/2021"

df_data = pd.ExcelFile('Terrain Cessy.xlsx', sheet_name='PdG').iloc[:46,:]
# # Find Lon / Lat of cities
# lon = []
# lat = []
# location = []
# geolocator = Nominatim(user_agent="Fred")
# for i in range(len(df_data)):
#     address = df_data.loc[i,'City']
#     location = geolocator.geocode(address)
#     # print(location.address)
#     # print(location.latitude, location.longitude)
#     lon.append(location.longitude)
#     lat.append(location.latitude)

# df_data['longitude'] = lon
# df_data['latitude'] = lat
# df_data.to_pickle('df_data')

def color_survived(val):
    color = 'red' if val == 'ID' else 'lightgreen'
    return f'background-color: {color}'

def build_aggrid(df, grid_height, title, boo_editable, boo_style, row_Height): # Build Ag-Grid tables !!

    # st.header(title)

    grid_width = '100%'
    
    return_mode_value = DataReturnMode.__members__['FILTERED'] # or 'AS_INPUT' or 'FILTERED_AND_SORTED'
    update_mode_value = GridUpdateMode.__members__['VALUE_CHANGED'] # or 'MODEL_CHANGED' or 'MANUAL' or 'SELECTION_CHANGED' or 'FILTERING_CHANGED' or 'SORTING_CHANGED'
    
    #Infer basic colDefs from dataframe types
    gb = GridOptionsBuilder.from_dataframe(df)
    
    #customize gridOptions
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=boo_editable)
    gb.configure_selection('single') # or 'multiple'
    gb.configure_grid_options(domLayout='normal', rowHeight=row_Height)

    cellstyle_jscode = JsCode("""
    function(params) {
    if (params.value == '11') {
        return {
        'color': 'white',
        'backgroundColor': 'darkred'
               }
    } 
    else {
        return {
        'color': 'black',
        'backgroundColor': 'white'
        }
    }
    };
    """)

    if boo_style:
        gb.configure_column("ID", cellStyle=cellstyle_jscode)

    gridOptions = gb.build()
    
    #Display the grid
    grid_response = AgGrid(
        df, 
        gridOptions=gridOptions,
        height=grid_height, 
        width=grid_width, # '100%',
        data_return_mode=return_mode_value, 
        update_mode=update_mode_value,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
        enable_enterprise_modules=False,
        )
    
    df_output = grid_response['data']
    
    return df_output

st.set_page_config(page_title="Real Estate in Pays de Gex",layout="wide")
st.header('Real Estate Analytics')
# st.header(dt.datetime.now())
st.markdown(date)
st.markdown(
    """<a style='display: block; text-align: center;' href="https://www.leboncoin.fr/recherche?category=9&locations=Cessy_01170__46.31905_6.07205_2916_10000&real_estate_type=3">leboncoin.fr</a>
    """,
    unsafe_allow_html=True,
)
st.info("### Terrains dans le Pays de Gex")

# df_data = pd.read_pickle('df_data')
df_data.index = [""] * len(df_data) # hide index
df_data['PriceM2'] = np.round(df_data['PriceM2'],1)
# st.dataframe(df_data.iloc[:,:6],height=1000)
# st.dataframe(data=df_data.iloc[:,:6].style.applymap(color_survived, subset=['ID']), height=2000)
# st.table(df_data.iloc[:,:6])
build_aggrid(df_data.iloc[:,:7], 1700, "", False, True, 35)
st.write('')
st.write('')

st.success("### Prix au m²")
# st.bar_chart(pd.DataFrame(index=range(1,len(df_data)+1),data=df_data['PriceM2'].values, columns=["Price / m²"]),)
colors = ['lightslategray',] * len(df_data)
colors[10] = 'crimson'
fig = go.Figure(data=[go.Bar(
    x=list(range(1,len(df_data)+1)),
    y=df_data['PriceM2'].values,
    text=df_data['PriceM2'].values,
    marker_color=colors # marker color can be a single color value or an iterable
)])
st.plotly_chart(fig, use_container_width=True)
st.write('')
st.write('')
# Stacked bar chart grouped by cities
st.write('Cumulatif par commune')
st.bar_chart(pd.DataFrame(index=df_data['City'],data=df_data['PriceM2'].values, columns=["Price / m²"]),)
st.write('')
st.write('')

# Groupby chart
st.write('Moyenne par commune')
st.bar_chart(pd.DataFrame(index=range(1,len(df_data)+1),data=df_data[['PriceM2','City']].values, columns=["Price / m²","City"]).groupby(['City']).sum() / pd.DataFrame(index=range(1,len(df_data)+1),data=df_data[['PriceM2','City']].values, columns=["Price / m²","City"]).groupby(['City']).count().sort_values(by='Price / m²',ascending=False))
# temp = pd.DataFrame(index=range(1,len(df_data)+1),data=df_data[['PriceM2','City']].values, columns=["Price / m²","City"]).groupby(['City']).sum() / pd.DataFrame(index=range(1,len(df_data)+1),data=df_data[['PriceM2','City']].values, columns=["Price / m²","City"]).groupby(['City']).count().sort_values(by='Price / m²',ascending=False)
# temp['City'] = temp.index
# st.write(alt.Chart(temp).mark_bar().encode(
#     x=alt.X('City', sort=alt.EncodingSortField(field='City',
#                                           order='ascending')),
#     # x = 'City',
#     y=alt.Y('Price / m²', sort=alt.EncodingSortField(field='Price / m²',
#                                          order='descending')),    
#     # y='Price / m²',
# ))

# Display represented countries on local map
st.info("### Localisation")
st.write('')
st.write('')
st.write('')
# Get longitude and latitude of countries
lon = df_data['longitude']
lat = df_data['latitude']
df_map_data = pd.DataFrame({'lat': lat, 'lon': lon})
st.map(df_map_data, zoom=11, use_container_width=True, )
st.write('')




















# # Crawler (but this doesn't work and the code has been taken from soccerstats.com)

# time = dt.datetime.now()

# city = 'Cessy'
# postal_code = '01170'
# category = 9 # annonces immobilières
# real_estate_type = 3 # terrains

# def get_soccerstats_data(country):
#     url='https://www.leboncoin.fr/recherche?category='+str(category)+'&locations='+city+'_'+postal_code+'__46.31905_6.07205_2916_10000&real_estate_type='+str(real_estate_type)
#     v_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
#     v_headers = {'User-Agent': v_user_agent}
#     v_request = urllib.request.Request(url=url,headers=v_headers)
#     v_response = urllib.request.urlopen(v_request)
#     soup = BeautifulSoup(v_response, 'html.parser')
#     page = requests.get(url)
#     doc = lh.fromstring(page.content)
#     # headers
#     tr_elements = doc.xpath("//table[@id='btable']/tr/th")
#     headers = []
#     iIncr = 0
#     for item in tr_elements[2:]:
#         iIncr += 1
#         if iIncr == 1 or iIncr == 2:
#             continue
#         # print(item.text_content())
#         headers.append(item.text_content())
#         if item.text_content() == 'FTS':
#             break

#     # Table ranking
#     elements = doc.xpath("//table[@id='btable']")
#     # elements[3] => form table (last 8 matches)
#     # elements[2] => ranking table
#     # elements[2].text_content().split("\r\n") => ranking table
#     rankings = []
#     table = []
# #    i = 0
#     if len(elements[2]) > 5:
#         table = elements[2]
#     else:
#         table = elements[1]
#     for item in table:
# #        if i == 0:
#             rankings.append(item.text_content().split("\r\n"))
# #        elif i < len(elements[2]):
# #            rankings.append([item.text_content().split("\r\n"),labels_array[i-1]])
# #        i += 1

#     table = []
#     labels_elements = []
#     labels_elements = soup.findAll('table', attrs={'id':"btable"})
#     if len(labels_elements[2]) > 11:
#         table = labels_elements[2]
#     else:
#         table = labels_elements[1]
#     labels = [item['class'] for item in table.select('div[class]')]
#     labels_array = []
#     for i in range(0,len(labels),int(len(labels)/(len(rankings)-1))):
#         # print(i)
#         if int(len(labels)/(len(rankings)-1)) == 6:
#             labels_array.append(labels[i+0][0][1:]+'-'+labels[i+1][0][1:]+'-'+labels[i+2][0][1:]+'-'+labels[i+3][0][1:]+'-'+labels[i+4][0][1:]+'-'+labels[i+5][0][1:])
#         elif int(len(labels)/(len(rankings)-1)) == 5:
#             labels_array.append(labels[i+0][0][1:]+'-'+labels[i+1][0][1:]+'-'+labels[i+2][0][1:]+'-'+labels[i+3][0][1:]+'-'+labels[i+4][0][1:])

#     df_rankings = pd.DataFrame(rankings)
#     df_rankings = df_rankings.drop([0])
#     for iCol in range(df_rankings.shape[1]):
#         if (iCol < 46 and df_rankings.loc[1,iCol] == '') or ((df_rankings.loc[:,iCol] == '').values.ravel().sum() == len(df_rankings)) or ((df_rankings.loc[:,iCol] == ' ').values.ravel().sum() == len(df_rankings)):
#             df_rankings.drop(iCol, axis=1, inplace=True)
#     df_rankings.drop(2, axis=1, inplace=True)
#     # put headers
#     df_rankings.rename(columns={5: 'Teams'}, inplace=True)
#     iIncr = 1
#     for iCol in range(len(headers)):
#         # print(iCol)
#         if iCol < 8:
#             df_rankings.rename(columns={df_rankings.columns[iIncr]: str(headers[iCol])}, inplace=True)
#             iIncr += 1
#     iIncr = 1
#     for iCol in range(9,9+36,6):
#         df_rankings.rename(columns={df_rankings.columns[iCol]: 'Form_Match #'+str(iIncr)}, inplace=True)
#         iIncr += 1
#     df_rankings.rename(columns={133: 'PPG'}, inplace=True)
#     df_rankings.rename(columns={134: 'PPG_last_8_matches'}, inplace=True)
#     df_rankings.rename(columns={135: '%_Clean_Sheet'}, inplace=True)
#     df_rankings.rename(columns={136: '%_Failed_To_Score'}, inplace=True)
#     df_rankings_clean = df_rankings.copy()
#     for iRow in range(len(df_rankings_clean)):
#         for iCol in range(df_rankings_clean.shape[1]):
#             if df_rankings.iloc[iRow, iCol] == ''and (iCol == 10 or iCol == 16 or iCol == 22 or iCol == 28 or iCol == 34 or iCol == 40):
#                 df_rankings_clean.iloc[iRow, iCol] = str(df_rankings.iloc[iRow, iCol+1])
#                 df_rankings_clean.iloc[iRow, iCol+1] = str(df_rankings.iloc[iRow, iCol+2])
#                 df_rankings_clean.iloc[iRow, iCol+2] = str(df_rankings.iloc[iRow, iCol+3])
#                 df_rankings_clean.iloc[iRow, iCol+3] = ''
#     #cols = list(range(13,44,6))
#     cols = list(range(13,13+int(len(labels)/(len(rankings)-1))*5+1,6))
#     df_rankings_clean.drop(columns=df_rankings_clean.columns[cols], axis=1, inplace=True)
#     #for iCol in range(10,10+30*5,5):
#     for iCol in range(10,10+int(len(labels)/(len(rankings)-1))*5,5):
#         df_rankings_clean.rename(columns={df_rankings_clean.columns[iCol]: ''}, inplace=True)
#         df_rankings_clean.rename(columns={df_rankings_clean.columns[iCol+1]: ''}, inplace=True)
#         df_rankings_clean.rename(columns={df_rankings_clean.columns[iCol+2]: ''}, inplace=True)
#         df_rankings_clean.rename(columns={df_rankings_clean.columns[iCol+3]: ''}, inplace=True)
#     # Add Last 6 matches FORM
#     temp = pd.DataFrame(labels_array)
#     temp.index = np.arange(1, len(temp)+1)
#     df_rankings_clean = pd.concat([df_rankings_clean, temp], axis=1)
    

#     # Form table
#     form = []
#     for item in elements[3]:
#         # print(item.text_content().split("\r\n"))
#         form.append(item.text_content().split("\r\n"))
#     if len(elements[3]) > 5:
#         df_form = pd.DataFrame(form)
#         df_form.drop([0], inplace=True)
#         df_form.drop([0,1,2,3,4,5,6,7,9,10,11,13,14,15,17,18,20,21,23,24,25,27,28,29,30,32,33,34,36,37,38,40,41,42], axis=1, inplace=True)
#         df_form.rename(columns={8: 'Form table (last 8 matches)', 12 : 'GP', 16 : 'W', 19 : 'D', 22 : 'L', 26 : 'GF', 31 : 'GA', 35 : 'GD', 39 : 'Pts'}, inplace=True)
#     else:
#         df_form = pd.DataFrame([['']*9])
#         df_form.rename(columns={0: 'Form table (last 8 matches)', 1 : 'GP', 2 : 'W', 3 : 'D', 4 : 'L', 5 : 'GF', 6 : 'GA', 7 : 'GD', 8 : 'Pts'}, inplace=True)


#     # Different method to get matches to be played (with BeautifulSoup)
#     url = 'https://www.soccerstats.com/latest.asp?league='+country
#     #build header
#     v_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
#     v_headers = {'User-Agent': v_user_agent}
#     #load web site
#     v_request = urllib.request.Request(url=url,headers=v_headers)
#     v_response = urllib.request.urlopen(v_request)
#     soup = BeautifulSoup(v_response, 'html.parser')
#     v_matches = soup.findAll('table', attrs={'cellspacing':"0"})
#     df_matches_info = []
#     matches_info = []
#     j=0  # 22
#     iIncr = 0
#     while j < len(v_matches):
#         v_match_info = v_matches[j].findAll('tr', attrs={'class': "trow2"})
#         i=0
#         if len(v_match_info) > 0 and len(v_match_info) <= 20:
#             #print(i,j)
#             while i < len(v_match_info):
#                 v_match_info_right = v_match_info[i].findAll('td', attrs={'align': "right"})
#                 v_match_info_center = v_match_info[i].findAll('td', attrs={'align': "center"})
#                 v_match_info_left = v_match_info[i].findAll('td', attrs={'align': "left"})
#                 try:
#                     labels = [item['class'] for item in v_match_info_left[3].select('div[class]')]
#                     labels = [i[0][1:] for i in labels]
#                     if i % 2 ==0: # even number
#                         matches_info.append([v_match_info_right[0].text.strip(), v_match_info_center[0].text.strip(), v_match_info_center[1].text.strip(), v_match_info_left[0].text.strip(), v_match_info_left[2].text.strip(), v_match_info_center[3].text.strip(), v_match_info_center[4].text.strip(), labels[0]+'-'+labels[1]+'-', labels[2]+'-'+labels[3]])
#                     else:
#                         matches_info.append([v_match_info_right[0].text.strip(), v_match_info_center[0].text.strip(), '', v_match_info_left[0].text.strip(), v_match_info_left[2].text.strip(), v_match_info_center[1].text.strip(), v_match_info_center[2].text.strip(), labels[0]+'-'+labels[1]+'-', labels[2]+'-'+labels[3]])
#                 except:
#                     break
#                 iIncr += 1
#                 i += 1
#         j += 1
#     df_matches_info = pd.DataFrame(matches_info)
#     df_matches_info.rename(columns={0: 'Upcoming matches', 1: 'Date', 2: 'Time', 3: 'Home/Away', 4: '% Points per game as compared to max nb of points', 5: 'Average total nb of goals (team+opponent)', 6: '% of matches with more than total 2.5 goals', 7: 'Last 4 results', 8: '(chronological order)'}, inplace=True)
#         # => df_matches_info

 

#     rows_nb = len(df_rankings_clean)
#     # concat df_rankings_clean, df_matches_info and df_form (to save space eventually in Excel)
#     temp2 = pd.DataFrame([[''] for _ in range(len(df_rankings_clean))], columns=[9])
#     temp2.index = np.arange(1, len(temp2)+1)
#     temp3 = pd.DataFrame([[''] for _ in range(len(df_form))], columns=[9])
#     temp3.index = np.arange(1, len(temp3)+1)
#     df_matches_matrix = pd.concat([pd.concat([df_rankings_clean.iloc[:,:df_form.shape[1]].T.reset_index(drop=True).T, temp2],axis=1), pd.DataFrame(['']*(df_form.shape[1]+1) for _ in range(1)).T.reset_index(drop=True).T, pd.concat([pd.DataFrame(df_matches_info.columns.tolist()).T.reset_index(drop=True),pd.DataFrame([''], columns=[9])], axis=1), pd.concat([df_matches_info.T.reset_index(drop=True).T,pd.DataFrame([''], columns=[9])],axis=1), pd.DataFrame(['']*(df_matches_info.shape[1]+1) for _ in range(1)).T.reset_index(drop=True).T, pd.concat([pd.DataFrame(df_form.columns.tolist()).T.reset_index(drop=True),pd.DataFrame([''], columns=[9])],axis=1), pd.concat([df_form.T.reset_index(drop=True).T, temp3],axis=1)], axis=0)
#     for _ in range(len(df_matches_matrix)):
#         if _ < len(df_rankings_clean):
#             df_matches_matrix.iloc[_,-1] = labels_array[_]
#         else:
#             df_matches_matrix.iloc[_,-1] = ''#    df_matches_matrix.rename(columns={0: 'Date', 1: 'Time', 2: 'home/Away', 3: 'Teams', 4: '% Points per game as compared to max nb of points', 5: 'Average total nb of goals (team+opponent)', 6: '% of matches with more than total 2.5 goals', 7: '', 8: ''}, inplace=True)
#     #df_matches_matrix.iloc[:,:-1].columns = df_form.columns
#     for _ in range(df_form.shape[1]):
#         df_matches_matrix.rename(columns={df_matches_matrix.columns[_]: df_form.columns[_]}, inplace=True)
#     df_matches_matrix.rename(columns={df_matches_matrix.columns[0]: 'Table ranking'}, inplace=True)
#     #df_matches_matrix.iloc[-rows_nb-1:,:].iloc[0,:] = df_form.columns.tolist()
#     df_matches_matrix.rename(columns={df_matches_matrix.columns[9]: 'Last 6 matches momentum'}, inplace=True)
   
#     return df_rankings_clean, df_matches_info, df_form, df_matches_matrix
#     # => df_matches_matrix



# '''
# df_rankings_clean, df_matches_info, df_form, df_matches_matrix = get_soccerstats_data('belgium')
# '''
# os.chdir('E:\Workarea\Python\Webcrawling')
# countries = ['slovakia','lithuania','croatia','spain','germany','denmark','italy','portugal','netherlands','england','belgium','czechrepublic','russia','france']
# with pd.ExcelWriter('Staff Predictor Statistics' + ' ' + dt.datetime.strftime(dt.datetime.now(), '%Y-%m-%d') + '.xlsx') as writer:
#     for c in countries:
#         df_rankings_clean, df_matches_info, df_form, df_matches_matrix = get_soccerstats_data(c)
#         # df_rankings_clean.to_csv('df_rankings_' + str(c) + '_' + dt.datetime.strftime(dt.datetime.now(), '%Y-%m-%d') + '.csv', sep=',')
#         # df_matches_matrix.to_csv('df_matches_stats_df_form_' + str(c) + '_' + dt.datetime.strftime(dt.datetime.now(), '%Y-%m-%d') + '.csv', sep=',')
#         print('Sheet',str(c))
#         df_matches_matrix.to_excel(writer, sheet_name=str(c), index=False)
 

# print('\n Time elapsed:', dt.datetime.now()-time)

 

 

 

 

 
