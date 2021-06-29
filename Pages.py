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

    def init_message(self):
        print('['+self.name+']')
        if self.init_func is not None:
            self.init_func()

    def user_selection(self):
        if self.prev_page is not None:
            print('0) ' + self.prev_page.name)
        c = 0
        for label in self.labels:
            print(str(c+1) + ') ' + label)
        selection = int(input('Enter function number:')) - 1
        func = self.funcs[selection]
        new_page = func()
        if new_page is not None:
            self.new_page = new_page

class LoginPage(Page):
    def __init__(self):
        user_ID = input('Enter username:')
        name = 'Login'
        funcs = []
        labels = []
        Page.__init__(user_ID,name,funcs,labels)

    def init_func(self):
        Page.new_page = SplashPage(Page)

class SplashPage(Page):
    def __init__(self,prev_page):
        user_ID = prev_page.user_ID
        name = 'Splash'
        funcs = [self.goto_friends]
        labels = ['Friends']
        Page.__init__(user_ID,name,funcs,labels,init_func=self.init_func)

    def init_func(self):
        self.print_leaderboard()

    def print_leaderboard():
        leaderboard = SQLutils.get_leaderboard()
        leaderboard = leaderboard.loc[:,['username','gamesplayed','gameswon','goodgames']]
        print(leaderboard)

    def goto_friends():
        return FriendsPage(prev_page=SplashPage(Page))

class FriendsPage(Page):

    def __init__(self,prev_page):
        user_ID = prev_page.user_ID
        name = 'Friends'
        funcs = []
        labels = []
        Page.__init__(user_ID,name,funcs,labels,init_func=self.init_func,prev_page=prev_page)

    def init_func(self):
        self.print_friends()

    def print_friends(self):
        friends = SQLutils.get_friends(Page.user_ID)
        print(friends)
