# coding: utf-8
import RPi.GPIO as GPIO
import sqlite3,json,requests,datetime,time,nfc,binascii,os


def main():
    setup()
    #TODO:フェリカリーダー待機するの
    TIME_cycle = 1.0
    TIME_interval = 0.2
    target = nfc.clf.RemoteTarget("212F")
    target.sensf_req = bytearray.fromhex("0000030000")
    while True:
            clf = nfc.ContactlessFrontend("usb")
            target_res = clf.sense(
                target,
                iterations=int(TIME_cycle//TIME_interval)+1,
                interval=TIME_interval)
            if target_res is not None:
                tag = nfc.tag.activate_tt3(clf, target_res)
                tag.sys = 3
                id = binascii.hexlify(tag.idm)
                logging(id);
                time.sleep(3)
            clf.close()

def logging(id):
    print('id:',id);
    #TODO:読み取ったIDいれるの
    f_id = (id,)
    for user in c.execute('select id,name,presence from users where id=?',f_id) :
        #叩く
        beep(True)
        knock_api( user[1], user[2] )
        #退勤反転
        c.execute('UPDATE users SET presence=? WHERE id=?', ( 1 if user[2]==0 else 0, user[0] ) )
        conn.commit()

#users流し込んだりテーブル立てたりするの
def setup():
    users = json.load(open('%s/users.json'%abspath,'r'))
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
    params = json.load(open('%s/slack.json'%abspath,'r'))
    params['username'] = '勤怠ログ'
    params['text'] = '\n>%s　%s　[%s]' % (stamp,name.encode('utf-8'),status)
    headers={'Content-type':'application/x-www-form-urlencoded'}
    r = requests.post(base_url,data=params,headers=headers)


#可否を伝えるベル。呼べばなる
def beep(success):
    do,re,mi,fa,so,ra,si = 261.626,293.665,329.628,349.228,391.995,440.,493.883
    octave = 1
    SOUNDER = 21
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SOUNDER, GPIO.OUT, initial = GPIO.LOW)
    p = GPIO.PWM(SOUNDER, 1)
    p.start(50)
    p.ChangeFrequency( si*4 if success else so )
    time.sleep( 0.1 if success else 0.5 )
    p.stop()
    time.sleep( 0.05 if success else 0.5 )
    p.start(50)
    p.ChangeFrequency( mi*8 if success else so )
    time.sleep( 0.2 if success else 0.5 )
    p.stop()
    GPIO.cleanup()

#db接続
abspath = os.path.abspath(os.path.dirname(__file__))
conn = sqlite3.connect('%s/users.db' % abspath)
c = conn.cursor()
users = None
main()
conn.close()
