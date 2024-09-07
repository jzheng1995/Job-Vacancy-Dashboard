import pandas as pd
import streamlit as st
from helper import *
import altair as alt
from datetime import datetime

# unadjusted df
unadjusted = DashDf()
unadjusted.add_df()
unadjusted.preprocess()

# unadj df - filter rows
prov_df = Filtered(unadjusted.get_df('14100371'))
prov_df.pivot(['GEO', 'REF_DATE'], 'Statistics','VALUE')
prov_df.date('2020-01-01', '2024-06-01')

# province choice selections
prov_names = prov_df.df['GEO'].unique().tolist()

# callback functions for prov selections
if 'prov_select' not in st.session_state:
    st.session_state.all_option = False
    st.session_state.prov_select = ['Canada']

def check_change():
    if st.session_state.all_option:
        st.session_state.prov_select = prov_names
    else:
        st.session_state.prov_select = ['Canada']
    return
def multi_change():
    if len(st.session_state.prov_select) == len(prov_names):
        st.session_state.all_option = True
    else:
        st.session_state.all_option = False
    return

#if 'date_select' not in st.session_state:
    #st.session_state.date_select = ['2024-06-01']



# unadj df NAICS - filter rows
sector_df = Filtered(unadjusted.get_df('14100372'))
sector_df.pivot(['NAICS', 'REF_DATE'], 'Statistics','VALUE')
sector_df.date('2020-01-01', '2024-06-01')

# layout
with st.container():
    st.markdown("<h1 style='text-align: center; color: deepskyblue;'>Canada Job Vacancy Dashboard</h1>", unsafe_allow_html=True)

    with st.container(border = True):
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.write('## Job vacancy rates across time: :orange[Use Dropdown to compare provinces &rarr;]')
            with st.container(border=True):
                # line chart - prov selection for df
                geo_prov_unadjusted = filter_choices(prov_df.df, 'GEO', st.session_state.prov_select)

                # altair elements
                time_axis = alt.Axis(format='%Y %b')
                hover = alt.selection_single(fields=['REF_DATE'], on='mouseover', nearest=True, empty='none', name='date')
                selection_date = alt.selection_single(encodings = ['x'],empty='none', nearest = True )

                # tooltips
                datetip = alt.Tooltip('REF_DATE:T', title='Date: ')
                regiontip = alt.Tooltip('GEO:N', title='Province: ')
                jvrtip = alt.Tooltip('Job vacancy rate:Q', title='Job vacancy rate: ')

                # line chart (timeseries)
                line = alt.Chart(geo_prov_unadjusted).mark_line().encode(
                    x=alt.X('REF_DATE:T', title='Date', axis=time_axis),
                    y=alt.Y('Job vacancy rate:Q', title='Job vacancy rate (%)'),
                    color=alt.Color('GEO:N', title='Provinces',scale = alt.Scale(scheme='category20')),
                    tooltip=[datetip, regiontip, jvrtip]
                )

                # vertical marker
                rule = alt.Chart(geo_prov_unadjusted).mark_rule(color='gray').encode(
                    x='REF_DATE:T'
                ).transform_filter(
                    hover
                )

                # points
                points = line.mark_circle().encode(
                    opacity=alt.condition(hover, alt.value(1), alt.value(0))
                ).add_selection(
                    hover
                ).add_selection(
                    selection_date)
                # Text that shows the date and value when hovering
                text = alt.Chart(geo_prov_unadjusted).mark_text(align='left', dx=5, dy=-5).encode(
                    x='REF_DATE:T',
                    y=alt.Y('Job vacancy rate:Q'),
                    text=alt.condition(hover, 'Job vacancy rate:Q', alt.value(' '))
                ).transform_filter(
                    hover
                )

                text2, highlight = rectangle()

                chart = (line + rule + points + text + highlight + text2).interactive()

                st.altair_chart(chart, use_container_width=True)
        with col2:
            st.write('## :orange[Drop down menu]')
            with st.container(border=True):
                st.checkbox('Show all', on_change=check_change, key='all_option')
                st.write('#### :orange[Add more provinces here &darr;]')
                st.multiselect(label='', options=prov_names, key='prov_select', on_change=multi_change)
            with st.container(border=True):
                st.write(
                    '- Data from the [Job Vacancy and Wage Survey](https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvey&SDDS=5217) by Statistics Canada')
                st.write(
                    '- :red[Job vacancy rate] is defined as proportion of job positions that are vacant or will become vacant for that month '
                )
                st.write(
                    '- Industry sectors are grouped by the [North American Industry Classification System (NAICS)](https://www23.statcan.gc.ca/imdb/p3VD.pl?Function=getVD&TVD=1181553).'
                )
    with st.container():

        datelist = sector_df.df['REF_DATE'].unique()

        initial_date = datetime.strptime('2024-06-01','%Y-%m-%d')
        st.write('## Monthly job vacancy rate by sector: :orange[Use slider to adjust month &darr;]')
        st.select_slider(label = '',options = datelist, format_func = lambda x: x.strftime( '%Y %b'), key = 'date_select', value = initial_date)
        variable_output = datetime.strftime(st.session_state.date_select, '%Y %b')
        html_str = f"""<style>
p.a {{
  font: bold 25px Courier center;
  text-align: center;
  color: orange;
}}
</style> 

<p class="a"> Selected Month: {variable_output}</p>"""
        st.markdown(html_str, unsafe_allow_html=True)
        sector_df_filtered = filter_choice(sector_df.df, 'REF_DATE', st.session_state.date_select)

        sector_chart = alt.Chart( sector_df_filtered).mark_bar().encode(
            x=alt.X('NAICS:N', axis=alt.Axis(labels = False), title = 'Industry category' ).sort('-y'),
            y='Job vacancy rate:Q',
            color = alt.Color('NAICS:N', legend = alt.Legend(title = 'NAICS'),
                              scale = alt.Scale(scheme='category20')),
            tooltip = [
                alt.Tooltip('NAICS:N', title='Sector: '),
                alt.Tooltip('Job vacancy rate', title='Job vacancy rate: '),
                alt.Tooltip('Job vacancies', title='Vacant positions: '),
                alt.Tooltip('Payroll employees', title='Employed positions: ')
            ]
        )

        st.altair_chart(sector_chart, use_container_width=True)







