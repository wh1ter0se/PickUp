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
        user_ID = int(max_ID) + 1
    else:
        user_ID = 1
    query = '''INSERT INTO user (ID, firstname, lastname, username, usersince)
        VALUES ('''
    query += str(user_ID) + ',\'' + firstname + '\',\'' + str(lastname) + '\',\'' + str(username) + '\',' + str(init_ts) + ')'
    sql_engine.connect().execute(query)
    print('User ' + str(user_ID) + ' inserted successfully.')

def update_username(user_ID,username):
    query = 'UPDATE user SET username=\'' + username + '\' WHERE ID=' + str(user_ID)
    sql_engine.connect().execute(query)
    print('Username ' + str(username) + ' updated successfully.')

def update_firstname(user_ID,firstname):
    query = 'UPDATE user SET firstname=\'' + firstname + '\' WHERE ID=' + str(user_ID)
    sql_engine.connect().execute(query)
    print('First name ' + str(firstname) + ' updated successfully.')

def update_lastname(user_ID,lastname):
    query = 'UPDATE user SET lastname=\'' + lastname + '\' WHERE ID=' + str(user_ID)
    sql_engine.connect().execute(query)
    print('Last name ' + str(lastname) + ' updated successfully.')

def get_user_ID(username):
    query = 'SELECT ID FROM user WHERE username=\'' + username + '\''
    df = pd.read_sql(sql=query,con=sql_engine)
    if df.shape[0] != 0:
        user_ID = df.iloc[0,0]
    else:
        user_ID = None
    return user_ID

def get_all_users():
    return get_table_df('user')

def get_leaderboard(sortby='goodgames'):
    if (sortby != 'gamesplayed') and (sortby != 'gameswon'):
        sortby = 'goodgames'
    query = 'SELECT * FROM user ORDER BY ' + str(sortby) + ' DESC'
    return pd.read_sql(sql=query,con=sql_engine)

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

def get_all_friendships():
    return get_table_df('friendships')
    
def get_friends(user_ID):
    query = 'SELECT * FROM friendship WHERE userA_ID=' + str(user_ID)
    A_df = pd.read_sql(sql=query,con=sql_engine)
    A_friends = A_df.loc[:,'userB_ID']
    query = 'SELECT * FROM friendship WHERE userB_ID=' + str(user_ID)
    B_df = pd.read_sql(sql=query,con=sql_engine)
    B_friends = B_df.loc[:,'userA_ID']
    friend_IDs = pd.concat([A_friends,B_friends],axis=0).to_numpy()
    friends = pd.DataFrame()
    for friend_ID in friend_IDs:
        subquery = 'SELECT * FROM user WHERE ID=' + str(friend_ID)
        friend = pd.read_sql(sql=subquery,con=sql_engine)
        friends = pd.concat([friends,friend],axis=0)
    return friends

class Roster():
    def __init__(self,ID):
        self.ID = ID
        self.refresh()
        
    def refresh(self):
        self.users = self.get_users()

    def get_users(self):
        query = 'SELECT user_ID FROM roster WHERE ID=' + str(self.ID)
        user_IDs = pd.read_sql(sql=query, con=sql_engine).to_numpy()
        out_df = pd.DataFrame()
        for user_ID in user_IDs:
            subquery = 'SELECT * FROM user WHERE ID = ' + str(user_ID[0])
            user = pd.read_sql(sql=subquery, con=sql_engine)
            out_df = pd.concat([out_df,user],axis=0)
        return out_df

    def add_user(self,user_ID):
        query = 'INSERT INTO roster (ID, user_ID) VALUES ('
        query += str(self.ID) + ',' + str(user_ID) +  ')'
        sql_engine.connect().execute(query)
        print('User ' + str(user_ID) + ' added to roster ' + str(self.ID) + ' successfully.')

def create_roster(host_ID):
    max_ID = pd.read_sql(sql='SELECT MAX(ID) FROM roster', con=sql_engine).iloc[0,0]
    if max_ID is not None:
        roster_ID = int(max_ID) + 1
    else:
        roster_ID = 1
    query = 'INSERT INTO roster (ID, user_ID, ishost) VALUES ('
    query += str(roster_ID) + ',' + str(host_ID) + ',True)'
    sql_engine.connect().execute(query)
    print('Roster ' + str(roster_ID) + ' inserted successfully.')
    return roster_ID

def get_roster(roster_ID):
    query = 'SELECT * FROM roster WHERE ID=' + str(roster_ID)
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

def get_all_courts():
    return get_table_df('court')

def get_courtname(court_ID):
    query = 'SELECT courtname FROM court WHERE ID=' + str(court_ID)
    courtname = pd.read_sql(sql=query,con=sql_engine).iloc[0,0]
    return courtname

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

class Game():
    def __init__(self,ID):
        self.ID = ID
        self.refresh()

    def refresh(self):
        query = '''SELECT * FROM game
               WHERE ID=''' + str(self.ID)
        df = pd.read_sql(sql=query, con=sql_engine)
        self.court_ID = df.loc[0,'court_ID']
        self.roster_ID = df.loc[0,'roster_ID']
        self.reservation_ID = df.loc[0, 'reservation_ID']
        self.start_ts = df.loc[0,'start_ts']
        self.end_ts = df.loc[0,'end_ts']
        self.matches = df.loc[0,'matches']

def insert_game(court_ID,roster_ID,start_ts,ts_length,matches=1,reservation_ID=None):
    max_ID = pd.read_sql(sql='SELECT MAX(ID) FROM game', con=sql_engine).iloc[0,0]
    if max_ID is not None:
        ID = int(max_ID) + 1
    else:
        ID = 1
    end_ts = start_ts + ts_length
    if reservation_ID is None:
        query = 'INSERT INTO game (ID, court_ID, roster_ID, start_ts, end_ts, matches) VALUES ('
        query += str(ID) + ',' + str(court_ID) + ',' + str(roster_ID) + ',' + str(start_ts) + ',' + str(end_ts) + ',' + str(matches) + ')'
    else:
        query = 'INSERT INTO game (ID, court_ID, roster_ID, reservation_ID, start_ts, end_ts) VALUES ('
        query += str(ID) + ',' + str(court_ID) + ',' + str(roster_ID) + ',' + str(reservation_ID) + ',' + str(start_ts) + ',' + str(end_ts) + ')'
    sql_engine.connect().execute(query)
    print('Court ' + str(ID) + ' inserted successfully.')
    return ID

def get_games(game_ID=None,court_ID=None,ts_range=None,cols=None):
    query = 'SELECT * FROM game'
    params = []
    if game_ID is not None:
        params.append('ID=' + str(game_ID))
    if court_ID is not None:
        params.append('court_ID=' + str(court_ID))
    if ts_range is not None:
        start_ts = ts_range[0]
        end_ts = ts_range[1]
        if start_ts is not None:
            params.append('start_ts>=' + str(start_ts))
        if end_ts is not None:
            params.append('start_ts<=' + str(end_ts))
    if params:
        condition = ' WHERE '
        for param in range(0,len(params)-1):
            condition += param + ' AND '
        condition += params[len(params)-1]
        query += condition
    #print(query)
    df = pd.read_sql(sql=query,con=sql_engine)
    if cols is not None:
        df = df.loc[:,cols]
    return df
    

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
#print(get_all_courts())
#insert_user('Billy','Bob','bbob')
#print(get_leaderboard())
#print(get_friends(1))
#insert_roster(1)
#roster = Roster(1)
#roster.add_user(2)
#print(roster.users)
#user = User(1)
#print(user.df)
#user.add_games_won(1)
#print(user.df)
#start_ts = time.time() + 30 * 60
#insert_game(2,)
#print(get_games(ts_range=[1625296800,None]))