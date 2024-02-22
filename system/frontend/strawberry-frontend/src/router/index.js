import { createRouter, createWebHistory } from 'vue-router'
import IndexView from '../views/Index.vue'
import LoginView from '../views/Login.vue'
import Upload from '../components/Upload.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      meta: { title: '登录' },
      component: LoginView
    },
    {
      path: '/login',
      redirect: '/',
    },
    {
      path: '/index',
      meta: { title: '首页' },
      component: IndexView,
      children: [
        {
          path: 'imageshow',
          meta: { title: '图片展示' },
          component: () => import('../views/ImageShow.vue')
        },
        {
          path: 'record',
          meta: { title: '记录' },
          component: () => import('../views/Record.vue')
        },
      ]
    },

  ]
})

export default router
