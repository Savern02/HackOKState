from flask import Blueprint, redirect, render_template, request, url_for
#from flask_login import current_user, login_required
from .models import Scrape
from . import db
from .webscraper import load_json_to_db, accept_link_to_scrape
import asyncio

discover = Blueprint('discover', __name__)


@discover.route('/locations')
def select_region(): 
    locations = Scrape.query.with_entities(Scrape.location).filter(Scrape.location != None).distinct().all()
    return render_template('discoverLoc.html', loc=locations)

#handles the string (request) received from the frontend 
@discover.route('/request_string', methods=['POST'])
def request_string():
    async def func(): 
        data = request.form.get('data')  # get the string from form data
        #accept_link_to_scrape(data)
        load_json_to_db(data)  # process the string as needed
    asyncio.run(func()) 
    return redirect(url_for('discover.select_region'))  # redirect back to the locations page

@discover.route('/locations_redirection', methods=['POST'])
def locations_redirection(): 
    location = request.form.get('location')
    return redirect(url_for('discover.show_discoveries', location=location))

@discover.route('/<location>', methods=['GET'])
def show_discoveries(location): 
    show_discoveries = Scrape.query.filter_by(location=location).all()
    return render_template('discover.html', discoveries=show_discoveries)




