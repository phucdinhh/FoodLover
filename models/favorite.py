from .. import db
from .user import User


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    recipe_id = db.Column(db.Integer, nullable=False)
