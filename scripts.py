import pandas as pd
import sqlite3
import plotly.express as px
import time

def generate_search_dataframe(query: str, params: list):
    conn = sqlite3.connect('shoe-data.db')

    df = pd.read_sql_query(query, conn, params=params)
    df['sale_price'] = df['sale_price'] // 100
    df['sale_time'] = pd.to_datetime(df['sale_time'], unit='s')
    df.rename(columns={'sale_price': 'Shoe Price', 'sale_time': 'Time of Sale', 'name': 'Shoe Name'}, inplace=True)

    conn.close()
    return df


def generate_last_sale_list():
    conn = sqlite3.connect('shoe-data.db')
    query = "SELECT name, sale_price, sale_time FROM shoes AS s1 WHERE sale_time = (SELECT MAX(sale_time) FROM shoes AS s2 WHERE s1.name = s2.name) ORDER BY sale_time DESC"

    df = pd.read_sql_query(query, conn)
    df['sale_price'] = df['sale_price'] // 100
    df['sale_time'] = pd.to_datetime(df['sale_time'], unit='s')
    df.rename(columns={'sale_price': 'Shoe Price', 'sale_time': 'Time of Sale', 'name': 'Shoe Name'}, inplace=True)

    conn.close()
    return df

def generate_plotly_chart(df):
    fig = px.area(
        df, 
        x='Time of Sale', 
        y='Shoe Price', 
        title='Sale Price Over Time',
        labels={'Time of Sale': 'Time of Sale', 'Shoe Price': 'Shoe Price'},
    )

    fig.update_traces(
        hovertemplate='<b>Time of Sale:</b> %{x}<br><b>Shoe Price:</b> $%{y:.2f}',
        line=dict(color='#B8B8FF', width=2), 
        marker=dict(size=4, line=dict(width=2, color='#B8B8FF'), color='#9381FF'), 
        mode='lines+markers',
    )


    fig.update_layout(
        title='Sale Price Over Time',
        xaxis_title='Time of Sale',
        yaxis_title='Shoe Price',
        yaxis=dict(autorange=True),
        xaxis=dict(tickformat='%b %d %H:%M',nticks=10),
        showlegend=False,
    )

    return fig


def generate_average_prices(df):
    df_mean = df.groupby('Shoe Name')['Shoe Price'].mean()
    df_mean = df_mean.round(2)
    df_mean.sort_values(inplace=True, ascending=True)
    df_mean.name = 'Average Price'


    return df_mean

def generate_query(name: str, size: int, user_time: int):
    if not name.strip() and not size and not user_time:
        return None

    params = []
    
    if name.split(' '):
        name_components = name.split(' ')

    query = "SELECT name, sale_time, sale_price FROM shoes"

    if name_components:
        query += " WHERE " 
        for index, component in enumerate(name_components):
            if index > 0:
                query += " AND "  
            query += "name LIKE ?"
            params.append(f"%{component}%")

    
    if size:
        if "WHERE" not in query:  
            query += " WHERE "
        else:
            query += " AND "
        query += "size = ?"
        params.append(size)


    if user_time:
        current_time = int(time.time())
        interval = current_time - user_time

        if "WHERE" not in query:  
            query += " WHERE "
        else:
            query += " AND "
        query += "sale_time > ?"
        params.append(interval)

    query += " ORDER BY sale_time"
    
    print("Query:", query)
    print("Params:", params)


    return [query, params]



def determine_time_interval(interval: str):
    mapping = {
        'Last 24 Hours': 86400,
        'Last Week': 604800,
        'Last 2 Weeks': 1209600,
        'Last Month': 2592000
    }

    return mapping[interval]


def generate_title(attributes: dict):
    title = []

    if sneaker := attributes.get('sneaker'):
        title.append(sneaker)
    
    if size := attributes.get('size'):
        title.append(str(size) + ' M')
    
    if time := attributes.get('time'):
        title.append(str(time))
    
    return ' | '.join(title)