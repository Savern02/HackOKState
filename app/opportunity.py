from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Request
from . import db

opportunity_bp = Blueprint('request', __name__)

@opportunity_bp.route('/request')
def request_page():
    return render_template('request.html')

@opportunity_bp.route('/request', methods=['POST'])
def create_opportunity():
    title = request.form.get('title')
    org_id = request.form.get('org_id')
    description = request.form.get('description')

    new_opportunity = Request(title=title, org_id=org_id, description=description)

    db.session.add(new_opportunity)
    db.session.commit()

    flash('Volunteer request submitted successfully!', 'success')
    return redirect(url_for('request.request_page'))
