from sqlalchemy import MetaData, Table, Column,Integer,String,Time,create_engine
import sqlite3
class ProfileDB:
    def __init__(self):
        engine = create_engine('sqlite:///Data.db')
        metadata = MetaData()

        account = Table(
            'account', metadata,
            Column('id', Integer, primary_key=True),
            Column('session_name', String),
            Column('wallet', String),
            Column('proxy', String),
            Column('twitter', String),
            Column('discord', String),
            Column('mail', String),
            Column('user_agent', String),
            Column('created', Time),
            Column('session_end', Time),
        )
        metadata.create_all(engine)

        self.con = sqlite3.connect('../../../data/Data.db')
        self.cur = self.con.cursor()

    def AddData(self, id: int, session_name: str, wallet: str = None, proxy: str = None, twitter: str = None, discord: str = None, mail: str = None, user_agent: str = None, created: str = None, session_end: str = None) -> None:
        info = (id, session_name, wallet, proxy, twitter, discord, mail, user_agent, created, session_end)
        self.cur.execute("INSERT INTO account (id, session_name, wallet, proxy, twitter, discord, mail, user_agent, created, session_end) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", info)
        self.con.commit()

    def Search(self,name,value):
        global result
        if name == 'id':
            result = self.cur.execute(f"""SELECT * FROM account WHERE id = {value}""").fetchone()
        if name == 'session_name':
            result = self.cur.execute(f"""SELECT * FROM account WHERE session_name = {value}""").fetchone()
        if name == 'wallet':
            result = self.cur.execute(f"""SELECT * FROM account WHERE wallet = {value}""").fetchone()
        if name == 'proxy':
            result = self.cur.execute(f"""SELECT * FROM account WHERE proxy = {value}""").fetchone()
        if name == 'twitter':
            result = self.cur.execute(f"""SELECT * FROM account WHERE twitter = {value}""").fetchone()
        if name == 'discord':
            result = self.cur.execute(f"""SELECT * FROM account WHERE discord = {value}""").fetchone()
        if name == 'mail':
            result = self.cur.execute(f"""SELECT * FROM account WHERE mail = {value}""").fetchone()
        if name == 'created':
            result = self.cur.execute(f"""SELECT * FROM account WHERE created = {value}""").fetchone()
        if name == 'session_end':
            result = self.cur.execute(f"""SELECT * FROM account WHERE session_end = {value}""").fetchone()
        if name == 'user_agent':
            result = self.cur.execute(f"""SELECT * FROM account WHERE user_agent = {value}""").fetchone()
        return result

class Profile:
    def __init__(self, result):
        self.id = result[0]
        self.name = result[1]
        self.wallet = result[2]
        self.proxy = result[3]
        self.twitter = result[4]
        self.discord = result[5]
        self.mail = result[6]
        self.user_agent = result[7]
        self.created = result[8]
        self.session_end = result[9]

Da = ProfileDB()
Da.AddData(283,'Poor','Ruby','124.23.3.21','Elon','Fichik','kwldwk@gmail.com','Yaya','00:10:00.0000000','01:20:34.0000000')
Da.AddData(284,'Poor','Ruby','124.23.3.21','Elon','Fichik','kwldwk@gmail.com','Yaya','00:10:00.0000000','01:20:34.0000000')

Profile1 = Profile(Da.Search('id',283))
print(Profile1.proxy)
Da.Search('id',284)