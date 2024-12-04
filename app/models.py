from app import db

# * Models
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(255), unique=True, nullable=False)
    college = db.Column(db.String(255), nullable=False)
    level = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.chat_id}>"