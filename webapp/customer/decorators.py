from functools import wraps

from flask import current_app, flash, request, redirect, url_for
from flask_login import config, current_user


def customer_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in config.EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.config.get('LOGIN_DISABLED'):
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif not current_user.is_customer:
            flash('Эта страница доступна только заказчикам')
            return redirect(url_for('sign.index'))
        return func(*args, **kwargs)
    return decorated_view
