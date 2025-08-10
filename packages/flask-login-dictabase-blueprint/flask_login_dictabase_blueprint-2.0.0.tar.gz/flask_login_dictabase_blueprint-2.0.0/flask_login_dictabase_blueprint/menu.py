from flask_login_dictabase_blueprint import get_current_user, admins

menu = []


def GetMenu(active=None):
    m = menu.copy()

    for item in m:
        item['active'] = item['title'] == active

    user = get_current_user()
    if user:
        m.append(dict(title='Logout', url='/logout', active=False))
    else:
        m.append(dict(title='Login', url='/login', active=False))
        m.append(dict(title='Sign Up', url='/register', active=False))

    # m now contains everything

    # remove things that are user only
    if user is None:
        for item in m.copy():
            if item.get('userOnly', False):
                m.remove(item)

    # remove admin menu options if user is not admin
    if user is None or user['email'] not in admins:
        for item in m.copy():
            if item.get('adminOnly', False):
                m.remove(item)

    return m


def AddMenuOption(title, url, adminOnly=False, userOnly=False):
    global menu
    item = dict(title=title, url=url, active=False, adminOnly=adminOnly, userOnly=userOnly)
    menu.append(item)
    menu = sorted(menu, key=lambda i: i['title'].upper())


def Setup(app):
    pass
