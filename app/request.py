from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Request
from . import db

request_bp = Blueprint('request', __name__)

@request_bp.route('/request')
def request_page():
    return render_template('request.html')

@request_bp.route('/request', methods=['POST'])
def request_volunteers():
    title = request.form.get('title')
    org_id = request.form.get('org_id')
    description = request.form.get('description')

    new_request = Request(title=title, org_id=org_id, description=description)

    db.session.add(new_request)
    db.session.commit()

    flash('Volunteer request submitted successfully!', 'success')
    return redirect(url_for('request.request_page'))
