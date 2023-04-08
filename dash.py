import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events


st.set_page_config(page_title = 'Russia Ukraine Dashboard',
                   layout='wide'
                   )
st.markdown("""<style>
               .main {
                background-color: #E8E8E8
                }
                </style>
                """,
                unsafe_allow_html = True)

header_left,header_mid,header_right = st.columns([1,2,1],gap='large')

with header_left:
    st.image('images/pic.png',width=100)
    st.subheader("Losses of Russia")
with header_mid:
    st.title('Russia Ukraine War Dashboard')

tab_titles = ["Total Losses","Personnel Losses","Equipment Losses"]
tabs = st.tabs(tab_titles) 
with tabs[0]:
    
    Personnel = pd.read_csv("data//russia_losses_personnel.csv")
    Equipment = pd.read_csv("data//russia_losses_equipment.csv")

    Personnel['date']= pd.to_datetime(Personnel['date']).dt.date
    Equipment['date']= pd.to_datetime(Equipment['date']).dt.date

    Equipment = Equipment.fillna(0)
    Equipment['vehicles and fuel tanks'] = Equipment['military auto'] + Equipment['fuel tank'] + Equipment['vehicles and fuel tanks']
    Personnel.drop(['day','POW','personnel*'], axis=1, inplace=True)
    Equipment.drop(['day','military auto', 'fuel tank', 'greatest losses direction'], axis=1, inplace=True)

    first_date = Personnel["date"].min()
    Personnel["days_since_start"] = (Personnel["date"] - first_date).dt.days + 1
    Personnel["week"] = np.ceil(Personnel["days_since_start"] / 7).astype(int)
    Personnel['month'] = np.ceil(Personnel['days_since_start'] / 30).astype(int)


    first_date = Equipment["date"].min()
    Equipment["days_since_start"] = (Equipment["date"] - first_date).dt.days + 1
    Equipment['month'] = np.ceil(Equipment['days_since_start'] / 30).astype(int)

    Personnel["daily_loss"] = Personnel["personnel"].diff().fillna(Personnel["personnel"])



    col1,col2,col3 = st.columns(3,gap='large')
    with col1:
        max_day =Personnel["days_since_start"].max()
        st.metric(label = '**Day since War Begin**', value= int(max_day))

    with col2:
        person_loss =Personnel["personnel"].max()
        st.metric(label = '**Loss of Personnel**', value= int(person_loss))

    with col3:
        equipment_loss = Equipment.drop([ "date","days_since_start","month"], axis=1).max().sum()
        st.metric(label = '**Loss of Equipment**', value= int(equipment_loss))
    

        
    st.subheader("Equipment Losses") 
    col1, col2 = st.columns(2,gap='large')

    air_columns = ['aircraft', 'helicopter', 'mobile SRBM system', 'drone']
    field_columns = ['tank','APC','field artillery','MRL','vehicles and fuel tanks','special equipment','anti-aircraft warfare']
    water_columns = ['naval ship','cruise missiles']
    with col1:
        air_loss = Equipment[air_columns].max().sum()
        field_loss = Equipment[field_columns].max().sum()
        water_loss = Equipment[water_columns].max().sum()
        fig1 = go.Figure()

        fig1.add_trace(go.Bar(x=['Air'], y=[air_loss], name='Air Equipments', text=[f'{int(air_loss):,}'], textposition='outside', texttemplate='<b><span style="color:black">%{text}</span></b>'))
        fig1.add_trace(go.Bar(x=['Water'], y=[water_loss], name='Water Equipments', text=[f'{int(water_loss):,}'], textposition='outside', texttemplate='<b><span style="color:black">%{text}</span></b>'))
        fig1.add_trace(go.Bar(x=['Field'], y=[field_loss], name='Field Equipments', text=[f'{int(field_loss):,}'], textposition='outside', texttemplate='<b><span style="color:black">%{text}</span></b>'))


        fig1.update_layout(title='Total Losses by Equipment Categories',
                        xaxis_title='Total Losses',
                        yaxis_title='Categories')

        st.plotly_chart(fig1)
    with col2:
        air_loss_by_month = Equipment.groupby('month')[air_columns].max().sum(axis=1)
        field_loss_by_month = Equipment.groupby('month')[field_columns].max().sum(axis=1)
        water_loss_by_month = Equipment.groupby('month')[water_columns].max().sum(axis=1)

        df = pd.concat([air_loss_by_month, field_loss_by_month, water_loss_by_month], axis=1)
        df.columns = ['Air', 'Field', 'Water']

        df = df.reset_index()

        fig = px.line(df, x='month', y=df.columns[1:], title='Monthly Loss by Equipment Category', markers=True)
        st.plotly_chart(fig)


    st.subheader("Personnel Losses") 

    col1, col2 = st.columns(2,gap='large')
    with col1:
        fig = px.line(Personnel, x='date', y="personnel",color_discrete_sequence=['blue'],markers=True)
        
        fig.update_layout(title='Total Losses ',
                        yaxis_title='Total Losses',
                        xaxis_title= 'Month')
        st.plotly_chart(fig)

    with col2:
        monthly_loss = Personnel.groupby('month')['daily_loss'].sum()
        fig2 = px.line(monthly_loss, x=monthly_loss.index, y=monthly_loss.values,markers=True,text=monthly_loss.values)
        fig2.update_traces(textposition='top center', textfont=dict(color='black'), line=dict(color='blue'))

        fig2.update_layout(title='Monthly Personnel Losses',
                        yaxis_title='Losses',
                        xaxis_title='Month')
        st.plotly_chart(fig2)

with tabs[1]:
        
    st.subheader("Personnel Losses") 

    Personnel1 = pd.read_csv("data//russia_losses_personnel.csv")

    Personnel1['date']= pd.to_datetime(Personnel1['date']).dt.date

    Personnel1.drop(['day','POW','personnel*'], axis=1, inplace=True)

    col1,col2= st.columns(2)
    with col1:
        date_range = st.slider("**Date Range**", min_value=Personnel1['date'].min(), max_value=Personnel1['date'].max(), value=(Personnel1['date'].min(), Personnel1['date'].max()))
        start_date, end_date = date_range
        filtered_Personnel = Personnel1[(Personnel1['date'] >= start_date) & (Personnel1['date'] <= end_date)]
    first_d = filtered_Personnel["date"].min()
    filtered_Personnel["days_since_start"] = (filtered_Personnel["date"] - first_d).dt.days + 1
    filtered_Personnel["daily_loss"] = filtered_Personnel["personnel"].diff().fillna(0)
    num_days = (filtered_Personnel['date'].max() - filtered_Personnel['date'].min()).days + 1
    filtered_Personnel['month'] = np.ceil(filtered_Personnel['days_since_start'] / 30).astype(int)
    filtered_Personnel["week"] = np.ceil(filtered_Personnel["days_since_start"] / 7).astype(int)


    col1,col2,col3,col4 = st.columns(4,gap='large')
    with col1:
        num_days = (filtered_Personnel['date'].max() - filtered_Personnel['date'].min()).days + 1
        st.metric(label = '**Number of days**', value = int(num_days))
    with col2:
        loss =filtered_Personnel["daily_loss"].sum()
        st.metric(label = '**Loss of Personnel**', value= int(loss))

    with col3:
        avg_loss =filtered_Personnel["daily_loss"].sum() / filtered_Personnel["days_since_start"].max()
        st.metric(label = '**Average lives lost per day**', value= int(avg_loss))

    with col4:
        highest_loss = filtered_Personnel["daily_loss"].max()
        highest_loss_date = filtered_Personnel.loc[filtered_Personnel["daily_loss"] == highest_loss, "date"].iloc[0]
        st.metric(label=f'**Highest number of losses in single day\n({highest_loss_date})**', value=int(highest_loss))


    header_left,header_mid,header_right = st.columns([1,2,1],gap='large')
    selected_month = st.session_state.get('selected_month', None)
    selected_week = st.session_state.get('selected_week', None)

    with header_mid:
        st.header("Monthly Personnel Loss")
        st.write("In this chart you can see a month of losses by selecting a bar ")
        p_monthly_loss = filtered_Personnel.groupby('month')['daily_loss'].sum()
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
        x=p_monthly_loss.index,
        y=p_monthly_loss.values,
        marker_color='blue',
        opacity=0.7,
        text=p_monthly_loss.values,
        textposition='outside',texttemplate='<b><span style="color:black">%{text}</span></b>',
                    hovertemplate='Loss: %{y}<extra></extra>'

            ))

        fig1.update_layout(title='Monthly Personnel Loss',
                        xaxis_title='Month', yaxis_title='Loss')

        selected_points = plotly_events(fig1)
        if selected_points:
            selected_month = selected_points[0]['x']
            st.session_state['selected_month'] = selected_month
    col1, col2 = st.columns(2, gap='large')

    with col1:
        if selected_month:
            filtered_month = filtered_Personnel[filtered_Personnel['month'] == selected_month]
            filtered_month.index = pd.to_datetime(filtered_month.index)
            first_d = filtered_month["date"].min()
            filtered_month["days_since_start_month"] = (filtered_month["date"] - first_d).dt.days + 1
            filtered_month["weeks"] = np.ceil(filtered_month["days_since_start_month"] / 7).astype(int)
            p_weekly_loss = filtered_month.groupby('weeks')['daily_loss'].sum()

            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=p_weekly_loss.index,
                y=p_weekly_loss.values,
                opacity=0.7,
                text=p_weekly_loss.values,
                textposition='outside',
                marker_color='green',
                hovertemplate='Loss: %{y}<extra></extra>'
            ))


            fig2.update_layout(title=f'Weekly Personnel Loss for {selected_month}',
                            xaxis_title='Week', yaxis_title='Loss')

            st.header(f"Weekly Personnel Loss for month {selected_month} ")
            st.write("**In this chart you can see a weekly losses by selecting a bar**")    

            selected_points = plotly_events(fig2)
            if selected_points:
                selected_week = int(selected_points[0]['x'])
                st.session_state['selected_week'] = selected_week

    with col2:
        if selected_week:
            filtered_week = filtered_month[filtered_month['weeks'] == selected_week]
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=filtered_week['date'],
                y=filtered_week['daily_loss'],
                mode='lines+markers',
                marker_color='red',
                hovertext=filtered_week['daily_loss'].values,
            ))

            fig3.update_layout(
                title=f'Daily Personnel Loss for Week {selected_week} in month {selected_month}',
                xaxis_title='Date',
                yaxis_title='Loss'
            )

            st.header(f"Daily Personnel Loss for Week {selected_week}")
            st.plotly_chart(fig3)

with tabs[2]:
    
    st.subheader("Equipment Losses") 
    Equipment1 = pd.read_csv("data//russia_losses_equipment.csv")
    Equipment1['date'] = pd.to_datetime(Equipment1['date']).dt.date

    Equipment1 = Equipment1.fillna(0)
    Equipment1['vehicles and fuel tanks'] = Equipment1['military auto'] + Equipment1['fuel tank'] + Equipment1['vehicles and fuel tanks']
    Equipment1.drop(['day', 'military auto', 'fuel tank', 'greatest losses direction'], axis=1, inplace=True)
    col1, col2 = st.columns(2)

    with col1:
        date_filter = st.slider("**Duration**", min_value=Equipment1['date'].min(), max_value=Equipment1['date'].max(), value=(Equipment1['date'].min(), Equipment1['date'].max()))
        start_date, end_date = date_filter
        filtered_Equipment = Equipment1[(Equipment1['date'] >= pd.to_datetime(start_date)) & (Equipment1['date'] <= pd.to_datetime(end_date))]

        selected_columns = ['aircraft', 'helicopter', 'mobile SRBM system', 'drone', 'tank', 'APC', 'field artillery', 'MRL', 'vehicles and fuel tanks', 'special equipment', 'anti-aircraft warfare', 'naval ship', 'cruise missiles']

        categories = st.multiselect('**Select categories**', ['Air', 'Field', 'Water'])
        if categories:
            air_columns = ['aircraft', 'helicopter', 'mobile SRBM system', 'drone'] if 'Air' in categories else []
            field_columns = ['tank', 'APC', 'field artillery', 'MRL', 'vehicles and fuel tanks', 'special equipment', 'anti-aircraft warfare'] if 'Field' in categories else []
            water_columns = ['naval ship', 'cruise missiles'] if 'Water' in categories else []

            selected_columns = []
            if air_columns:
                selected_columns += air_columns
            if field_columns:
                selected_columns += field_columns
            if water_columns:
                selected_columns += water_columns

            equipment_filter = st.multiselect('**Select Equipment**', selected_columns, default=selected_columns)
            if not equipment_filter:
                filtered_Equipment = filtered_Equipment.copy()
                selected_columns = selected_columns.copy()
            else:
                filtered_Equipment = filtered_Equipment[['date'] + equipment_filter]
                selected_columns = equipment_filter.copy()
        
    col1,col2,col3,col4 = st.columns(4,gap='large')

    with col1:
        num_days_e = (filtered_Equipment['date'].max() - filtered_Equipment['date'].min()).days + 1
        st.metric(label = '**Number of days**', value = int(num_days_e))

    with col2:
        equipment_loss1 = filtered_Equipment.drop([ "date"], axis=1).max().sum()
        st.metric(label = '**Loss of Equipment**', value= int(equipment_loss1))

    with col3:
        avg_equip_loss = equipment_loss1 / num_days_e
        st.metric(label = '**Average Loss of Equipment**', value= int(avg_equip_loss))
    

    header_left,header_mid,header_right = st.columns([1,2,1],gap='large')

        
    first_D = filtered_Equipment["date"].min()
    filtered_Equipment["days_since_start"] = (filtered_Equipment["date"] - first_D).dt.days + 1

    daily_loss = filtered_Equipment[selected_columns].diff().fillna(filtered_Equipment[selected_columns])
    daily_loss[daily_loss < 0] = 0

    filtered_Equipment[selected_columns] = daily_loss

    filtered_Equipment['month'] = np.ceil(filtered_Equipment['days_since_start'] / 30).astype(int)
    grouped_equipment = filtered_Equipment.groupby('month', as_index=False).sum()
    colors = px.colors.qualitative.Dark2
        
    fig = px.bar(grouped_equipment, x='month', y=selected_columns, title='Monthly Equipment Counts',
                labels={'month': 'Month', 'value': 'Counts'},color_discrete_sequence=colors,opacity=0.8
                )

    fig.update_traces(textposition='outside', hovertemplate=None)

    fig.update_layout(barmode='stack', showlegend=True)
    selected_month = st.session_state.get('selected_month', None)
    selected_week = st.session_state.get('selected_week', None)

    with header_mid:
        st.header("Monthly Equipment Losses")
        st.write("**In this chart you can see a month of losses by selecting a bar**")    
        selected_points = plotly_events(fig)
        if selected_points:
            selected_month = selected_points[0]['x']
            st.session_state["selected_month"] = selected_month

    plot3, plot4 = st.columns(2,gap='large')
    
    with plot3:
        if selected_month:
            filtered_month = filtered_Equipment[filtered_Equipment["month"] == selected_month]
            filtered_month["date"] = pd.to_datetime(filtered_month["date"]).dt.date
            filtered_month["days_since_start_month"] = (filtered_month["date"] - first_D).dt.days + 1
            filtered_month["days_since_start_week"] = filtered_month["days_since_start_month"] - 1
            filtered_month["week"] = np.floor((filtered_month["days_since_start_week"] - filtered_month["days_since_start_week"].min()) / 7).astype(int) + 1

            grouped_week = filtered_month.groupby("week", as_index=False).sum()
            colors = px.colors.qualitative.Dark2

            fig_week = px.bar(grouped_week, x="week", y=selected_columns, title=f"Weekly Equipment Counts for Month {selected_month}",
                            labels={'month': 'Week', 'value': 'Counts'},color_discrete_sequence=colors,opacity=0.7)
            fig.update_traces(textposition='outside', hovertemplate='')

            fig_week.update_layout(barmode='stack', showlegend=True)

            num_weeks = len(grouped_week)
            x_tick_labels = [f"Week {i+1}" for i in range(num_weeks)]
            fig_week.update_xaxes(tickmode='array', tickvals=grouped_week['week'], ticktext=x_tick_labels)

            st.header(f"Weekly Equipment Loss for month {selected_month} ")
            st.write("**In this chart you can see a weekly losses by selecting a bar**")    

            week_event = plotly_events(fig_week)
            if week_event:
                selected_week = week_event[0]['x']
                st.session_state["selected_week"] =  selected_week

    with plot4:            

        if selected_week:
            filtered_week = filtered_month[filtered_month["week"] == selected_week]
            filtered_week_grouped = filtered_week.groupby("date", as_index=False).sum()
            fig_daily_loss = px.line(filtered_week_grouped, x="date", y=selected_columns, title=f"Daily Loss for Week {st.session_state['selected_week']} in month {selected_month}")
            fig_daily_loss.update_traces(mode="markers+lines")

            st.header(f"Daily Equipment Loss for week {st.session_state['selected_week']}")
            st.plotly_chart(fig_daily_loss, use_container_width=True)
