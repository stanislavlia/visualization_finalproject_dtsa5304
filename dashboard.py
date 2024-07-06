import streamlit as st
import pandas as pd
import altair as alt

# CSS to inject contained in a string
st.markdown(
    """
    <style>
    .small-box {
        width: 50px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def build_price_histogram(filtered_df):
    if filtered_df.empty:
        return None
    
    max_price = filtered_df["Price"].max() if not filtered_df["Price"].empty else 100  # Ensure there's a max price
    hist_chart = alt.Chart(filtered_df).mark_bar(color='yellow').encode(
        alt.X('Price:Q', bin=alt.Bin(maxbins=30),
              title='Ticket Price (pounds)', 
              scale=alt.Scale(domain=[0, max_price]),
              axis=alt.Axis(tickCount=10)),
        alt.Y('count():Q', title='Count')
    ).properties(
        width=450,  # Reduced width
        height=300,  # Reduced height
        title=f"Price for this trip"
    )

    return hist_chart

def create_pie_chart(data, column, title):
    pie_data = data[column].value_counts().reset_index()
    pie_data.columns = [column, 'count']
    
    pie_chart = alt.Chart(pie_data).mark_arc().encode(
        theta=alt.Theta(field="count", type="quantitative"),
        color=alt.Color(field=column, type="nominal", 
                        legend=alt.Legend(title=title), 
                        scale=alt.Scale(domain=pie_data[column].tolist(),
                                        range=["#FFFF66", "#FFFF33", "#FFFF00", "#FFCC00", "#FFCC33"])),
        tooltip=[column, 'count']
    ).properties(
        width=75,  # Reduced width
        height=75,  # Reduced height
        title=title
    )

    return pie_chart

def main():
    st.title("UK Railways Train Ticket Dashboard")

    # Load data 
    try:
        df = pd.read_csv("railway.csv")
    except FileNotFoundError:
        st.error("File not found. Please make sure 'railway.csv' is in the correct directory.")
        return
    except pd.errors.EmptyDataError:
        st.error("The file is empty. Please provide a valid CSV file.")
        return
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return

    options_source = ['Birmingham New Street', 'Liverpool Lime Street', 'York',
                      'Manchester Piccadilly', 'Reading']
    
    options_dest = ['Liverpool Lime Street', 'Manchester Piccadilly', 'London Euston', 
                    'London Paddington', 'London Kings Cross']
    
    col1, col2 = st.columns([1, 1])

    with col1:
        source = st.selectbox("Select Source:", options_source)
    with col2:
        destination = st.selectbox("Select Destination:", options_dest)

    st.write(
        """
        <style>
        .stSelectbox > div > div > div > select {
            width: 50px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Filter data based on selections
    filtered_df = df[(df["Departure Station"] == source) & (df["Arrival Destination"] == destination)]

    # Display filtered data count
    st.write(f"Number of records: {len(filtered_df)}")

    hist_chart = build_price_histogram(filtered_df)
    
    if hist_chart:
        # Create pie charts
        purchase_type_chart = create_pie_chart(filtered_df, 'Purchase Type', 'Purchase Type')
        ticket_class_chart = create_pie_chart(filtered_df, 'Ticket Class', 'Ticket Class')
        ticket_type_chart = create_pie_chart(filtered_df, 'Ticket Type', 'Ticket Type')

        # Combine charts
        combined_chart = alt.hconcat(
            hist_chart,
            alt.vconcat(purchase_type_chart, ticket_class_chart, ticket_type_chart).resolve_scale(color='independent')
        ).resolve_legend(
            color="independent"
        )

        st.altair_chart(combined_chart, use_container_width=True)
    else:
        st.write("No data available for the selected route.")

if __name__ == "__main__":
    main()
