flask_login_dictabase_blueprint
===============================

A Flask Blueprint for managing users.

Example App
===========

::

    from flask import Flask, render_template, flash
    from flask_login_dictabase_blueprint import (
        bp,
        VerifyLogin,
        VerifyAdmin,
        NewUser,
        ForgotPassword,
        MagicLink,
        AddAdmin,
        GetUsers,
        GetUser,
        SignedIn
    )
    import flask_dictabase

    app = Flask('Test')
    app.db = flask_dictabase.Dictabase(app)
    app.config["SECRET_KEY"] = "randomUnguessableString"
    app.register_blueprint(bp)


    @app.route('/')
    def Index():
        # This page is visible to anyone (logged in or not)
        return render_template('index.html', user=GetUser())


    @app.route('/private')
    @VerifyLogin
    def Private():
        # This page is only viewable to logged-in users.
        return render_template('private.html', user=GetUser())


    AddAdmin('grant@grant-miller.com')  # You can add one or more "admins"


    @app.route('/admin')
    @VerifyAdmin
    def Admin():
        # This page is only viewable by the admins
        return render_template(
            'admin.html',
            users=GetUsers(),
            user=GetUser(),
        )


    @NewUser
    def NewUserCallback(user):
        # Called whenever a new user is created
        print('NewUserCallback(user=', user)
        flash(f'Welcome new user {user["email"]}')


    @ForgotPassword
    def ForgotPasswordCallback(user, forgotURL):
        # Called when a user request to reset their password.
        # You should email the forgotURL to the user
        print('ForgotPasswordCallback(user=', user, forgotURL)
        flash('Send an email with the forgotURL to the user', 'info')


    @MagicLink
    def MagicLinkCallback(user, magicLink):
        # Used to simplify login. Email the magicLink to the user.
        # If they click on the magicLink, they will be logged in.
        print('MagicLinkCallback(user=', user, magicLink)
        flash('Send an email with the magic link to the user', 'info')


    @SignedIn
    def SignedInCallback(user):
        print(f'SignedIn {user["email"]}')




    if __name__ == '__main__':
        app.run(debug=True)