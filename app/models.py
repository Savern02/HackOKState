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
	groups = db.relationship('Group', secondary='group_member', back_populates='members', lazy='dynamic')

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

	def friends(self):
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

class Friends(db.Model):
	__tablename__ = 'friends'
	friend_a = db.Column(db.BigInteger, db.ForeignKey('user.user_id', name='fk_friends_friend_a_user_user_id'), primary_key=True)
	friend_b = db.Column(db.BigInteger, db.ForeignKey('user.user_id', name='fk_friends_friend_b_user_user_id'), primary_key=True)
	accepted = db.Column(db.Boolean, default=False)

	def __repr__(self):
		return f"<Friends {self.friend_a} - {self.friend_b}>"


class Group(db.Model):
	__tablename__ = 'group'
	group_id = db.Column(db.BigInteger, primary_key=True)

	# members via association table `group_member`
	members = db.relationship('User', secondary='group_member', back_populates='groups', lazy='dynamic')

	def __repr__(self):
		return f"<Group {self.group_id}>"


class GroupMember(db.Model):
	__tablename__ = 'group_member'
	group_id = db.Column(db.BigInteger, db.ForeignKey('group.group_id', name='fk_group_member_group_id_group_group_id'), primary_key=True)
	user_id = db.Column(db.BigInteger, db.ForeignKey('user.user_id', name='fk_group_member_user_id_user_user_id'), primary_key=True)


class Org(db.Model):
	__tablename__ = 'org'
	org_id = db.Column(db.Integer, primary_key=True)
	org_name = db.Column(db.String(255), nullable=False)
	creator_id = db.Column(db.BigInteger, db.ForeignKey('user.user_id', name='fk_org_creator_id_user_user_id'))

	opportunitys = db.relationship('Opportunity', back_populates='org', lazy='dynamic')

	def __repr__(self):
		return f"<Org {self.org_id}>"


class Opportunity(db.Model):
	__tablename__ = 'opportunity'
	opp_id = db.Column(db.Integer, primary_key=True)
	org_id = db.Column(db.BigInteger, db.ForeignKey('org.org_id', name='fk_opportunity_org_id_org_org_id'), nullable=False)
	title = db.Column(db.String(255), nullable=True)
	description = db.Column(db.Text, nullable=True)

	org = db.relationship('Org', back_populates='opportunitys')
	pledges = db.relationship('Pledge', back_populates='opportunity', lazy='dynamic')

	def __repr__(self):
		return f"<opportunity {self.opp_id} org={self.org_id}>"


class Scrape(db.Model):
	__tablename__ = 'scrape'
	scrape_id = db.Column(db.BigInteger, primary_key=True)
	title = db.Column(db.String(255), nullable=True)
	description = db.Column(db.Text, nullable=True)

	pledges = db.relationship('Pledge', back_populates='scrape', lazy='dynamic')

	def __repr__(self):
		return f"<Scrape {self.scrape_id}>"


class Promotes(db.Model):
	__tablename__ = 'promotes'
	promotes_id = db.Column(db.BigInteger, primary_key=True)
	group_id = db.Column(db.BigInteger, db.ForeignKey('group.group_id', name='fk_promotes_group_id_group_group_id'))
	scrape_id = db.Column(db.BigInteger, db.ForeignKey('scrape.scrape_id', name='fk_promotes_scrape_id_scrape_scrape_id'), nullable=True)
	opp_id = db.Column(db.BigInteger, db.ForeignKey('opportunity.opp_id', name='fk_promotes_opp_id_opportunity_opp_id'), nullable=True)
	type = db.Column(db.String(50), nullable=True)

	def __repr__(self):
		return f"<Promotes {self.promotes_id} group={self.group_id}>"


class Pledge(db.Model):
	__tablename__ = 'pledge'
	pledge_id = db.Column(db.BigInteger, primary_key=True)
	opp_id = db.Column(db.BigInteger, db.ForeignKey('opportunity.opp_id', name='fk_pledge_opp_id_opportunity_opp_id'), nullable=True)
	scrape_id = db.Column(db.BigInteger, db.ForeignKey('scrape.scrape_id', name='fk_pledge_scrape_id_scrape_scrape_id'), nullable=True)
	user_id = db.Column(db.BigInteger, db.ForeignKey('user.user_id', name='fk_pledge_user_id_user_user_id'))
	type = db.Column(db.String(50), nullable=True)

	user = db.relationship('User', back_populates='pledges')
	opportunity = db.relationship('Opportunity', back_populates='pledges')
	scrape = db.relationship('Scrape', back_populates='pledges')

	def __repr__(self):
		return f"<Pledge {self.pledge_id} user={self.user_id}>"

