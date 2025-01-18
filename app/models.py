from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

followers = sa.Table(
    'followers', db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True),
    sa.Column('followed_id',sa.Integer, sa.ForeignKey('user_id'), primary_key=True)
)

class User(UserMixin,db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)

    email: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)

    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.MappedColumn[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    posts: so.WriteOnlyMapped['Post']= so.relationship(back_populates='author')

    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
    secondaryjoin=(followers.c.followe_id == id),
    back_populates='followers'    
    )
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following'
    )

    def __repr__(self):
        return (f'User: {self.username}')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
class Post(db.Model):
    id: so.Mapped[int]= so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(200))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return (f'Post: {self.body}')