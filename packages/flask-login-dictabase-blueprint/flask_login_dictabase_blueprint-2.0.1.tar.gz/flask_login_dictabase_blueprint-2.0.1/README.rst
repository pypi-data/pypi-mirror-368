flask_login_dictabase_blueprint
===============================

A Flask Blueprint for managing users.

Example App
===========

::

    import time

    from flask import render_template, flash, jsonify

    from flask_login_dictabase_blueprint import (
        verify_is_user,
        verify_is_admin,
        new_user,
        forgot_password,
        on_magic_link_created,
        add_admin,
        get_users,
        get_current_user,
        on_signin,
        do_render_template,
        menu,
        get_app
    )

    app = get_app({
        'SECRET_KEY': 'random_string',
    })


    @app.route('/')
    def index():
        """This page is visible to anyone (logged in or not)."""
        return render_template('index.html', user=get_current_user())


    @app.route('/private')
    @verify_is_user
    def private():
        """This page is only viewable to logged-in users."""
        return render_template('private.html', user=get_current_user())


    add_admin('grant@grant-miller.com')  # You can add one or more "admins"


    @app.route('/admin')
    @verify_is_admin
    def admin():
        """This page is only viewable by the admins."""
        return render_template(
            'admin.html',
            users=get_users(),
            user=get_current_user(),
        )


    @new_user
    def new_user_callback(user):
        """Called whenever a new user is created."""
        print('NewUserCallback(user=', user)
        flash(f'Welcome new user {user["email"]}')


    @forgot_password
    def forgot_password_callback(user, forgot_url):
        """Called when a user requests to reset their password. You should email the forgot_url to the user."""
        print('ForgotPasswordCallback(user=', user, forgot_url)
        flash('Send an email with the forgot_url to the user', 'info')


    @on_magic_link_created
    def magic_link_callback(user, magic_link):
        """Used to simplify login. Email the magic_link to the user. If they click on the magic_link, they will be logged in."""
        print('MagicLinkCallback(user=', user, magic_link)
        flash('Send an email with the magic link to the user', 'info')


    @on_signin
    def signed_in_callback(user):
        print(f'SignedIn {user["email"]}')


    @do_render_template
    def render_template_callback(template_name):
        print('RenderTemplateCallback(templateName=', template_name)
        return {
            'message': f'The time is {time.asctime()}',
            'title': 'My Title',
        }


    menu.AddMenuOption('Test Title', '/test_url', adminOnly=False)
    menu.AddMenuOption('Admin Title', '/admin_url', adminOnly=True)
    menu.AddMenuOption('User Title', '/user_url', userOnly=True)


    @app.route('/menu')
    def menu_view():
        return jsonify(menu.GetMenu())


    if __name__ == '__main__':
        app.run(debug=True)
