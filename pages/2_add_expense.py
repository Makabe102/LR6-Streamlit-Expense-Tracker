import sqlite3
from datetime import date

import streamlit as st

import db

st.title("Додати запис")
st.write("Заповни форму, щоб додати витрату до списку.")

categories = db.get_categories()
if not categories:
    st.warning("Спершу створи категорію витрат.")
else:
    with st.form("add_expense", clear_on_submit=True):
        title = st.text_input("Назва витрати", placeholder="Наприклад, обід у їдальні")
        col_amount, col_date = st.columns(2)
        with col_amount:
            amount = st.number_input("Сума, грн", min_value=1.0, value=100.0, step=10.0)
        with col_date:
            expense_date = st.date_input("Дата", value=date.today())
        category_name = st.selectbox("Категорія", [item["name"] for item in categories])
        note = st.text_input("Примітка", placeholder="Необов'язково")
        submitted = st.form_submit_button("Додати витрату", type="primary")

    if submitted:
        if not title.strip():
            st.error("Вкажи назву витрати.")
        else:
            category_id = next(
                item["id"] for item in categories
                if item["name"] == category_name
            )
            db.add_expense(title, amount, expense_date, category_id, note)
            st.success(f"Додано запис «{title.strip()}».")

st.divider()
st.subheader("Додати категорію")
with st.form("add_category", clear_on_submit=True):
    new_category = st.text_input("Назва категорії", placeholder="Наприклад, Спорт")
    monthly_limit = st.number_input(
        "Місячний ліміт, грн", min_value=1.0, value=1000.0, step=100.0
    )
    add_category = st.form_submit_button("Створити категорію")

if add_category:
    if not new_category.strip():
        st.error("Вкажи назву категорії.")
    else:
        try:
            db.add_category(new_category, monthly_limit)
            st.success(f"Категорію «{new_category.strip()}» створено.")
            st.rerun()
        except sqlite3.IntegrityError:
            st.error("Категорія з такою назвою вже є.")