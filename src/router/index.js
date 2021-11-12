import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import MatchLoadouts from '../views/MatchLoadouts.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/matchLoadouts',
    name: 'MatchLoadouts',
    component: MatchLoadouts
  },
  {
    path: '/github',
    redirect: 'https://github.com/isaacKenyon/VALORANT-rank-yoinker'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
