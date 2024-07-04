import streamlit as st
import pandas as pd
import altair as alt

# Load the data
df = pd.read_csv('railway.csv')

# Preprocess data (same as above)
df['Date of Purchase'] = pd.to_datetime(df['Date of Purchase'])
df['Date of Journey'] = pd.to_datetime(df['Date of Journey'])
df['Time of Purchase'] = pd.to_datetime(df['Time of Purchase']).dt.time
df['Departure Time'] = pd.to_datetime(df['Departure Time']).dt.time
df['Arrival Time'] = pd.to_datetime(df['Arrival Time']).dt.time
df['Actual Arrival Time'] = pd.to_datetime(df['Actual Arrival Time']).dt.time
df.fillna(value={'Railcard': 'None', 'Reason for Delay': 'No delay'}, inplace=True)

# Streamlit dashboard layout
st.title("Low-Fidelity Prototype of Dashboard")

source = st.selectbox("Select Source:", df['Departure Station'].unique())
destination = st.selectbox("Select Destination:", df['Arrival Destination'].unique())

# Filter data based on selections
filtered_df = df[(df['Departure Station'] == source) & (df['Arrival Destination'] == destination)]

st.subheader("Distribution of Price for this trip")
price_chart = alt.Chart(filtered_df).transform_density(
    'Price',
    as_=['Price', 'density']
).mark_area(color='green').encode(
    x='Price:Q',
    y='density:Q'
)

# Function to create pie charts
def create_pie_chart(data, column, title):
    pie_data = data[column].value_counts().reset_index()
    pie_data.columns = [column, 'count']
    
    pie_chart = alt.Chart(pie_data).mark_arc().encode(
        theta=alt.Theta(field="count", type="quantitative"),
        color=alt.Color(field=column, type="nominal", legend=alt.Legend(title=title)),
        tooltip=[column, 'count']
    ).properties(
        title=title
    )
    return pie_chart

purchase_type_chart = create_pie_chart(filtered_df, 'Purchase Type', 'Purchase Type')
ticket_class_chart = create_pie_chart(filtered_df, 'Ticket Class', 'Ticket Class')
ticket_type_chart = create_pie_chart(filtered_df, 'Ticket Type', 'Ticket Type')

# Combine charts for display
combined_charts = alt.hconcat(
    price_chart,
    alt.vconcat(purchase_type_chart, ticket_class_chart, ticket_type_chart)
).resolve_legend(
    color="independent"
)

st.altair_chart(combined_charts, use_container_width=True)
