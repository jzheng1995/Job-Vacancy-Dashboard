import streamlit as st

page_1 = st.Page("page1.py", title = "Introduction", icon=":material/home:", default = True)
#page_2 = st.Page("page2.py", title = "Employment Status", icon=":material/space_dashboard:")
#page_3 = st.Page("page3.py", title = "Demographics", icon=":material/space_dashboard:")
pg = st.navigation([page_1])
st.set_page_config(page_title="Canada Labour Statistics", page_icon=":material/edit:", layout = 'wide')
pg.run()