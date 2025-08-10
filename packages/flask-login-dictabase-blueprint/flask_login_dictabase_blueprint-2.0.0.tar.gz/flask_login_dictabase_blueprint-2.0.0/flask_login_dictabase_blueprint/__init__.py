import functools
import hashlib
import uuid
import warnings

import flask_dictabase
import flask_login
from flask import (
    Blueprint,
    flash,
    redirect,
    request,
    render_template, Flask
)

LOGIN_FAILED_FLASH_MESSAGE = 'Username and/or Password is incorrect. Please try again.'
bp = Blueprint('login', __name__, template_folder='templates')


class UserClass(flask_login.UserMixin, flask_dictabase.BaseTable):
    def get_id(self, *a, **k):
        print('UserClass.get_id(', a, k, self)
        return self['id']

    def __str__(self):
        return flask_dictabase.BaseTable.__str__(self)


app = None


@bp.record
def record(state):
    global app
    app = state.app
    print('Record(state=', state)

    if not hasattr(state.app, 'db'):
        raise KeyError('state has no attribute "db". You must run flask_dictabase.Dictabase(app) first.')

    if not state.app.config.get('SECRET_KEY', None):
        raise KeyError(
            'flask_login requires a SECRET_KEY in the app.config. Try calling app.config["SECRET_KEY"] = "randomUnguessableString" first')

    loginManager = flask_login.LoginManager()
    loginManager.login_view = '/login'
    loginManager.init_app(state.app)

    @loginManager.user_loader
    def LoadUser(user_id):
        return state.app.db.FindOne(UserClass, id=int(user_id))


@bp.route('/login', methods=['GET', 'POST'])
def login_page():
    user = get_current_user()
    if user:
        print('user already logged in, redirecting to "/"')
        flash(f'You are currently logged in as "{user["email"]}".', 'success')
        return redirect('/')

    if request.method == 'POST':

        email = request.form.get('email', None)
        email = email.lower() if email else None

        password = request.form.get('password', None)
        passwordHash = get_hash(password, salt=email) if password else None

        if password is None:
            flash('Please enter a password.', 'danger')

        if email is None:
            flash('Please enter a username.', 'danger')

        if email and password:
            userObj = app.db.FindOne(UserClass, email=email)

            if userObj is None:
                print('User with this email does not exist in db')
                flash(LOGIN_FAILED_FLASH_MESSAGE, 'danger')
                kwargs = renderTemplateCallback('login.html') if renderTemplateCallback else {}
                return render_template(
                    'login.html',
                    **kwargs,
                )
            else:
                if userObj.get('passwordHash', None) == passwordHash:
                    # correct password
                    flask_login.login_user(
                        userObj,
                        remember=True,
                        force=True,
                    )
                    _do_signed_in_callback(userObj)
                    return redirect(request.args.get('next', None) or '/')

                else:
                    print('Wrong password')
                    flash(LOGIN_FAILED_FLASH_MESSAGE, 'danger')
                    return redirect('/login')

        else:
            # user did not enter a email/password, try again
            kwargs = renderTemplateCallback('login.html') if renderTemplateCallback else {}
            return render_template(
                'login.html',
                **kwargs,
            )

    kwargs = renderTemplateCallback('login.html') if renderTemplateCallback else {}
    return render_template(
        'login.html',
        **kwargs,
    )


@bp.route('/logout')
def logout_current_user():
    logout_user()
    return redirect('/')


@bp.route('/register', methods=['GET', 'POST'])
def register_new_user():
    email = request.form.get('email', None)
    email = email.lower() if email else None

    password = request.form.get('password', None)
    passwordConfirm = request.form.get('passwordConfirm', None)

    if request.method == 'POST':
        if email is None:
            flash('Please provide an email address.', 'danger')
        if password != passwordConfirm:
            flash('Passwords do not match.', 'danger')

        existingUser = app.db.FindOne(UserClass, email=email)
        if existingUser is not None:
            flash('Invalid Email', 'danger')
        elif passwordConfirm == password:
            newUser = app.db.New(
                UserClass,
                email=email.lower(),
                passwordHash=get_hash(password, salt=email),
            )
            flask_login.login_user(
                newUser,
                remember=True,
                force=True,
            )
            flash('Your account has been created. Thank you.', 'success')
            if newUserCallbacks:
                for func in newUserCallbacks:
                    func(newUser)

            _do_signed_in_callback(newUser)
            return redirect(request.args.get('next', None) or '/')

        kwargs = renderTemplateCallback('register.html') if renderTemplateCallback else {}
        return render_template(
            'register.html',
            **kwargs,
        )

    else:
        kwargs = renderTemplateCallback('register.html') if renderTemplateCallback else {}
        return render_template(
            'register.html',
            **kwargs,
        )


@bp.route('/forgot', methods=['GET', 'POST'])
def forgot_requested():
    if request.method == 'POST':
        if request.form.get('password', None) != request.form.get('passwordConfirm', None):
            flash('Passwords do not match.', 'danger')
            kwargs = renderTemplateCallback('forgot.html') if renderTemplateCallback else {}
            return render_template(
                'forgot.html',
                **kwargs,
            )

        resetToken = str(uuid.uuid4())
        resetURL = f'/reset_password/{resetToken}'

        email = request.form.get('email', '').lower()

        user = app.db.FindOne(UserClass, email=email)
        if user is None:
            pass
        else:
            user['resetToken'] = resetToken
            user['tempPasswordHash'] = get_hash(request.form.get('password'), salt=email)
            if forgotPasswordCallback:
                forgotPasswordCallback(user, resetURL)
        return redirect('/')

    else:
        kwargs = renderTemplateCallback('forgot.html') if renderTemplateCallback else {}
        return render_template(
            'forgot.html',
            **kwargs,
        )


@bp.route('/reset_password/<resetToken>')
def reset_password_token_submitted(resetToken):
    user = app.db.FindOne(UserClass, resetToken=resetToken)
    if user:
        tempHash = user.get('tempPasswordHash', None)
        if tempHash:
            user['passwordHash'] = tempHash
            user['resetToken'] = None
            user['tempPasswordHash'] = None
            flash('Your password has been changed.', 'success')
    else:
        flash('Unrecognized token', 'danger')

    return redirect('/')


@bp.route('/magic_link', methods=['GET', 'POST'])
def magic_link_submitted():
    if request.method == 'POST':
        email = request.form.get('email', None)
        email = email.lower() if email else None
        if email is None:
            flash('Please enter your email address.')
        else:
            print('email=', email)
            existingUser = app.db.FindOne(UserClass, email=email)
            if existingUser:
                magicCode = str(uuid.uuid4())
                existingUser['magic_code'] = magicCode
                magicLink = f'/magic_link_login?magic_code={magicCode}'
                if magicLinkCallback:
                    magicLinkCallback(existingUser, magicLink)
                else:
                    raise RuntimeError(
                        'No magic link callback.'
                        'Use the @MagicLink decorator to email the magic link to the user.'
                        '@MagicLink'
                        'def MagicLinkCallback(user, magicLink):'
                        '    SendEmail(to=user["email"], body=magicLink)'
                    )
            flash('A magic link has been emailed to you. Click the magic link to login.', 'success')

    kwargs = renderTemplateCallback('magic_link.html') if renderTemplateCallback else {}
    return render_template(
        'magic_link.html',
        **kwargs,
    )


@bp.route('/magic_link_login', methods=['GET', 'POST'])
def magic_link_login():
    magicCode = request.args.get('magic_code', None)
    user = app.db.FindOne(UserClass, magic_code=magicCode)
    if user:
        flask_login.login_user(user, remember=True, force=True)
        _do_signed_in_callback(user)
        flash('You are now logged in. :-)', 'success')
    else:
        flash('Unrecognized magic code', 'danger')
    return redirect('/')


def get_current_user(email=None):
    # return user object if logged in, else return None
    # if user provides an email then return that user obj
    if email:
        return app.db.FindOne(UserClass, email=email)

    user = flask_login.current_user
    if user.is_anonymous:
        return None
    return user


def verify_is_user(func):
    '''
    Use this decorator on view's that require a log in, it will auto redirect to login page
    :param func:
    :return:
    '''

    return flask_login.login_required(func)


def verify_is_admin(func):
    @functools.wraps(func)
    def verify_admin_wrapper(*a, **k):
        user = get_current_user()
        if user and user['email'] in admins:
            return func(*a, **k)
        else:
            flash('You are not an admin.', 'danger')
            return redirect('/')

    return verify_admin_wrapper


newUserCallbacks = []


def new_user(func):
    global newUserCallbacks
    newUserCallbacks.append(func)


forgotPasswordCallback = None


def forgot_password(func):
    global forgotPasswordCallback
    forgotPasswordCallback = func


magicLinkCallback = None


def on_magic_link_created(func):
    global magicLinkCallback
    magicLinkCallback = func


signedInCallback = None


def on_signin(func):
    global signedInCallback
    signedInCallback = func


def _do_signed_in_callback(user):
    if signedInCallback:
        signedInCallback(user)


renderTemplateCallback = None


def do_render_template(func):
    # func should accept one argument, a str indictating the template name
    # func should return a dict of kwargs to be used when rendering the template
    global renderTemplateCallback
    renderTemplateCallback = func


def logout_user():
    print('LogoutUser()')
    flask_login.logout_user()


def get_hash(strng, salt=''):
    salt = app.config.get('SECRET_KEY', '') + salt
    hash1 = hashlib.sha512(bytes(strng, 'utf-8')).hexdigest()
    hash1 += salt
    hash2 = hashlib.sha512(bytes(hash1, 'utf-8')).hexdigest()
    return hash2


admins = set()


def add_admin(email):
    admins.add(email.lower())


def get_admins():
    return admins.copy()


def get_users():
    warnings.warn(
        f"Function GetUsers is deprecated. We are moving to pep8. Please use get_users() in the future.",
        category=DeprecationWarning,
        stacklevel=2
    )
    return app.db.FindAll(UserClass)


def is_admin():
    '''
    :return: True if the current user is an admin, False otherwise
    '''
    return get_current_user()['email'] in get_admins() if get_current_user() else False


def get_app(config):
    '''
    A quick way to get the app with the blueprint already applied
    :return:
    '''
    new_app = Flask('Test Page')
    new_app.config['SECRET_KEY'] = config['SECRET_KEY'] if isinstance(config, dict) else config.SECRET_KEY
    new_app.db = flask_dictabase.Dictabase(new_app)
    new_app.register_blueprint(bp)
    return new_app
