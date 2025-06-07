<template>
  <div>
    <!-- Floating Bolt Button -->
    <div class="floating-circle" @click="togglePanel">
      <i class="fas fa-bolt"></i>
    </div>

    <!-- Slide-up Fullscreen Panel -->
    <transition name="slide-up">
      <div v-if="showPanel" class="floating-panel">
        <div class="panel-header">
          <h2>Upload Section</h2>
          <button class="close-btn" @click="togglePanel">&times;</button>
        </div>
        <div class="panel-content">
              <!-- Post Input Form -->
    <div class="post-input">
      <textarea v-model="postText" id="postText" placeholder="What's your opinion?"></textarea>
      <input type="file" id="file-input" accept="image/*" @change="handleImageUpload" />
      <img v-if="imagePreview" :src="imagePreview" id="image-preview" alt="Image Preview" />
      <button id="submitBtn" @click="postOpinion">Post Opinion</button>
    </div>

        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Ably from 'ably';

// User info from localStorage
const loggedInUsername = ref(localStorage.getItem('username') || '');
const userId = ref(localStorage.getItem('userId') || '');
const profilePic = ref(localStorage.getItem('profilePic') || '');
const sessionId = ref(localStorage.getItem('sessionId') || '');

 const ably = new Ably.Realtime('eCkrsA.JzcmYQ:JLywAltPtm-KWD6Rd0MItQRgi-I4R7zn6BpI1UVQ3Eg'); // Replace with your actual Ably API key

    // Get channel for real-time updates
 const channel = ably.channels.get('posts-channel');
    
const generateSessionId = () => {
 return Math.random().toString(36).substring(2, 15) +
             Math.random().toString(36).substring(2, 15);
    };

// State
const showPanel = ref(false);
const postText = ref('');
const imagePreview = ref(null);
const imageData = ref(null);
const uploadedImage = ref(null);
const fileInput = ref(null);
const lastSentPostId = ref(null);

// Toggle floating nav panel
const togglePanel = () => {
  showPanel.value = !showPanel.value;
};

// Handle image upload and resizing
const handleImageUpload = async (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onloadend = async () => {
      try {
        const resizedImage = await resizeImageToMaxSize(reader.result, 65);
        imageData.value = await blobToBase64(resizedImage);
        imagePreview.value = reader.result;
        uploadedImage.value = file;
      } catch (error) {
        showNotification('Error processing image.', true);
      }
    };
    reader.readAsDataURL(file);
  }
};

// Resize image to specified max size (in KB)
const resizeImageToMaxSize = (imageSrc, maxSizeKB = 65) => {
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
        (blob) => {
          if (blob.size / 1024 <= maxSizeKB) {
            resolve(blob);
          } else {
            reject(new Error('Image exceeds max size after resizing.'));
          }
        },
        'image/webp',
        0.4
      );
    };
    img.onerror = () => reject(new Error('Error loading image.'));
  });
};

// Convert Blob to Base64
const blobToBase64 = (blob) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
};

// Submit the post
const postOpinion = async () => {
  if (!sessionId.value || !loggedInUsername.value) {
    showNotification('Error: Session ID and Username are required', true);
    return;
  }
  if (!postText.value && !imageData.value) {
    showNotification('Post content cannot be empty!', true);
    return;
  }

  const postData = {
    message: postText.value,
    username: loggedInUsername.value,
    sessionId: sessionId.value,
    userId: userId.value,
    profilePic: profilePic.value,
    photo: imageData.value,
  };

  try {
    const response = await fetch('https://sports321.vercel.app/api/postOpinion', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify(postData),
    });

    if (!response.ok) throw new Error('Failed to submit post');

    const newPost = await response.json();
    lastSentPostId.value = newPost._id;
    addPostToFeed(newPost, true);
    showNotification('Post submitted successfully!', false);
    channel.publish('newOpinion', newPost);
    resetForm();

    await fetch('https://2damnit.vercel.app/api/notifications', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'send-push-notification' }),
    });
  } catch (error) {
    showNotification('Error submitting post: ' + error.message, true);
  }
};
// Reset form
const resetForm = () => {
  postText.value = '';
  imagePreview.value = null;
  imageData.value = null;
  uploadedImage.value = null;
  if (fileInput.value) fileInput.value.value = '';
};

  // Subscribe to Ably channels
  channel.subscribe('newOpinion', message => {
    const incomingPost = message.data;
    if (incomingPost?._id && incomingPost._id !== lastSentPostId.value) {
      showNotification('New post added!', false);
      addPostToFeed(incomingPost, true);
    }
  });
</script>


<style scoped>
.floating-circle {
  position: fixed;
  margin-bottom: 12%;
  bottom: 70px;
  right: 20px;
  width: 48px;
  height: 48px;
  background-color: #0d6efd;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
  z-index: 1001;
  cursor: pointer;
  transition: transform 0.3s ease;
}
.floating-circle:hover {
  transform: scale(1.1);
}

.floating-panel {
  position: fixed;
  bottom: 8%;
  right: 0%;
  left: 0%;
  top: 8.5%;
  background-color: #000;
  z-index: 1002;
  box-shadow: 0 -4px 10px rgba(0, 0, 0, 0.15);
  padding: 20px;
  display: flex;
  flex-direction: column;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.close-btn {
  font-size: 24px;
  border: none;
  background: none;
  cursor: pointer;
}
.panel-content {
  margin-top: 20px;
  overflow-y: auto;
  flex-grow: 1;
}
/* Simple slide-up transition */
.slide-up-enter-active, .slide-up-leave-active {
  transition: transform 0.3s ease;
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translateY(100%);
}
/* Post Input Form */
.post-input {
  margin-bottom: 20px;
}
.post-input {
  margin-bottom: 20px;
  background: #222;
  padding: 20px;
  border-radius: 10px;
  color: #fff;
  font-family: sans-serif;
}
.post-input textarea {
  width: 100%;
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #444;
  background-color: #333;
  color: #fff;
  font-size: 14px;
  resize: vertical;
  margin-bottom: 15px;
}
</style>
