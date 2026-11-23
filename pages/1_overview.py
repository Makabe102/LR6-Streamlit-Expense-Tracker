from datetime import date

import pandas as pd
import streamlit as st

import db

st.title("Облік витрат студента")
st.caption("Список записів і коротка статистика за витратами")

categories = db.get_categories()
category_options = {"Усі категорії": None}
category_options.update({item["name"]: item["id"] for item in categories})

col_category, col_search = st.columns([1, 2])
with col_category:
    selected_category = st.selectbox("Категорія", list(category_options))
with col_search:
    search_text = st.text_input("Пошук", placeholder="Назва або примітка")

expenses = db.get_expenses(category_options[selected_category], search_text)
total = sum(item["amount"] for item in expenses)
average = total / len(expenses) if expenses else 0

col_total, col_count, col_average = st.columns(3)
col_total.metric("Усього витрачено", f"{total:.2f} грн")
col_count.metric("Кількість записів", len(expenses))
col_average.metric("Середня витрата", f"{average:.2f} грн")

st.subheader("Усі витрати")
if expenses:
    table = pd.DataFrame(expenses)[
        ["expense_date", "title", "category_name", "amount", "note"]
    ]
    table.columns = ["Дата", "Назва", "Категорія", "Сума, грн", "Примітка"]
    st.dataframe(table, width="stretch", hide_index=True)
else:
    st.info("За цими умовами витрат не знайдено.")

st.subheader("Місячні ліміти за категоріями")
month = date.today().strftime("%Y-%m")
category_totals = db.get_category_totals(month)
if category_totals:
    budget = pd.DataFrame(category_totals)
    budget["Залишок, грн"] = budget["monthly_limit"] - budget["total_spent"]
    budget = budget.rename(columns={
        "category_name": "Категорія",
        "monthly_limit": "Ліміт, грн",
        "total_spent": "Витрачено, грн",
    })
    st.dataframe(
        budget[["Категорія", "Ліміт, грн", "Витрачено, грн", "Залишок, грн"]],
        width="stretch",
        hide_index=True,
    )
    chart = budget.set_index("Категорія")[["Ліміт, грн", "Витрачено, грн"]]
    st.bar_chart(chart)

if expenses:
    with st.expander("Редагувати або видалити витрату"):
        expense_options = {
            f"#{item['id']} — {item['title']}": item for item in expenses
        }
        selected_label = st.selectbox("Оберіть запис", list(expense_options))
        selected = expense_options[selected_label]
        category_names = [item["name"] for item in categories]
        current_category = next(
            item["name"] for item in categories
            if item["id"] == selected["category_id"]
        )

        with st.form("edit_expense"):
            new_title = st.text_input("Назва витрати", value=selected["title"])
            new_amount = st.number_input(
                "Сума, грн", min_value=1.0,
                value=float(selected["amount"]), step=10.0,
            )
            new_date = st.date_input(
                "Дата", value=date.fromisoformat(selected["expense_date"])
            )
            new_category = st.selectbox(
                "Категорія", category_names,
                index=category_names.index(current_category),
            )
            new_note = st.text_input("Примітка", value=selected["note"] or "")
            col_save, col_delete = st.columns(2)
            save = col_save.form_submit_button("Зберегти зміни")
            delete = col_delete.form_submit_button("Видалити запис")

        if save:
            if not new_title.strip():
                st.error("Введіть назву витрати.")
            else:
                new_category_id = next(
                    item["id"] for item in categories
                    if item["name"] == new_category
                )
                db.update_expense(
                    selected["id"], new_title, new_amount, new_date,
                    new_category_id, new_note,
                )
                st.success("Зміни збережено.")
                st.rerun()
        if delete:
            db.delete_expense(selected["id"])
            st.success("Запис видалено.")
            st.rerun()