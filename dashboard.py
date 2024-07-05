import streamlit as st
import pandas as pd
import altair as alt

# CSS to inject contained in a string
st.markdown(
    """
    <style>
    .small-box {
        width: 100px !important;
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
              scale=alt.Scale(domain=[0, max_price])),
        alt.Y('count():Q', title='Count')
    ).properties(
        width=700,
        height=400,
        title=f"Price for this trip",
    ).configure_axis(
        grid=False,
        tickCount=10,
    )

    return hist_chart

def main():
    st.title("UK Railways Train Ticket Dashboard")

    # Load data 
    df = pd.read_csv("railway.csv")

    options_source = ['Birmingham New Street', 'Liverpool Lime Street', 'York',
                        'Manchester Piccadilly', 'Reading']
    
    options_dest = ['Liverpool Lime Street', 'Manchester Piccadilly', 'London Euston', 
       'London Paddington', 'London Kings Cross']
    
    col1, col2 = st.columns([1, 1])

    with col1:
        source = st.selectbox("Select Source:", options_source, )
    with col2:
        destination = st.selectbox("Select Destination:",  options_dest,)

    st.write(
        """
        <style>
        .stSelectbox > div > div > div > select {
            width: 100px !important;
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
        st.altair_chart(hist_chart, use_container_width=True)
    else:
        st.write("No data available for the selected route.")

if __name__ == "__main__":
    main()
