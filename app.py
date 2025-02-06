import streamlit as st
from scripts import generate_search_dataframe, generate_last_sale_list, generate_plotly_chart, generate_average_prices, generate_query, determine_time_interval, generate_title

if "prev_queries" not in st.session_state:
    st.session_state.prev_queries = []


def load_page_1():
    # Title
    st.markdown("<h1 style='text-align: center;'>Sneaker Sales Dashboard</h1>", unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    # Search Bar and Filters
    with st.container():
        # Search Bar
        st.header("Search")
        sneaker_name = st.text_input("Search By Sneaker Name", placeholder="e.g., Travis Scott x Jordan 1 Mocha")
        sneaker_size = None
        timeframe_selection = None
        interval = None


        col1, col2 = st.columns([0.25, 1])        
        # Size Filter
        with col1:
            with st.container():
                if "size_clicked" not in st.session_state:
                    st.session_state.size_clicked = False

                if st.button("Search By Size"):
                    st.session_state.size_clicked = not st.session_state.size_clicked


        if st.session_state.size_clicked:
            sneaker_size = st.slider(label="Select a Size", min_value=4.0, max_value=18.0, step=0.5)
            st.write(f"Selected Size: {sneaker_size} M")  


        # Timeframe Filter
        with col2:
            with st.container():
                if "time_clicked" not in st.session_state:
                    st.session_state.time_clicked = False


                if st.button("Search By Timeframe"):
                    st.session_state.time_clicked = not st.session_state.time_clicked

        if st.session_state.time_clicked:
            timeframes = ['Last 24 Hours', 'Last Week', 'Last 2 Weeks', 'Last Month']
            timeframe_selection= st.selectbox('Select a timeframe to view the data: ', timeframes)
            interval = determine_time_interval(timeframe_selection)

        # Search Button
        st.markdown('<br>', unsafe_allow_html=True)
        with st.container():
            if st.button('Search'):
                st.session_state.sneaker = sneaker_name
                st.session_state.size = sneaker_size
                st.session_state.time = timeframe_selection

                query_and_parameters = generate_query(sneaker_name, sneaker_size, interval)

                if query_and_parameters:
                    st.session_state.query = query_and_parameters[0]
                    st.session_state.query_params = query_and_parameters[1]

                    prev_query = {
                        'sneaker': sneaker_name,
                        'size': sneaker_size,
                        'time': timeframe_selection,
                        'query': query_and_parameters[0],
                        'params': query_and_parameters[1]
                    }

                    st.session_state.prev_queries.append(prev_query)

                else:
                    st.markdown("Please provide a sneaker name, size or time interval")
                
                switch_page(2)

        st.markdown("-------------------------------")

    # Previous Queries
    if st.session_state.prev_queries:
        st.header("Previous Searches")
        with st.container():
            for index, query in enumerate(st.session_state.prev_queries):
                title = generate_title(query)
                if st.button(title, use_container_width=True, key=index):
                    st.session_state.sneaker = query['sneaker']
                    st.session_state.size = query['size']
                    st.session_state.time = query['time']
                    st.session_state.query = query['query']
                    st.session_state.query_params = query['params']

                    switch_page(2)
                
    
        st.markdown("-------------------------------")

    # Last Sales
    with st.container():
        st.header("Last Sales")
        df = generate_last_sale_list()
        st.dataframe(df.set_index(df.columns[0]), use_container_width=True)




def load_page_2():
    cols = st.columns([1, 10])

    # Back Button
    with cols[0].container():
        st.html("<span class='button'></span>")
        if st.button("←"):
            st.session_state.size_clicked = False
            st.session_state.time_clicked = False
            st.session_state.sneaker = None
            st.session_state.size = None
            st.session_state.time = None
            st.session_state.query = None
            st.session_state.query_params = None
            switch_page(1)

    # Search Results, Average and Data
    with cols[1].container():
        # Search Results
        st.markdown("<h1 style='text-align: center;'>Search Results</h1>", unsafe_allow_html=True)

        with st.container():
            st.markdown(f"<h6>Results For: {generate_title(st.session_state.prev_queries[-1])}</h6>", unsafe_allow_html=True)

        st.markdown("-------------------------------")


        with st.container():
            if st.session_state.query and st.session_state.query_params:
                query = st.session_state.query
                params = st.session_state.query_params

                df = generate_search_dataframe(query=query, params=params)
                df_mean = generate_average_prices(df)

                if not df.empty:
                    # Search Graph
                    with st.container():
                        fig = generate_plotly_chart(df)

                        st.subheader('Sale Price v. Time')
                        st.plotly_chart(fig)
                    st.markdown("-------------------------------")

                    # Search Data
                    with st.container():
                        st.subheader('All Sales')
                        st.dataframe(df.set_index(df.columns[0]), use_container_width=True)
                        
                        # Mean Data
                        st.subheader("Average Prices")
                        st.dataframe(df_mean, use_container_width=True)
                                                
                else:
                    st.markdown("No Results found for your search.")

            else:
                st.markdown("No Results found for your search.")


    

# Page Functionality
def switch_page(page_number: int):
    st.session_state.page = f'Page {page_number}'
    st.rerun()    

if 'page' not in st.session_state:
    st.session_state.page = 'Page 1'

if st.session_state.page == 'Page 1':
    load_page_1()
elif st.session_state.page == 'Page 2':
    load_page_2()