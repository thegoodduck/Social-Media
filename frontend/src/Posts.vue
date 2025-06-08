<template>
  <div>
    <div id="loading" v-show="loading" class="loading"><div class="spinner"></div></div>
    <div id="sort-options" style="gap:15%;">
      <button class="sort-button" :class="{ active: sortOption === 'most-liked' }" @click="sortPosts('most-liked')">General</button>
      <button class="sort-button" :class="{ active: sortOption === 'most-comments' }" @click="sortPosts('most-comments')">Trending</button>
      <button class="sort-button" :class="{ active: sortOption === 'newest' }" @click="sortPosts('newest')">Newest</button>
    </div>
    <div id="posts" class="posts-feed">
      <div v-for="post in posts" :key="post._id" class="post-card" :data-id="post._id" :data-liked-by="JSON.stringify(post.likedBy || [])" :data-disliked-by="JSON.stringify(post.dislikedBy || [])">
        <div class="post-header">
    <div class="profile-picture" @click="redirectToUserProfile(post.username)">
      <img :src="post.profilePicture || 'pfp2.jpg'" :alt="`${post.username}'s profile picture`" />
    </div>
    <div class="username" @click="redirectToUserProfile(post.username)">
      <strong>{{ post.username }}</strong>
    </div>
  </div>
        <p class="post-message" style="font-size: 13px; margin-top: 8px; font-family: 'Whitney', 'Helvetica Neue', Helvetica, Arial, sans-serif; cursor: pointer;" @click="openFullScreenPost(post._id)">{{ post.message || "" }}</p>
        <img v-if="post.photo" :src="post.photo" alt="Post Image" style="width: 100%; max-width:300px; max-height:280px; border-radius: 10px; margin-bottom: 10px; cursor: pointer;" @click="openFullScreenPost(post._id)" />
        <div class="post-timestamp"><small>{{ formatTimestamp(post.timestamp) }}</small></div>
        <div class="actions">
          <button class="like-btn" :class="{ liked: post.likedBy?.includes(loggedInUsername) }" @click="likePost(post._id)">👍 {{ post.likes || 0 }}</button>
          <button class="dislike-btn" :class="{ disliked: post.dislikedBy?.includes(loggedInUsername) }" @click="dislikePost(post._id)">👎 {{ post.dislikes || 0 }}</button>
          <button class="comment-btn" @click="openFullScreenPost(post._id)" style="color:#ff1100;">Comments ({{ post.comments?.length || 0 }})</button>
          <button class="view-btn">💫 ({{ post.views || 0 }})</button>
          <button v-if="post.username === loggedInUsername || post.sessionId === sessionId" @click="editPost(post._id, post.username)">Edit</button>
          <button v-if="post.username === loggedInUsername || post.sessionId === sessionId" @click="deletePost(post._id)">Delete</button>
        </div>
      </div>
    </div>
    <div v-if="selectedPost" class="full-screen-post-modal" @click.self="closeFullScreenPost">
      <div class="full-screen-post-content">
        <button class="close-full-screen-btn" @click="closeFullScreenPost" aria-label="Close full-screen post">✖</button>
        <div class="post-header">
          <div class="profile-picture" @click="showUserProfile(selectedPost.username, selectedPost.profilePicture)">
            <img :src="selectedPost.profilePicture || 'pfp2.jpg'" :alt="`${selectedPost.username}'s profile picture`" />
          </div>
          <div class="username"><strong>{{ selectedPost.username }}</strong></div>
        </div>
        <p class="post-message" style="font-size: 16px; margin-top: 10px; font-family: 'Whitney', 'Helvetica Neue', Helvetica, Arial, sans-serif;">{{ selectedPost.message || "" }}</p>
        <img v-if="selectedPost.photo" :src="selectedPost.photo" alt="Post Image" loading="lazy" style="width: 100%; max-height: 50vh; border-radius: 10px; margin-bottom: 10px;" />
        <div class="post-timestamp"><small>{{ formatTimestamp(selectedPost.timestamp) }}</small></div>
        <div class="actions" style="margin: 10px 0;">
          <button class="like-btn" :class="{ liked: selectedPost.likedBy?.includes(loggedInUsername) }" @click="likePost(selectedPost._id)">👍 {{ selectedPost.likes || 0 }}</button>
          <button class="dislike-btn" :class="{ disliked: selectedPost.dislikedBy?.includes(loggedInUsername) }" @click="dislikePost(selectedPost._id)">👎 {{ selectedPost.dislikes || 0 }}</button>
          <button class="comment-btn" style="color:#ff1100;">Comments ({{ selectedPost.comments?.length || 0 }})</button>
          <button class="view-btn">💫 ({{ selectedPost.views || 0 }})</button>
          <button v-if="selectedPost.username === loggedInUsername || selectedPost.sessionId === sessionId" @click="editPost(selectedPost._id, selectedPost.username)">Edit</button>
          <button v-if="selectedPost.username === loggedInUsername || selectedPost.sessionId === sessionId" @click="deletePost(selectedPost._id)">Delete</button>
        </div>
        <div class="comments-section" style="padding: 0; background-color: #000; font-size: 14px; margin: 0; width: 100%; box-sizing: border-box; overflow: hidden;">
          <div class="comments-list" style="background-color: #000; padding: 0; margin-top:5px; font-size: 14px; width: 100%; overflow-y: auto; max-height: 40vh;">
            <div v-for="comment in selectedPost.comments" :key="comment.commentId" class="comment" :id="`comment-${comment.commentId}`" style="margin: 0 0 15px 0; padding: 0; background-color: #000;">
              <div style="display: flex; background-color: #000; padding: 10px 15px; width: 100%;">
                <div style="width: 40px; height: 40px; border-radius: 50%; overflow: hidden; margin-right: 12px; flex-shrink: 0;">
                  <img :src="comment.profilePicture || 'https://latestnewsandaffairs.site/public/pfp3.jpg'" :alt="`${comment.username || 'Unknown'}'s profile`" style="width: 100%; height: 100%; object-fit: cover;" />
                </div>
                <div style="flex: 1; color:#ffffff; display: flex; flex-direction: column;">
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; font-size: 16px;">{{ comment.username || "Unknown" }}</span>
                    <span style="font-size: 12px; color: #ccc;">{{ getTimeAgo(new Date(comment.timestamp)) }}</span>
                  </div>
                  <div style="font-size: 14px; color: #fff; margin-top: 5px;">{{ comment.comment || "No comment" }}</div>
                  <div style="font-size: 12px; margin-top: 8px; display: flex; align-items: center; gap: 15px;">
                    <button class="like-comment-btn" :class="{ liked: comment.likedBy?.includes(loggedInUsername) }" @click="likeComment(selectedPost._id, comment.commentId, comment.username)">❤️ <span class="like-count">{{ comment.hearts || 0 }}</span></button>
                    <button class="reply-btn" @click="toggleReplies(selectedPost._id, comment.commentId, comment.username, $event.target)">💬 <span v-if="comment.replies?.length > 0">({{ comment.replies.length }})</span></button>
                    <button v-if="comment.username === loggedInUsername || comment.sessionId === sessionId" class="delete-comment-btn" @click="deleteComment(selectedPost._id, comment.commentId)">🗑️ Delete</button>
                  </div>
                </div>
              </div>
              <div v-for="reply in comment.replies" :key="reply.replyId" :id="`reply-${reply.replyId}`" class="reply" style="margin-bottom: 10px; display: flex; background-color: #000; padding: 10px 15px; border-radius: 8px; margin-left: 40px;">
                <div style="width: 30px; height: 30px; border-radius: 50%; overflow: hidden; margin-right: 10px;">
                  <img :src="reply.profilePicture || 'https://latestnewsandaffairs.site/public/pfp3.jpg'" :alt="`${reply.username || 'Unknown'}'s profile`" style="width: 100%; height: 100%; object-fit: cover;" />
                </div>
                <div style="flex: 1; color: #fff; font-size: 14px; display: flex; flex-direction: column;">
                  <div style="display: flex; justify-content: space-between;">
                    <span style="font-weight: bold;">{{ reply.username || 'Unknown' }}</span>
                    <span style="font-size: 12px; color: #ccc;">{{ getTimeAgo(new Date(reply.timestamp)) }}</span>
                  </div>
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 5px;">
                    <p style="margin: 0; flex: 1;">{{ reply.reply || 'No reply' }}</p>
                    <button class="like-reply-btn" :class="{ liked: reply.likedBy?.includes(loggedInUsername) }" @click="likeReply(selectedPost._id, comment.commentId, reply.replyId)" style="background-color: #000; border: none; color: #fff; cursor: pointer; font-size: 14px; align-self: flex-end;">❤️ <span class="like-count">{{ reply.hearts || 0 }}</span></button>
                  </div>
                </div>
              </div>
              <div v-if="!comment.replies || comment.replies.length === 0" class="no-replies" style="color: #ccc; font-size: 13px; padding: 10px 0;"><p>No replies yet</p></div>
              <div :id="`reply-box-${comment.commentId}`" class="reply-box"></div>
            </div>
          </div>
          <div class="comment-input-container" style="position: absolute; bottom: 20px; left: 0; width: 100%; padding: 5px 10px; display: flex; align-items: center; justify-content: center; gap: 10px;">
            <input :id="`commentInput-${selectedPost._id}`" type="text" placeholder="Add a comment..." class="comment-input" style="width: 80%; padding: 5px 10px; border-radius: 25px; border: 1px solid #444; background-color: #333; color: #fff; font-size: 14px; transition: all 0.3s ease; box-sizing: border-box; outline: none; box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);" @keyup.enter="addComment(selectedPost._id)" />
            <button @click="addComment(selectedPost._id)" style="background-color: #007bff; color: white; padding: 5px 10px; border: none; border-radius: 25px; transition: background-color 0.3s ease; cursor: pointer; font-size: 14px; box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);">Post</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showModal" class="modal">
      <div class="modal-content">
        <p>{{ modalMessage }}</p>
        <div class="modal-actions">
          <button class="modal-cancel" @click="closeModal">Cancel</button>
          <button class="modal-confirm" @click="modalAction">Yes, {{ modalActionText }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import usePosts from './Posts.js';
import { useRouter } from 'vue-router';

const router = useRouter();

// ✅ This just changes the route, no logic or fetching here
function redirectToUserProfile(username) {
  router.push({ name: 'UserProfile', params: { username } });
}

// Use general post state and actions only
const {
  posts,
  loading,
  sortOption,
  sortPosts,
  formatTimestamp,
  getTimeAgo,
  likePost,
  dislikePost,
  addComment,
  toggleReplies,
  likeComment,
  likeReply,
  editPost,
  deletePost,
  deleteComment,
  showModal,
  modalMessage,
  modalAction,
  modalActionText,
  closeModal,
  openFullScreen,
  openFullScreenPost,
  closeFullScreenPost,
  selectedPost,
  loggedInUsername,
  sessionId,
} = usePosts();
</script>


<style scoped>
.full-screen-post-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  z-index: 1000;
  overflow-y: auto;
}

.full-screen-post-content {
  background: #000;
  width: 90%;
  border-radius: 10px;
  padding: 20px;
  position: relative;
  overflow-y: auto;
}
.close-full-screen-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #222;
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease;
}

.close-full-screen-btn:hover {
  background: #444;
}

body{
   font-family: 'Whitney', 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
.post-header {
  display: flex;
  align-items: center;
  padding: 5px 10px;
}
.post-header .profile-picture img {
  width: 29px;
  height: 29px;
  border-radius: 50%;
  object-fit: cover;
}
.post-header .username {
  font-size: 14px;
   margin-left: 15px;
   margin-bottom: 5px;
}
.post-message {
  font-size: 14px;
  margin-top: 8px;
}
.post-card img {
  width: 100%;
  max-width: 300px;
  max-height: 280px;
  border-radius: 10px;
  margin-bottom: 10px;
  cursor: pointer;
}
.comment .like-comment-btn,
.comment .reply-btn,
.comment .delete-comment-btn {
  background: none;
  border: none;
  color: #ccc;
  cursor: pointer;
  font-size: 14px;
  padding: 4px 8px;
  transition: color 0.2s;
}
.comment button:hover {
  color: #fff;
}
  #sort-options {
       display: flex;
  justify-content: center; /* Center buttons */
        margin-bottom: 20px;
        padding-left: 8%; /* 8% gap at the start */
        padding-right: 8%; /* 8% gap at the end */
          max-width: 800px; 
    }
.sort-button {
  padding: 6px 18px;
  border: 2px solid #44444432; /* Subtle dark border */
  border-radius: 30px; /* Fully rounded pill shape */
  background-color: #1a1a1a; /* Dark gray button base */
  color: #00ffe0; /* Neon cyan text */
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

.sort-button:hover {
  background: linear-gradient(135deg, #00ffe0, #00bfff); /* Neon cyan to sky blue */
  color: #000; /* Contrast text */
  border-color: #00ffe0;
  box-shadow: 0 0 10px #00ffe0;
}

.sort-button.active {
  background: linear-gradient(135deg, #ff00cc, #3333ff); /* Magenta to neon blue */
  color: #fff;
  border-color: #ff00cc;
  box-shadow: 0 0 12px #ff00cc;
}

/* Modal Wrapper */
.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 11;
}
/* Modal Box */
.modal-content {
  background: #1a1a1a;
  padding: 20px;
  width: 280px;
  border-radius: 14px 10px 14px 10px;
  color: #e0fefc;
  text-align: center;
  box-shadow: 0 0 12px rgba(0, 255, 224, 0.2);
  border: 1px solid #2e2e2e;
}
/* Button Container */
.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}
/* Shared Button Styles */
.modal-actions button {
  flex: 1;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 12px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: 0.3s ease all;
}
/* Cancel (Red) */
.modal-actions .modal-cancel {
  color: #ff4d4f;
  background: #121212;
  border-color: #ff4d4f;
}
.modal-actions .modal-cancel:hover {
  background: #aa0000;
  color: #fff;
  box-shadow: 0 0 6px rgba(255, 77, 79, 0.4);
}
/* Confirm (Neon Cyan) */
.modal-actions .modal-confirm {
  color: #00ffe0;
  background: #121212;
  border-color: #00ffe0;
}
.modal-actions .modal-confirm:hover {
  background: linear-gradient(135deg, #00ffe0, #00bfff);
  color: #000;
  box-shadow: 0 0 6px rgba(0, 255, 224, 0.4);
}
</style>



