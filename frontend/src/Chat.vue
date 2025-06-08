<template>
  <section class="chat-section" style="background: linear-gradient(135deg, #232526 0%, #414345 100%); border:none; min-height: 700px;">
    <div class="tabs">
      <button
        :class="{ active: activeSection === 'users-section' }"
        @click="switchSection('users-section')"
      >
        <i class="fas fa-comments"></i> Conversation
      </button>
      <button
        :class="{ active: activeSection === 'World Chat' }"
        @click="switchSection('World Chat')"
      >
        <i class="fas fa-globe"></i> World Chat
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
            class="user-card user-card-animated"
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
            <transition-group name="fade" tag="div">
              <div
                v-for="message in messages"
                :key="message.id"
                class="message message-animated"
              >
                <div class="bubble">
                  <div class="text-row">
                    <div
                      class="username"
                      :style="getusernameStyle(message.username)"
                    >
                      {{ message.username || 'Unknown' }}
                    </div>
                    <span class="message-text">{{ message.text || '[Empty Message]' }}</span>
                  </div>
                </div>
              </div>
            </transition-group>
          </div>
          <div id="input-container">
            <input
              v-model="inputMessage"
              id="input-message"
              type="text"
              placeholder="Type a message..."
              @keyup.enter="sendMessage"
            />
            <button id="send-button" @click="sendMessage"><i class="fas fa-paper-plane"></i></button>
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
      loggedInusername: localStorage.getItem('username')?.trim() || null,
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
        const addedusernames = new Set();
        this.users = users.filter(user => {
          if (addedusernames.has(user.username)) return false;
          addedusernames.add(user.username);
          return true;
        });
      } catch (error) {
        console.error('Error fetching users:', error);
      } finally {
        this.loading = false;
      }
    },
    handleUserClick(user) {
      if (user.username !== this.loggedInusername) {
        localStorage.setItem('chatWith', user.username);
        localStorage.setItem('chatWithId', user.id);
        localStorage.setItem('profileImage', user.profile_picture || 'default-pfp.jpg');
        this.activeSection = 'World Chat';
        this.inputMessage = '';
      }
    },
    getColorForusername(name) {
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
    getusernameStyle(username) {
      if (username === 'username99') {
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
        color: this.getColorForusername(username)
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
<style>
.chat-section {
    padding: 20px;
    min-height: 650px;
    height: 100vh;        /* Fill the full viewport height */
    width: 100%;          /* Ensure full width */
    box-sizing: border-box; /* Ensure padding doesn't increase height */
}
.tabs {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 30px;
}
.tabs button {
  background: linear-gradient(45deg, #6a11cb, #2575fc);
  color: #fff;
  border: none;
  border-radius: 25px;
  padding: 10px 30px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s, transform 0.2s;
  box-shadow: 0 2px 8px rgba(106, 17, 203, 0.15);
  outline: none;
}
.tabs button.active {
  background: linear-gradient(45deg, #ff512f, #dd2476);
  transform: scale(1.08);
  box-shadow: 0 4px 16px rgba(255, 81, 47, 0.15);
}
.user-card-animated {
  animation: fadeInUp 0.5s;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.message-animated {
  animation: fadeIn 0.4s;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
#chat-container {
  background: rgba(255,255,255,0.04);
  border-radius: 18px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.12);
  padding: 20px 0 0 0;
}
#input-container {
  display: flex;
  align-items: center;
  padding: 18px 20px;
  background: rgba(245, 245, 245, 0.95);
  border-top: 1px solid rgba(0, 0, 0, 0.07);
  border-radius: 0 0 18px 18px;
}
#input-message {
  width: 85%;
  padding: 10px 16px;
  border: none;
  border-radius: 25px;
  background: #fff;
  box-shadow: 0 2px 3px rgba(0, 0, 0, 0.08);
  font-size: 15px;
  outline: none;
  margin-right: 10px;
}
#send-button {
  padding: 10px 18px;
  background: linear-gradient(45deg, #ff512f, #dd2476);
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 700;
  font-size: 1.1rem;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(255, 81, 47, 0.15);
}
#send-button:hover {
  transform: translateY(-2px) scale(1.08);
  box-shadow: 0 4px 16px rgba(255, 81, 47, 0.25);
}
#messages {
  padding: 18px 20px 0 20px;
  overflow-y: auto;
  max-height: 400px;
  scrollbar-width: thin;
  scrollbar-color: #888 #f0f0f0;
}
.bubble {
  background: linear-gradient(135deg, #f8fafc 60%, #e0e7ef 100%);
  margin-bottom: 12px;
  max-width: 80%;
  border-radius: 18px;
  padding: 10px 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.text-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.message-text {
  color: #222;
  word-break: break-word;
  flex: 1;
  font-size: 1.05rem;
}
#warning-message {
  color: #ff4c4c;
  font-weight: 600;
  margin-top: 10px;
  text-align: center;
}
</style>
