import sqlite3


class SQLiteDatabase:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.conn = sqlite3.connect(self.file_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def add_iin(self, iin: str, status: int) -> None:
        self.cursor.execute(
            """
            INSERT INTO iins (iin, status)
            VALUES (?, ?)
            """, (iin, status)
        )

        self.conn.commit()

    def select_iin(self) -> tuple:
        self.cursor.execute(
            """
            SELECT id, iin from iins 
            where status != 1 
            order by id asc limit 1;
            """
        )

        return self.cursor.fetchone()

    def update_iin_status(self, id: int, status: int) -> None:
        self.cursor.execute(
            """
            UPDATE iins
            SET status = (?)
            WHERE id = (?)
            """,
            (status, id)
        )

        self.conn.commit()

    def count_iins(self) -> int:
        self.cursor.execute(
            """
            SELECT COUNT(*) FROM iins;
            """
        )

        return self.cursor.fetchone()[0]
