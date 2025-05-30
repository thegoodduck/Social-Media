<template>
  <div class="min-h-screen flex flex-col">
    <!-- Show Auth component if not authenticated -->
    <Auth v-if="!isAuthenticated" @auth-success="handleAuthSuccess" />
    
    <!-- Main app content (only show when authenticated) -->
    <template v-else>
      <!-- Header -->
      <header>
        <h1 style="font-size: 23px; margin-left: 5%">𝓢𝔂𝓷𝓬</h1>
        <div class="user-section" style="gap: 12px; display: flex;">
          <i class="fas fa-search search-icon" @click="toggleSearch" style="font-size: 25px; color: #5eead4; margin-right: 15%; cursor: pointer; margin-top: 5px"></i>
          <transition name="fade">
            <div v-if="searchVisible" class="search-dropdown">
              <input v-model="searchQuery" type="text" placeholder="Search posts or videos...">
            </div>
          </transition>
          <div class="relative">
            <img :src="userProfile.avatar" alt="User Avatar" class="hover-scale" @click="toggleProfileMenu" style="width: 32px; height: 32px; border-radius: 50%; cursor: pointer; border: 2px solid #000; margin-right: 20px;">
            <transition name="fade">
              <div v-if="showProfileMenu" class="profile-menu">
                <p class="name">{{ userProfile.name }}</p>
                <p class="email">{{ userProfile.email }}</p>
                <button @click="logout">Logout</button>
              </div>
            </transition>
          </div>
        </div>
      </header>
      
      <!-- Main Content -->
      <main>
        <Posts v-if="currentTab === 'posts'" 
               :searchQuery="searchQuery" 
               :loggedInUsername="loggedInUsername" 
               :sessionId="sessionId"
               :userId="userId"
               :authToken="authToken" />
        <Videos v-if="currentTab === 'videos'" 
                :searchQuery="searchQuery"
                :userId="userId" />
        <Chat v-if="currentTab === 'chat'" 
              :userId="userId"
              :username="loggedInUsername" />
        <Settings v-if="currentTab === 'settings'" 
                  :settings="settings" 
                  :userProfile="userProfile"
                  @update:settings="settings = $event" />
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
    </template>
  </div>
</template>

<script>
import Posts from './Posts.vue';
import Videos from './Videos.vue';
import Chat from './Chat.vue';
import Settings from './Settings.vue';
import Auth from './Auth.vue';
import { nodeAPI } from './config/api.js';

export default {
  components: { Posts, Videos, Chat, Settings, Auth },
  data() {
    return {
      currentTab: 'posts',
      searchVisible: false,
      searchQuery: '',
      showProfileMenu: false,
      userProfile: {
        name: 'John Doe',
        email: 'john.doe@example.com',
        avatar: 'https://via.placeholder.com/32'
      },
      loggedInUsername: localStorage.getItem('username') || 'Unknown',
      sessionId: sessionStorage.getItem('sessionId') || this.generateSessionId(),
      userId: localStorage.getItem('userId'),
      authToken: localStorage.getItem('authToken'),
      settings: {
        darkMode: false,
        notifications: true
      }    };
  },
  computed: {
    isAuthenticated() {
      return !!(this.userId && this.authToken);
    }
  },
  async mounted() {
    // Initialize session if not exists
    if (!this.sessionId) {
      this.sessionId = this.generateSessionId();
      sessionStorage.setItem('sessionId', this.sessionId);
    }
    
    // Load user profile if authenticated
    if (this.userId && this.authToken) {
      await this.loadUserProfile();
    }
  },  methods: {
    generateSessionId() {
      return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    },
    
    async loadUserProfile() {
      try {
        const response = await nodeAPI.getUserInfo(this.userId);
        if (response.user) {
          this.userProfile = {
            name: response.user.username,
            email: response.user.email,
            avatar: response.user.avatar || 'https://via.placeholder.com/32'
          };
          this.loggedInUsername = response.user.username;
          localStorage.setItem('username', response.user.username);
        }
      } catch (error) {
        console.error('Error loading user profile:', error);
        // Clear invalid auth data
        this.clearAuthData();
      }
    },
    
    clearAuthData() {
      localStorage.removeItem('userId');
      localStorage.removeItem('authToken');
      localStorage.removeItem('username');
      this.userId = null;
      this.authToken = null;
      this.userProfile = {
        name: 'Guest',
        email: '',
        avatar: 'https://via.placeholder.com/32'
      };
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
    },    logout() {
      console.log('User logged out');
      this.clearAuthData();
      this.showProfileMenu = false;
      // Optionally redirect to login or refresh
    },
    
    handleAuthSuccess(authData) {
      this.userId = authData.user.id;
      this.authToken = authData.token;
      this.userProfile = {
        name: authData.user.username,
        email: authData.user.email,
        avatar: authData.user.avatar || 'https://via.placeholder.com/32'
      };
      this.loggedInUsername = authData.user.username;
      console.log('Authentication successful:', authData.user.username);
    }
  }
};
</script>