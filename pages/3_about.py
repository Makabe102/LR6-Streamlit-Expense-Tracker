from pathlib import Path

import streamlit as st

st.title("Про автора та проєкт")

photo_path = Path(__file__).resolve().parents[1] / "assets" / "author.jpg"
author_col, photo_col = st.columns([2, 1], vertical_alignment="top")

with author_col:
    st.subheader("Інформація про автора")
    st.write("**Студент:** Ворончак Василь")
    st.write("**Група:** П-31")
    st.write("**Навчальний заклад:** Гусятинський фаховий коледж ТНТУ імені Івана Пулюя")
    st.write("**Дисципліна:** Інформаційні технології")

    st.subheader("Про застосунок")
    st.write(
        "Програма призначена для обліку щоденних витрат: записи можна "
        "розподіляти за категоріями, шукати й порівнювати з місячними лімітами."
    )
    st.write("Для зберігання даних створено дві пов'язані таблиці:")
    st.markdown(
        "- `categories` — назви категорій і місячні ліміти;\n"
        "- `expenses` — витрати із зовнішнім ключем `category_id`."
    )

with photo_col:
    if photo_path.exists():
        st.image(str(photo_path), caption="Ворончак Василь", width=260)

st.info(
    "Локально дані зберігаються у SQLite. У Streamlit Community Cloud "
    "локальна база не гарантує збереження записів після перезапуску."
)
