import { createRouter, createWebHistory } from 'vue-router';

import Posts from '../Posts.vue';
import Search2 from '../Search2.vue';
import Chat from '../Chat.vue';
import Chatbox from '../Chatbox.vue'; // One-on-one chat
import Settings from '../Settings.vue';
import Videos from '../Videos.vue';
import Viewer from '../Viewer.vue';

const routes = [
  {
    path: '/',
    name: 'Posts',
    component: Posts
  },
  {
    path: '/posts',
    name: 'PostsPage',
    component: Posts
  },
  {
    path: '/videos',
    name: 'Videos',
    component: Videos
  },
  {
    path: '/user/:username',
    name: 'UserProfile',
    component: Search2,
    props: true
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat
  },
  {
    path: '/chatbox/:userId/:username',
    name: 'Chatbox',
    component: Chatbox,
    props: true
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  },
  {
    path: '/viewer',
    name: 'Viewer',
    component: Viewer
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
