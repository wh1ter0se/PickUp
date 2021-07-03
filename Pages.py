from datetime import datetime
import time

import SQLutils

class Page():

    def __init__(self,user_ID,name,funcs,labels,init_func=None,prev_page=None):
        self.name = name
        self.user_ID = user_ID
        self.funcs = funcs
        self.labels = labels
        self.init_func = init_func
        self.prev_page = prev_page
        self.new_page = None
        self.has_funcs = len(funcs) != 0

    def init_message(name):
        print()
        print('--['+name+']---------------------')
        #print()

    def UI_selection(self):
        if self.prev_page is not None:
            print('0) Return to ' + self.prev_page.name)
        c = 0
        for label in self.labels:
            print(str(c+1) + ') ' + label)
            c += 1
        selection = int(input('Enter function number:')) - 1
        if selection == -1:
            self.new_page = self.prev_page
        else:
            func = self.funcs[selection]
            new_page = func()
            if new_page is not None:
                self.new_page = new_page

class LoginPage(Page):

    def __init__(self):
        name = 'Login'
        Page.init_message(name)
        username = str(input('Enter username:'))
        user_ID = SQLutils.get_user_ID(username)
        self.user_ID = user_ID
        funcs = []
        labels = []
        Page.__init__(self,user_ID,name,funcs,labels,init_func=self.init_func)

    def init_func(self):
        self.new_page = SplashPage(self.user_ID)

class SplashPage(Page):
    def __init__(self,user_ID):
        name = 'Splash'
        Page.init_message(name)
        #user_ID = prev_page.user_ID
        self.user_ID = user_ID
        funcs = [self.goto_friends,
                 self.goto_create_game]
        labels = ['Friends',
                  'Create Game']
        Page.__init__(self,user_ID,name,funcs,labels,init_func=self.init_func)
        #self.prev_page = prev_page

    def init_func(self):
        self.print_leaderboard()

    def print_leaderboard(self):
        leaderboard = SQLutils.get_leaderboard()
        leaderboard = leaderboard.loc[:,['username','gamesplayed','gameswon','goodgames']]
        print(leaderboard)

    def goto_friends(self):
        return FriendsPage(prev_page=SplashPage(self.user_ID))

    def goto_create_game(self):
        return CreateGamePage(prev_page=SplashPage(self.user_ID))

class FriendsPage(Page):

    def __init__(self,prev_page):
        name = 'Friends'
        Page.init_message(name)
        user_ID = prev_page.user_ID
        funcs = []
        labels = []
        Page.__init__(self,user_ID,name,funcs,labels,init_func=self.init_func,prev_page=prev_page)
        self.has_funcs = True

    def init_func(self):
        self.print_friends()

    def print_friends(self):
        friends = SQLutils.get_friends(self.user_ID)
        friends = friends.loc[:,['firstname','lastname','username','gamesplayed','gameswon','goodgames']]
        print(friends)

class CreateGamePage(Page):

    def __init__(self,prev_page):
        name = 'Create Game'
        Page.init_message(name)
        user_ID = prev_page.user_ID
        funcs = [self.select_court,
                 self.create_roster,
                 self.set_matches,
                 self.set_start_ts,
                 self.set_length_ts,
                 self.confirm_game]
        labels = ['Pick court',
                  'Pick players',
                  'Set matches',
                  'Set start time',
                  'Set length',
                  'Confirm game']
        Page.__init__(self,user_ID,name,funcs,labels,init_func=self.init_func,prev_page=prev_page)
        self.init_ts = time.time() + 5*60
        self.ts_length = 30 * 60
        self.court_ID = None
        self.roster_ID = None
        self.matches = 1

    def init_func(self):
        self.print_options()

    def print_options(self):
        if self.court_ID is None:
            print('[Court]:'+'Court has not been selected yet')
        else:
            print('[Court]: '+SQLutils.get_courtname(self.court_ID))
        if self.roster_ID is None:
            print('[Roster]:'+'Roster has not been created yet')
        else:
            print('[Roster]:')
            print(SQLutils.get_roster(self.roster_ID))
        print('[Matches]: ' + str(self.matches))
        print('[Start time]: ' + str(datetime.fromtimestamp(self.init_ts)))
        print('[End time]: ' + str(datetime.fromtimestamp(self.init_ts + self.ts_length)))

    def select_court(self):
        courts = SQLutils.get_all_courts()
        print(courts.loc[:,['ID','courtname','courtsavail']])
        self.court_ID = input('Select court ID:')

    def create_roster(self):
        self.roster_ID = SQLutils.create_roster(self.user_ID)
        roster = SQLutils.Roster(self.roster_ID)
        users = [self.user_ID]
        curr_input = ''
        while curr_input != '0':
            curr_input = input('Add user by username (or 0 to exit):')
            if curr_input != '0':
                user = SQLutils.get_user_ID(curr_input)
                if user is None:
                    print('Username does not exist')
                elif user == self.user_ID:
                    print('That is your username')
                else:
                    users.append(user)
                    roster.add_user(user)

    def set_matches(self):
        matches = input('Number of matches:')
        self.matches = matches

    def set_start_ts(self):
        start_ts = input('Start time (in seconds since epoch):')
        self.init_ts = start_ts

    def set_length_ts(self):
        length = input('Game length (in minutes):')
        self.ts_length = length * 60

    def confirm_game(self):
        if self.court_ID is None:
            print('No court has been picked yet')
        elif self.roster_ID is None:
            print('No roster has been created yet')
        else:
            SQLutils.insert_game(self.court_ID,
                                 self.roster_ID,
                                 self.init_ts,
                                 self.ts_length,
                                 self.matches)
            self.new_page = self.prev_page