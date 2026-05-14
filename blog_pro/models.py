from datetime import datetime
from blog_pro import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id) :
    return User.query.get(int(user_id))

post_likes = db.Table('post_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
    )
comment_likes = db.Table("comment_likes",
    db.Column("user_id",db.Integer,db.ForeignKey('user.id'), primary_key=True),
    db.Column("comment_id",db.Integer,db.ForeignKey('comment.id'), primary_key=True)
    )

class User(db.Model,UserMixin) :
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(60) ,unique=True ,nullable=False)
    password = db.Column(db.String(120), nullable=False)
    image_file = db.Column(db.String(500), nullable=False, default='default.JPG')
    posts = db.relationship("Post",backref="author",lazy=True, cascade="all, delete-orphan")
    comments = db.relationship("Comment",backref="author",lazy=True, cascade="all, delete-orphan")
  
    liked_posts = db.relationship('Post', secondary='post_likes', backref='likes', lazy='dynamic')
    liked_comment = db.relationship('Comment',secondary='comment_likes', backref='likes', lazy="dynamic")


    def __repr__(self):
        return f'User {self.id} , {self.username} , {self.email} , {self.image_file}'
    
class Post(db.Model) :
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_post = db.Column(db.DateTime,nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    comments = db.relationship("Comment",backref="post",lazy=True, cascade="all, delete-orphan")
    images = db.relationship("ImagePost",backref="post",lazy=True, cascade="all, delete-orphan")


    def __repr__(self):
        return f"Post id: {self.id}, title: {self.title}, date: {self.date_post}"

class ImagePost(db.Model) : 
    id = db.Column(db.Integer,primary_key=True)
    file_name = db.Column(db.String(500), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)

    

class Comment(db.Model) :
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_comment = db.Column(db.DateTime,nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


    def __repr__(self):
        return f"comment id: {self.id}, post_id: {self.post_id}, date: {self.date_comment}"
    


class Notification(db.Model) :
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), default="info")
    link=db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime,nullable=False, default=datetime.utcnow)
    is_global = db.Column(db.Boolean, default=False)
