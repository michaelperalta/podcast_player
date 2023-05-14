import requests
import json
import xmltodict
import pandas
import streamlit as st
import random
from increment_counter import increment
from remove_from_remove_list import remove

st.set_page_config(layout='wide')

filter_options = [
    'contains',
    'does not contain'
    ]


if 'filter_count' not in st.session_state:
    st.session_state.filter_count = 0

if 'filters_selected' not in st.session_state:
    st.session_state.filters_selected = []
    
if 'filters_selected' not in st.session_state:
    st.session_state.filters_selected = []
    
if 'filter_remove_list' not in st.session_state:
    st.session_state.filter_remove_list = [] 

def filter_container():
    # st.sidebar.markdown('---')
    st.sidebar.write('Select Filter(s)')
    cols = st.sidebar.columns(3)
    
    for i in st.session_state.filters_selected:
        if i not in st.session_state.filter_remove_list:
            operator = cols[0].selectbox('Select Filter',options=filter_options,key='filter_%s' % i,label_visibility="collapsed")

            if operator in ['contains','does not contain']:
                cols[1].text_input('Input Value',placeholder='Input Value',key='filter_value_%s' % i,label_visibility="collapsed")
                cols[2].button('Remove',key='remove_filter_%s' % i,on_click=remove,kwargs={'session_state_attribute':'filter_remove_list','session_state_value':i})
            
    
    st.sidebar.button('Add Filter',on_click=increment,kwargs={'session_state_attribute':'filter_count','session_state_attribute_list':'filters_selected'})

filter_container()

def get_filter_selections(filter_select_list,filter_remove_list,input_keys,default_states):
    
    selections = []
    
    for s in st.session_state[filter_select_list]:
        if s not in st.session_state[filter_remove_list]:
            
            filter_operator = st.session_state['filter_%s' % s]
            
            if filter_operator not in default_states:
                filter_value = st.session_state['filter_value_%s' % s]
                if filter_value not in default_states and filter_value != '' and filter_value != []:
                    selections.append([filter_operator,filter_value])
                    
    return selections

selected_filters = get_filter_selections('filters_selected','filter_remove_list',['filter','filter_value'],['Select Column','Select Filter','Select Value'])

url = 'https://itunes.apple.com/search?term=All Fantasy Everything&media=podcast'

r = requests.get(url)

response = json.loads(r.text)['results'][0]['feedUrl']

episodes = requests.get(response).text

episodes = xmltodict.parse(episodes)
episodes = episodes['rss']['channel']['item']

episodes = pandas.DataFrame(episodes)

cols = st.sidebar.columns(2)

# operator = cols[0].selectbox('Operator',options=['contains','does not contain'],label_visibility='hidden')
# search_value = cols[1].text_input('Search Value',label_visibility='hidden')

if len(selected_filters) > 0:
    
    for selected_filter in selected_filters:
        if selected_filter[0] == 'contains':
            episodes = episodes[episodes['title'].str.contains('%s' % selected_filter[1],case=False) == True]
            episodes = episodes[['title','description','itunes:episode','pubDate','enclosure']]
            episodes.sort_values(by=['itunes:episode'])
        if selected_filter[0] == 'does not contain':
            episodes = episodes[episodes['title'].str.contains('%s' % selected_filter[1],case=False) == False]
            episodes = episodes[['title','description','itunes:episode','pubDate','enclosure']]
            episodes.sort_values(by=['itunes:episode'])
            
    st.sidebar.subheader(str(len(episodes)) + ' episodes match your criteria')
    
    select_random_episode = st.sidebar.checkbox('Select Random Episode',value=True)
        
    if select_random_episode:
    
        random_episode = st.sidebar.button('Select Again')
        random_episode = True
        
        if random_episode:
            random_episode_number = random.randint(0,len(episodes)-1)
            episode_name = episodes['title'].values.tolist()[random_episode_number]
            episode_number = episodes['itunes:episode'].values.tolist()[random_episode_number]
            episode_air_date = episodes['pubDate'].values.tolist()[random_episode_number]
            episode_description = episodes['description'].values.tolist()[random_episode_number].split('</p>')[0]
            episode_link = episodes['enclosure'].values.tolist()[random_episode_number]
            
            
            st.title('Episode ' + str(episode_number) + ': ' + episode_name)
            st.markdown(episode_description, unsafe_allow_html=True)
            
            st.audio(episode_link['@url'])
            
    else:
        selected_episode = st.sidebar.selectbox('Select Episode',options=episodes['title'])
        episodes = episodes.query('title == "%s"' % selected_episode)
        
        episode_name = episodes['title'].values.tolist()[0]
        episode_number = episodes['itunes:episode'].values.tolist()[0]
        episode_air_date = episodes['pubDate'].values.tolist()[0]
        episode_description = episodes['description'].values.tolist()[0].split('</p>')[0]
        episode_link = episodes['enclosure'].values.tolist()[0]
        
        
        st.title('Episode ' + str(episode_number) + ': ' + episode_name)
        st.markdown(episode_description, unsafe_allow_html=True)
        
        st.audio(episode_link['@url'])