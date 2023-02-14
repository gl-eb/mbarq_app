from pathlib import Path
from typing import List
import pandas as pd
import pandera as pa
import plotly.express as px
import streamlit as st
import yaml
from pandera.errors import SchemaError
from scripts.datasets import LibraryMap
from scripts.graphs import define_color_scheme


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')


def app():
    st.markdown(""" # Library Map """)
    with st.expander('How this works: '):
        st.markdown("""

        ### Visualize insertion position along the genome.

        - Takes in library map **CSV** file (`*.annotated.csv`) produced by `mbarq map`. Expects to find the following columns in the file: `barcode`, `abundance_in_mapping_library`, `insertion_site`, `chr`, `distance_to_feature`, `strand`. 
        - Can load more than one library file at the same time to compare! 
        - You can select which sequence (e.g. chromosome or plasmids) to display, and color the insertions by distance to feature, multimapping or library.
        - You can click on the figure legend to only show a specific subset of data (i.e. if looking at multiple libraries, double clicking on the specific library name will show data for that library only)

        """)

    with st.container():
        # Get the data
        if 'lib_map' in st.session_state.keys():
            lm = st.session_state['lib_map']
        else:
            st.info('Browse the example data set below or load your own data on **⬆️ Data Upload** page')
            map_files = [Path('examples/example_library_map.annotated.csv')]
            st.subheader('Example mapping file')
            df = pd.read_csv(map_files[0])
            st.download_button(
                label="Download example data as CSV",
                data=convert_df(df),
                file_name='example_library_mapping_file.csv',
                mime='text/csv',
            )
            lm = LibraryMap(map_df=df)
            lm.load_map()
            lm.validate_lib_map()

        if lm.lib_map.empty:
            st.error(f"""⚠️ Something went wrong when processing library map files. 
                            Please check the file formats and try again ⚠️""")
            st.stop()
        if st.checkbox("Show sample of the Library Map?"):
            st.write(lm.lib_map.sample(5))
        # Graph coverage map or individual insertion abundance
        with st.container():
            # Define colors
            colors, alphabetClrs, all_clrs = define_color_scheme()
            graph_type = st.radio("Choose graph", ['Coverage Histogram', 'Individual Insertions'])
            c1, c2, c3 = st.columns(3)
            chr_col_choice = c1.selectbox('Choose sequence to display', lm.lib_map[lm.chr_col].unique())
            if graph_type == 'Individual Insertions':
                color_by_choice = c2.selectbox('Color by', lm.color_by_cols)
                fig = lm.graph_insertions(chr_col_choice, color_by_choice, all_clrs)
            else:
                try:
                    num_bins = c2.number_input('Number of bins', value=100)
                    hist_col = c3.text_input('Color (hex, rgb, hsl, hsv or color name)', value=colors['teal'])
                    fig = lm.graph_coverage_hist(chr_col_choice, num_bins, hist_col)
                except ValueError:
                    st.write("Please enter a valid color. The following formats are accepted: hex, rgb, hsl, hsv or color name")
                    return

            st.plotly_chart(fig, use_container_width=True)

        # Generate summary stats for the libraries
        with st.container():
            name_col = st.selectbox("Choose attribute column", lm.attributes)
            lm.get_stats(name_col)
            st.markdown("#### Insertion Summary")
            st.table(lm.stats)

app()