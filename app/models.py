from flask_login import UserMixin
from . import db


class User(db.Model, UserMixin):
	__tablename__ = 'user'
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(150), unique=True, nullable=False)
	email = db.Column(db.String(255), unique=True, nullable=False)
	password = db.Column(db.String(255), nullable=False)
	is_admin = db.Column(db.Boolean, default=False)

	# relationships
	pledges = db.relationship('Pledge', back_populates='user', lazy='dynamic')
	organizations = db.relationship('Org', backref='creator', lazy='dynamic')

	def __repr__(self):
		return f"<User {self.user_id} {self.email}>"
	
	def get_id(self):
		return str(self.user_id)

	def is_friend(self, other_user):
		# Use SQLAlchemy boolean operators (& and |) here. Using Python's
		# `and`/`or` would evaluate as Python boolean logic and not produce
		# the intended SQL expressions, which makes the check behave
		# incorrectly (directional or error). This matches the pattern used
		# in `remove_friend` below.
		friendship = Friends.query.filter(
			((Friends.friend_a == self.user_id) & (Friends.friend_b == other_user.user_id)) |
			((Friends.friend_a == other_user.user_id) & (Friends.friend_b == self.user_id))
		).first()
		return friendship is not None and friendship.accepted

	def has_requested_friendship(self, other_user):
		friendship = Friends.query.filter_by(friend_a=self.user_id, friend_b=other_user.user_id).first()
		return friendship is not None and not friendship.accepted

	def send_friend_request(self, other_user):
		if not self.is_friend(other_user) and not self.has_requested_friendship(other_user):
			friend_request = Friends(friend_a=self.user_id, friend_b=other_user.user_id, accepted=False)
			db.session.add(friend_request)
			db.session.commit()
	
	def accept_friend_request(self, other_user):
		friendship = Friends.query.filter_by(friend_a=other_user.user_id, friend_b=self.user_id).first()
		if friendship and not friendship.accepted:
			friendship.accepted = True
			db.session.commit()

	def remove_friend(self, other_user):
		friendship = Friends.query.filter(
			((Friends.friend_a == self.user_id) & (Friends.friend_b == other_user.user_id)) |
			((Friends.friend_a == other_user.user_id) & (Friends.friend_b == self.user_id))
		).first()
		if friendship:
			db.session.delete(friendship)
			db.session.commit()

	def get_friends(self):
		friendships = Friends.query.filter(
			((Friends.friend_a == self.user_id) | (Friends.friend_b == self.user_id)) &
			(Friends.accepted == True)
		).all()
		friend_ids = set()
		for friendship in friendships:
			if friendship.friend_a == self.user_id:
				friend_ids.add(friendship.friend_b)
			else:
				friend_ids.add(friendship.friend_a)
		return User.query.filter(User.user_id.in_(friend_ids)).all()
	
	def get_orgs(self):
		return Org.query.join(OrgMember, OrgMember.org_id == Org.org_id).filter(OrgMember.user_id == self.user_id).all()
	
	def get_pledges(self):
		return Pledge.query.filter_by(user_id=self.user_id).all()

	def get_pledged_opportunities(self):
		return Opportunity.query.join(Pledge, Pledge.opp_id == Opportunity.opp_id).filter(Pledge.user_id == self.user_id).all()

	def get_org_count_label(self):
		count = Org.query.join(OrgMember, OrgMember.org_id == Org.org_id).filter(OrgMember.user_id == self.user_id).count()
		return f"({count})" if count > 0 else ""

class Friends(db.Model):
	__tablename__ = 'friends'
	friend_a = db.Column(db.Integer, db.ForeignKey('user.user_id', name='fk_friends_friend_a_user_user_id'), primary_key=True)
	friend_b = db.Column(db.Integer, db.ForeignKey('user.user_id', name='fk_friends_friend_b_user_user_id'), primary_key=True)
	accepted = db.Column(db.Boolean, default=False)

	def __repr__(self):
		return f"<Friends {self.friend_a} - {self.friend_b}>"

class Org(db.Model):
	__tablename__ = 'org'
	org_id = db.Column(db.Integer, primary_key=True)
	org_name = db.Column(db.String(255), nullable=False)
	creator_id = db.Column(db.Integer, db.ForeignKey('user.user_id', name='fk_org_creator_id_user_user_id'))

	opportunitys = db.relationship('Opportunity', back_populates='org', lazy='dynamic')

	members = db.relationship('OrgMember', backref='org', lazy='dynamic')

	def __repr__(self):
		return f"<Org {self.org_id}>"

	def get_members(self):
		return User.query.join(OrgMember, OrgMember.user_id == User.user_id).filter(OrgMember.org_id == self.org_id).all()

	def get_member_count(self):
		return OrgMember.query.filter_by(org_id=self.org_id).count()

	def get_owner(self):
		return User.query.get(self.creator_id)

	def is_member_of(self, user):
		membership = OrgMember.query.filter_by(org_id=self.org_id, user_id=user.user_id).first()
		return membership is not None

	def add_member(self, user):
		if not self.is_member_of(user):
			new_member = OrgMember(org_id=self.org_id, user_id=user.user_id)
			db.session.add(new_member)
			db.session.commit()

	def get_opportunities(self):
		return Opportunity.query.filter_by(org_id=self.org_id).all()

	def get_opportunities_count(self):
		return Opportunity.query.filter_by(org_id=self.org_id).count()
	
	def get_opportunities_count_label(self):
		count = self.get_opportunities_count()
		return f"({count})" if count > 0 else ""

class OrgMember(db.Model):
	__tablename__ = 'org_member'
	org_id = db.Column(db.Integer, db.ForeignKey('org.org_id', name='fk_org_member_org_id_org_org_id'), primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', name='fk_org_member_user_id_user_user_id'), primary_key=True)

	def __repr__(self):
		return f"<OrgMember org={self.org_id} user={self.user_id}>"


class Opportunity(db.Model):
	__tablename__ = 'opportunity'
	opp_id = db.Column(db.Integer, primary_key=True)
	org_id = db.Column(db.Integer, db.ForeignKey('org.org_id', name='fk_opportunity_org_id_org_org_id'), nullable=False)
	title = db.Column(db.String(255), nullable=False)
	description = db.Column(db.Text, nullable=False)
	timestamp = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

	org = db.relationship('Org', back_populates='opportunitys')
	pledges = db.relationship('Pledge', back_populates='opportunity', lazy='dynamic')

	def __repr__(self):
		return f"<opportunity {self.opp_id} org={self.org_id}>"

	def get_org(self):
		return Org.query.get(self.org_id)

	def get_pledged_users(self):
		return User.query.join(Pledge, Pledge.user_id == User.user_id).filter(Pledge.opp_id == self.opp_id).all()
	
	def is_pledged_by(self, user):
		pledge = Pledge.query.filter_by(opp_id=self.opp_id, user_id=user.user_id).first()
		return pledge is not None

	def add_pledged_user(self, user):
		if not self.is_pledged_by(user):
			new_pledge = Pledge(opp_id=self.opp_id, user_id=user.user_id)
			db.session.add(new_pledge)
			db.session.commit()

	def small_description(self, length=100):
		if len(self.description) <= length:
			return self.description
		else:
			return self.description[:length-3] + "..."

class Scrape(db.Model):
	__tablename__ = 'scrape'
	scrape_id = db.Column(db.Integer, primary_key=True)
	#attributes from the scrape
	name = db.Column(db.String(255), nullable=True)
	link = db.Column(db.String(500), nullable=True)
	location = db.Column(db.String(100), nullable=True)

	description = db.Column(db.Text, nullable=True)

	pledges = db.relationship('Pledge', back_populates='scrape', lazy='dynamic')

	def __repr__(self):
		return f"<Scrape {self.scrape_id}>"

class Pledge(db.Model):
	__tablename__ = 'pledge'
	pledge_id = db.Column(db.Integer, primary_key=True)
	opp_id = db.Column(db.Integer, db.ForeignKey('opportunity.opp_id', name='fk_pledge_opp_id_opportunity_opp_id'), nullable=True)
	scrape_id = db.Column(db.Integer, db.ForeignKey('scrape.scrape_id', name='fk_pledge_scrape_id_scrape_scrape_id'), nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', name='fk_pledge_user_id_user_user_id'))
	type = db.Column(db.String(50), nullable=True)

	user = db.relationship('User', back_populates='pledges')
	opportunity = db.relationship('Opportunity', back_populates='pledges')
	scrape = db.relationship('Scrape', back_populates='pledges')

	def __repr__(self):
		return f"<Pledge {self.pledge_id} user={self.user_id}>"

	def get_opportunity(self):
		return Opportunity.query.get(self.opp_id)
	
	def get_user(self):
		return User.query.get(self.user_id)

