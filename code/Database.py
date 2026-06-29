import sqlite3

class Database:
    def __init__(self, db_name='tiny_forest.db'):
        #estabelece conexão com o arquivo local ou fabricará se o arquivo for inexistente
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self):
        #cria a tabela guardando: id automático, nome com 4 letras e tempo em segundos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                time_survived INTEGER NOT NULL)''')
        self.connection.commit()

    def save_score(self, name, time_survived):
        """insere o recorde no banco blindado contra SQL Injection"""
        self.cursor.execute('''
                    INSERT INTO leaderboard (name, time_survived) VALUES (?, ?)
                    ''', (name.upper(), time_survived))
        self.connection.commit()

    def get_top_10(self):
        """realiza consulta ordenada dos 10 melhores"""
        self.cursor.execute('''
            SELECT name, time_survived FROM leaderboard
            ORDER BY time_survived DESC LIMIT 10''')
        return self.cursor.fetchall()