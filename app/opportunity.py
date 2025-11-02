from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models import Opportunity, Org, User
from . import db

opportunity_bp = Blueprint('opportunity', __name__)

@opportunity_bp.route('/opportunity')
def opportunities():
    return render_template('opportunities.html')

@opportunity_bp.route('/create-opportunity', methods=['POST'])
def create_opportunity():
    title = request.form.get('title')
    org_id = request.form.get('org_id')
    description = request.form.get('description')

    new_opportunity = Opportunity(title=title, org_id=org_id, description=description)

    db.session.add(new_opportunity)
    db.session.commit()

    flash('Volunteer request submitted successfully!', 'success')
    return render_template('create-opportunity.html')

@opportunity_bp.route('/opportunity')
@login_required
def get_current_user_orgs():
    # This function should return a list of Org objects associated with the current user.

    results = Org.query.filter_by(creator_id=current_user.user_id).all()

    return render_template('opportunity.html', orgs=results)
