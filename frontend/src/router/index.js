import { createRouter, createWebHistory } from 'vue-router';
import Posts from '../Posts.vue';
import Search2 from '../Search2.vue';

const routes = [
  { path: '/', name: 'Posts', component: Posts },
  { path: '/user/:username', name: 'UserProfile', component: Search2, props: true }, // <-- this is critical
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

