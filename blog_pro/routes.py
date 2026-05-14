from flask import Blueprint, jsonify, render_template, flash, redirect, url_for, request, abort, current_app
from flask_login import current_user, login_required
from blog_pro import db
from blog_pro.models import User, Post, Comment, Notification, ImagePost
from blog_pro.post.routes import add_post
from blog_pro.cloudinary_utils import upload_image
import datetime


def allowed_file(filename):
    """Check if a filename has an allowed image extension."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'jpg', 'jpeg', 'png', 'gif', 'webp'})



main_bp = Blueprint('main', __name__)

def get_post_date_delta(post_date):
    delta_date_days = (datetime.datetime.now() - post_date).days
    if delta_date_days == 0:
        days_ago = 'Today'
    elif delta_date_days == 1:
        days_ago = "Yesterday"
    else:
        days_ago = str(delta_date_days) + "d ago"
    delta_post_date = f"{days_ago} - {post_date.strftime('%H:%M')}"
    return delta_post_date


@main_bp.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", user=current_user, Post=Post)


@main_bp.route('/post_card/<int:post_id>')
def post_card(post_id):
    post = Post.query.get_or_404(post_id)
    delta_post_date = get_post_date_delta(post.date_post)
    is_owner = post.author == current_user
    return render_template("_partials/post_card_index.html", post=post, is_owner=is_owner, delta_post_date=delta_post_date, current_user=current_user)


@main_bp.route("/get_posts")
def get_post() :
    page = request.args.get("page",type=int,default=1)
    per_page = 3
    pagination = Post.query.order_by(Post.date_post.desc())\
    .paginate(page=page,per_page=per_page,error_out=False)
    
    posts = pagination.items
    rendered_post = [
        render_template("_partials/post_card_index.html", post=p, is_owner=(p.author == current_user), delta_post_date=get_post_date_delta(p.date_post), current_user=current_user)
          for p in posts
    ]
    return jsonify({
        "posts" : rendered_post,
        "has_next" : pagination.has_next
    })

@main_bp.route("/get_post_image/<int:post_id>/<int:index>")
def get_post_image(post_id, index):
    images = Post.query.get_or_404(post_id).images
    if index >= len(images) or index < 0:
        return {"error": "no image out of index"}, 404
    # file_name now stores the full Cloudinary secure_url
    return jsonify({"url": images[index].file_name})
    


def save_post_image(form_image, user_id: int) -> str:
    """Compress and upload a post image to Cloudinary under post-img/."""
    return upload_image(form_image, folder="post-img")

@main_bp.route('/submit_new_post',methods=["GET", "POST"])
@login_required
def submit_new_post():
    title = request.form.get("title_field")
    content = request.form.get("post_field")
    images = request.files.getlist("images-field")

    if not (title and (content or images)):
        return ""
    
    post = Post(title=title, content=content, user_id=current_user.id)
    add_post(post)

    if images:
        for image in images:
            # Skip empty file inputs and files with disallowed extensions
            if not image.filename or not allowed_file(image.filename):
                continue
            image_fn = save_post_image(image, current_user.id)
            img = ImagePost(file_name=image_fn, post_id=post.id)
            db.session.add(img)
        db.session.commit()
        
        
    notify_new_post(post.id)
    return post_card(post.id)


@main_bp.route('/edit/<int:post_id>', methods=['GET'])
def get_edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    delta_post_date = get_post_date_delta(post.date_post)
    return jsonify({
        "html" : render_template("_partials/edit_post_form.html", post=post, delta_post_date=delta_post_date)
    })

@main_bp.route('/save_edit_post/<int:post_id>',methods=["POST"])
def sava_edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    post.title = request.form['title']
    post.content = request.form['content']
    db.session.commit()
    return post_card(post_id)


@main_bp.route('/cancel/<int:post_id>')
def cancel_edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify({
        "html" : post_card(post.id)
    })

@main_bp.route("/like_handler/<int:post_id>")
def like_handler(post_id):
    if not current_user.is_authenticated:
        abort(500)
    post: Post = Post.query.get_or_404(post_id)
    if current_user not in post.likes:
        post.likes.append(current_user)
        notify_new_like(post_id)
    elif current_user in post.likes:
        post.likes.remove(current_user)
    else:
        abort(500)
    db.session.commit()
    return ""


@main_bp.route("/get_comment/<int:comment_id>")
def get_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    delta_comment_date = get_post_date_delta(comment.date_comment)
    return render_template("_partials/comment_card_index.html", comment=comment, delta_comment_date=delta_comment_date)


@main_bp.route('/submit_new_comment/<int:post_id>',methods=["POST"])
@login_required
def submit_new_comment(post_id):
    content = request.form['comment-field']
    user_id = current_user.id
    if not content:
        return ""
    comment = Comment(content=content, user_id=user_id, post_id=post_id)
    db.session.add(comment)
    db.session.commit()
    notify_new_comment(post_id,comment=content)
    
    return "<div class='comment-card visible'>" + get_comment(comment.id) + "</div>"

@main_bp.route("/get_comments_post/<int:post_id>")
def get_comments(post_id) :
    page = request.args.get("page",type=int)
    if page == 1 : # default comment when load for first time 
        per_page = 2
    else :
        per_page = 3
        
    comments = Comment.query.filter_by(post_id=post_id)\
        .order_by(Comment.date_comment.desc())
    
    if not comments.count() : # No comments
        return jsonify({
        'status' : '404'
        })
    
    pagination = comments.paginate(page=page,per_page=per_page,error_out=False)
    comments= pagination.items
    rendered_comments = [
        render_template("_partials/comment_card_index.html", comment=c, delta_comment_date=get_post_date_delta(c.date_comment))
        for c in comments
    ]
    return jsonify({
        'status' : 'success',
        "comments" : rendered_comments,
        "has_next" : pagination.has_next
    })

@main_bp.route("/comment_like_handler/<int:comment_id>")
def comment_like_handler(comment_id):
    if not current_user.is_authenticated:
        abort(500)
    comment: Comment = Comment.query.get_or_404(comment_id)
    if current_user not in comment.likes:
        comment.likes.append(current_user)
    elif current_user in comment.likes:
        comment.likes.remove(current_user)
    else:
        abort(500)
    db.session.commit()
    return ""


@main_bp.route('/post/<int:post_id>/likes')
def view_likes(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('_partials/likes_list.html', post=post)


#-----------------Notifications-----------------------------------------------------------------
def notify_new_comment(post_id, comment:str) :
    post = Post.query.get_or_404(post_id)
    comment = comment[:12] + " ..."
    msg = f"{current_user.username} : comment in your post: {post.title} => {comment}"
    notif = Notification(user_id=post.user_id, message=msg, type="comment", link=url_for('main.post_card',post_id=post_id))
    db.session.add(notif)
    db.session.commit()

def notify_new_like(post_id) :
    post = Post.query.get_or_404(post_id)
    msg = f"New like ♥ from {current_user.username} in your post"
    notif = Notification(user_id=post.user_id, message=msg, type="like", link=url_for('main.post_card',post_id=post_id))
    db.session.add(notif)
    db.session.commit()

def notify_new_post(post_id) :
    post = Post.query.get_or_404(post_id)
    msg = f"New post from 👤 {current_user.username} ✍ {post.title}"
    notif = Notification(is_global=True, message=msg, type="newpost", link=url_for('main.post_card',post_id=post_id))
    db.session.add(notif)
    db.session.commit()

@main_bp.route('/notify_all_users/<string:message>')
def notify_all_users(message:str, notif_type="system", link="#"):
    notif = Notification(user_id=None, message=message, type=notif_type, link=link, is_global=True)
    db.session.add(notif)
    db.session.commit()

# 🔹 جلب آخر ID عند تحميل الصفحة
@main_bp.route("/get_latest_notification_id")
def get_latest_notification_id():
    last = Notification.query.filter((Notification.user_id==current_user.id) | (Notification.is_global==True)).order_by(Notification.id.desc()).first()
    return jsonify({"last_id": last.id if last else 0})


# 🔹 جلب الإشعارات الجديدة فقط
@main_bp.route("/get_notifications")
def get_notifications():
    since_id = request.args.get("since", 0, type=int)
    new_notifs = Notification.query.filter((Notification.user_id==current_user.id) | (Notification.is_global==True)).filter(Notification.id > since_id).order_by(Notification.id.asc()).all()

    return jsonify({
        "new_notifications": [
            {
                "id": n.id,
                "type": n.type,
                "message": n.message,
                "time": n.created_at.strftime("%H:%M"),
                "link": n.link or "#"
            }
            for n in new_notifs
        ]
    })

# 🔹 عرض كل الإشعارات (للواجهة)
@main_bp.route("/all_notifications")
def all_notifications():
    notifs = Notification.query.filter(
    (Notification.user_id==current_user.id) | (Notification.is_global==True)
).order_by(Notification.created_at.desc()).limit(50).all()
    data = [
        {
            "id": n.id,
            "type": n.type,
            "message": n.message,
            "time": n.created_at.isoformat(),
            "link": n.link or "#"
        } for n in notifs
    ]
    return jsonify(data)


# 🔹 مسح جميع الإشعارات (اختياري)
@main_bp.route("/clear_notifications", methods=["POST"])
def clear_notifications():
    Notification.query.filter(Notification.user_id==current_user.id).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({"status": "cleared"})

# ------------------------------------------------------------
