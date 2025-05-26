<template>
  <section class="chat-section">
    <div class="tabs">
      <button
        :class="{ active: activeSection === 'users-section' }"
        @click="switchSection('users-section')"
      >
        Conversation
      </button>
      <button
        :class="{ active: activeSection === 'World Chat' }"
        @click="switchSection('World Chat')"
      >
        World Chat
      </button>
    </div>
    <div class="sections">
      <div v-show="activeSection === 'users-section'" class="section active">
        <div id="loading" class="loading" v-if="loading">
          <div class="spinner"></div>
        </div>
        <div id="load-more-trigger"></div>
        <div class="users-container">
          <div
            v-for="user in users"
            :key="user.username"
            class="user-card"
            @click="handleUserClick(user)"
          >
            <div class="profile-picture">
              <img :src="user.profile_picture || 'default-pfp.jpg'" :alt="user.username + ' profile'" />
            </div>
            <div class="username"><strong>{{ user.username }}</strong></div>
          </div>
        </div>
      </div>
      <div v-show="activeSection === 'World Chat'" class="section">
        <div id="chat-container">
          <div id="messages">
            <div
              v-for="message in messages"
              :key="message.id"
              class="message"
            >
              <div class="bubble">
                <div class="text-row">
                  <div
                    class="username"
                    :style="getUsernameStyle(message.username)"
                  >
                    {{ message.username || 'Unknown' }}
                  </div>
                  <span class="message-text">{{ message.text || '[Empty Message]' }}</span>
                </div>
              </div>
            </div>
          </div>
          <div id="input-container">
            <input
              v-model="inputMessage"
              id="input-message"
              type="text"
              placeholder="Type a message..."
              @keyup.enter="sendMessage"
            />
            <button id="send-button" @click="sendMessage">Send</button>
          </div>
          <div id="warning-message">{{ warningMessage }}</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import * as Ably from 'ably';

export default {
  name: 'Chat',
  data() {
    return {
      activeSection: 'users-section',
      users: [],
      loading: false,
      loggedInUsername: localStorage.getItem('username')?.trim() || null,
      inputMessage: '',
      messages: [],
      warningMessage: '',
      sentMessages: new Set(),
      username: localStorage.getItem('username')?.trim() || 'Unknown',
      userColors: {},
      ably: null,
      channel: null
    };
  },
  methods: {
    switchSection(section) {
      this.activeSection = section;
    },
    async fetchUsers() {
      this.loading = true;
      try {
        const response = await fetch('https://1999-theta.vercel.app/api/UserListChat', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        const users = await response.json();
        const addedUsernames = new Set();
        this.users = users.filter(user => {
          if (addedUsernames.has(user.username)) return false;
          addedUsernames.add(user.username);
          return true;
        });
      } catch (error) {
        console.error('Error fetching users:', error);
      } finally {
        this.loading = false;
      }
    },
    handleUserClick(user) {
      if (user.username !== this.loggedInUsername) {
        localStorage.setItem('chatWith', user.username);
        localStorage.setItem('chatWithId', user.id);
        localStorage.setItem('profileImage', user.profile_picture || 'default-pfp.jpg');
        window.location.href = `https://latestnewsandaffairs.site/public/react.html`;
      }
    },
    getColorForUsername(name) {
      if (!this.userColors[name]) {
        const colors = [
          '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
          '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe',
          '#008080', '#e6beff', '#9a6324', '#800000'
        ];
        this.userColors[name] = colors[Math.floor(Math.random() * colors.length)];
      }
      return this.userColors[name];
    },
    getUsernameStyle(username) {
      if (username === 'USERNAME99') {
        return {
          backgroundColor: '#000',
          color: '#fff',
          fontSize: '23px',
          marginRight: '8px',
          whiteSpace: 'nowrap',
          padding: '4px 8px',
          borderRadius: '4px'
        };
      }
      return {
        fontWeight: 'bold',
        color: this.getColorForUsername(username)
      };
    },
    appendMessage(text, username, id) {
      if (this.sentMessages.has(id)) return;
      this.messages.push({ text, username, id });
      this.sentMessages.add(id);
      this.$nextTick(() => {
        const messagesContainer = this.$el.querySelector('#messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      });
    },
    sendMessage() {
      const message = this.inputMessage.trim();
      this.warningMessage = '';
      if (!this.username || this.username === 'Unknown') {
        this.warningMessage = 'Please sign up before sending a message.';
        return;
      }
      if (message) {
        const messageId = Date.now() + Math.random();
        this.appendMessage(message, this.username, messageId);
        if (this.channel) {
          this.channel.publish('new-message', {
            text: message,
            id: messageId,
            username: this.username
          });
        }
        this.inputMessage = '';
      }
    }
  },
  mounted() {
    this.fetchUsers();
    // Initialize Ably
    this.ably = new Ably.Realtime('9frHeA.Si13Zw:KVzVyovw6hCu4RRuy6P11Tyl0h7MJIzv2Q_n4YgbNnE'); // Replace with your Ably API key
    this.ably.connection.on('connected', () => {
      console.log('Connected to Ably');
      this.channel = this.ably.channels.get('chat-room');
      this.channel.subscribe('new-message', (msg) => {
        const { text, id, username } = msg.data;
        if (!this.sentMessages.has(id)) {
          this.appendMessage(text, username, id);
        }
      });
    });
    this.ably.connection.on('failed', () => {
      console.error('Failed to connect to Ably');
      this.warningMessage = 'Failed to connect to chat service.';
    });
  },
  beforeUnmount() {
    if (this.channel) {
      this.channel.unsubscribe('new-message');
    }
    if (this.ably) {
      this.ably.close();
    }
  }
};
</script>