# -*- coding: utf-8
import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

# テーブル新規作成
try:
    c.execute('''create table users (id varchar(256), name varchar(64), presence int)''')
    conn.commit()
except OperationalError:
    None

#新規ユーザー追加
sql = 'insert into users (id, name, presence) values (?,?,?)'
user = ('sodijfoisdjf', 'Taro', 1)
c.execute(sql, user)#executemanyで2次配列で複数追加可能

#実行結果の保存
conn.commit()

#入力結果の出力
for row in c.execute('select * from users'): print(row)
#接続クローズ
conn.close()
