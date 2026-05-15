from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_required
from blog_pro import db
from blog_pro.models import User, Post
from blog_pro.cloudinary_utils import upload_image, delete_image
from .forms import UpdateAccount

profile = Blueprint("profile",__name__,url_prefix="/profile",template_folder='templates',static_folder="static")

@profile.route("/")
@login_required
def my_profile():
    post_count = len(current_user.posts)
    image_file = current_user.image_file
    return render_template("my_profile.html", user=current_user, post_count=post_count, image_file=image_file)


@profile.route("/<string:username>")
def account(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    if user == current_user:
        return redirect(url_for("profile.my_profile"))
    post_count = len(user.posts)
    image_file = user.image_file
    return render_template("account.html", user=user, post_count=post_count, image_file=image_file)

@profile.route("/update", methods=["GET", "POST"])
@login_required
def update_profile():
    image_file = current_user.image_file
    form = UpdateAccount()
    if form.validate_on_submit():
        if form.file_field.data:
            # Delete the old Cloudinary image before uploading a new one
            delete_image(current_user.image_file)
            current_user.image_file = upload_image(
                form.file_field.data,
                folder="profiles"
            )
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("profile.update_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    for errors in form.errors.values():
        for error in errors:
            flash(error, category="Error")

    return render_template("update_profile.html", form=form, image_file=image_file)



@profile.route('/post_card/<int:post_id>')
def post_card(post_id) :
    post = Post.query.get_or_404(post_id)
    is_owner = post.author == current_user
    return render_template("_partials/post_card_profile.html",post=post, is_owner=is_owner)
    
@profile.route('/edit/<int:post_id>', methods=['GET'])
def get_edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    return render_template("_partials/edit_post_form_profile.html", post=post)


@profile.route('/edit/<int:post_id>', methods=['POST'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  
    post.title = request.form['title']
    post.content = request.form['content']
    db.session.commit()
    return render_template("_partials/post_card_profile.html", post=post, is_owner=True)

@profile.route('/cancel/<int:post_id>')
def cancel_edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("_partials/post_card_profile.html", post=post, is_owner=True)
