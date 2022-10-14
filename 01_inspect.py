import pandas as pd
import streamlit as st
import dhlab as dh

#st.session_state.update(st.session_state)

@st.cache(suppress_st_warning=True, show_spinner=False)
def get_counts(words = None, corpus = None):
    return dh.Counts(corpus, words=words).counts

st.header('Inspiser termene i korpuset')

corpus = st.session_state['corpus']
corpusdf = corpus.corpus

if "search_term" not in st.session_state:
    search = ""
else:
    search = st.session_state['search_term']
    
with st.form("my_form"):
    
    col1, col2 = st.columns(2)
    
    with col1:
        words = st.text_input("Frekvenser for en liste ord", search, key="search_term", help="Skriv inn ordene skilt med komma. For å ta med komma, legg inn et til slutt")
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
        columns = st.multiselect("Hvordan skal dokumentene vises", 
                                 options=list(corpusdf.columns),
                                 default=['authors', 'title', 'year'], 
                                 help="Plukk ut metadata som beskriver dokumentene eller skiller dem fra hverandre")
        
        if columns == [] or 'urn' != columns[0]:
            columns.insert(0, 'urn')
        
        
        names = {x[0]:' '.join([str(z) for z in x[1:]]) for x in corpusdf[columns].values}
        
        
    colA, colB = st.columns(2)
    
    with colA:
        st.write('Kontroller visning')
        transpose = st.checkbox("Tabellen viser ordene i kolonner", value=True, help="Fjern krysset for å la kolonnene bestå av dokumenter")
 #   with colB:
 #       if transpose:
 #           sort_col = st.number_input(f"Sorter etter kolonne max {len(df.transpose().columns)}", min_value = 1, max_value = len(df.transpose().columns), value = 1) -1
 #       else:
 #           sort_col = st.number_input(f"Sorter etter kolonne max {len(df.columns)}", min_value = 1, max_value = len(df.columns), value = 1)-1

    submitted = st.form_submit_button("Klikk her når alt er klart")
    #st.write(words)
    
    tbl = df.loc[[w for w in words if w in df.index]]
    if submitted:
        
        tbl = tbl.rename(columns=names)
        
        try:
            if transpose:
                t = tbl.transpose()
                t = t.reset_index()
                
                a = list(t.columns[1:])
                a.append(str(t.columns[0]))
                t = t[a]
                st.dataframe(
                    t.sort_values(by = t.columns[0], ascending = False).style.format(precision=0).background_gradient().hide(axis=0)
                )
            else:
                st.dataframe(
                    tbl.sort_values(by = tbl.columns[0], ascending = False).style.format(precision=0).background_gradient()
                )
        except:
            st.markdown("Noe gikk galt - kolonnenavn må være entydig, om dokumentinformasjon antyder kolonner, prøv å legg til _dhlabid_ som del av visningen")