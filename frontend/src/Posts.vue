<template>
  <section class="posts-section">
    <!-- Sorting Buttons -->
    <div id="sort-options" style="gap:15%;">
      <button class="sort-button" :class="{ active: sortOption === 'most-liked' }" @click="sortPosts('most-liked')">𝓖𝓮𝓷𝓮𝓻𝓪𝓵</button>
      <button class="sort-button" :class="{ active: sortOption === 'most-comments' }" @click="sortPosts('most-comments')">𝓣𝓻𝓮𝓷𝓭𝓲𝓷𝓰</button>
      <button class="sort-button" :class="{ active: sortOption === 'newest' }" @click="sortPosts('newest')">𝓝𝓮𝔀𝓮𝓼𝓽</button>
    </div>
    <!-- Posts Feed -->
    <div v-for="post in filteredPosts" :key="post._id" class="post-card hover-scale" :data-id="post._id">
      <div v-html="getPostHeaderHtml(post)"></div>
      <p class="post-message">{{ post.message || '' }}</p>
      <img
        v-if="post.photo"
        :src="post.photo"
        alt="Post Image"
        class="post-image"
        @click="openFullScreen(post.photo)"
      />
      <div class="post-timestamp">
        <small>{{ formatTimestamp(post.timestamp) }}</small>
      </div>
      <div class="actions">
        <button @click="likePost(post._id)" class="like-btn">
          <span>👍</span><span>{{ post.likes }}</span>
        </button>
        <button @click="dislikePost(post._id)" class="dislike-btn">
          <span>👎</span><span>{{ post.dislikes }}</span>
        </button>
        <button @click="toggleComments(post._id)" class="comment-btn">
          <span>💬</span><span>{{ post.comments.length }}</span>
        </button>
        <button class="view-btn">
          <span>💫</span><span>{{ post.views }}</span>
        </button>
        <button
          v-if="post.username === loggedInUsername || post.sessionId === sessionId"
          @click="editPost(post._id, post.username)"
        >
          Edit
        </button>
        <button
          v-if="post.username === loggedInUsername || post.sessionId === sessionId"
          @click="deletePost(post._id)"
        >
          Delete
        </button>
      </div>
      <transition name="fade">
        <div v-if="post.showComments" class="comments" :id="`comments-${post._id}`">
          <div class="comments-list">
            <div
              v-for="comment in post.comments"
              :key="comment.commentId"
              class="comment"
              v-html="getCommentHtml(post._id, comment)"
              @mouseenter="hoverComment"
              @mouseleave="leaveComment"
            ></div>
          </div>
          <div class="comment-input-container">
            <input
              :id="`commentInput-${post._id}`"
              v-model="post.commentInput"
              placeholder="Add a comment..."
              class="comment-input"
              @keyup.enter="addComment(post._id)"
            />
            <button @click="addComment(post._id)">Post</button>
          </div>
          <button @click="closeComments(post._id)" class="close-comments-btn">
            Close
          </button>
        </div>
      </transition>
    </div>
    <div id="loading" :style="{ display: loading ? 'flex' : 'none' }">
      Loading...
    </div>
  </section>
</template>

<script>
export default {
  props: ['searchQuery', 'loggedInUsername', 'sessionId'],
  data() {
    return {
      posts: [],
      currentPage: 1,
      loading: false,
      hasMorePosts: true,
      sortOption: 'most-liked',
      postText: '',
      imagePreview: null,
      lastSentPostId: null
    };
  },
  computed: {
    filteredPosts() {
      return this.posts.filter(post =>
        (post.message || '').toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }
  },
  methods: {
    getPostHeaderHtml(post) {
      return `
        <div class="post-header">
          <div class="profile-picture" onclick="showUserProfile('${post.username.replace(/'/g, "\\'")}', '${post.profilePicture || 'pfp2.jpg'}')">
            <img src="${post.profilePicture || 'pfp2.jpg'}" alt="${post.username.replace(/'/g, "\\'")}\'s profile picture" />
          </div>
          <div class="username">
            <strong>${post.username.replace(/'/g, "\\'")}</strong>
          </div>
        </div>
      `;
    },
    getCommentHtml(postId, comment) {
      const replies = Array.isArray(comment.replies) ? comment.replies : [];
      const timeAgo = this.getTimeAgo(new Date(comment.timestamp));
      const commentUsername = comment.username || 'Unknown';
      const commentProfilePicture = comment.profilePicture || 'https://latestnewsandaffairs.site/public/pfp3.jpg';
      let repliesHtml = replies.length > 0
        ? replies.map(reply => {
            const validReplyId = reply.replyId || '';
            return validReplyId ? `
              <div class="reply" id="reply-${validReplyId}">
                <div class="reply-profile">
                  <img src="${reply.profilePicture || 'https://latestnewsandaffairs.site/public/pfp3.jpg'}" alt="${(reply.username || 'Unknown').replace(/'/g, "\\'")}\'s profile" />
                </div>
                <div class="reply-content">
                  <div class="reply-header">
                    <span class="reply-username">${(reply.username || 'Unknown').replace(/'/g, "\\'")}</span>
                    <span class="reply-timestamp">${this.getTimeAgo(new Date(reply.timestamp))}</span>
                  </div>
                  <p class="reply-text">${(reply.reply || 'No reply').replace(/'/g, "\\'")}</p>
                </div>
                <button class="like-reply-btn" onclick="likeReply('${postId}', '${comment.commentId}', '${validReplyId}')">
                  ❤️ <span class="like-count">${reply.hearts || 0}</span>
                </button>
              </div>
            ` : '';
          }).join('')
        : '<p>No replies yet</p>';
      return `
        <div id="comment-${comment.commentId}" class="comment-inner">
          <div class="comment-profile">
            <img src="${commentProfilePicture}" alt="${commentUsername.replace(/'/g, "\\'")}\'s profile" />
          </div>
          <div class="comment-content">
            <div class="comment-header">
              <span class="comment-username">${commentUsername.replace(/'/g, "\\'")}</span>
              <span class="comment-timestamp">${timeAgo}</span>
            </div>
            <div class="comment-text">${(comment.comment || 'No comment').replace(/'/g, "\\'")}</div>
            <div class="comment-actions">
              <button class="like-comment-btn" onclick="likeComment('${postId}', '${comment.commentId}', '${commentUsername.replace(/'/g, "\\'")}')">
                ❤️ <span class="like-count">${comment.hearts || 0}</span>
              </button>
              <button class="reply-btn" onclick="toggleReplies('${postId}', '${comment.commentId}', '${commentUsername.replace(/'/g, "\\'")}')">
                💬 ${replies.length > 0 ? `(${replies.length})` : ''}
              </button>
              ${comment.username === this.loggedInUsername || this.sessionId === comment.sessionId ? `
                <button class="delete-comment-btn" onclick="deleteComment('${postId}', '${comment.commentId}')">
                  🗑️ Delete
                </button>
              ` : ''}
            </div>
            <div class="replies" style="display: ${comment.showReplies ? 'block' : 'none'};">
              ${repliesHtml}
            </div>
          </div>
        </div>
      `;
    },
    async fetchPosts(page = 1, sort = 'newest') {
      try {
        const response = await fetch(
          `https://sports321.vercel.app/api/posts?page=${page}&limit=16&sort=${sort}`
        );
        if (!response.ok) throw new Error('Failed to load posts');
        return await response.json();
      } catch (error) {
        console.error('Error fetching posts:', error);
        return { posts: [], hasMorePosts: false };
      }
    },
    showLoading() {
      this.loading = true;
    },
    hideLoading() {
      this.loading = false;
    },
    async loadMorePosts() {
      if (this.loading || !this.hasMorePosts) return;
      this.showLoading();
      const newPosts = await this.fetchPosts(this.currentPage, this.sortOption);
      if (newPosts && newPosts.posts.length > 0) {
        newPosts.posts.forEach(post => {
          post.showComments = false;
          post.commentInput = '';
          post.comments = post.comments || [];
          post.likes = post.likes || 0;
          post.dislikes = post.dislikes || 0;
          post.views = post.views || 0;
          post.comments.forEach(comment => {
            comment.showReplies = false;
            comment.replies = Array.isArray(comment.replies) ? comment.replies : [];
          });
          this.posts.push(post);
        });
        this.currentPage++;
        this.hasMorePosts = newPosts.hasMorePosts;
      } else {
        this.hasMorePosts = false;
      }
      this.hideLoading();
    },
    sortPosts(sortBy) {
      this.sortOption = sortBy;
      this.posts = [];
      this.currentPage = 1;
      this.hasMorePosts = true;
      this.loadMorePosts();
    },
    async postOpinion() {
      if (!this.sessionId || !this.loggedInUsername) {
        this.showNotification('Error: Session ID and Username are required', true);
        return;
      }
      const submitBtn = document.getElementById('submitBtn');
      const imageInput = document.getElementById('file-input');
      let imageData = null;
      if (imageInput.files.length > 0) {
        const file = imageInput.files[0];
        const reader = new FileReader();
        reader.onloadend = async () => {
          try {
            imageData = await this.blobToBase64(await this.resizeImageToMaxSize(reader.result, 65));
            await this.submitPost(this.postText.trim(), imageData);
          } catch (error) {
            this.showNotification('Error processing image.', true);
          }
        };
        reader.readAsDataURL(file);
      } else {
        await this.submitPost(this.postText.trim(), null);
      }
    },
    async submitPost(postText, imageData) {
      if (!postText && !imageData) {
        this.showNotification('Post content cannot be empty!', true);
        return;
      }
      const submitBtn = document.getElementById('submitBtn');
      submitBtn.classList.add('button-clicked');
      try {
        const postData = {
          message: postText,
          username: this.loggedInUsername,
          sessionId: this.sessionId,
          photo: imageData,
        };
        const response = await fetch('https://sports321.vercel.app/api/postOpinion', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
          body: JSON.stringify(postData),
          credentials: 'include',
        });
        if (!response.ok) {
          this.showNotification('Error: Failed to submit post', true);
          return;
        }
        const newPost = await response.json();
        this.lastSentPostId = newPost._id;
        newPost.showComments = false;
        newPost.commentInput = '';
        newPost.comments = newPost.comments || [];
        newPost.likes = newPost.likes || 0;
        newPost.dislikes = newPost.dislikes || 0;
        newPost.views = newPost.views || 0;
        newPost.comments.forEach(comment => {
          comment.showReplies = false;
          comment.replies = Array.isArray(comment.replies) ? comment.replies : [];
        });
        this.posts.unshift(newPost);
        this.showNotification('Post submitted successfully!', false);
        const pushNotificationResponse = await fetch(
          'https://2damnit.vercel.app/api/notifications',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'send-push-notification' }),
          }
        );
        if (!pushNotificationResponse.ok) {
          console.error('Error sending push notification.');
        }
      } catch (error) {
        this.showNotification('Error submitting post: ' + error.message, true);
      } finally {
        submitBtn.classList.remove('button-clicked');
        this.resetForm();
      }
    },
    resetForm() {
      this.postText = '';
      this.imagePreview = null;
      const imageInput = document.getElementById('file-input');
      if (imageInput) imageInput.value = '';
    },
    resizeImageToMaxSize(imageSrc, maxSizeKB = 65) {
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.src = imageSrc;
        img.onload = () => {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          const maxWidth = 200;
          const scale = maxWidth / img.width;
          canvas.width = img.width * scale;
          canvas.height = img.height * scale;
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          canvas.toBlob(
            blob => {
              if (blob.size / 1024 <= maxSizeKB) {
                resolve(blob);
              } else {
                reject('Image exceeds max size after resizing.');
              }
            },
            'image/webp',
            0.4
          );
        };
        img.onerror = () => reject('Error loading image.');
      });
    },
    blobToBase64(blob) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = e => {
          this.imagePreview = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },
    formatTimestamp(timestamp) {
      const date = new Date(timestamp);
      if (isNaN(date)) {
        console.error('Invalid timestamp', timestamp);
        return 'Invalid Date';
      }
      const options = { day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' };
      return date.toLocaleString('en-GB', options);
    },
    getTimeAgo(date) {
      const now = new Date();
      const diffInSeconds = Math.floor((now - date) / 1000);
      const years = Math.floor(diffInSeconds / (60 * 60 * 24 * 365));
      const days = Math.floor(diffInSeconds / (60 * 60 * 24));
      const hours = Math.floor(diffInSeconds / (60 * 60));
      const minutes = Math.floor(diffInSeconds / 60);
      if (years > 0) return `${years} year${years > 1 ? 's' : ''} ago`;
      if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
      if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
      if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
      return 'Just now';
    },
    toggleComments(postId) {
      const post = this.posts.find(p => p._id === postId);
      if (post) post.showComments = !post.showComments;
    },
    closeComments(postId) {
      const post = this.posts.find(p => p._id === postId);
      if (post) post.showComments = false;
    },
    addComment(postId) {
      const post = this.posts.find(p => p._id === postId);
      if (post && post.commentInput.trim()) {
        post.comments.push({
          commentId: `temp-${Date.now()}`,
          username: this.loggedInUsername,
          comment: post.commentInput,
          timestamp: new Date().toISOString(),
          hearts: 0,
          replies: [],
          showReplies: false,
        });
        post.commentInput = '';
      }
    },
    hoverComment(event) {
      event.currentTarget.style.backgroundColor = '#333';
      event.currentTarget.style.transform = 'scale(1.02)';
    },
    leaveComment(event) {
      event.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
      event.currentTarget.style.transform = 'scale(1)';
    },
    showNotification(message, isError) {
      console.log(`${isError ? 'Error' : 'Success'}: ${message}`);
    },
    likePost(postId) {
      const post = this.posts.find(p => p._id === postId);
      if (post) post.likes++;
    },
    dislikePost(postId) {
      const post = this.posts.find(p => p._id === postId);
      if (post) post.dislikes++;
    },
    editPost(postId, username) {
      console.log(`Editing post ${postId} by ${username}`);
    },
    deletePost(postId) {
      console.log(`Deleting post ${postId}`);
    },
    showUserProfile(username, profilePicture) {
      window.location.href = `search2.html?username=${encodeURIComponent(username)}`;
    },
    likeComment(postId, commentId, username) {
      console.log(`Liking comment ${commentId} on post ${postId} by ${username}`);
    },
    toggleReplies(postId, commentId, username) {
      const post = this.posts.find(p => p._id === postId);
      if (post) {
        const comment = post.comments.find(c => c.commentId === commentId);
        if (comment) comment.showReplies = !comment.showReplies;
      }
    },
    likeReply(postId, commentId, replyId) {
      console.log(`Liking reply ${replyId} on comment ${commentId} in post ${postId}`);
    },
    deleteComment(postId, commentId) {
      console.log(`Deleting comment ${commentId} on post ${postId}`);
    }
  },
  created() {
    this.loadMorePosts();
    const style = document.createElement('style');
    style.textContent = `
      .post-header { padding: 5px 10px; display: flex; align-items: center; }
      .profile-picture { cursor: pointer; }
      .profile-picture img { width: 30px; height: 30px; border-radius: 50%; }
      .username { font-size: 14px; margin-left: 5px; }
      .username strong { color: #fff; }
      .comment { margin-bottom: 6px; background-color: rgba(255, 255, 255, 0.1); color: #fff; font-size: 12px; border-radius: 0; transition: background-color 0.3s ease, transform 0.2s ease; }
      .comment:hover { background-color: #333; transform: scale(1.02); }
      .comment-inner { display: flex; background-color: #000; padding: 10px 15px; margin: 0; width: 100%; border-radius: 0; }
      .comment-profile { width: 40px; height: 40px; border-radius: 50%; overflow: hidden; margin-right: 12px; }
      .comment-profile img { width: 100%; height: 100%; object-fit: cover; }
      .comment-content { flex: 1; color: #fff; display: flex; flex-direction: column; }
      .comment-header { display: flex; justify-content: space-between; align-items: center; margin: 0; }
      .comment-username { font-weight: bold; font-size: 16px; margin: 0; }
      .comment-timestamp { font-size: 12px; color: #ccc; margin-left: auto; }
      .comment-text { font-size: 14px; color: #fff; margin-top: 5px; margin-left: 0; }
      .comment-actions { font-size: 12px; margin-top: 8px; display: flex; align-items: center; gap: 10px; }
      .like-comment-btn, .reply-btn, .delete-comment-btn { background: none; border: none; color: #fff; cursor: pointer; padding: 0; }
      .reply-btn { margin-left: 50px; font-size: 13px; }
      .delete-comment-btn { font-size: 12px; margin-left: 10px; }
      .replies { margin-top: 10px; }
      .reply { margin-left: 20px; display: flex; background-color: #222; padding: 10px 15px; border-radius: 8px; position: relative; }
      .reply-profile { width: 30px; height: 30px; border-radius: 50%; overflow: hidden; margin-right: 10px; }
      .reply-profile img { width: 100%; height: 100%; object-fit: cover; }
      .reply-content { flex: 1; color: #fff; font-size: 14px; }
      .reply-header { display: flex; justify-content: space-between; align-items: center; }
      .reply-username { font-weight: bold; }
      .reply-timestamp { font-size: 12px; color: #ccc; }
      .reply-text { margin-top: 5px; }
      .like-reply-btn { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; color: #fff; font-size: 12px; cursor: pointer; padding: 0; }
      .comments-section { padding: 0; background: #000; border-radius: 0; font-size: 14px; margin-bottom: 20px; }
      .comments-list { padding: 0; background-color: #000; font-size: 14px; margin: 0; width: 100%; height: auto; overflow-y: auto; }
      .comment-input-container { position: absolute; bottom: 20px; left: 0; width: 100%; padding: 10px 15px; display: flex; align-items: center; justify-content: center; gap: 10px; }
      .comment-input { width: 80%; padding: 10px 15px; border-radius: 25px; border: 1px solid #444; background-color: #333; color: #fff; font-size: 14px; transition: all 0.3s ease; box-sizing: border-box; outline: none; box-shadow: 0 0 5px rgba(0, 0, 0, 0.2); }
      .comment-input-container button { background-color: #007bff; color: white; padding: 8px 16px; border: none; border-radius: 25px; transition: background-color 0.3s ease; cursor: pointer; font-size: 14px; box-shadow: 0 0 5px rgba(0, 0, 0, 0.2); }
      .close-comments-btn { position: absolute; top: 10px; right: 10px; background-color: #ff4c4c; color: white; border: none; padding: 5px 10px; border-radius: 20px; cursor: pointer; }
    `;
    document.head.appendChild(style);
  },
  mounted() {
    window.addEventListener('scroll', this.handleScroll);
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.handleScroll);
  },
  handleScroll() {
    if (
      window.innerHeight + window.scrollY >= document.body.offsetHeight - 500 &&
      !this.loading &&
      this.hasMorePosts
    ) {
      this.loadMorePosts();
    }
  }
};
</script>