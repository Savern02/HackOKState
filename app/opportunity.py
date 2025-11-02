from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models import Opportunity, Pledge
from . import db

opportunity_bp = Blueprint('opportunity', __name__)

@opportunity_bp.route('/opportunities/create', methods=['GET', 'POST'])
def create_opportunity():
    if request.method == 'GET':
        org_options = current_user.organizations
        return render_template('create-opportunity.html', org_options=org_options)
    else:
        title = request.form.get('title')
        org_id = request.form.get('org-id')
        description = request.form.get('description')

        new_opportunity = Opportunity(title=title, org_id=org_id, description=description)

        db.session.add(new_opportunity)
        db.session.commit()

        return redirect(url_for('opportunity.opp_detail', opp_id=new_opportunity.opp_id))

@opportunity_bp.route('/opportunities', methods=['GET'])
def opportunities():
    opportunities = Opportunity.query.all()
    popular_opportunities = sorted(opportunities, key=lambda opp: opp.pledges.count(), reverse=True)[:5]
    return render_template('opportunities.html', opportunities=opportunities, popular_opportunities=popular_opportunities)

@opportunity_bp.route('/opportunities/<int:opp_id>', methods=['GET'])
def opp_detail(opp_id):
    opportunity = Opportunity.query.get_or_404(opp_id)
    user_is_pledged = Opportunity.query.join(Opportunity.pledges).filter(
        Opportunity.opp_id == opp_id, Pledge.user_id == current_user.user_id).count() > 0 if current_user.is_authenticated else False
    return render_template('opp_detail.html', opportunity=opportunity, user_is_pledged=user_is_pledged)


@opportunity_bp.route('/opportunities/<int:opp_id>/pledge', methods=['POST'])
def pledge(opp_id):
    opportunity = Opportunity.query.get_or_404(opp_id)
    if not opportunity.is_pledged_by(current_user):
        opportunity.add_pledged_user(current_user)
        # flash('You have pledged for this opportunity!', 'success')
    return redirect(url_for('opportunity.opp_detail', opp_id=opp_id), 302)
