from flask import Blueprint, render_template, flash, redirect , url_for, request, abort
from flask_login import current_user , login_required
from blog_pro import db
from blog_pro.models import Post

post_bp = Blueprint("post",__name__,url_prefix="/post",template_folder='Templates')

def add_post(post:Post) :
    db.session.add(post)
    db.session.commit()
    return post


@post_bp.route("/delete/<int:post_id>", methods=["DELETE","GET","POST"]) 
def delete_post(post_id) :
    post = Post.query.get_or_404(post_id)
    if not (current_user.is_authenticated and post and post.user_id == current_user.id):
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Delete it successfuly!", category="success")
    if not current_user.posts :
        return '''<div class="post-card">
                    <p>No posts yet.</p>
                </div> '''
    return ""