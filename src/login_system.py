from flask_login import LoginManager
from flask_login import UserMixin
from flask import current_app
from flask import redirect, request


class User(UserMixin):

    def __init__(self, data):
        self.data = data

    @classmethod
    def load(cls, user_id):
        data = current_app.db['users'].find({'name': user_id}).limit(1)[0]
        return cls(data)

    def get_id(self):
        return self.data['name']


def load_user(user_id):
    user = User.load(user_id)
    return user


def init_login_system(app):
    app.secret_key = 'my secret key!'
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.unauthorized_handler
    def unauthorized():
        referer = request.path
        url = "/login"
        if referer:
            url += "?next=" + referer
        return redirect(url)

    login_manager.user_callback = load_user

