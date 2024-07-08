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
    .stSelectbox > div > div > div > select {
        width: 50px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def build_price_histogram(filtered_df):
    if filtered_df.empty:
        return None
    
    max_price = filtered_df["Price"].max() if not filtered_df["Price"].empty else 100 
    total_count = len(filtered_df)
    
    # Create the histogram with fractions
    hist_chart = alt.Chart(filtered_df).transform_bin(
        "binned_price",
        "Price",
        bin=alt.Bin(maxbins=30)
    ).transform_aggregate(
        count='count()',
        groupby=["binned_price"]
    ).transform_calculate(
        fraction="datum.count / ({} * 1)".format(total_count)
    ).mark_bar(color='yellow').encode(
        alt.X('binned_price:Q', title='Ticket Price (pounds)',
              scale=alt.Scale(domain=[0, max_price]),
              axis=alt.Axis(values=list(range(0, int(max_price) + 1, 5)))),
        alt.Y('fraction:Q', title='Percentage', axis=alt.Axis(format='.1%'),
              scale=alt.Scale(domain=[0, 0.7])),
        tooltip=[alt.Tooltip('binned_price:Q', title='Price'), alt.Tooltip('fraction:Q', format='.1f', title='Percentage')]
    ).properties(
        width=600,  
        height=400,  
        title=f"Price for this trip"
    )

    return hist_chart

def create_pie_chart(data, column, title):
    pie_data = data[column].value_counts().reset_index()
    pie_data.columns = [column, 'count']
    pie_data['percentage'] = pie_data['count'] / pie_data['count'].sum() * 100
    tooltip=[column, 'count', alt.Tooltip('percentage:Q', format='.2f', title='Percentage % ')]
    
    pie_chart = alt.Chart(pie_data).mark_arc().encode(
        theta=alt.Theta(field="count", type="quantitative"),
        color=alt.Color(field=column, type="nominal", 
                        legend=alt.Legend(title=title), 
                        scale=alt.Scale(domain=pie_data[column].tolist(),
                                        range=["#FFD700", "#FFA500", "#FFFF00", "#FFD700", "#FFEC8B"])),
        tooltip=tooltip
    ).properties(
        width=95,  # Reduced width
        height=95,  # Reduced height
        title=title
    )

    return pie_chart

def main():
    st.markdown(
        """
        <h2 style="text-align: center;">
            <img src="https://upload.wikimedia.org/wikipedia/en/a/ae/Flag_of_the_United_Kingdom.svg" alt="UK Flag" width="60">
            UK Railways Train Ticket Dashboard
        </h2>
        """,
        unsafe_allow_html=True
    )

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

    options_source = ['Birmingham New Street', 'Liverpool Lime Street',
                      'Manchester Piccadilly', 'Reading']
    
    options_dest = ['Liverpool Lime Street', 'Manchester Piccadilly', 'London Euston', 
                    'London Paddington', 'London Kings Cross']
    
    col1, col2 = st.columns([1, 1])

    with col1:
        source = st.selectbox("Select Source:", options_source)
    with col2:
        destination = st.selectbox("Select Destination:", options_dest)

    if source == destination:
        st.warning("Your source is the same as destination!")

    filtered_df = df[(df["Departure Station"] == source) & (df["Arrival Destination"] == destination)]

    st.write(f"Number of records: {len(filtered_df)}")

    hist_chart = build_price_histogram(filtered_df)
    
    if hist_chart:
        purchase_type_chart = create_pie_chart(filtered_df, 'Purchase Type', 'Purchase Type')
        ticket_class_chart = create_pie_chart(filtered_df, 'Ticket Class', 'Ticket Class')
        ticket_type_chart = create_pie_chart(filtered_df, 'Ticket Type', 'Ticket Type')

        combined_chart = alt.hconcat(
            hist_chart,
            alt.vconcat(purchase_type_chart, ticket_class_chart, ticket_type_chart).resolve_scale(color='independent')
        ).resolve_legend(
            color="independent"
        ).configure_title(fontSize=26).configure_view(
            continuousWidth=500,
            continuousHeight=300,
            stroke=None
        )

        st.altair_chart(combined_chart, use_container_width=True)
    else:
        st.write("No data available for the selected route.")

if __name__ == "__main__":
    main()
