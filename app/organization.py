from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models import Org
from . import db

org_bp = Blueprint('org', __name__)

@org_bp.route('/create-org', methods=['POST'])
@login_required
def create_org():
    if request.method == 'POST':
        org_name = request.form.get('org_name')
        creator_id = current_user.user_id

        new_org = Org(org_name=org_name, creator_id=creator_id)

        db.session.add(new_org)
        db.session.commit()

        flash('Organization created successfully!', 'success')
        return redirect(url_for('org.create_org'))
    return render_template('create-org.html')
