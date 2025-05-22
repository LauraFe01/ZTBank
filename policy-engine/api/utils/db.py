import psycopg2

class DBConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = psycopg2.connect(
                dbname="mydb",
                user="myuser",
                password="mypass",
                host="db",
                port=5432
            )
        return cls._instance

    def get_conn(self):
        return self.conn