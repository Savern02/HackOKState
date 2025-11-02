from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models import Org
from . import db

org = Blueprint('org', __name__)

@org.route('/create-org', methods=['POST', 'GET'])
@login_required
def create_org():
    if request.method == 'POST':
        org_name = request.form.get('org_name')
        creator_id = current_user.user_id

        new_org = Org(org_name=org_name, creator_id=creator_id)

        db.session.add(new_org)
        db.session.commit()

        # flash('Organization created successfully!', 'success')
        return redirect(url_for('org.org_detail', org_id=new_org.org_id), 302)
    elif request.method == 'GET':
        return render_template('create-org.html')
    else:
        return "Method Not Allowed", 405

@org.route('/orgs', methods=['GET'])
def organizations():
    orgs = Org.query.all()
    return render_template('organizations.html', orgs=orgs)

@org.route('/orgs/<int:org_id>', methods=['GET'])
def org_detail(org_id):
    organization = Org.query.get_or_404(org_id)
    return render_template('org_detail.html', organization=organization)