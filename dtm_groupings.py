import dhlab as dh
import streamlit as st
import pandas as pd
import re
import requests
import traceback

normal_size = 5000
max_doc = 50000

@st.cache_data(show_spinner=False)
def get_counts(words = None, corpus = None):
    res = dh.api.dhlab_api.get_document_frequencies(list(corpus.urn), words=words)['freq']
    return res

@st.cache_data(show_spinner=False)
def deduplicate(docs = None, column = None):
    """Cells in columns have /-separated values. For counting, these are better distributed on different rows
    :param docs: is a dataframe of a corpus object
    :param column: is a column name, the one to be deduplicated"""
    
    de_df = []
    for r in docs.iterrows():
        d = dict(r[1])  # view the row as a dict - col-names become keys
        try:
            for value in [v.strip() for v in d[column].split('/')]:
                row = d.copy()    # important to make a fresh new copy of the row dict
                row[column] = value  # let the copy get a unary value
                #print(row)
                de_df.append(row)  # add it to new rows
        except AttributeError:
            de_df.append(d)
    return pd.DataFrame(de_df).drop_duplicates()

@st.cache_data(show_spinner=False)
def countby(dedup=None, counts = None, column=None):
    """Deduplicated corpus against a counts object
    :param dedup: is deduplicated corpus
    :param counts: an instance of Counts().counts - i.e the dataframe
    :param column: the column to aggregate over"""
    
    cols = list(counts.columns)
    result = pd.concat([
        dedup[['dhlabid', column]].set_index('dhlabid'), 
        counts.transpose().reset_index().set_index('urn')], axis = 1).groupby(column).sum(cols)
    return result


st.set_page_config(page_title="DTM", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

st.sidebar.markdown("Velg et korpus fra [corpus-appen](https://beta.nb.no/dhlab/corpus/) eller hent en eller flere URNer fra nb.no eller andre steder")


corpus_defined = False
urner = st.sidebar.text_area("Lim inn URNer:","", help="Lim inn en liste med URNer, trenger ikke å være formatert")
if urner != "":
    urns = re.findall("URN:NBN[^\s.,]+", urner)
    if urns != []:
        corpus_defined = True
        corpus = dh.Corpus()
        corpus.extend_from_identifiers(urns)
        
    else:
        st.write('Fant ingen URNer')

uploaded_file = st.sidebar.file_uploader("Last opp et korpus", help="Dra en fil over hit, fra et nedlastningsikon, eller velg fra en mappe")

if uploaded_file is not None:
    corpus_defined = True
    dataframe = pd.read_excel(uploaded_file)
    #st.write(dataframe)
    st.sidebar.subheader('Korpus')
    corpus = dataframe
    #corpus = dh.Corpus()
    #corpus.extend_from_identifiers(list(dataframe.urn))


if corpus_defined:
    if len(corpus) > 1:
        
        st.sidebar.write(f"Korpuset består av {len(corpus)} dokumenter")
        if len(corpus) > max_doc:
            st.sidebar.write(f"Siden korpuset er ganske stort, arbeides det videre med et utvalg av dokumenter. Lag et mindre korpus for å få med alt. " 
                             "Utvalget vil kunne endre seg fra søk til søk")
            samplesize = st.sidebar.number_input("Utvalgsstørrelse", 1, int(normal_size), int(normal_size)/2)
            corpus = corpus.sample(int(samplesize))
            
            
    elif len(corpus) == 1:
        st.sidebar.write("Korpuset er ett dokument")
    
    else:
        st.sidebar.write("Tomt korpus")
        
    st.session_state['corpus'] = corpus
    try:
        corpus.dhlabid = corpus.dhlabid.astype(int)
        corpus.year = corpus.year.astype(int)
        #st.write(corpus)
    except:
        pass
    #st.sidebar.write(corpus.corpus.sample(min(len(corpus.corpus), 20))["title authors year".split()])

    


st.header('Inspiser ordfrekvenser')
st.markdown("Velg et korpus av bøker, aviser, tidsskrift eller manuskript ved hjelp av sidefeltet. Skriv inn ordene du vil undersøke i feltet under for å se hvor mange ganger de forekommer i de enkelte dokumentene.")

if "search_term" not in st.session_state:
    search = ""
else:
    search = st.session_state['search_term']

if corpus_defined:
    
    
    #with st.form("my_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        words = st.text_input(
            "Frekvenser for en liste ord", 
            search, 
            key="search_term", 
            help="Skriv inn ordene skilt med komma. For å ta med komma, legg inn et til slutt")
        words = [w.strip() for w in words.split(',')]

        if "" in words:
            words.append(',')
        #st.write(words)

        words = [w for w in words if w != ""]

        if words == [',']:
            words = ['.',',','!',"?", ';']

        words = list(set(words))

        df = get_counts(words = words, corpus = corpus)

    with col2:
        gruppering = st.selectbox(
            'Velg grupperingskolonne', 
            options = ["hele korpuset"] + ["frekvens pr. bok"] + [x for x in corpus.columns if x not in 'dhlabid urn sesamid isbn oaiid isbn10'.split()]
        )

    with col3:
        axis_coloring = st.checkbox("Kryss av for å fargelegge matrisen horisontalt", value=True, help="Fjern avkrysning for endringer vertikalt")
        if axis_coloring == True:
            axis = 1
        else:
            axis = 0

    #submitted = st.form_submit_button("Klikk her når alt er klart")

    tbl = df.loc[[w for w in words if w in df.index]]

    if  gruppering == "frekvens pr. bok":
        t = tbl.rename(dict (zip(corpus['dhlabid'], corpus['urn'])), axis = 1).transpose().reset_index()
        t['link'] = t.urn.map(lambda x: f"https://nb.no/items/{x}")
        #st.dataframe(t[t.columns[1:]].style.format(precision=0).background_gradient(axis=axis))
        (st.markdown(t[t.columns[1:]]
                     #.style.format(precision=0)
                     #.background_gradient(axis=axis)
                     .to_html(render_links=True, escape=False),unsafe_allow_html=True)
        )

    elif gruppering == "hele korpuset":
        t = tbl.transpose().sum().reset_index()
        t.columns = ["word", "freq"]
        st.dataframe(t)

    else:
        de_df = deduplicate(docs = corpus, column=gruppering)
        #st.write(de_df)
        count_df = countby(dedup=de_df, counts = tbl, column = gruppering)
        st.dataframe(count_df.style.format(precision=0).background_gradient(axis = axis))
