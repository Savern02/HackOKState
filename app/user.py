from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from .models import User

users = Blueprint('users', __name__)

@users.route('/users')
def users_list():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@users.route('/users/<string:username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    is_friend = current_user.is_authenticated and current_user.is_friend(user)
    is_pending_friend = current_user.is_authenticated and current_user.has_requested_friendship(user)
    has_request_from = current_user.is_authenticated and user.has_requested_friendship(current_user)
    friends = user.friends()
    return render_template('profile.html', user=user, is_friend=is_friend, is_pending_friend=is_pending_friend, has_request_from=has_request_from, friends=friends)

@users.route('/users/<string:username>/add_friend', methods=['POST'])
@login_required
def add_friend(username):
    user = User.query.filter_by(username=username).first_or_404()
    current_user.send_friend_request(user)
    return redirect(url_for('users.user_profile', username=user.username), 302)

@users.route('/users/<string:username>/remove_friend', methods=['POST'])
@login_required
def remove_friend(username):
    user = User.query.filter_by(username=username).first_or_404()
    current_user.remove_friend(user)
    return redirect(url_for('users.user_profile', username=user.username), 302)

@users.route('/users/<string:username>/accept_friend', methods=['POST'])
@login_required
def accept_friend(username):
    user = User.query.filter_by(username=username).first_or_404()
    current_user.accept_friend_request(user)
    return redirect(url_for('users.user_profile', username=user.username), 302)