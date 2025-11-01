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


class Friends(db.Model):
	__tablename__ = 'friends'
	friend_a = db.Column(db.BigInteger, db.ForeignKey('user.user_id', name='fk_friends_friend_a_user_user_id'), primary_key=True)
	friend_b = db.Column(db.BigInteger, db.ForeignKey('user.user_id', name='fk_friends_friend_b_user_user_id'), primary_key=True)

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

	opportunitys = db.relationship('opportunity', back_populates='org', lazy='dynamic')

	def __repr__(self):
		return f"<Org {self.org_id}>"


class Opportunity(db.Model):
	__tablename__ = 'opportunity'
	opportunity_id = db.Column(db.BigInteger, primary_key=True)
	org_id = db.Column(db.BigInteger, db.ForeignKey('org.org_id', name='fk_opportunity_org_id_org_org_id'))
	title = db.Column(db.String(255), nullable=True)
	description = db.Column(db.Text, nullable=True)

	org = db.relationship('Org', back_populates='opportunitys')
	pledges = db.relationship('Pledge', back_populates='opportunity', lazy='dynamic')

	def __repr__(self):
		return f"<opportunity {self.opportunity_id} org={self.org_id}>"


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
	opportunity_id = db.Column(db.BigInteger, db.ForeignKey('opportunity.opportunity_id', name='fk_promotes_opportunity_id_opportunity_opportunity_id'), nullable=True)
	type = db.Column(db.String(50), nullable=True)

	def __repr__(self):
		return f"<Promotes {self.promotes_id} group={self.group_id}>"


class Pledge(db.Model):
	__tablename__ = 'pledge'
	pledge_id = db.Column(db.BigInteger, primary_key=True)
	opportunity_id = db.Column(db.BigInteger, db.ForeignKey('opportunity.opportunity_id', name='fk_pledge_opportunity_id_opportunity_opportunity_id'), nullable=True)
	scrape_id = db.Column(db.BigInteger, db.ForeignKey('scrape.scrape_id', name='fk_pledge_scrape_id_scrape_scrape_id'), nullable=True)
	user_id = db.Column(db.BigInteger, db.ForeignKey('user.user_id', name='fk_pledge_user_id_user_user_id'))
	type = db.Column(db.String(50), nullable=True)

	user = db.relationship('User', back_populates='pledges')
	opportunity = db.relationship('opportunity', back_populates='pledges')
	scrape = db.relationship('Scrape', back_populates='pledges')

	def __repr__(self):
		return f"<Pledge {self.pledge_id} user={self.user_id}>"

