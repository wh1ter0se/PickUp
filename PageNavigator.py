import Pages, time

curr_page = Pages.LoginPage()

while True:
    if curr_page.init_func is not None:
        curr_page.init_func()
    if curr_page.has_funcs:
        curr_page.UI_selection()
    if curr_page.new_page is not None:
        curr_page = curr_page.new_page
