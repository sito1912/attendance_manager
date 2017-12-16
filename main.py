# -*- coding: utf-8
import RPi.GPIO as GPIO
import sqlite3,json,requests,datetime,time


def main():
    setup()
    #TODO:フェリカリーダー待機するの

    #TODO:読み取ったIDいれるの
    f_id = ("your-felica-id",)
    for user in c.execute('select id,name,presence from users where id=?',f_id) :
        #叩く
        knock_api( user[1], user[2] )
        #退勤反転
        c.execute('UPDATE users SET presence=? WHERE id=?', ( 1 if user[2]==0 else 0, user[0] ) )
        conn.commit()

    conn.close()



#users流し込んだりテーブル立てたりするの
def setup():
    users = json.load(open('users.json','r'))
    # なければテーブルを作るの
    try:
        c.execute('''CREATE TABLE users (id varchar(256) PRIMARY KEY UNIQUE, name varchar(64), presence int)''')
        conn.commit()
    except sqlite3.OperationalError: None

    # 新規ユーザー追加したりするの
    try:
        before = []
        for user in c.execute('SELECT * FROM users') : before.append(user)
        c.executemany('REPLACE INTO users (id, name, presence) VALUES (?,?,?)', users)
        c.executemany('REPLACE INTO users (id, name, presence) VALUES (?,?,?)', before)
        conn.commit()
    except sqlite3.IntegrityError: None




#slack api 叩くの
def knock_api(name,presence):
    status = "出勤" if presence==0 else "退勤"
    d = datetime.datetime.today()#スタンプ作るの
    stamp = "%s年%02d月%02d日%02d:%02d" % (d.year,d.month,d.day,d.hour,d.minute)
    base_url = "https://slack.com/api/chat.postMessage"
    params = json.load(open('slack.json','r'))
    params['username'] = '勤怠ログ'
    params['text'] = '\n>%s　%s　[%s]' % (stamp,name,status)
    headers={'Content-type':'application/x-www-form-urlencoded'}
    r = requests.post(base_url,data=params,headers=headers)
    beep()

#可否を伝えるベル。呼べばなる
def beep():
    SOUNDER = 21
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SOUNDER, GPIO.OUT, initial = GPIO.LOW)
    p = GPIO.PWM(SOUNDER, 1)
    p.start(50)
    p.ChangeFrequency(10000)
    time.sleep(0.2)
    p.ChangeFrequency(13000)
    time.sleep(0.1)
    p.stop()
    GPIO.cleanup()

#db接続
conn = sqlite3.connect('users.db')
c = conn.cursor()
main();
