from datetime import date, timedelta
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "expenses.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.create_function(
        "casefold", 1,
        lambda value: str(value).casefold() if value is not None else "",
    )
    return connection


def init_db():
    with get_connection() as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        count = connection.execute(
            "SELECT COUNT(*) FROM categories"
        ).fetchone()[0]
        if count == 0:
            categories = [
                ("Харчування", 3500),
                ("Транспорт", 1200),
                ("Навчання", 1500),
                ("Зв'язок", 600),
                ("Дозвілля", 1000),
            ]
            connection.executemany(
                "INSERT INTO categories (name, monthly_limit) VALUES (?, ?)",
                categories,
            )
            category_ids = {
                row["name"]: row["id"]
                for row in connection.execute("SELECT id, name FROM categories")
            }
            today = date.today()
            expenses = [
                ("Обід у їдальні", 145, 0, "Комплексний обід"),
                ("Проїзний на автобус", 420, 1, "Місячний квиток"),
                ("Зошити та ручки", 210, 2, "Канцтовари"),
                ("Поповнення мобільного", 250, 3, "Тариф на 4 тижні"),
                ("Продукти в магазині", 580, 0, "Покупки на тиждень"),
                ("Друк навчальних матеріалів", 185, 2, "Чорно-білий друк"),
                ("Кава з друзями", 160, 4, "Після занять"),
                ("Квиток у кіно", 220, 4, "Вечірній сеанс"),
                ("Продукти на вихідні", 490, 0, "Супермаркет"),
                ("Домашній інтернет", 300, 3, "Щомісячна оплата"),
            ]
            records = [
                (
                    title,
                    amount,
                    str(today - timedelta(days=min(index, max(today.day - 1, 0)))),
                    category_ids[categories[category_index][0]],
                    note,
                )
                for index, (title, amount, category_index, note) in enumerate(expenses)
            ]
            connection.executemany(
                "INSERT INTO expenses "
                "(title, amount, expense_date, category_id, note) "
                "VALUES (?, ?, ?, ?, ?)",
                records,
            )


def get_categories():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, name, monthly_limit FROM categories ORDER BY name"
        ).fetchall()
        return [dict(row) for row in rows]


def add_category(name, monthly_limit):
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO categories (name, monthly_limit) VALUES (?, ?)",
            (name.strip(), float(monthly_limit)),
        )


def delete_category(category_id):
    with get_connection() as connection:
        used = connection.execute(
            "SELECT COUNT(*) FROM expenses WHERE category_id = ?",
            (category_id,),
        ).fetchone()[0]
        if used:
            raise ValueError("Спершу видали витрати цієї категорії.")
        connection.execute("DELETE FROM categories WHERE id = ?", (category_id,))


def get_expenses(category_id=None, search_text=""):
    query = (
        "SELECT e.id, e.title, e.amount, e.expense_date, e.category_id, "
        "c.name AS category_name, e.note "
        "FROM expenses AS e JOIN categories AS c ON c.id = e.category_id "
        "WHERE 1 = 1"
    )
    parameters = []
    if category_id is not None:
        query += " AND e.category_id = ?"
        parameters.append(category_id)
    if search_text.strip():
        query += " AND (casefold(e.title) LIKE casefold(?) " \
                 "OR casefold(e.note) LIKE casefold(?))"
        pattern = f"%{search_text.strip()}%"
        parameters.extend([pattern, pattern])
    query += " ORDER BY e.expense_date DESC, e.id DESC"
    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]


def get_category_totals(month):
    query = (
        "SELECT c.name AS category_name, c.monthly_limit, "
        "COALESCE(SUM(CASE WHEN substr(e.expense_date, 1, 7) = ? "
        "THEN e.amount ELSE 0 END), 0) AS total_spent "
        "FROM categories AS c LEFT JOIN expenses AS e ON e.category_id = c.id "
        "GROUP BY c.id ORDER BY c.name"
    )
    with get_connection() as connection:
        rows = connection.execute(query, (month,)).fetchall()
        return [dict(row) for row in rows]


def add_expense(title, amount, expense_date, category_id, note=""):
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO expenses "
            "(title, amount, expense_date, category_id, note) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                title.strip(), float(amount), str(expense_date),
                int(category_id), note.strip(),
            ),
        )


def update_expense(expense_id, title, amount, expense_date, category_id, note=""):
    with get_connection() as connection:
        connection.execute(
            "UPDATE expenses SET title = ?, amount = ?, expense_date = ?, "
            "category_id = ?, note = ? WHERE id = ?",
            (
                title.strip(), float(amount), str(expense_date), int(category_id),
                note.strip(), int(expense_id),
            ),
        )


def delete_expense(expense_id):
    with get_connection() as connection:
        connection.execute("DELETE FROM expenses WHERE id = ?", (int(expense_id),))
