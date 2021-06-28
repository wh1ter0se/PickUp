from sqlalchemy import create_engine
import pandas as pd
import time
import googlemaps
import gmplot

maps_API_key = open('API_keys/.googlemapsAPIkey','r').read()
gmaps = googlemaps.Client(key=maps_API_key)

schema_name = 'schema_1-0'

def generate_engine():
    prefix = 'mysql://'
    user = open('DB_login/.dbuser','r').read()
    password = open('DB_login/.dbpass','r').read()
    host = open('DB_login/.dbhost','r').read()
    engine_address = prefix + user + ':' + password + '@' + host + '/' + schema_name
    sql_engine = create_engine(engine_address)
    return sql_engine

sql_engine = generate_engine()

def get_table_df(table_name):
    query = "SELECT * FROM " + table_name
    stored_df = pd.read_sql(sql=query,
                            con=sql_engine)
    return stored_df



class User():
    def __init__(self,ID):
        self.ID = ID
        self.refresh()

    def refresh(self):
        print('ID = ' + str(self.ID))
        query = '''SELECT * FROM user
               WHERE ID = ''' + str(self.ID)
        df = pd.read_sql(sql=query, con=sql_engine)
        self.df=df
        self.firstname = df.loc[0,'firstname']
        self.lastname = df.loc[0,'lastname']
        self.username = df.loc[0, 'username']
        self.games_played = df.loc[0,'gamesplayed']
        self.games_won = df.loc[0,'gameswon']
        self.good_games = df.loc[0,'goodgames']

    def add_games_played(self,delta):
        games_played = pd.read_sql(
            sql='SELECT gamesplayed FROM user WHERE ID=' + str(self.ID), 
            con=sql_engine).iloc[0,0]
        games_played += delta
        query = 'UPDATE user SET gamesplayed=' + str(games_played) + ' WHERE ID=' + str(self.ID)
        sql_engine.connect().execute(query)
        self.refresh()

    def add_games_won(self,delta):
        games_won = pd.read_sql(
            sql='SELECT gameswon FROM user WHERE ID=' + str(self.ID), 
            con=sql_engine).iloc[0,0]
        games_won += delta
        query = 'UPDATE user SET gameswon=' + str(games_won) + ' WHERE ID=' + str(self.ID)
        sql_engine.connect().execute(query)
        self.refresh()
    
    def add_good_games(self,delta):
        ggs = pd.read_sql(
            sql='SELECT goodgames FROM user WHERE ID=' + str(self.ID), 
            con=sql_engine).iloc[0,0]
        ggs += delta
        query = 'UPDATE user SET goodgames=' + str(ggs) + ' WHERE ID=' + str(self.ID)
        sql_engine.connect().execute(query)
        self.refresh()  

def insert_user(firstname,lastname,username):
    init_ts = time.time()
    max_ID = pd.read_sql(sql='SELECT MAX(ID) FROM user', con=sql_engine).iloc[0,0]
    if max_ID is not None:
        ID = int(max_ID) + 1
    else:
        ID = 1
    query = '''INSERT INTO user (ID, firstname, lastname, username, usersince)
        VALUES ('''
    query += str(ID) + ',\'' + firstname + '\',\'' + str(lastname) + '\',\'' + str(username) + '\',' + str(init_ts) + ')'
    query = str(query)
    sql_engine.connect().execute(query)
    print('User ' + str(ID) + ' inserted successfully.')

def insert_friendship(userA_ID,userB_ID):
    init_ts = time.time()
    max_ID = pd.read_sql(sql='SELECT MAX(ID) FROM friendship', con=sql_engine).iloc[0,0]
    if max_ID is not None:
        ID = int(max_ID) + 1
    else:
        ID = 1
    query = '''INSERT INTO friendship (ID, userA_ID, userB_ID, init_ts)
        VALUES ('''
    query += str(ID) + ',' + str(userA_ID) + ',' + str(userB_ID) + ',' + str(init_ts) + ')'
    query = str(query)
    sql_engine.connect().execute(query)
    print('Friendship ' + str(ID) + ' inserted successfully.')

def get_friends(userID):
    query = 'SELECT * FROM friendship WHERE userA_ID=\'' + str(userID) + '\''
    A_df = pd.read_sql(sql=query,con=sql_engine)
    A_friends = A_df.loc[:,'userB_ID']
    query = 'SELECT * FROM friendship WHERE userB_ID=\'' + str(userID) + '\''
    B_df = pd.read_sql(sql=query,con=sql_engine)
    B_friends = B_df.loc[:,'userA_ID']
    return pd.concat([A_friends,B_friends],axis=0)

def get_leaderboard(sortby='goodgames'):
    if (sortby != 'gamesplayed') and (sortby != 'gameswon'):
        sortby = 'goodgames'
    query = 'SELECT * FROM user ORDER BY ' + str(sortby) + ' DESC'
    return pd.read_sql(sql=query,con=sql_engine)

class Court():
    def __init__(self,ID):
        self.ID = ID
        self.refresh()

    def refresh(self):
        query = '''SELECT * FROM court
               WHERE ID=''' + str(self.ID)
        df = pd.read_sql(sql=query, con=sql_engine)
        self.df = df
        self.name = df.loc[0,'courtname']
        self.courts = df.loc[0,'courtsavail']
        self.games_played = df.loc[0, 'gamesplayed']
        self.latitude = df.loc[0,'latitude']
        self.longitude = df.loc[0,'longitude']

    def add_games_played(self,delta):
        games_played = pd.read_sql(
            sql='SELECT gamesplayed FROM court WHERE ID=' + str(self.ID), 
            con=sql_engine).iloc[0,0]
        games_played += delta
        query = 'UPDATE court SET gamesplayed=' + str(games_played) + ' WHERE ID=' + str(self.ID)
        sql_engine.connect().execute(query)
        self.refresh()

def insert_court(name,courts,latitude,longitude):
    max_ID = pd.read_sql(sql='SELECT MAX(ID) FROM court', con=sql_engine).iloc[0,0]
    if max_ID is not None:
        ID = int(max_ID) + 1
    else:
        ID = 1
    query = '''INSERT INTO court (ID, courtname, courtsavail, latitude, longitude)
        VALUES ('''
    query += str(ID) + ',\'' + name + '\',' + str(courts) + ',' + str(latitude) + ',' + str(longitude) + ')'
    query = str(query)
    sql_engine.connect().execute(query)
    print('Court ' + str(ID) + ' inserted successfully.')

def all_court_IDs():
    query = 'SELECT ID FROM court'
    return pd.read_sql(sql=query,con=sql_engine).loc[:,'ID']

def plot_all_courts():
    lat = []
    lng = []
    lbl = []
    for court_ID in all_court_IDs():
        court = Court(court_ID)
        lat.append(court.latitude)
        lng.append(court.longitude)
        lbl.append(court.name)
        print(court_ID)
    gmap = gmplot.GoogleMapPlotter(lat[0],lng[0],13)
    gmap.scatter(lat,lng,title=lbl,size=120,color='#FF0000',marker=True)
    gmap.apikey = maps_API_key
    gmap.draw('C:\\Users\\camel\\Documents\\Git\\PickUp\\gmap.html')

#print(get_table_df('user'))
#print(gmaps.geocode('Brittingham Park - Basketball Court'))

#insert_court('Edward Klief Park',2,43.066923,-89.406920)
#court = get_court(1)
#print(court.loc[0,'latitude'])
#print(court.loc[0,'longitude'])
#court = Court(5)
#print(court.df)
#court.add_games_played(1)
#print(court.df)
plot_all_courts()
#insert_user('Billy','Bob','bbob')
print(get_leaderboard())
print(get_friends(1))
#user = User(1)
#print(user.df)
#user.add_games_won(1)
#print(user.df)
