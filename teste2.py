import numpy as np
import pandas as pd
import streamlit as st
import time
import pandas as pd
import concurrent.futures
import os
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.express as px
import numpy as np
import plotly.io as pio
import streamlit as st
from PIL import Image
import requests
from io import BytesIO


if 'initial_df' not in st.session_state:
    st.session_state.initial_df = None
button_clicked = False


st.set_page_config(
    page_title="Kabum E-sports",
    page_icon="🥷",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data
def carregar_dados():
    resultado = pd.read_csv('gamegeralfiltrado.csv')

    return resultado

@st.cache_resource
def carregar_image(image_url,name,quantidade,presence):
    # Use requests para obter a imagem da URL
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))

    image = st.image(image, width=70)
    st.caption(f'{name} -  {quantidade} J - Presence {presence}%')

    return image

@st.cache_resource
def carregar_image_pick(image_url,name,quantidade,winrate,presence):
    # Use requests para obter a imagem da URL
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    image = st.image(image, width=70)
    if winrate>50:
        st.caption(f'{name}-{quantidade}J WR: :green[{winrate}%] - Presence {presence}%')
    else:
        st.caption(f'{name}-{quantidade}J WR: :red[{winrate}%] - Presence {presence}%')
    return image

with st.sidebar:
    with st.container():
        image = Image.open('logo-kabum.png')

        st.image(image,width=250)
        # Coletando parâmetros do usuário
        resultado = carregar_dados()
        ###
        nomes_unicos_league = sorted(resultado['league'].unique())
        Liga = st.selectbox("Liga:", nomes_unicos_league)
        data_time = resultado.loc[resultado['league'] == Liga]
        nomes_unicos_times = sorted(data_time['teamname'].unique())
        time = st.selectbox("Time:", nomes_unicos_times)

        data_time_escolhido = data_time.loc[data_time['teamname'] == time]
        ###
        nomes_unicos_split = sorted(data_time_escolhido['split'].unique())
        split = st.selectbox("Split:",['All'] + nomes_unicos_split)
        if split != 'All':
            data_time_escolhido = data_time_escolhido.loc[data_time_escolhido['split'] == split]
        ###
        nomes_unicos_patch = sorted(data_time_escolhido['patch'].unique())
        patch = st.selectbox("Patch:", ['All'] + nomes_unicos_patch)
        if patch != 'All':
            data_time_escolhido = data_time_escolhido.loc[data_time_escolhido['patch'] == patch]
        ###
        playoffs = st.selectbox("Playoffs:", ['All', 'Playoff', 'Fase de Ponto'])
        if playoffs != 'All':
            if playoffs=='Playoff':
                playoffs=1
            else:
                playoffs = 0
            data_time_escolhido = data_time_escolhido.loc[data_time_escolhido['playoffs'] == playoffs]

        ###

        gameid=data_time_escolhido['gameid'].unique()

        nomes_unicos_times_adv = sorted(data_time[data_time['gameid'].isin(gameid)]['teamname'].unique())

        nomes_unicos_times_adv = [x for x in nomes_unicos_times_adv if x != time]
        timesadv = st.selectbox("Time Adversario:", ['All']+nomes_unicos_times_adv)

        if timesadv!='All':
            data_time_adv = data_time.loc[data_time['teamname'] == timesadv]
            gameid_adv = data_time_adv[data_time_adv['gameid'].isin(gameid)]['gameid'].unique().tolist()
            data_time_escolhido=data_time_escolhido[data_time_escolhido['gameid'].isin(gameid_adv)]

try:
    tab1, tab2, tab3 = st.tabs(["Geral",'Draft','Players'])
    data_time_escolhido_players=data_time_escolhido.loc[data_time_escolhido['position']!='team']
    with tab1:
        if 'data_time_escolhido' in locals():
            with st.container():
                col1, col2,col3 = st.columns([0.2,0.5,0.25])
                data_teams=data_time_escolhido.loc[data_time_escolhido['position']=='team']
                data_time_adv=data_time.loc[data_time['position']=='team']
                with col1:
                    winrate = round(data_teams["result"].mean() * 100,0)
                    blueside=data_teams.loc[data_teams['side']=='Blue']
                    bluewin=blueside["result"].sum()
                    redside=data_teams.loc[data_teams['side']=='Red']
                    redwin=redside["result"].sum()
                    a={'result':[redwin,bluewin]}
                    df_win = pd.DataFrame({'Teams': ['Red', 'Blue'], 'Values': a["result"]})
                    pio.templates.default = "plotly"
                    fig_kind = px.pie(df_win, names='Teams', values='Values',
                                      color='Teams',
                                      color_discrete_map={'Red': 'red', 'Blue': 'blue'},
                                      title=f'{len(data_teams["result"])} Games {data_teams["result"].sum()}V - {len(data_teams["result"]) - data_teams["result"].sum()}D - Win Rate de {winrate:.2f}%')
                    st.plotly_chart(fig_kind, use_container_width=True)
                with col2:
                    gameid=data_teams['gameid'].unique()
                    nomes_unicos_times_adv = data_time_adv[data_time_adv['gameid'].isin(gameid)]['teamname'].tolist()
                    nomes_unicos_times_adv = [x for x in nomes_unicos_times_adv if x != time]
                    df_nomes_unicos_times_adv = pd.DataFrame({'teamname': nomes_unicos_times_adv})
                    df_nomes_unicos_times_adv['teamname'] = df_nomes_unicos_times_adv.groupby('teamname').cumcount().add(1).astype(str) + ' ' + df_nomes_unicos_times_adv['teamname']
                    fig = px.bar(data_teams,x=df_nomes_unicos_times_adv['teamname'], y=['golddiffat10','golddiffat15'],
                                 color_discrete_sequence=['#48D1CC', '#90EE90'],
                                 labels={'golddiffat10': 'Golddiff at 10', 'golddiffat15': 'Golddiff at 15'},barmode='group')
                    st.plotly_chart(fig, use_container_width=True)
                with col3:
                    st.subheader('Estats Early')
                    gold_med = round(data_teams['golddiffat15'].mean(), 1)
                    if gold_med > 0:
                        st.markdown(f'''Gold diff aos 15: :green[+{gold_med}]''')
                    else:
                        st.markdown(f'''Gold diff aos 15: :red[{gold_med}]''')
                    gold_med10 = round(data_teams['golddiffat10'].mean(), 1)
                    if gold_med10 > 0:
                        st.markdown(f'''Gold diff aos 10: :green[+{gold_med10}]''')
                    else:
                        st.markdown(f'''Gold diff aos 10: :red[{gold_med10}]''')
                    winrateat15 = round(data_teams.loc[data_teams['golddiffat10']>0]['result'].mean()*100, 1)
                    winrateat15_1000 = round(data_teams.loc[data_teams['golddiffat10'] > 1500]['result'].mean()*100, 0)
                    if winrateat15 > 0:
                        st.markdown(f'''Win rate com golddiff at 15 min: :green[{winrateat15}%]''')
                    else:
                        st.markdown(f'''Win rate com golddiff at 15 min: :red[+{winrateat15}%]''')

                    if winrateat15_1000 > 0:
                        st.markdown(f'''Win rate com 1500 de golddiff at 15 min: :green[{winrateat15_1000}%]''')
                    else:
                        st.markdown(f'''Win rate com 1500 de golddiff at 15 min: :red[{winrateat15_1000}%]''')
                    tempomedio=data_teams["gamelength"].mean()
                    st.write(f'Tempo médio de jogo: {int(tempomedio//60)}:{int(tempomedio%60)}')
                    st.write(f'First Blood: {round(data_teams["firstblood"].mean()*100,0)}%')
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    dragon = Image.open('dragon1.png')
                    st.image(dragon, width=200)
                    st.write(f'First Dragon: {round(data_teams["firstdragon"].mean() * 100, 0)}% - Blue {round(blueside["firstdragon"].mean() * 100, 0)}% - Red {round(redside["firstdragon"].mean() * 100, 0)}%')
                    st.write(f'Dragons / game: {round(data_teams["dragons"].mean(), 1)} - Blue {round(blueside["dragons"].mean(), 1)} - Red {round(redside["dragons"].mean() , 1)}')
                    st.write(f'Dragons Domination: {round(data_teams["dragons"].mean()/(data_teams["dragons"].mean()+data_teams["opp_dragons"].mean())*100, 0)}% - Blue {round(blueside["dragons"].mean()/(blueside["dragons"].mean()+blueside["opp_dragons"].mean())*100, 0)}% - Red {round(redside["dragons"].mean()/(redside["dragons"].mean()+redside["opp_dragons"].mean())*100, 0)}%')
                    st.write(
                        f'First Dragon = Victory: {round(data_teams.loc[data_teams["firstdragon"] == 1]["result"].mean() * 100, 0)}%')
                    st.write(
                    f'First Tower Mid  = Dragons Domination: {round(data_teams.loc[data_teams["firstmidtower"] == 1]["dragons"].mean()/(data_teams.loc[data_teams["firstmidtower"] == 1]["dragons"].mean()+data_teams.loc[data_teams["firstmidtower"] == 1]["opp_dragons"].mean())*100  , 0)}%')
                with col2:
                    arauto = Image.open('Arauto.png')
                    st.image(arauto, width=105)
                    st.write(
                        f'First Herald: {round(data_teams["firstherald"].mean() * 100, 0)}% - Blue {round(blueside["firstherald"].mean() * 100, 0)}% - Red {round(redside["firstherald"].mean() * 100, 0)}%')
                    st.write(
                        f'Heralds / game: {round(data_teams["heralds"].mean(), 1)} - Blue {round(blueside["heralds"].mean(), 1)} - Red {round(redside["heralds"].mean(), 1)}')
                    st.write(
                        f'Heralds Domination: {round(data_teams["heralds"].mean() / (data_teams["heralds"].mean() + data_teams["opp_heralds"].mean()) * 100, 0)}% - Blue {round(blueside["heralds"].mean() / (blueside["heralds"].mean() + blueside["opp_heralds"].mean()) * 100, 0)}% - Red {round(redside["heralds"].mean() / (redside["heralds"].mean() + redside["opp_heralds"].mean()) * 100, 0)}%')
                    st.write(
                        f'First Herald = Victory: {round(data_teams.loc[data_teams["firstherald"]==1]["result"].mean() * 100, 0)}%')
                    st.write(
                        f'First Herald = First Tower: {round(data_teams.loc[data_teams["firstherald"] == 1]["firsttower"].mean() * 100, 0)}%')
                with col3:
                    baron = Image.open('baron.png')
                    st.image(baron, width=80)
                    st.write(
                        f'First Baron: {round(data_teams["firstbaron"].mean() * 100, 0)}% - Blue {round(blueside["firstbaron"].mean() * 100, 0)}% - Red {round(redside["firstbaron"].mean() * 100, 0)}%')
                    st.write(
                        f'Barons / game: {round(data_teams["barons"].mean(), 1)} - Blue {round(blueside["barons"].mean(), 1)} - Red {round(redside["barons"].mean(), 1)}')
                    #st.write(f'Barons Domination: {round(data_teams["barons"].mean() / (data_teams["barons"].mean() + data_teams["opp_barons"].mean()) * 100, 0)}% - Blue {round(blueside["barons"].mean() / (blueside["barons"].mean() + blueside["opp_barons"].mean()) * 100, 0)}% - Red {round(redside["barons"].mean() / (redside["barons"].mean() + redside["opp_barons"].mean()) * 100, 0)}%')
                    st.write(
                        f'First Baron = Victory: {round(data_teams.loc[data_teams["firstbaron"] == 1]["result"].mean() * 100, 0)}%')
                with col4:
                    turret = Image.open('Turret.png')
                    st.image(turret, width=60)
                    st.write(
                        f'First Tower: {round(data_teams["firsttower"].mean() * 100, 0)}% - Blue {round(blueside["firsttower"].mean() * 100, 0)}% - Red {round(redside["firsttower"].mean() * 100, 0)}%')
                    st.write(
                        f'Towers / game: {round(data_teams["towers"].mean(), 1)} - Blue {round(blueside["towers"].mean(), 1)} - Red {round(redside["towers"].mean(), 1)}')
                    st.write(f'Plates Diff: {round((data_teams["turretplates"].mean() - data_teams["opp_turretplates"].mean()) , 1)} - First Herald = Plates Diff: {round((data_teams.loc[data_teams["firstherald"]==1]["turretplates"].mean() - data_teams.loc[data_teams["firstherald"]==1]["opp_turretplates"].mean()) , 1)}')

                    st.write(f'Towers Diff: {round((data_teams["towers"].mean() - data_teams["opp_towers"].mean()) , 1)} ')
                    st.write(
                        f'First Tower Mid/Three  = Victory: {round(data_teams.loc[data_teams["firstmidtower"] == 1]["result"].mean() * 100, 0)}%/{round(data_teams.loc[data_teams["firsttothreetowers"] == 1]["result"].mean() * 100, 0)}%')
                    st.write(f'Inib / Game: {round(data_teams["inhibitors"].mean(),1)}')
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                data_teams = data_time_escolhido.loc[data_time_escolhido['position'] == 'team']
    with tab2:
        tab1, tab2 = st.tabs(["Pick",'Bans'])
        data_champ = pd.read_csv('datachamps.csv')
        with tab1:
            col11, col21,col31 = st.columns([0.45,0.05,0.45])
            max_threads = os.cpu_count()
            blueside_champ = data_time_escolhido_players.loc[data_time_escolhido_players['side'] == 'Blue']
            redside_champ = data_time_escolhido_players.loc[data_time_escolhido_players['side'] == 'Red']
            with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
                with col11:
                    st.title(f''':blue[Blue Side - Pick]''')
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.subheader('Top')
                        position= blueside_champ.loc[blueside_champ['position']=='top']
                        ban1_counts = position['champion'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 0)
                            winrate=round(position.loc[position['champion']==name]['result'].mean()*100,0)
                            carregar_image_pick(image_url[0], name, quantidade,winrate,presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 2)
                                    winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100,
                                                    0)
                                    carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                    with col2:
                        st.subheader('Jungle')
                        position= blueside_champ.loc[blueside_champ['position']=='jng']
                        ban1_counts = position['champion'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 2)
                            winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100, 0)
                            carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 2)
                                    winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100,
                                                    0)
                                    carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                    with col3:
                        st.subheader('Mid')
                        position= blueside_champ.loc[blueside_champ['position']=='mid']
                        ban1_counts = position['champion'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 2)
                            winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100, 0)
                            carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 2)
                                    winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100,
                                                    0)
                                    carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                    with col4:
                        st.subheader('Adc')
                        position= blueside_champ.loc[blueside_champ['position']=='bot']
                        ban1_counts = position['champion'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 2)
                            winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100, 0)
                            carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 2)
                                    winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100,
                                                    0)
                                    carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                    with col5:
                        st.subheader('Sup')
                        position= blueside_champ.loc[blueside_champ['position']=='sup']
                        ban1_counts = position['champion'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 2)
                            winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100, 0)
                            carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 2)
                                    winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100,
                                                    0)
                                    carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                with col21:
                    st.write()
                with col31:
                    st.title(f''':red[Red Side - Pick]''')
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.subheader('Top')
                        position= redside_champ.loc[redside_champ['position']=='top']
                        ban1_counts = position['champion'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 0)
                            winrate=round(position.loc[position['champion']==name]['result'].mean()*100,0)
                            carregar_image_pick(image_url[0], name, quantidade,winrate,presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 2)
                                    winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100,
                                                    0)
                                    carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                    with col2:
                        st.subheader('Jungle')
                        position= redside_champ.loc[redside_champ['position']=='jng']
                        ban1_counts = position['champion'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 2)
                            winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100, 0)
                            carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 2)
                                    winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100,
                                                    0)
                                    carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                    with col3:
                        st.subheader('Mid')
                        position= redside_champ.loc[redside_champ['position']=='mid']
                        ban1_counts = position['champion'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 2)
                            winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100, 0)
                            carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 2)
                                    winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100,
                                                    0)
                                    carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                    with col4:
                        st.subheader('Adc')
                        position= redside_champ.loc[redside_champ['position']=='bot']
                        ban1_counts = position['champion'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 2)
                            winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100, 0)
                            carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 2)
                                    winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100,
                                                    0)
                                    carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                    with col5:
                        st.subheader('Sup')
                        position= redside_champ.loc[redside_champ['position']=='sup']
                        ban1_counts = position['champion'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 2)
                            winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100, 0)
                            carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 2)
                                    winrate = round(position.loc[position['champion'] == name]['result'].mean() * 100,
                                                    0)
                                    carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
        with tab2:
            col11, col21, col31 = st.columns([0.45, 0.05, 0.45])

            max_threads = os.cpu_count()
            with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
                with col11:
                    st.title(f''':blue[Blue Side - Ban]''')
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.subheader('1')
                        ban1_counts = blueside['ban1'].value_counts()
                        top5_ban1_counts=ban1_counts[:4]
                        resto_ban1_counts=ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade=count
                            total = ban1_counts.sum()
                            presence=round((quantidade/total)*100,0)
                            carregar_image(image_url[0], name, quantidade,presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 0)
                                    carregar_image(image_url[0], name, quantidade, presence)
                    with col2:
                        st.subheader('2')
                        ban1_counts = blueside['ban2'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 0)
                            carregar_image(image_url[0], name, quantidade, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 0)
                                    carregar_image(image_url[0], name, quantidade, presence)
                    with col3:
                        st.subheader('3')
                        ban1_counts = blueside['ban3'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 0)
                            carregar_image(image_url[0], name, quantidade, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 0)
                                    carregar_image(image_url[0], name, quantidade, presence)
                    with col4:
                        st.subheader('4')
                        ban1_counts = blueside['ban4'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 0)
                            carregar_image(image_url[0], name, quantidade, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 0)
                                    carregar_image(image_url[0], name, quantidade, presence)
                    with col5:
                        st.subheader('5')
                        ban1_counts = blueside['ban5'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 0)
                            carregar_image(image_url[0], name, quantidade, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 0)
                                    carregar_image(image_url[0], name, quantidade, presence)
                with col21:
                    st.write()
                with col31:
                    st.title(f''':red[Red Side - Ban]''')
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.subheader('1')
                        ban1_counts = redside['ban1'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 0)
                            carregar_image(image_url[0], name, quantidade, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 0)
                                    carregar_image(image_url[0], name, quantidade, presence)
                    with col2:
                        st.subheader('2')
                        ban1_counts = redside['ban2'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 0)
                            carregar_image(image_url[0], name, quantidade, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 0)
                                    carregar_image(image_url[0], name, quantidade, presence)
                    with col3:
                        st.subheader('3')
                        ban1_counts = redside['ban3'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 0)
                            carregar_image(image_url[0], name, quantidade, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 0)
                                    carregar_image(image_url[0], name, quantidade, presence)
                    with col4:
                        st.subheader('4')
                        ban1_counts = redside['ban4'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            name1 = name.replace(" ", "")
                            image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 0)
                            carregar_image(image_url[0], name, quantidade, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 0)
                                    carregar_image(image_url[0], name, quantidade, presence)
                    with col5:
                        st.subheader('5')
                        ban1_counts = redside['ban5'].value_counts()
                        top5_ban1_counts = ban1_counts[:4]
                        resto_ban1_counts = ban1_counts[4:]
                        for ban1, count in top5_ban1_counts.items():
                            name = ban1
                            image_url = data_champ.loc[data_champ['champ'] == name.lower()]['imagem'].unique()
                            quantidade = count
                            total = ban1_counts.sum()
                            presence = round((count / total) * 100, 0)
                            carregar_image(image_url[0], name, quantidade, presence)
                        if not resto_ban1_counts.empty:
                            with st.expander("Ver mais"):
                                for ban1, count in resto_ban1_counts.items():
                                    name = ban1
                                    name1 = name.replace(" ", "")
                                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                                    quantidade = count
                                    total = ban1_counts.sum()
                                    presence = round((count / total) * 100, 0)
                                    carregar_image(image_url[0], name, quantidade, presence)
    with tab3:
        st.subheader('Estats Gerais')
        nomes_players=data_time_escolhido['playername'].dropna().unique()
        jogador=st.selectbox("Jogador :",nomes_players)
        data_players=data_time_escolhido.loc[data_time_escolhido['playername']==jogador]
        with st.container():
            col1, col2, col3 = st.columns([0.6,0.2,0.2])
            with col1:
                gameid = data_players['gameid'].unique()
                nomes_unicos_times_adv = data_time_adv[data_time_adv['gameid'].isin(gameid)]['teamname'].tolist()
                nomes_unicos_times_adv = [x for x in nomes_unicos_times_adv if x != time]
                df_nomes_unicos_times_adv = pd.DataFrame({'teamname': nomes_unicos_times_adv})
                df_nomes_unicos_times_adv['teamname'] = df_nomes_unicos_times_adv.groupby('teamname').cumcount().add(
                    1).astype(str) + ' ' + df_nomes_unicos_times_adv['teamname']
                fig = px.bar(data_players, x=df_nomes_unicos_times_adv['teamname'], y=['golddiffat10', 'golddiffat15'],
                             color_discrete_sequence=['#48D1CC', '#90EE90'],
                             labels={'golddiffat10': 'Golddiff at 10', 'golddiffat15': 'Golddiff at 15'}, barmode='group')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader('Mais Pickados')
                ban1_counts = data_players['champion'].value_counts()
                top5_ban1_counts = ban1_counts[:3]
                for ban1, count in top5_ban1_counts.items():
                    name = ban1
                    name1 = name.replace(" ", "")
                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                    quantidade = count
                    total = ban1_counts.sum()
                    presence = round((count / total) * 100, 0)
                    winrate = round(data_players.loc[data_players['champion'] == name]['result'].mean() * 100, 0)
                    carregar_image_pick(image_url[0], name, quantidade, winrate, presence)

            with col3:
                st.subheader('Melhor Early')
                champion_stats = data_players.groupby('champion').agg({'golddiffat15': 'mean', 'champion': 'count'})
                champion_stats = champion_stats.rename(
                    columns={'golddiffat15': 'MeanGoldDiffAt15', 'champion': 'Count'})
                champion_stats = champion_stats.sort_values(by='MeanGoldDiffAt15', ascending=False)
                champion_stats3= champion_stats[:3]
                for i in range(len(champion_stats3)):
                    name = champion_stats3.index[i]
                    name1 = name.replace(" ", "")
                    image_url = data_champ.loc[data_champ['champ'] == name1.lower()]['imagem'].unique()
                    quantidade = champion_stats3.iloc[i,1]
                    total = champion_stats['Count'].sum()
                    presence = round((quantidade / total) * 100, 0)
                    winrate = round(data_players.loc[data_players['champion'] == name]['result'].mean() * 100, 0)
                    carregar_image_pick(image_url[0], name, quantidade, winrate, presence)
                    golddiff15=round(champion_stats3.iloc[i,0],1)
                    st.caption(f'Golddiff aos 15: {golddiff15}')

        with st.container():
            col1, col2, col3,col4, col5, col6 = st.columns(6)
            with col1:
                st.subheader('Early at 10')
                cs_med = round(data_players['opp_csat10'].mean(), 1)
                if cs_med > 0:
                    st.markdown(f'''Cs diff aos 10: :green[+{cs_med}]''')
                else:
                    st.markdown(f'''Cs diff aos 10: :red[{cs_med}]''')
                xp_med = round(data_players['xpdiffat10'].mean(), 1)
                if xp_med > 0:
                    st.markdown(f'''XP diff aos 10: :green[+{xp_med}]''')
                else:
                    st.markdown(f'''XP diff aos 10: :red[{xp_med}]''')
                gold_med = round(data_players['golddiffat10'].mean(), 1)
                if gold_med > 0:
                    st.markdown(f'''Gold diff aos 10: :green[+{gold_med}]''')
                else:
                    st.markdown(f'''Gold diff aos 10: :red[{gold_med}]''')

            with col2:
                st.subheader('Early at 15')
                cs_med = round(data_players['opp_csat15'].mean(), 1)
                if cs_med > 0:
                    st.markdown(f'''Cs diff aos 15: :green[+{cs_med}]''')
                else:
                    st.markdown(f'''Cs diff aos 15: :red[{cs_med}]''')
                xp_med = round(data_players['xpdiffat15'].mean(), 1)
                if xp_med > 0:
                    st.markdown(f'''XP diff aos 15: :green[+{xp_med}]''')
                else:
                    st.markdown(f'''XP diff aos 15: :red[{xp_med}]''')
                gold_med = round(data_players['golddiffat15'].mean(), 1)
                if gold_med > 0:
                    st.markdown(f'''Gold diff aos 15: :green[+{gold_med}]''')
                else:
                    st.markdown(f'''Gold diff aos 15: :red[{gold_med}]''')
            with col3:
                st.subheader('Visão')
                st.write(f'VisionScorepm: {round(data_players["vspm"].mean(),1)}')
                st.write(
                    f'Sentinela Detectora compradas: {round(data_players["controlwardsbought"].mean(),1)}')
                st.write(f'Wards Destruidas por minuto: {round(data_players["wcpm"].mean(),1)}')
                st.write(
                    f'Wards colocadas por minuto: {round(data_players["wpm"].mean(),1)} - Wards colocados {round(data_players["wardsplaced"].mean(),1)} ')

            with col4:
                st.subheader('Gold')
                ahead15=round(len(data_players.loc[data_players["golddiffat15"]>0])/len(data_players)*100,0)
                if ahead15>50:
                    st.write(f'A frente em gold aos 15 min: :green[{ahead15}%]')
                else:
                    st.write(f'A frente em gold aos 15 min: :red[{ahead15}%]')

                goldahedvic=round(data_players.loc[data_players["golddiffat15"] > 1000]["result"].mean()*100,0)
                if goldahedvic>50:
                    st.write(f'1000 de gold a frente aos 15 = Victory: :green[{goldahedvic}%]')
                else:
                    st.write(f'1000 de gold a frente aos 15 = Victory: :red[{goldahedvic}%]')
                st.write(f'Gold%: {round(data_players["earnedgoldshare"].mean() * 100, 0)}%')
                st.write(f'Goldpm: {round(data_players["earned gpm"].mean(), 1)}')

            with col5:
                st.subheader('Combate')
                st.write(f'Cspm: {round(data_players["cspm"].mean(),1)}')
                st.write(
                    f'Dano%: {round(data_players["damageshare"].mean()*100,0)}%')
                st.write(f'Participação em FB: {round(data_players["firstblood"].mean()*100,0)}%')
                st.write(f'Vitima de FB: {round(data_players["firstbloodvictim"].mean()*100,0)}%')
                st.write(f'KDA: {round((data_players["kills"].mean()+data_players["assists"].mean())/data_players["deaths"].mean(),1)}')
                st.write(f'DPM:{round(data_players["dpm"].mean(),1)}')








except Exception as e:
    st.subheader('Esperando Dados...')
    print(f"Erro na função process_data(): {str(e)}")





