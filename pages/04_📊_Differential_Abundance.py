import streamlit as st
from scripts.datasets import ResultDataSet
from pathlib import Path
st.set_page_config(layout='wide')


def app():
    st.markdown(""" # Fitness Results """)
    with st.expander('How this works: '):
        an_url = "https://mbarq.readthedocs.io/en/latest/analysis.html"
        st.markdown(f"""
        
        #### Fitness data: 
        - For this page you need to upload a `csv` file produced by `mbarq analyze` command. To learn more about how to use `mbarq analyze`, please read [here]({an_url}).
        - First column must be a gene identifier (for example, locus tag). 
        - Must also include `LFC` and `contrast` columns, where `LFC` is log2 fold change in gene abundance for a specific treatment compared to control, and `contrast` specifies the treatment.  
        - You can define hits by setting LFC and FDR cutoffs, and visualize them either by rank or via heatmaps. 
        
        """)

    with st.container():
        # Get the data
        if 'results_ds' in st.session_state.keys():
            rds = st.session_state['results_ds']
            #gene_id = st.session_state['results_gene_id']
        else:
            st.info('Browse example results file or upload your data in **⬆️ Data Upload**')
            result_files = [Path("examples/example_rra_results.csv")]
            gene_id = 'Name'
            rds = ResultDataSet(result_files=result_files, gene_id=gene_id)
            rds.load_results()
            rds.validate_results_df()

        if st.checkbox('Show sample of the dataset'):
            try:
                st.write(rds.results_df.sample(5))
            except ValueError:
                st.write('Result table is empty')

    if not rds.results_df.empty:
        contrasts = rds.results_df[rds.contrast_col].sort_values().unique()
        libraries = rds.results_df[rds.library_col].sort_values().unique()
        st.subheader("Fitness Results")
        if len(libraries) > 1:
            libraries = ['All'] + list(libraries)
            library_to_show = st.selectbox('Select experiment to show', libraries)
        else:
            library_to_show = libraries[0]
        # SUBSET DATAFRAME TO SPECIFIC CONTRAST AND LIBRARY
        contrast_col, lfc_col1, lfc_col2, fdr_col = st.columns(4)
        contrast_to_show = contrast_col.multiselect('Select a contrast', contrasts, default=contrasts[0])
        fdr_th = fdr_col.number_input('FDR cutoff', value=0.05)
        type_lfc_th = lfc_col1.radio('Absolute LFC cutoff or define range', ['Absolute', 'Range'])
        if type_lfc_th == 'Absolute':
            lfc_low = lfc_col2.number_input('Log FC cutoff (absolute)', min_value=0.0, step=0.5, value=1.0)
            lfc_hi = None
        else:
            lfc_low = lfc_col2.number_input('Min Log FC',  step=0.5, value=-5.0)
            lfc_hi = lfc_col2.number_input('Max Log FC',  step=0.5, value=-1.0)

        rds.identify_hits(library_to_show,  lfc_low, lfc_hi, fdr_th)
        fig = rds.graph_by_rank(contrast=contrast_to_show, kegg=False)
        st.plotly_chart(fig, use_container_width=True)
        st.subheader('Fitness heatmaps')
        genes = st.multiselect('Choose genes of interest', rds.results_df[rds.gene_id].unique())
        if genes:
            fig = rds.graph_heatmap(genes)
            st.plotly_chart(fig, use_container_width=True)


app()
