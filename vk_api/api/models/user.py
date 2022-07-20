from vk_api.api.models.base import db
from vk_api.api.models.group import Group

users_groups = db.Table('users_groups',
                        db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                        db.Column('group_id', db.Integer, db.ForeignKey('groups.id'))
                        )

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
                     )


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    groups = db.relationship(Group,
                             secondary=users_groups,
                             primaryjoin=(users_groups.c.user_id == id),
                             backref=db.backref('user_groups', lazy='dynamic'),
                             lazy='dynamic')
    user_follower = db.relationship('User',
                                    secondary=followers,
                                    primaryjoin=(followers.c.follower_id == id),
                                    secondaryjoin=(followers.c.followed_id == id),
                                    backref=db.backref('user_followed', lazy='dynamic'),
                                    lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

    def list_identify_follower(self):
        u = db.session.execute(self.user_follower).scalars().all()
        return [i.id for i in u]

    def group_follow(self, group):
        if not self.group_is_following(group):
            self.groups.append(group)
            return self

    def group_unfollow(self, group):
        if self.group_is_following(group):
            self.groups.remove(group)
            return self

    def user_follow(self, user):
        if not self.user_is_following(user):
            self.user_follower.append(user)
            return self

    def user_unfollow(self, user):
        if self.is_following(user):
            self.user_follower.remove(user)
            return self

    def user_is_following(self, user):
        return self.user_follower.filter(followers.c.followed_id == user.id).count() > 0

    def group_is_following(self, group):
        return self.groups.filter(users_groups.c.user_id == self.id).count() > 0
