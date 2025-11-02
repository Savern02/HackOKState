from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import User

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        organizations = current_user.get_orgs()
        organization_opportunities = [ org.get_opportunities() for org in organizations ]
        opportunities = [opp for sublist in organization_opportunities for opp in sublist]

        friends = current_user.get_friends()
        friends_pledges = [ friend.get_pledges() for friend in friends ]
        friend_opportunities = list(set([pledge.get_opportunity() for sublist in friends_pledges for pledge in sublist]))
        return render_template('dashboard.html', friend_opportunities=friend_opportunities, organization_opportunities=opportunities)
    else:
        return render_template('hero.html')