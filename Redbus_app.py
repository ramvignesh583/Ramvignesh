import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
# Function to fetch data from the database

def fetch_data(query):
    mydb = mysql.connector.connect(
        user='root',
        password='Ramvignesh@123',
        host='127.0.0.1',
        database='redbus'
    )
    cursor = mydb.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    mydb.close()
    return data

# Function to fetch unique values for a specific column
def fetch_unique_values(column_name):
    mydb = mysql.connector.connect(
        user='root',
        password='Ramvignesh@123',
        host='127.0.0.1',
        database='redbus'
    )
    cursor = mydb.cursor()
    query = f"SELECT DISTINCT `{column_name}` FROM redbus_details"
    cursor.execute(query)
    values = [row[0] for row in cursor.fetchall()]
    cursor.close()
    mydb.close()
    return values

st.set_page_config(layout="wide")

st.markdown("<h1 style='text-align: center;'>RedBus Bus Details and Analysis</h1>", unsafe_allow_html=True)

st.sidebar.image("data/file.png")

page = st.sidebar.radio("Go to", ["Bus Details", "Data Analysis"])

if page == "Bus Details":
    mydb = mysql.connector.connect(
        user='root',
        password='Ramvignesh@123',
        host='127.0.0.1',
        database='redbus'
    )
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM redbus_details")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
    cursor.close()
    mydb.close()

    # Display the initial data in an expander
    with st.expander("Bus Route and Bus Details"):
        st.dataframe(df)

    # Fetch unique values for Route Name, Bus Name, and Bus Type
    unique_routes = fetch_unique_values('Route Name')
    unique_bus_names = fetch_unique_values('Bus Name')
    unique_bus_types = fetch_unique_values('Bus Type')

    # Sidebar filters
    route_name = st.sidebar.selectbox("Select Route Name:", [""] + unique_routes)
    bus_name = st.sidebar.selectbox("Select Bus Name:", [""] + unique_bus_names)
    bus_type = st.sidebar.selectbox("Select Bus Type:", [""] + unique_bus_types)
    min_price, max_price = st.sidebar.slider("Select Price Range:", min_value=0, max_value=10000, value=(0, 10000), step=100)
    min_rating, max_rating = st.sidebar.slider("Select Rating Range:", min_value=0.0, max_value=5.0, value=(0.0, 5.0), step=0.1)
    start_time = st.sidebar.time_input("Select Start Time:", value=pd.to_datetime("00:00").time())
    end_time = st.sidebar.time_input("Select End Time:", value=pd.to_datetime("23:59").time())

    # Generate the query based on filters
    query = "SELECT * FROM redbus_details WHERE 1=1"
    if route_name:
        query += f" AND `Route Name` = '{route_name}'"
    if bus_name:
        query += f" AND `Bus Name` = '{bus_name}'"
    if bus_type:
        query += f" AND `Bus Type` = '{bus_type}'"
    query += f" AND `Price` BETWEEN {min_price} AND {max_price}"
    query += f" AND `Bus Rating` BETWEEN {min_rating} AND {max_rating}"
    query += f" AND `Departure Time` >= '{start_time}'"
    query += f" AND `Arrival Time` <= '{end_time}'"

    # Fetch and display filtered data
    data = fetch_data(query)
    columns_query = "SHOW COLUMNS FROM redbus_details"
    columns = [col[0] for col in fetch_data(columns_query)]
    if data:
        df = pd.DataFrame(data, columns=columns)
        st.write("Search Results:")
        st.dataframe(df)
        st.session_state['df'] = df
    else:
        st.write("No results found for the given filters.")

elif page == "Data Analysis":
    st.markdown("<h2 style='text-align: center;'>Data Analysis</h2>", unsafe_allow_html=True)
    if 'df' in st.session_state:
        df = st.session_state['df']
        col1, col2, col3, col4= st.columns(4)
        with col1:
            st.metric("Total Buses", len(df))
            fig_gauge_total_buses = go.Figure(go.Indicator(
                mode="gauge+number",
                value=len(df),
                title={'text': "Total Buses"},
                gauge={'axis': {'range': [None, 100]}}
            ))
            st.plotly_chart(fig_gauge_total_buses)
    
        with col2:
            avg_price = df['Price'].mean()
            st.metric("Average Price", f"{avg_price:.2f}")
            fig_gauge_avg_price = go.Figure(go.Indicator(
                mode="gauge+number",
                value=avg_price,
                title={'text': "Average Price"},
                gauge={'axis': {'range': [None, 10000]}}
            ))
            st.plotly_chart(fig_gauge_avg_price)

        with col3:
            avg_rating = df['Bus Rating'].mean()
            st.metric("Average Rating", f"{avg_rating:.2f}")
            fig_gauge_avg_rating = go.Figure(go.Indicator(
                mode="gauge+number",
                value=avg_rating,
                title={'text': "Average Rating"},
                gauge={'axis': {'range': [None, 5]}}
            ))
            st.plotly_chart(fig_gauge_avg_rating)

        with col4:
            total_seats = df['Available Seats'].sum()
            st.metric("Total Seats Available", total_seats)
            fig_gauge_total_seats = go.Figure(go.Indicator(
                mode="gauge+number",
                value=total_seats,
                title={'text': "Total Seats Available"},
                gauge={'axis': {'range': [None, 1000]}}
            ))
            st.plotly_chart(fig_gauge_total_seats)
    
        fig_scatter = px.scatter(df, x='Price', y='Bus Rating', color='Bus Type', title='Scatter Plot of Price vs Rating')
        st.plotly_chart(fig_scatter)

        fig_box = px.box(df, x='Bus Type', y='Price', title='Box Plot of Price by Bus Type')
        st.plotly_chart(fig_box)
    
        st.markdown("#### Histogram for Price Distribution")
        plt.figure(figsize=(10, 6))
        sns.histplot(df['Price'], bins=30, kde=True)
        st.pyplot(plt)
    
        fig_pie = px.pie(df, names='Bus Type', title='Bus Type Distribution')
        st.plotly_chart(fig_pie)
    
        df_sorted = df.sort_values('Departure Time')
        fig_line = px.line(df_sorted, x='Departure Time', y='Price', title='Line Chart of Price over Time')
        st.plotly_chart(fig_line)
    
        st.markdown("#### Hexagonal Bin Plot of Price vs Rating")
        plt.figure(figsize=(10, 6))
        plt.hexbin(df['Price'], df['Bus Rating'], gridsize=30, cmap='Blues')
        plt.colorbar(label='Count')
        plt.xlabel('Price')
        plt.ylabel('Bus Rating')
        st.pyplot(plt)
    
        fig_3d = px.scatter_3d(df, x='Price', y='Bus Rating', z='Departure Time', color='Bus Type', title='3D Plot of Price, Rating, and Departure Time')
        st.plotly_chart(fig_3d)
    
        fig_scatter_seats = px.scatter(df, x='Price', y='Available Seats', color='Bus Type', title='Scatter Plot of Price vs Seats Available')
        st.plotly_chart(fig_scatter_seats)
    
        fig_box_duration = px.box(df, x='Bus Type', y='Duration', title='Box Plot of Duration by Bus Type')
        st.plotly_chart(fig_box_duration)

    else:
        st.write("No data to display. Please go to the Main Page and apply filters first.")
