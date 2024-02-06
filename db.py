"""
MIT License

Copyright (c) 2022 - 2024 Tasfers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sqlite3
from sqlite3.dbapi2 import Cursor
from typing import Any

class SQLITE:

    def __init__(self, dbname: str = None):
        if dbname is None:
            dbname = 'database.db'

        self.sqlite = sqlite3.connect(dbname)

        self.db = self.sqlite.cursor()

        self.db.execute('CREATE TABLE IF NOT EXISTS json (id TEXT, value BIGTEXT)')
        self.sqlite.commit()


    def add(self, query: str = None, value = None) -> Cursor:
        """Увеличить значение в БД"""
        if query is None or value is None:
            raise TypeError('Параметры в add должны быть настроеными')

        if isinstance(value, int) is False:
            raise TypeError('Значение для добавления должно быть числом')

        self.db.execute("SELECT value FROM json WHERE id = ?", [query])
        if self.db.fetchone() is None:
            self.db.execute("INSERT INTO json VALUES (?, ?)", [query, value])
            self.sqlite.commit()
            return True
        else:
            try:
                self.db.execute("SELECT value FROM json WHERE id = ?", [query])
                int(self.db.fetchone()[0])
            except:
                raise TypeError('Текущие значение столба не число для добавления к нему')
            


            
            self.db.execute("SELECT value FROM json WHERE id = ?", [query])
            self.db.execute("UPDATE json SET value = ? WHERE id = ?", [str(int(self.db.fetchone()[0]) + value), query])
            self.sqlite.commit()
            return True


    def set(self, query: str = None, value = None) -> Cursor:
        """Установить значение в БД"""
        if query == None or value is None:
            raise TypeError('Параметры для set должны быть настроеными')

        self.db.execute("SELECT value FROM json WHERE id = ?", [query])
        if self.db.fetchone() is None:
            if isinstance(value, int) is True:
                self.db.execute("INSERT INTO json VALUES (?, ?)", [query, value])
                self.sqlite.commit()
            else:
                self.db.execute("INSERT INTO json VALUES (?, ?)", [query, value])
                self.sqlite.commit()
            return True
        else:
            if isinstance(value, int) is True:
                self.db.execute("UPDATE json SET value = ? WHERE id = ?", [value, query])
                self.sqlite.commit()
            else:
                self.db.execute("UPDATE json SET value = ? WHERE id = ?", [value, query])
                self.sqlite.commit()
            return True


    def get(self, query: str = None) -> Any or None:
        """Получить данные по ключу из БД"""
        if query == None:
            raise TypeError('Параметры get должны быть настроеными')

        self.db.execute("SELECT value FROM json WHERE id = ?", [query])
        if self.db.fetchone() is None:
            return None
        else:
            self.db.execute("SELECT value FROM json WHERE id = ?", [query])
            return self.db.fetchone()[0]

    def subtract(self, query: str = None, value = None) -> Cursor:
        """Убавить значение в БД"""
        if query == None or value is None:
            raise TypeError('Параметры для subtract должны быть настроеными')

        if isinstance(value, int) is False:
            raise TypeError('Значение для убавления должно быть числом')

        self.db.execute("SELECT value FROM json WHERE id = ?", [query])
        if self.db.fetchone() is None:
            self.db.execute("INSERT INTO json VALUES (?, ?)", [query, value])
            self.sqlite.commit()
            return True
        else:
            try:
                self.db.execute("SELECT value FROM json WHERE id = ?", [query])
                int(self.db.fetchone()[0])
            except:
                raise TypeError('Значение столба должно быть числом для убавления')

            self.db.execute("SELECT value FROM json WHERE id = ?", [query])
            self.db.execute("UPDATE json SET value = ? WHERE id = ?", [str(int(self.db.fetchone()[0]) - value), query])
            self.sqlite.commit()
            return True

    def fetch(self, query: str = None) -> list:
        """Получить множество из БД по ключу"""
        self.db.execute(f"SELECT value FROM json WHERE id LIKE '{query}~%'")
        db = self.db.fetchall()
        if len(db) == 0: return []
        return list(map(lambda a: a[0], db))

    def has(self, query: str = None) -> bool:
        """Проверить на наличие данные в БД"""

        if query == None:
            raise TypeError('Параметры для has должны быть настроеными')
        
        self.db.execute("SELECT value FROM json WHERE id = ?", [query])
        if self.db.fetchone() is None:
            return False
        else:
            return True

    def all(self) -> list:
        """Получить все данные из БД в массиве"""
        arr = []
        self.db.execute("SELECT * FROM json")
        if self.db.execute("SELECT * FROM json") is None:
            return []


        self.db.execute("SELECT * FROM json")
        for a in self.db.fetchall():
            arr.append(a)

        return arr
    
    def delete(self, query: str = None) -> Cursor:
        """Удалить данные по ключу из БД"""

        self.db.execute("SELECT value FROM json WHERE id = ?", [query])
        if self.db.fetchone() is None:
            raise TypeError('Нельзя удалить не существующие данные из БД')
        else:
            self.db.execute("DELETE FROM json WHERE id = ?", [query])
            self.sqlite.commit()
            return True
    
    def push(self, query: str, value: str) -> Cursor:
        """Добавить ещё одно значение по ключу"""

        db = self.db.execute(f"SELECT * FROM json WHERE id LIKE '{query}~%'")
        self.set(f'{query}~{len(db.fetchall())}', value)
    
    def pull(self, query: str, value: str) -> Cursor:
        self.db.execute(f"DELETE FROM json WHERE id LIKE '{query}~%' AND value = '{value}'")
        self.sqlite.commit()
