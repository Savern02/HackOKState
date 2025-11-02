from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models import Opportunity, Org, User
from . import db

opportunity_bp = Blueprint('opportunity', __name__)

@opportunity_bp.route('/opportunities/create', methods=['GET', 'POST'])
def create_opportunity():
    if request.method == 'GET':
        org_options = current_user.organizations
        return render_template('create-opportunity.html', org_options=org_options)
    else:
        title = request.form.get('title')
        org_id = request.form.get('org_select')
        description = request.form.get('description')

        new_opportunity = Opportunity(title=title, org_id=org_id, description=description)

        db.session.add(new_opportunity)
        db.session.commit()

        return redirect(url_for('opportunity.opp_detail', opp_id=new_opportunity.opp_id))

@opportunity_bp.route('/opportunities', methods=['GET'])
def opportunities():
    opportunities = Opportunity.query.all()
    return render_template('opportunities.html', opportunities=opportunities)

@opportunity_bp.route('/opportunities/<int:opp_id>', methods=['GET'])
def opp_detail(opp_id):
    opportunity = Opportunity.query.get_or_404(opp_id)
    return render_template('opp_detail.html', opportunity=opportunity)