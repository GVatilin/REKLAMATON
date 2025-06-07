import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Welcome',
    component: () => import('../pages/start/index.vue')
  },
  {
    path: '/schedule',
    name: 'Schedule Page',
    component: () => import('../pages/schedule/ScheduleIndex.vue')
  },
  {
    path: '/deadlines',
    name: 'Deadlines Page',
    component: () => import('../pages/deadlines/index.vue')
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
    path: '/login',
    name: 'Login',
    component: () => import('../pages/login/LoginIndex.vue'),
    meta: { isLogin: true }
  },
  {
    path: '/profile',
    name: 'Profile Page',
    component: () => import('../pages/profile/index.vue')
  },
  {
    path: '/settings',
    name: 'Settings Page',
    component: () => import('../pages/settings/index.vue')
  },
  {
    path: '/payment',
    name: 'Payment Page',
    component: () => import('../pages/payment/index.vue')
  },
  {
    path: '/debug',
    name: 'Debug',
    component: () => import('../pages/debug/index.vue')
  },
  {
    path: '/auth/google/callback',
    name: 'Google Auth',
    component: () => import('../pages/google_redirect/index.vue')
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