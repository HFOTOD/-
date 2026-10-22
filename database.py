import sqlite3
from config import DB_PATH

db = sqlite3.connect(DB_PATH)
db.execute(
    """CREATE TABLE IF NOT EXISTS tariffs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        days INTEGER NOT NULL)"""
)
db.execute(
    """CREATE TABLE IF NOT EXISTS payments(
        order_id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        tariff_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending')"""
)
db.commit()


def add_tariff(name: str, price: float, days: int) -> None:
    db.execute("INSERT INTO tariffs(name, price, days) VALUES(?,?,?)", (name, price, days))
    db.commit()


def delete_tariff(tariff_id: int) -> None:
    db.execute("DELETE FROM tariffs WHERE id=?", (tariff_id,))
    db.commit()


def get_tariffs():
    return db.execute("SELECT id, name, price, days FROM tariffs").fetchall()


def get_tariff(tariff_id: int):
    return db.execute(
        "SELECT name, price, days FROM tariffs WHERE id=?", (tariff_id,)
    ).fetchone()


def create_payment(order_id: str, user_id: int, tariff_id: int) -> None:
    db.execute(
        "INSERT INTO payments(order_id, user_id, tariff_id) VALUES(?,?,?)",
        (order_id, user_id, tariff_id),
    )
    db.commit()


def get_payment(order_id: str):
    return db.execute(
        "SELECT user_id, tariff_id, status FROM payments WHERE order_id=?", (order_id,)
    ).fetchone()


def mark_paid(order_id: str) -> None:
    db.execute("UPDATE payments SET status='paid' WHERE order_id=?", (order_id,))
    db.commit()
