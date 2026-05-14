class PostImageManager {
    constructor(){
        this.imageCache = {};
    }
    async loadImage(postId, direction) {
        const imgElm = document.getElementById(`active-img-${postId}`); 
        const newIndex = parseInt(imgElm.dataset.index) + direction;
        const caption = document.getElementById(`img-caption-${postId}`);
        const cacheKey = `${postId}-${newIndex}`;
        this.showSkeleton(imgElm);
        if(this.imageCache[cacheKey]){ 
            this.updateImage(imgElm, caption, this.imageCache[cacheKey], newIndex, postId);
            return;
        }
        const newImg = await this.fetchImageFromServer(postId,newIndex);
        if (newImg) {
            this.updateImage(imgElm, caption, newImg, newIndex);
        }else {
            console.log("No more images for this post.");
            this.hideSkeleton(imgElm);
        }
    
    }
    // ===============================
    // 🔹 Update UI with new image
    // ===============================
    updateImage(imgElem, caption, src, index){
        imgElem.src = src;
        console.log(imgElem)
        imgElem.dataset.index = index;
        caption.textContent = `Image ${index + 1}`;
        this.hideSkeleton(imgElem);
    }

    async fetchImageFromServer(postId, index) {
        const res = await fetch(`/get_post_image/${postId}/${index}`);
        if (!res.ok) return null;
        const data = await res.json();
        const imgRes = await fetch(data.url);
        const blob = await imgRes.blob();
        const objectURL = URL.createObjectURL(blob);
        console.log(objectURL);
        const cacheKey = `${postId}-${index}`;
        this.imageCache[cacheKey] = objectURL;
        return objectURL;

    }

    // ===============================
    // 🔹 Skeleton Loading Effect
    // ===============================
    showSkeleton(imgElem) {
        imgElem.classList.add("skeleton");
    }

    hideSkeleton(imgElem) {
        setTimeout(() => {
            imgElem.classList.remove("skeleton");
        },3000, this.skeletonDuration);
    }


}

const postImageManager = new PostImageManager();

document.addEventListener("click",(e)=>{
    if((e.target.classList.contains("nav-arrow"))){
        const postId = e.target.dataset.postId;
        const direction = e.target.classList.contains("next")? 1 : -1;
        postImageManager.loadImage(postId,direction);
    }
});