<template>
  <div>
    <!-- Loading Spinner -->
    <div id="loading" v-show="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <!-- Sort Buttons -->
    <div id="sort-options" style="gap:15%;">
      <button class="sort-button" :class="{ active: sortOption === 'most-liked' }" @click="sortPosts('most-liked')">General</button>
      <button class="sort-button" :class="{ active: sortOption === 'most-comments' }" @click="sortPosts('most-comments')">Trending</button>
      <button class="sort-button" :class="{ active: sortOption === 'newest' }" @click="sortPosts('newest')">Newest</button>
    </div>

    <!-- Posts Feed -->
    <div id="posts" class="posts-feed">
      <div
        v-for="post in posts"
        :key="post._id"
        class="post-card"
        :data-id="post._id"
        :data-liked-by="JSON.stringify(post.likedBy || [])"
        :data-disliked-by="JSON.stringify(post.dislikedBy || [])"
      >
        <!-- Post Header -->
        <div class="post-header">
          <div class="profile-picture" @click="showUserProfile(post.username, post.profilePicture)">
            <img :src="post.profilePicture || 'pfp2.jpg'" :alt="`${post.username}'s profile picture`" />
          </div>
          <div class="username">
            <strong>{{ post.username }}</strong>
          </div>
        </div>
        <!-- Comments Section -->

         <div
            :id="`comments-${post._id}`"
             class="comments-section"
            :class="{ fullscreen: post.showComments }"
             v-show="post.showComments"
            style="padding: 0; background-color: #000; border-radius: 0; font-size: 14px; margin: 0; width: 100%; height: 100%; box-sizing: border-box; overflow: hidden;">

         <div class="comments-list"
     style="background-color: #000; padding: 0; margin-top:5px; font-size: 14px; width: 100%; overflow-y: auto;">

            <div
            v-for="comment in post.comments"
             :key="comment.commentId"
             class="comment"
            :id="`comment-${comment.commentId}`"
            style="margin: 0 0 15px 0; padding: 0; background-color: #000;">

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

                  <!-- Comment Actions -->
                  <div style="font-size: 12px; margin-top: 8px; display: flex; align-items: center; gap: 15px;">
                    <button class="like-comment-btn" :class="{ liked: comment.likedBy?.includes(loggedInUsername) }" @click="likeComment(post._id, comment.commentId, comment.username)">
                      ❤️ <span class="like-count">{{ comment.hearts || 0 }}</span>
                    </button>

                    <button class="reply-btn" @click="toggleReplies(post._id, comment.commentId, comment.username, $event.target)">
                      💬 <span v-if="comment.replies?.length > 0">({{ comment.replies.length }})</span>
                    </button>

                    <button
                      v-if="comment.username === loggedInUsername || comment.sessionId === sessionId"
                      class="delete-comment-btn"
                      @click="deleteComment(post._id, comment.commentId)"
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              </div>
              <!-- Replies Section -->
              <div
                :id="`replies-${comment.commentId}`"
                class="replies"
                :style="{ display: comment.showReplies ? 'block' : 'none', marginTop: '10px', paddingLeft: '52px' }"
              >
                <div
                  v-for="reply in comment.replies"
                  :key="reply.replyId"
                  :id="`reply-${reply.replyId}`"
                  class="reply"
                  style="margin-bottom: 10px; display: flex; background-color: #222; padding: 10px 15px; border-radius: 8px; position: relative;"
                >
                  <div style="width: 30px; height: 30px; border-radius: 50%; overflow: hidden; margin-right: 10px;">
                    <img :src="reply.profilePicture || 'https://latestnewsandaffairs.site/public/pfp3.jpg'" :alt="`${reply.username || 'Unknown'}'s profile`" style="width: 100%; height: 100%; object-fit: cover;" />
                  </div>

                  <div style="flex: 1; color: #fff; font-size: 14px;">
                    <div style="display: flex; justify-content: space-between;">
                      <span style="font-weight: bold;">{{ reply.username || 'Unknown' }}</span>
                      <span style="font-size: 12px; color: #ccc;">{{ getTimeAgo(new Date(reply.timestamp)) }}</span>
                    </div>
                    <p style="margin: 0;">{{ reply.reply || 'No reply' }}</p>
                  </div>

                  <button
                    class="like-reply-btn"
                    :class="{ liked: reply.likedBy?.includes(loggedInUsername) }"
                    @click="likeReply(post._id, comment.commentId, reply.replyId)"
                    style="position: absolute; right: 10px; top: 10px;"
                  >
                    ❤️ <span class="like-count">{{ reply.hearts || 0 }}</span>
                  </button>
                </div>

                <!-- No replies -->
                <div v-if="!comment.replies || comment.replies.length === 0" class="no-replies" style="color: #ccc; font-size: 13px; padding: 10px 0;">
                  <p>No replies yet</p>
                </div>

                <div :id="`reply-box-${comment.commentId}`" class="reply-box"></div>
              </div>
            </div>
          </div>

        <!-- Comment Input -->
<div
  class="comment-input-container"
  style="position: absolute; bottom: 20px; left: 0; width: 100%; padding: 5px 10px; display: flex; align-items: center; justify-content: center; gap: 10px;"
>
  <input
    :id="`commentInput-${post._id}`"
    type="text"
    placeholder="Add a comment..."
    class="comment-input"
    style="width: 80%; padding: 5px 10px; border-radius: 25px; border: 1px solid #444; background-color: #333; color: #fff; font-size: 14px; transition: all 0.3s ease; box-sizing: border-box; outline: none; box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);"
    @keyup.enter="addComment(post._id)"
  />
  <button
    @click="addComment(post._id)"
    style="background-color: #007bff; color: white; padding: 5px 10px; border: none; border-radius: 25px; transition: background-color 0.3s ease; cursor: pointer; font-size: 14px; box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);"
  >
    Post
  </button>
</div>
          <div style="padding: 10px 15px; border-top: 1px solid #333;">
            <button class="close-comments-btn" @click="closeComments(post._id)">Close</button>
          </div>
        </div>

        <!-- Post Message & Image -->
        <p class="post-message" style="font-size: 13px; margin-top: 8px;font-family: 'Whitney', 'Helvetica Neue', Helvetica, Arial, sans-serif;">{{ post.message || "" }}</p>
        <img
          v-if="post.photo"
          :src="post.photo"
          alt="Post Image"
          style="width: 100%; max-width:300px; max-height:280px; border-radius: 10px; margin-bottom: 10px;"
          @click="openFullScreen(post.photo)"
        />

        <!-- Timestamp & Actions -->
        <div class="post-timestamp">
          <small>{{ formatTimestamp(post.timestamp) }}</small>
        </div>

        <div class="actions" >
          <button class="like-btn" :class="{ liked: post.likedBy?.includes(loggedInUsername) }" @click="likePost(post._id)">
            👍 {{ post.likes || 0 }}
          </button>
          <button class="dislike-btn" :class="{ disliked: post.dislikedBy?.includes(loggedInUsername) }" @click="dislikePost(post._id)">
            👎 {{ post.dislikes || 0 }}
          </button>
          <button class="comment-btn" @click="toggleComments(post._id)" style="color:#ff1100;">Comments ({{ post.comments?.length || 0 }} )</button>
          <button class="view-btn">💫 ({{ post.views || 0 }})</button>
          <button v-if="post.username === loggedInUsername || post.sessionId === sessionId" @click="editPost(post._id, post.username)">Edit</button>
          <button v-if="post.username === loggedInUsername || post.sessionId === sessionId" @click="deletePost(post._id)">Delete</button>
        </div>
      </div> <!-- ✅ Closes v-for post-card -->
    </div> <!-- ✅ Closes #posts -->

    <!-- Modal -->
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

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import Ably from 'ably';

export default {
  name: 'Posts',
  setup() {
    // Reactive state
    const posts = ref([]);
    const currentPage = ref(1);
    const loading = ref(false);
    const hasMorePosts = ref(true);
    const sortOption = ref('most-liked');
    const postText = ref('');
    const imagePreview = ref(null);
    const imageData = ref(null);
    const lastSentPostId = ref(null);
    const loggedInUsername = ref(localStorage.getItem('username') || 'Unknown');
     const sessionId = ref(null);
    const showModal = ref(false);
    const modalMessage = ref('');
    const modalAction = ref(null);
    const modalActionText = ref('');

    const ably = new Ably.Realtime('eCkrsA.JzcmYQ:JLywAltPtm-KWD6Rd0MItQRgi-I4R7zn6BpI1UVQ3Eg'); // Replace with your actual Ably API key

    // Get channel for real-time updates
    const channel = ably.channels.get('posts-channel');
    
       const generateSessionId = () => {
      return Math.random().toString(36).substring(2, 15) +
             Math.random().toString(36).substring(2, 15);
    };

    // Fetch posts
    const fetchPosts = async (page = 1, sort = 'newest') => {
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
    };

    // Load more posts
    const loadMorePosts = async () => {
      if (loading.value || !hasMorePosts.value) return;
      loading.value = true;
      const newPosts = await fetchPosts(currentPage.value, sortOption.value);
      if (newPosts?.posts?.length > 0) {
        posts.value.push(
          ...newPosts.posts.map(post => ({
            ...post,
            showComments: false,
            comments: post.comments?.map(comment => ({
              ...comment,
              showReplies: false,
              replies: Array.isArray(comment.replies) ? comment.replies : [],
            })) || [],
            likedBy: post.likedBy || [],
            dislikedBy: post.dislikedBy || [],
          }))
        );
        currentPage.value++;
        hasMorePosts.value = newPosts.hasMorePosts;
      } else {
        hasMorePosts.value = false;
      }
      loading.value = false;
    };

    // Sort posts
    const sortPosts = sortBy => {
      sortOption.value = sortBy;
      posts.value = [];
      currentPage.value = 1;
      hasMorePosts.value = true;
      loadMorePosts();
    };

    // Add post to feed
    const addPostToFeed = (post, isNewPost = false) => {
      if (!post || !post._id) return;
      const formattedPost = {
        ...post,
        likes: post.likes || 0,
        dislikes: post.dislikes || 0,
        comments: post.comments?.map(comment => ({
          ...comment,
          showReplies: false,
          replies: Array.isArray(comment.replies) ? comment.replies : [],
        })) || [],
        views: post.views || 0,
        likedBy: post.likedBy || [],
        dislikedBy: post.dislikedBy || [],
        showComments: false,
      };
      if (isNewPost) {
        posts.value.unshift(formattedPost);
      } else {
        posts.value.push(formattedPost);
      }
      incrementViewOnScroll(post._id);
    };

    // Format timestamp
    const formatTimestamp = timestamp => {
      const date = new Date(timestamp);
      if (isNaN(date)) return 'Invalid Date';
      return date.toLocaleString('en-GB', {
        day: 'numeric',
        month: 'long',
        hour: '2-digit',
        minute: '2-digit',
      });
    };

    // Get time ago
    const getTimeAgo = date => {
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
    };

    // Show user profile
    const showUserProfile = (username, profilePicture) => {
      window.location.href = `search2.html?username=${encodeURIComponent(
        username
      )}`;
    };

    // Scroll handler
    const handleScroll = () => {
      if (
        window.innerHeight + window.scrollY >=
        document.body.offsetHeight - 500
      ) {
        loadMorePosts();
      }
      posts.value.forEach(post => incrementViewOnScroll(post._id));
    };

    // Increment view on scroll
    const incrementViewOnScroll = postId => {
      const postElement = document.querySelector(
        `.post-card[data-id="${postId}"]`
      );
      if (postElement && isElementInViewport(postElement)) {
        const hasViewed = sessionStorage.getItem(`viewed_${postId}`);
        if (!hasViewed) {
          const post = posts.value.find(p => p._id === postId);
          if (post) {
            post.views = (post.views || 0) + 1;
            sessionStorage.setItem(`viewed_${postId}`, 'true');
            sessionStorage.setItem(`views_${postId}`, post.views);
            updatePostInFeed({ _id: postId, views: post.views });
          }
        }
      }
    };

    // Check if element is in viewport
    const isElementInViewport = el => {
      const rect = el.getBoundingClientRect();
      return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <=
          (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
      );
    };

    // Like post
    const likePost = async postId => {
      const post = posts.value.find(p => p._id === postId);
      if (!post) return;
      const likedBy = post.likedBy || [];
      const dislikedBy = post.dislikedBy || [];
      let likeCount = post.likes || 0;
      if (likedBy.includes(loggedInUsername.value)) {
        likeCount--;
        post.likedBy = likedBy.filter(user => user !== loggedInUsername.value);
      } else {
        likeCount++;
        post.likedBy = [...likedBy, loggedInUsername.value];
        if (dislikedBy.includes(loggedInUsername.value)) {
          post.dislikes--;
          post.dislikedBy = dislikedBy.filter(
            user => user !== loggedInUsername.value
          );
        }
      }
      post.likes = likeCount;
      try {
        const response = await fetch('https://sports123.vercel.app/api/editPost', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            postId,
            username: loggedInUsername.value,
            action: 'like',
          }),
        });
        if (!response.ok) throw new Error('Failed to like post');
        const result = await response.json();
        showNotification('Post liked successfully!', false);
        updatePostInFeed(result);
      } catch (error) {
        showNotification(error.message, true);
        post.likes--;
      }
    };

    // Dislike post
    const dislikePost = async postId => {
      const post = posts.value.find(p => p._id === postId);
      if (!post) return;
      const likedBy = post.likedBy || [];
      const dislikedBy = post.dislikedBy || [];
      let dislikeCount = post.dislikes || 0;
      if (dislikedBy.includes(loggedInUsername.value)) {
        dislikeCount--;
        post.dislikedBy = dislikedBy.filter(
          user => user !== loggedInUsername.value
        );
      } else {
        dislikeCount++;
        post.dislikedBy = [...dislikedBy, loggedInUsername.value];
        if (likedBy.includes(loggedInUsername.value)) {
          post.likes--;
          post.likedBy = likedBy.filter(user => user !== loggedInUsername.value);
        }
      }
      post.dislikes = dislikeCount;
      try {
        const response = await fetch('https://sports123.vercel.app/api/editPost', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            postId,
            username: loggedInUsername.value,
            action: 'dislike',
          }),
        });
        if (!response.ok) throw new Error('Failed to dislike post');
        const result = await response.json();
        showNotification('Post disliked successfully!', false);
        updatePostInFeed(result);
      } catch (error) {
        showNotification(error.message, true);
        post.dislikes--;
      }
    };

    // Update post in feed
    const updatePostInFeed = updatedPost => {
      const index = posts.value.findIndex(p => p._id === updatedPost._id);
      if (index !== -1) {
        posts.value[index] = {
          ...posts.value[index],
          ...updatedPost,
          comments: updatedPost.comments?.map(comment => ({
            ...comment,
            showReplies: posts.value[index].comments.find(
              c => c.commentId === comment.commentId
            )?.showReplies || false,
            replies: Array.isArray(comment.replies) ? comment.replies : [],
          })) || [],
          likedBy: updatedPost.likedBy || posts.value[index].likedBy,
          dislikedBy: updatedPost.dislikedBy || posts.value[index].dislikedBy,
        };
      }
    };

    // Toggle comments
    const toggleComments = postId => {
      const post = posts.value.find(p => p._id === postId);
      if (post) {
        post.showComments = !post.showComments;
      }
    };

    // Close comments
    const closeComments = postId => {
      const post = posts.value.find(p => p._id === postId);
      if (post) {
        post.showComments = false;
      }
    };

    // Add comment
    const addComment = async postId => {
      const input = document.getElementById(`commentInput-${postId}`);
      const commentText = input.value.trim();
      if (!commentText) return;
      const commentId = Date.now().toString();
      const newComment = {
        commentId,
        username: loggedInUsername.value,
        comment: commentText,
        timestamp: new Date().toISOString(),
        profilePicture: localStorage.getItem('profilePic')|| 'pfp2.jpg', 
        hearts: 0,
        replies: [],
      };
      const post = posts.value.find(p => p._id === postId);
      if (post) {
        post.comments.push(newComment);
        try {
          const response = await fetch('https://sports123.vercel.app/api/editPost', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              postId,
              username: loggedInUsername.value,
              action: 'comment',
              comment: commentText,
              commentId,
            }),
          });
          if (!response.ok) throw new Error('Failed to add comment');
          const result = await response.json();
          updatePostInFeed(result);
          input.value = '';
        } catch (error) {
          post.comments = post.comments.filter(c => c.commentId !== commentId);
          showNotification(error.message, true);
        }
      }
    };

    // Toggle replies
    const toggleReplies = (postId, commentId, commentUsername, buttonElement) => {
      const post = posts.value.find(p => p._id === postId);
      if (!post) return;
      const comment = post.comments.find(c => c.commentId === commentId);
      if (comment) {
        comment.showReplies = !comment.showReplies;
        showReplyBox(postId, commentId, commentUsername);
      }
    };

    // Show reply box
    const showReplyBox = (postId, commentId, commentUsername) => {
      const repliesContainer = document.getElementById(`replies-${commentId}`);
      const existingReplyBox = document.getElementById(`reply-box-${commentId}`);
      if (existingReplyBox) existingReplyBox.remove();
      const replyBox = document.createElement('div');
      replyBox.id = `reply-box-${commentId}`;
      replyBox.className = 'reply-box';
      replyBox.innerHTML = `
        <input
          type="text"
          id="reply-input-${commentId}"
          placeholder="Write a reply..."
          class="reply-input"
        />
        <button onclick="document.getElementById('add-reply-${commentId}').click()">
          Send
        </button>
        <button
          id="add-reply-${commentId}"
          style="display: none;"
          onclick="window.vueInstance.addReply('${postId}', '${commentId}', document.getElementById('reply-input-${commentId}').value, '${loggedInUsername.value}')"
        ></button>
      `;
      repliesContainer.appendChild(replyBox);
    };

    // Add reply
    const addReply = async (postId, commentId, replyText, replyUsername) => {
      if (!replyText.trim()) {
        console.error('Reply cannot be empty');
        return;
      }
      const replyId = Date.now().toString();
      const post = posts.value.find(p => p._id === postId);
      if (!post) return;
      const comment = post.comments.find(c => c.commentId === commentId);
      if (!comment) return;
      const newReply = {
        replyId,
        username: replyUsername,
        reply: replyText,
        timestamp: new Date().toISOString(),
        profilePicture: localStorage.getItem('profilePic') || 'pfp2.jpg',
                        
        hearts: 0,
      };
      comment.replies.push(newReply);
      comment.showReplies = true;
      try {
        const response = await fetch('https://sports321.vercel.app/api/editPost', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            postId,
            commentId,
            username: replyUsername,
            action: 'reply',
            reply: replyText,
            replyId,
          }),
        });
        if (!response.ok) throw new Error('Failed to add reply');
        const updatedPost = await response.json();
        updatePostInFeed(updatedPost);
      } catch (error) {
        comment.replies = comment.replies.filter(r => r.replyId !== replyId);
        showNotification('Error adding reply: ' + error.message, true);
      }
    };

    // Like comment
    const likeComment = async (postId, commentId, commentUsername) => {
      const post = posts.value.find(p => p._id === postId);
      if (!post) return;
      const comment = post.comments.find(c => c.commentId === commentId);
      if (!comment) return;
      const isAlreadyLiked = comment.likedBy?.includes(loggedInUsername.value);
      comment.likedBy = comment.likedBy || [];
      let likeCount = comment.hearts || 0;
      if (isAlreadyLiked) {
        comment.hearts = likeCount - 1;
        comment.likedBy = comment.likedBy.filter(
          user => user !== loggedInUsername.value
        );
      } else {
        comment.hearts = likeCount + 1;
        comment.likedBy.push(loggedInUsername.value);
      }
      try {
        const response = await fetch('https://sports321.vercel.app/api/editPost', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            postId,
            username: loggedInUsername.value,
            action: 'heart comment',
            commentId,
          }),
        });
        if (!response.ok) throw new Error('Failed to update comment');
        const updatedPost = await response.json();
        updatePostInFeed(updatedPost);
      } catch (error) {
        console.error('Error liking comment:', error);
        comment.hearts = isAlreadyLiked ? likeCount + 1 : likeCount - 1;
        if (isAlreadyLiked) {
          comment.likedBy.push(loggedInUsername.value);
        } else {
          comment.likedBy = comment.likedBy.filter(
            user => user !== loggedInUsername.value
          );
        }
      }
    };

    // Like reply
    const likeReply = async (postId, commentId, replyId) => {
      const post = posts.value.find(p => p._id === postId);
      if (!post) return;
      const comment = post.comments.find(c => c.commentId === commentId);
      if (!comment) return;
      const reply = comment.replies.find(r => r.replyId === replyId);
      if (!reply) return;
      const isAlreadyLiked = reply.likedBy?.includes(loggedInUsername.value);
      reply.likedBy = reply.likedBy || [];
      let likeCount = reply.hearts || 0;
      if (isAlreadyLiked) {
        reply.hearts = likeCount - 1;
        reply.likedBy = reply.likedBy.filter(
          user => user !== loggedInUsername.value
        );
      } else {
        reply.hearts = likeCount + 1;
        reply.likedBy.push(loggedInUsername.value);
      }
      try {
        const response = await fetch('https://sports321.vercel.app/api/editPost', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            postId,
            username: loggedInUsername.value,
            action: 'heart reply',
            commentId,
            replyId,
          }),
        });
        if (!response.ok) throw new Error('Failed to update reply');
        const updatedPost = await response.json();
        updatePostInFeed(updatedPost);
      } catch (error) {
        console.error('Error liking reply:', error);
        reply.hearts = isAlreadyLiked ? likeCount + 1 : likeCount - 1;
        if (isAlreadyLiked) {
          reply.likedBy.push(loggedInUsername.value);
        } else {
          reply.likedBy = reply.likedBy.filter(
            user => user !== loggedInUsername.value
          );
        }
      }
    };

    // Edit post
    const editPost = (postId, postUsername) => {
      if (postUsername !== loggedInUsername.value) {
        showNotification('You can only edit your own posts.', true);
        return;
      }
      modalMessage.value = 'Are you sure you want to edit this post?';
      modalAction.value = () => confirmEdit(postId);
      modalActionText.value = 'Edit';
      showModal.value = true;
    };

    const confirmEdit = async postId => {
      const postText = prompt('Edit your opinion:');
      if (!postText) {
        showNotification('Post content cannot be empty!', true);
        return;
      }
      const updatedPost = {
        id: postId,
        message: postText,
        username: loggedInUsername.value,
        timestamp: new Date().toISOString(),
      };
      try {
        const response = await fetch('https://sports123.vercel.app/api/deletePost', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedPost),
        });
        if (!response.ok) throw new Error('Failed to update post');
        showNotification('Post updated successfully!', false);
        channel.publish('editOpinion', updatedPost);
        updatePostInFeed(updatedPost);
        showModal.value = false;
      } catch (error) {
        showNotification('Error editing post: ' + error.message, true);
      }
    };

    // Delete post
    const deletePost = postId => {
      modalMessage.value =
        'Are you sure you want to delete this post? This action cannot be undone.';
      modalAction.value = () => confirmDeletePost(postId);
      modalActionText.value = 'Delete';
      showModal.value = true;
    };

    const confirmDeletePost = async postId => {
      try {
        const response = await fetch('https://sports321.vercel.app/api/deletePost', {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            postId,
            username: loggedInUsername.value,
            sessionId: sessionId.value,
          }),
        });
        if (!response.ok) throw new Error('Failed to delete post');
        showNotification('Post deleted successfully!', false);
        channel.publish('deleteOpinion', { id: postId });
        posts.value = posts.value.filter(p => p._id !== postId);
        showModal.value = false;
      } catch (error) {
        showNotification('Failed to delete post', true);
      }
    };

    // Delete comment
    const deleteComment = (postId, commentId) => {
      modalMessage.value =
        'Are you sure you want to delete this comment? This action cannot be undone.';
      modalAction.value = () => confirmDeleteComment(postId, commentId);
      modalActionText.value = 'Delete';
      showModal.value = true;
    };

    const confirmDeleteComment = async (postId, commentId) => {
      try {
        const response = await fetch('https://sports123.vercel.app/api/deletecomment', {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            postId,
            commentId,
            username: loggedInUsername.value,
            sessionId: sessionId.value,
          }),
        });
        if (!response.ok) throw new Error('Failed to delete comment');
        showNotification('Comment deleted successfully!', false);
        const post = posts.value.find(p => p._id === postId);
        if (post) {
          post.comments = post.comments.filter(c => c.commentId !== commentId);
        }
        showModal.value = false;
      } catch (error) {
        showNotification(`Error deleting comment: ${error.message}`, true);
      }
    };

    // Close modal
    const closeModal = () => {
      showModal.value = false;
    };

    // Open full-screen image
    const openFullScreen = imageSrc => {
      // Implement full-screen image logic if needed
      console.log('Open full-screen image:', imageSrc);
    };

    // Notification (mock, replace with actual implementation)
    const showNotification = (message, isError) => {
      console.log(`${isError ? 'Error' : 'Success'}: ${message}`);
      // Implement actual notification UI
    };

// Lifecycle hooks
onMounted(() => {
  loadMorePosts();
  window.addEventListener('scroll', handleScroll);

  // Ensure session ID exists
  const existingId = localStorage.getItem('sessionId');
  if (!existingId) {
    const newId = generateSessionId();
    localStorage.setItem('sessionId', newId);
    sessionId.value = newId;
  } else {
    sessionId.value = existingId;
  }

  // Subscribe to Ably channels
  channel.subscribe('newOpinion', message => {
    const incomingPost = message.data;
    if (incomingPost?._id && incomingPost._id !== lastSentPostId.value) {
      showNotification('New post added!', false);
      addPostToFeed(incomingPost, true);
    }
  });

  channel.subscribe('editOpinion', message => {
    updatePostInFeed(message.data);
  });

  channel.subscribe('deleteOpinion', message => {
    posts.value = posts.value.filter(p => p._id !== message.data.id);
  });

  channel.subscribe('likePost', message => {
    updatePostInFeed(message.data);
  });

  channel.subscribe('dislikePost', message => {
    updatePostInFeed(message.data);
  });

  channel.subscribe('addComment', message => {
    updatePostInFeed(message.data);
  });

  channel.subscribe('deleteComment', message => {
    updatePostInFeed(message.data);
  });

  // Expose addReply to global scope for reply box
  window.vueInstance = { addReply };
});


    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll);
      // Unsubscribe from Ably channels if needed
    });

    return {
      posts,
      sessionId,
      loading,
      sortOption,
      postText,
      imagePreview,
      sortPosts,
      showUserProfile,
      formatTimestamp,
      getTimeAgo,
      likePost,
      dislikePost,
      toggleComments,
      closeComments,
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
    };
  },
};
</script>
<style scoped>
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
.comments-section.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  background-color: #000;
    z-index: 1000;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    padding: 40px;
    justify-content: flex-start;
    align-items: flex-start; /* Align to left */
}
.comments-section .close-comments-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #ff4c4c;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 20px;
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

</style>

