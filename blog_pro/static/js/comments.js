let commentPages = {}

function loadComments(postId){
    const container = document.getElementById(`comments-${postId}`);
    const btn = document.getElementById(`load-btn-${postId}`);
    if (!commentPages[postId]) {
        commentPages[postId] = 1;
    }

    if (commentPages[postId] == -1) {  // Already loaded
        if (container.classList.contains('hidden')) {
            container.classList.remove('hidden');
            setTimeout(() => {
                container.classList.remove('collapsed');
            }, 10);
            btn.innerText = "🔼 Show less";
        } else {
            container.classList.add('collapsed');
            setTimeout(() => {
                container.classList.add('hidden');
            }, 400);
            btn.innerText = "💬 Show Comments";
        }
    } else {
        const page = commentPages[postId];
        fetch(`get_comments_post/${postId}?page=${page}`)
            .then(res => res.json())
            .then(data => {
                if(data.status == '404'){return} // no comments
                data.comments.forEach(html => {
                    const div = document.createElement("div");
                    div.classList.add("comment-card"); // Apply initial state
                    div.innerHTML = html;

                    // Prepend first (invisible)
                    container.prepend(div);

                    // Trigger animation using requestAnimationFrame
                    requestAnimationFrame(() => {
                        div.classList.add("visible");
                    });
                });

                if (!data.has_next) {
                    btn.innerText = "🔼 Show less";
                    commentPages[postId] = -1
                    return
                }
                else{
                commentPages[postId] += 1;
                btn.innerText = "💬 More Comments";
                }
            });
    }
}

function editPost(postId){
    const container = document.getElementById(`post-${postId}`);
    const btn = document.getElementById(`post-${postId}-settings-btn`);
    fetch(`edit/${postId}`)
    .then(res => res.json())
    .then(data =>{
        container.outerHTML = data.html;

    })
}
function cancelEditPost(postId){
    const container = document.getElementById(`post-${postId}`);
    const btn = document.getElementById(`post-${postId}-settings-btn`);
    fetch(`cancel/${postId}`)
    .then(res => res.json())
    .then(data =>{
        container.outerHTML = data.html;
    })
}

function savaEditPost(event, postId) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    fetch(`/save_edit_post/${postId}`, {method: "POST",body: formData})
    .then(res => res.text()) // Get plain HTML
    .then(html => {
        document.getElementById(`post-${postId}`).outerHTML = html;
    })
    .catch(err => console.error("Error saving post:", err));
}


document.body.addEventListener('htmx:afterRequest', function(evt) {
    if (evt.target.classList.contains('post-form')) {
        evt.target.reset();  // يفرغ الحقول داخل الفورم
    }
    if (evt.target.classList.contains('add-comment')) {
        evt.target.reset();  // يفرغ الحقول داخل الفورم
    }
});

function postLike(postId) {
    const like_btn = document.getElementById(`like-btn-${postId}`);
    const like_count = document.getElementById(`like-count-${postId}`);
    let count = parseInt(like_count.textContent, 10);
    
    fetch(`/like_handler/${postId}`).then(response => {
        if(response.ok){
            
            if (like_btn.classList.contains('not-liked')) {
                like_btn.classList.remove('not-liked');
                like_btn.classList.add('liked');
                like_btn.innerText = "🖤";
                like_count.textContent = count + 1 ;
        
            } else {
                like_btn.classList.remove('liked');
                like_btn.classList.add('not-liked');
                like_count.textContent = count - 1 ;
                like_btn.innerText = "🤍";
                like_count.textContent = count -1 ;
            }
        }
    })
}

function commentLike(commentId) {
    const like_btn = document.getElementById(`comment-like-btn-${commentId}`);
    const like_count = document.getElementById(`comment-like-count-${commentId}`);
    let count = parseInt(like_count.textContent, 10);
    
    fetch(`/comment_like_handler/${commentId}`).then(response => {
        if(response.ok){
   
            if (like_btn.classList.contains('active')) {
                like_btn.classList.remove('active');
                like_count.textContent = count - 1 ;
        
            } else {
                like_btn.classList.add('active');
                like_count.textContent = count + 1 ;
            }
        }
    })
    
}


let currentPage = 1;
let loading = false;
function loadPosts() {
    if (loading) return;
    loading = true;

    // Show spinner
    document.getElementById("load-more").style.display = "block";
    document.getElementById("no-more").style.display = "none";

    fetch(`/get_posts?page=${currentPage}`)
        .then(response => response.json())
        .then(data => {
            data.posts.forEach(postHtml => {
                const tempDiv = document.createElement("div");
                tempDiv.innerHTML = postHtml.trim();
                // tempDiv.firstElementChild.classList.add("post");
                let id = parseInt(tempDiv.firstElementChild.id.split('-')[1]);
                document.getElementById("posts-container").appendChild(tempDiv.firstElementChild);
                loadComments(id); // load comment for frist time (number of commment will loaded from server)
                
                    
            });

            if (!data.has_next) {
                document.getElementById("load-more").style.display = "none";
                const noMore = document.getElementById("no-more");
                noMore.style.display = "block";
                noMore.style.animation = "popUp 0.5s ease forwards";
                window.removeEventListener('scroll', handleScroll);
            }else {
                document.getElementById("load-more").style.display = "none";
            }


            currentPage++;
            loading = false;
        })
        .catch(() => {
            loading = false;
            document.getElementById("load-more").style.display = "none";
            document.getElementById("no-more").innerHTML = "<p style='color:red;'>Error loading posts</p>";
            document.getElementById("no-more").style.display = "block";
        });
}
function handleScroll() {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight+50) {
        loadPosts();
    }
}
window.addEventListener('scroll', handleScroll);
// Load first page when page opens
loadPosts();


function submitNewComment(event, postId) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);


    fetch(`/submit_new_comment/${postId}`, {method: "POST",body: formData})
    .then(res => res.text()) // Get plain HTML
    .then(html => {
        document.getElementById(`new_comment-container-${postId}`).insertAdjacentHTML("afterbegin",html);
        form.reset();  // يفرغ الحقول داخل الفورم
    })
    .catch(err => console.error("Error saving post:", err));
}

