import dhlab as dh
import streamlit as st
import pandas as pd

st.set_page_config(page_title="DTM", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
st.session_state.update(st.session_state)



st.header("Tell ord i korpus")
st.markdown("Velg et korpus fra [corpus-appen](https://beta.nb.no/dhlab/corpus/)")


uploaded_file = st.file_uploader("last opp korpus", help="slipp en fil, eller velg fra en mappe")
if uploaded_file is not None:
    dataframe = pd.read_excel(uploaded_file)
    st.subheader('Korpus')
    st.write(dataframe.head(3))
    st.subheader('Dokument/term-matrise')
    corpus = dh.Corpus(doctype='digibok',limit=0)
    corpus.extend_from_identifiers(list(dataframe.urn))
    dtm = dh.Counts(corpus)
    st.write(dtm.counts)
    st.session_state['dtm'] = dtm.counts
    st.subheader('Totalen')
    totalen = pd.DataFrame(dtm.counts.sum(axis = 1))
    totalen.columns = ['freq']
    st.write(f"Antall unike ord {len(totalen)}, løpende ord {int(totalen.freq.sum())}")
    st.session_state['totalen'] = totalen
    st.write(totalen)