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
        print('['+name+']')

    def UI_selection(self):
        if self.prev_page is not None:
            print('0) Return to ' + self.prev_page.name)
        c = 0
        for label in self.labels:
            print(str(c+1) + ') ' + label)
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
        funcs = [self.goto_friends]
        labels = ['Friends']
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
        funcs = []
        labels = []
        Page.__init__(self,user_ID,name,funcs,labels,prev_page=prev_page)
