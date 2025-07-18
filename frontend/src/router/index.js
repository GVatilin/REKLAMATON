import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Welcome',
    component: () => import('../pages/start/index.vue')
  },
  {
    path: '/login',
    name: 'Login Page',
    component: () => import('../pages/login/LoginIndex.vue'),
    meta: { isLogin: true }
  },
  {
    path: '/registration',
    name: 'Registration',
    component: () => import('../pages/login/LoginIndex.vue'),
    meta: { isLogin: false }
  },
  {
    path: '/debug',
    name: 'Debug',
    component: () => import('../pages/debug/index.vue')
  },
  {
    path: '/404',
    name: '404',
    component: () => import('../pages/error404/index.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router