CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    monthly_limit REAL NOT NULL CHECK (monthly_limit > 0)
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    expense_date TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);