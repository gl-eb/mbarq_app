import streamlit as st
from PIL import Image
from scripts import library_map, eda, results
import base64
st.set_page_config(page_title="mBARq App", layout='wide',
                   page_icon=Image.open("images/image.png")
                    )
st.image("images/mbarq-logo.png")


def home_page():
    url = "https://github.com/MicrobiologyETHZ/mbarq"


    st.markdown(f""" 
    
    
    
  #
    
    This app allows exploration of data processed and analyzed with [mBARq tool]({url}). It is currently in beta!

    ## Tabs:

    1. ### 📍 Library Map: 

        - Allows you to visualize the insertions found in your library and provides some basic summary statistics.
        - Requires mapping file generated by `mbarq map` command
    
    ***

    2. ### 📈 Exploratory Analysis: 

        - Generates an interactive PCA plot
        - Generates barcode abundance plots for genes of interest
        - Requires merged count file generated by `mbarq count` and a the same sample data file used for the analysis

    ***
    
    3. ### 📊 Differential Abundance Results

        - Visualize differential abundance results for all genes or specific KEGG pathways
        - Draw heatmaps of log fold changes across the conditions for specific KEGG pathways
        - Requires a `gene summary` files generated by `mbarq analyze` command and a `gmt` file


    """)

home_tab, lib_tab, eda_tab, dea_tab = st.tabs(["  🏠 Home   ", "   📍 Library Map   ",
                               "   📈 Exploratory Analysis   ", '   📊 Differential Abundance'])
with home_tab:
    home_page()

with lib_tab:
    library_map.app()

with eda_tab:
    eda.app()

with dea_tab:
    results.app()

