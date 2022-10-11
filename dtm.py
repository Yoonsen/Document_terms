import dhlab as dh
import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="DTM", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
st.session_state.update(st.session_state)



st.header("Tell ord i korpus")
st.markdown("Velg et korpus fra [corpus-appen](https://beta.nb.no/dhlab/corpus/) eller hent en eller flere URNer fra nb.no eller andre steder")

corpus_defined = False

col1, col2 = st.columns(2)
with col1:
    urner = st.text_area("Lim inn URNer:","", help="Lim en tekst som har URNer i seg. Teksten trenger ikke å være formatert")
    if urner != "":
        urns = re.findall("URN:NBN[^\s.,]+", urner)
        if urns != []:
            corpus_defined = True
            corpus = dh.Corpus(doctype='digibok',limit=0)
            corpus.extend_from_identifiers(urns)
            #st.write(urns)
        else:
            st.write('Fant ingen URNer')

with col2:
    uploaded_file = st.file_uploader("Last opp korpus", help="Dra en fil over hit, fra et nedlastningsikon, eller velg fra en mappe")
    if uploaded_file is not None:
        corpus_defined = True
        dataframe = pd.read_excel(uploaded_file)
        st.subheader('Korpus')
        corpus = dh.Corpus(doctype='digibok',limit=0)
        corpus.extend_from_identifiers(list(dataframe.urn))

        

if corpus_defined:
    st.write("Et utvalg fra korpuset")
    st.session_state['corpus'] = corpus
    corpus.corpus.dhlabid = corpus.corpus.dhlabid.astype(int)
    corpus.corpus.year = corpus.corpus.year.astype(int)
    st.write(corpus.corpus.sample(min(len(corpus.corpus), 20)))

#    st.subheader('Dokument/term-matrise')
     
#    dtm = dh.Counts(corpus)
#    st.write(dtm.counts)
#    st.session_state['dtm'] = dtm.counts
#    st.subheader('Totalen')
#    totalen = pd.DataFrame(dtm.counts.sum(axis = 1))
#    totalen.columns = ['freq']
#    st.write(f"Antall unike ord {len(totalen)}, løpende ord {int(totalen.freq.sum())}")
#    st.session_state['totalen'] = totalen
#    st.write(totalen)