
<template>
  <div>
    <!-- Loading Spinner -->
    <div id="loading" v-show="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <!-- Search Input -->
    <div v-if="!userProfile" class="search-container" style="margin: 20px 0; display: flex; justify-content: center; gap: 10px;">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search for a user..."
        class="search-input"
     style="width: 70%; max-width: 400px; padding: 6px 12px; border-radius: 25px; border: 1px solid #444; background-color: #333; color: #fff; font-size: 13px; outline: none; box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);"

        @keyup.enter="searchUser"
        aria-label="Search for a user by username"
      />
      <button
        @click="searchUser"
        style="background-color: #007bff; color: white; padding: 5px 10px; border: none; border-radius: 15px; cursor: pointer; font-size: 14px; transition: background-color 0.3s ease; box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);"
      >
        Search
      </button>
    </div>

    <!-- User Profile -->
    <div v-if="userProfile" class="user-profile" style="text-align: center; margin: 20px 0;">
      <button
        @click="resetSearch"
        style="background-color: #007bff; color: white; padding: 8px 16px; border: none; border-radius: 25px; cursor: pointer; margin-bottom: 10px;"
      >
        Back to Search
      </button>
      <div class="profile-picture" style="width: 80px; height: 80px; border-radius: 50%; overflow: hidden; margin: 0 auto;">
        <img :src="userProfile.profilePicture || 'pfp2.jpg'" :alt="`${userProfile.username}'s profile picture`" style="width: 100%; height: 100%; object-fit: cover;" />
      </div>
      <h2 style="font-size: 24px; margin: 10px 0; color: #fff;">{{ userProfile.username }}</h2>
      <p v-if="userProfile.description" style="font-size: 14px; color: #ccc; margin: 0;">{{ userProfile.description }}</p>
      <p v-if="userProfile.location" style="font-size: 14px; color: #ccc; margin: 0;">Location: {{ userProfile.location }}</p>
      <p v-if="userProfile.status" style="font-size: 14px; color: #ccc; margin: 0;">Status: {{ userProfile.status }}</p>
      <p v-if="userProfile.profession" style="font-size: 14px; color: #ccc; margin: 0;">Profession: {{ userProfile.profession }}</p>
      <p v-if="userProfile.hobby" style="font-size: 14px; color: #ccc; margin: 0;">Hobby: {{ userProfile.hobby }}</p>
    </div>

    <!-- No User Found -->
    <div v-if="searched && !userProfile" class="no-user" style="text-align: center; color: #ccc; margin: 20px 0;">
      <p>User not found.</p>
      <button @click="$router.push('/')" style="background-color: #007bff; color: white; padding: 8px 16px; border: none; border-radius: 25px; cursor: pointer;">
        Back to Feed
      </button>
    </div>

    <!-- User Posts -->
    <div v-if="userProfile && posts.length" class="posts-container">
      <div v-for="post in posts" :key="post._id" class="post-card" :data-id="post._id">
        <div class="post-header">
          <img :src="post.profilePicture || 'pfp2.jpg'" alt="Profile picture" class="post-profile-pic" />
          <div>
            <span class="post-username" @click="showUserProfile(post.username)">{{ post.username }}</span>
            <span class="post-timestamp">{{ formatTimestamp(post.timestamp) }}</span>
          </div>
        </div>
        <p class="post-message">{{ post.message }}</p>
        <img v-if="post.photo" :src="post.photo" alt="Post image" class="post-image" @click="openFullScreen(post.photo)" />
        <div class="post-actions">
          <button @click="likePost(post._id)">Like ({{ post.likes }})</button>
          <button @click="dislikePost(post._id)">Dislike ({{ post.dislikes }})</button>
          <button @click="openFullScreenPost(post._id)">Comment ({{ post.comments.length }})</button>
          <button v-if="post.username === loggedInUsername" @click="editPost(post._id, post.username)">Edit</button>
          <button v-if="post.username === loggedInUsername" @click="deletePost(post._id)">Delete</button>
        </div>
        <!-- Comments Section -->
        <div v-if="post.comments.length" class="comments-section">
          <div v-for="comment in post.comments" :key="comment.commentId" class="comment">
            <div class="comment-header">
              <img :src="comment.profilePicture || 'pfp2.jpg'" alt="Commenter picture" class="comment-profile-pic" />
              <span class="comment-username">{{ comment.username }}</span>
              <span class="comment-timestamp">{{ formatTimestamp(comment.timestamp) }}</span>
            </div>
            <p>{{ comment.comment }}</p>
            <div class="comment-actions">
              <button @click="likeComment(post._id, comment.commentId, comment.username)">Heart ({{ comment.hearts }})</button>
              <button @click="toggleReplies(post._id, comment.commentId, comment.username)">Reply ({{ comment.replies.length }})</button>
              <button v-if="comment.username === loggedInUsername" @click="deleteComment(post._id, comment.commentId)">Delete</button>
            </div>
            <div v-if="comment.showReplies" class="replies" :id="`replies-${comment.commentId}`">
              <div v-for="reply in comment.replies" :key="reply.replyId" class="reply">
                <div class="reply-header">
                  <img :src="reply.profilePicture || 'pfp2.jpg'" alt="Reply picture" class="reply-profile-pic" />
                  <span class="reply-username">{{ reply.username }}</span>
                  <span class="reply-timestamp">{{ formatTimestamp(reply.timestamp) }}</span>
                </div>
                <p>{{ reply.reply }}</p>
                <button @click="likeReply(post._id, comment.commentId, reply.replyId)">Heart ({{ reply.hearts }})</button>
              </div>
            </div>
          </div>
        </div>
        <div class="comment-input">
          <input :id="`commentInput-${post._id}`" type="text" placeholder="Add a comment..." />
          <button @click="addComment(post._id)">Post</button>
        </div>
      </div>
    </div>

    <!-- Full-Screen Post Modal -->
    <div v-if="selectedPost" class="fullscreen-post">
      <div class="fullscreen-content">
        <button @click="closeFullScreenPost" class="close-button">Close</button>
        <div class="post-header">
          <img :src="selectedPost.profilePicture || 'pfp2.jpg'" alt="Profile picture" class="post-profile-pic" />
          <div>
            <span class="post-username" @click="showUserProfile(selectedPost.username)">{{ selectedPost.username }}</span>
            <span class="post-timestamp">{{ formatTimestamp(selectedPost.timestamp) }}</span>
          </div>
        </div>
        <p class="post-message">{{ selectedPost.message }}</p>
        <img v-if="selectedPost.photo" :src="selectedPost.photo" alt="Post image" class="post-image" />
        <div class="post-actions">
          <button @click="likePost(selectedPost._id)">Like ({{ selectedPost.likes }})</button>
          <button @click="dislikePost(selectedPost._id)">Dislike ({{ selectedPost.dislikes }})</button>
        </div>
        <div class="comments-section">
          <div v-for="comment in selectedPost.comments" :key="comment.commentId" class="comment">
            <div class="comment-header">
              <img :src="comment.profilePicture || 'pfp2.jpg'" alt="Commenter picture" class="comment-profile-pic" />
              <span class="comment-username">{{ comment.username }}</span>
              <span class="comment-timestamp">{{ formatTimestamp(comment.timestamp) }}</span>
            </div>
            <p>{{ comment.comment }}</p>
            <div class="comment-actions">
              <button @click="likeComment(selectedPost._id, comment.commentId, comment.username)">Heart ({{ comment.hearts }})</button>
              <button @click="toggleReplies(selectedPost._id, comment.commentId, comment.username)">Reply ({{ comment.replies.length }})</button>
            </div>
            <div v-if="comment.showReplies" class="replies" :id="`replies-${comment.commentId}`">
              <div v-for="reply in comment.replies" :key="reply.replyId" class="reply">
                <div class="reply-header">
                  <img :src="reply.profilePicture || 'pfp2.jpg'" alt="Reply picture" class="reply-profile-pic" />
                  <span class="reply-username">{{ reply.username }}</span>
                  <span class="reply-timestamp">{{ formatTimestamp(reply.timestamp) }}</span>
                </div>
                <p>{{ reply.reply }}</p>
                <button @click="likeReply(selectedPost._id, comment.commentId, reply.replyId)">Heart ({{ reply.hearts }})</button>
              </div>
            </div>
          </div>
        </div>
        <div class="comment-input">
          <input :id="`commentInput-${selectedPost._id}`" type="text" placeholder="Add a comment..." />
          <button @click="addComment(selectedPost._id)">Post</button>
        </div>
      </div>
    </div>

    <!-- Modal for Edit/Delete Confirmation -->
    <div v-if="showModal" class="modal">
      <div class="modal-content">
        <p>{{ modalMessage }}</p>
        <button @click="modalAction">{{ modalActionText }}</button>
        <button @click="closeModal">Cancel</button>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue';
import { debounce } from 'lodash';
import { useRoute, useRouter } from 'vue-router';
import usePosts from './Posts.js';

const router = useRouter();
const route = useRoute();

const username = ref(route.params.username ?? '');
const searchQuery = ref(route.params.username ?? '');
const userProfile = ref(null);
const searched = ref(false);

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
} = usePosts();

const fetchUserData = async (usernameToFetch) => {
  if (!usernameToFetch) return;

  loading.value = true;
  searched.value = false;

  try {
    const response = await fetch(`https://sports321.vercel.app/api/search?username=${usernameToFetch}`, {
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      searched.value = true;
      if (response.status === 404) {
        userProfile.value = null;
        posts.value = [];
        showNotification('User not found', true);
        return;
      }
      throw new Error('Failed to fetch user data');
    }

    const data = await response.json();
    searched.value = true;

    userProfile.value = {
      username: data.user.username,
      profilePicture: data.user.profile_picture,
      description: data.user.description,
      location: data.user.location,
      status: data.user.status,
      profession: data.user.profession,
      hobby: data.user.hobby,
    };

    posts.value = data.posts.map(post => ({
      ...post,
      comments: post.comments?.map(comment => ({
        ...comment,
        showReplies: false,
        replies: Array.isArray(comment.replies) ? comment.replies : [],
      })) || [],
      likedBy: post.likedBy || [],
      dislikedBy: post.dislikedBy || [],
      views: post.views || 0,
    }));
  } catch (error) {
    console.error('Error fetching user data:', error);
    searched.value = true;
    userProfile.value = null;
    posts.value = [];
    showNotification(`Error: ${error.message}`, true);
  } finally {
    loading.value = false;
  }
};

const searchUser = debounce(() => {
  if (!searchQuery.value.trim()) {
    showNotification('Please enter a username', true);
    return;
  }
  
  router.push(`/user/${searchQuery.value.trim()}`);
}, 300);

const resetSearch = () => {
  userProfile.value = null;
  posts.value = [];
  searched.value = false;
  searchQuery.value = '';
  router.push('/user');
};

// Initial load
onMounted(() => {
  if (username.value) {
    fetchUserData(username.value);
  }
});

// React to route changes and update search input
watch(() => route.params.username, (newUsername) => {
  if (newUsername) {
    username.value = newUsername;
    searchQuery.value = newUsername;
    fetchUserData(newUsername);
  }
});

const showNotification = (message, isError) => {
  console.log(`${isError ? '❌ Error' : '✅ Success'}: ${message}`);
};
</script>


<style scoped>
.post-card {
  background: #444;
  padding: 16px;
  margin: 10px 0;
  border-radius: 8px;
  color: #fff;
}

.post-header, .comment-header, .reply-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.post-profile-pic, .comment-profile-pic, .reply-profile-pic {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.post-username, .comment-username, .reply-username {
  font-weight: bold;
  cursor: pointer;
}

.post-timestamp, .comment-timestamp, .reply-timestamp {
  color: #ccc;
  font-size: 12px;
}

.post-message, .comment, .reply {
  margin: 10px 0;
}

.post-image {
  max-width: 100%;
  border-radius: 8px;
  cursor: pointer;
}

.post-actions, .comment-actions {
  display: flex;
  gap: 10px;
}

.post-actions button, .comment-actions button, .reply-box button {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 25px;
  cursor: pointer;
}

.comments-section {
  margin-top: 10px;
  padding-left: 20px;
}

.comment {
  border-left: 2px solid #666;
  padding-left: 10px;
  margin: 10px 0;
}

.replies {
  margin-left: 20px;
}

.reply {
  border-left: 2px solid #888;
  padding-left: 10px;
  margin: 5px 0;
}

.comment-input, .reply-box {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.comment-input input, .reply-input {
  flex: 1;
  padding: 8px;
  border-radius: 25px;
  border: 1px solid #444;
  background: #333;
  color: #fff;
}

.fullscreen-post {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.fullscreen-content {
  background: #444;
  padding: 20px;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 80%;
  overflow-y: auto;
}

.close-button {
  background: #ff4444;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 25px;
  cursor: pointer;
  float: right;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.modal-content button {
  margin: 10px;
  padding: 8px 16px;
  border-radius: 25px;
  cursor: pointer;
}
</style>
