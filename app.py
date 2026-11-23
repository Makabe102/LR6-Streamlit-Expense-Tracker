import streamlit as st
import db

st.set_page_config(
    page_title="Облік витрат студента",
    page_icon="💳",
    layout="wide",
)

db.init_db()

pages = [
    st.Page("pages/1_overview.py", title="Перегляд витрат", default=True),
    st.Page("pages/2_add_expense.py", title="Додати запис"),
    st.Page("pages/3_about.py", title="Про автора"),
]

st.sidebar.caption("Ворончак Василь · група П-31")
page = st.navigation(pages)
page.run()