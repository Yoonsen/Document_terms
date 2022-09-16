import pandas as pd
import streamlit as st

st.session_state.update(st.session_state)

df = st.session_state['dtm']

#st.table(df.head())
st.header('Inspiser termene i korpuset')

with st.form("my_form"):
    
    col1, col2 = st.columns(2)
    
    with col1:
        words = st.text_input("Angi ord som skal sammenlignes", "", help="Skriv inn ordene skilt med komma. For å ta med komma, legg inn et til slutt")
        words = [w.strip() for w in words.split(',')]
        if "" in words:
            words.append(',')
        words = [w for w in words if w != ""]
        
        
    with col2:
        sort_col = st.number_input("Sorter etter kolonne", min_value = 0, max_value = len(df.columns) - 1, value = 0)
    
    #st.write(words)

    submitted = st.form_submit_button("klikk når alt er klart")
    #st.write(words)
    if words == [","]:
        tbl = df.sample(10)
    else:
        tbl = df.loc[[w for w in words if w in df.index]]
    if submitted:
        st.table(
            tbl.sort_values(by = tbl.columns[sort_col], ascending = False).head(50).style.background_gradient()
        )