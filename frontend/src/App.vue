
<template>
  <div class="min-h-screen flex flex-col">
    <!-- Header -->
    <header>
      <h1 style="font-size: 23px; margin-left: 5%">𝓢𝔂𝓷𝓬</h1>
      <div class="user-section" style="gap: 12px; display: flex;">
        <i class="fas fa-search search-icon" @click="toggleSearch" style="font-size: 25px; color: blue; margin-right: 15%; cursor: pointer; margin-top: 5px"></i>
        <transition name="fade">
          <div v-if="searchVisible" class="search-dropdown">
            <input v-model="searchQuery" type="text" placeholder="Search posts or videos...">
          </div>
        </transition>
        <div class="relative">
          <span class="username-display" @click="toggleProfileMenu">{{ userProfile.username }}</span>
          <transition name="fade">
            <div v-if="showProfileMenu" class="profile-menu">
              <button @click="authAction">{{ isSignedIn ? 'Logout' : 'Login' }}</button>
            </div>
          </transition>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main>
      <Posts v-if="currentTab === 'posts'" :searchQuery="searchQuery" :username="userProfile.username" :userId="userProfile.userId" />
      <Videos v-if="currentTab === 'videos'" :searchQuery="searchQuery" :username="userProfile.username" :userId="userProfile.userId" />
      <Chat v-if="currentTab === 'chat'" />
      <Settings v-if="currentTab === 'settings'" :settings="settings" @update:settings="settings = $event" />
    </main>

    <!-- Navbar -->
    <nav class="glassmorphism">
      <ul>
        <li :class="{ active: currentTab === 'posts' }" @click="switchTab('posts')">
          <i class="fas fa-home"></i>
        </li>
        <li :class="{ active: currentTab === 'videos' }" @click="switchTab('videos')">
          <i class="fab fa-youtube"></i>
        </li>
        <li :class="{ active: currentTab === 'chat' }" @click="switchTab('chat')">
          <i class="fas fa-comment"></i>
        </li>
        <li :class="{ active: currentTab === 'settings' }" @click="switchTab('settings')">
          <i class="fas fa-cog"></i>
        </li>
      </ul>
    </nav>

         <!-- ✅ Floating Widget (like Llama) -->
    <Float />

  </div>
</template>

<script>
import Posts from './Posts.vue';
import Videos from './Videos.vue';
import Chat from './Chat.vue';
import Settings from './Settings.vue';
import Float from './Float.vue';
export default {
  components: { Posts, Videos, Chat, Settings,Float },
  data() {
    return {
      currentTab: 'posts',
      searchVisible: false,
      searchQuery: '',
      showProfileMenu: false,
      userProfile: {
        username: localStorage.getItem('username') || 'Guest',
        userId: localStorage.getItem('userId') || null,
        profilePic: localStorage.getItem('profilePic') || 'default-pic.png',    
      },
      settings: {
        darkMode: false,
        notifications: true,
      },
    };
  },
  computed: {
    isSignedIn() {
      return !!this.userProfile.username && this.userProfile.username !== 'Guest';
    },
  },
  methods: {
    decodeJWT(token) {
      try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(c =>
          '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
        ).join(''));
        return JSON.parse(jsonPayload);
      } catch {
        return null;
      }
    },
    async verifyToken(token) {
      const decoded = this.decodeJWT(token);
      if (!decoded) {
        this.authAction();
        return;
      }

      const currentUsername = localStorage.getItem('username');
      if (decoded?.username && decoded.username !== currentUsername) {
        try {
          const res = await fetch('https://1999-theta.vercel.app/api/authorize', {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          const data = await res.json();
          if (!res.ok) {
            this.authAction();
            return;
          }

          // Update localStorage and UI
          localStorage.setItem('username', decoded.username);
          localStorage.setItem('userId', decoded.userId || data.user.userId);
          localStorage.setItem('profilePic', decoded.profilePic || data.user.profilePic || localStorage.getItem('profilePic') || 'default-pic.png');
          
          this.userProfile.username = decoded.username;
          this.userProfile.userId = decoded.userId || data.user.userId;
          this.userProfile.profilePic = decoded.profilePic || data.user.profilePic || localStorage.getItem('profilePic') || 'default-pic.png';
          
          const usernameDisplay = document.getElementById('username-display');
          if (usernameDisplay) {
            usernameDisplay.textContent = decoded.username;
          }
        } catch {
          this.authAction();
        }
      }
    },
    switchTab(tab) {
      this.currentTab = tab;
      this.searchVisible = false;
      this.showProfileMenu = false;
    },
    toggleSearch() {
      this.searchVisible = !this.searchVisible;
      this.showProfileMenu = false;
      if (this.searchVisible) {
        this.$nextTick(() => {
          const searchInput = document.querySelector('.search-dropdown input');
          if (searchInput) searchInput.focus();
        });
      }
    },
    toggleProfileMenu() {
      this.showProfileMenu = !this.showProfileMenu;
      this.searchVisible = false;
    },
    authAction() {
      if (this.isSignedIn) {
        localStorage.removeItem('username');
        localStorage.removeItem('userId');
        localStorage.removeItem('authToken');
        localStorage.removeItem('profilePic');
        this.userProfile.username = 'Guest';
        this.userProfile.userId = null;
        this.userProfile.profilePic = 'default-pic.png';
        console.log('User logged out');
      }
      this.showProfileMenu = false;
      window.location.href = 'https://latestnewsandaffairs.site/public/signup';
    },
    updateUserProfile() {
      this.userProfile.username = localStorage.getItem('username') || 'Guest';
      this.userProfile.userId = localStorage.getItem('userId') || null;
      this.userProfile.profilePic = localStorage.getItem('profilePic') || 'default-pic.png';
    },
  },
  mounted() {
    // Verify token on mount
    const token = localStorage.getItem('authToken');
    if (token) {
      this.verifyToken(token);
    }

    // Listen for storage changes to sync across tabs
    window.addEventListener('storage', (event) => {
      if (event.key === 'username' || event.key === 'userId' || event.key === 'profilePic') {
        this.updateUserProfile();
      }
    });
    // Initial sync
    this.updateUserProfile();
  },
};
</script>

<style scoped>
.username-display {
  font-size: 19px;
  color: blue;
  cursor: pointer;
  margin-right: 16px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

</style>
