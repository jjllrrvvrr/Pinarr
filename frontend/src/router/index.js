import { createRouter, createWebHistory } from 'vue-router'
import BottleList from '../views/BottleList.vue'
import BottleDetail from '../views/BottleDetail.vue'
import AddBottle from '../views/AddBottle.vue'
import MapView from '../views/MapView.vue'
import RegionView from '../views/RegionView.vue'
import CaveList from '../views/CaveList.vue'
import CaveEdit from '../views/CaveEdit.vue'
import CaveView from '../views/CaveView.vue'
import LoginView from '../views/LoginView.vue'
import { authGuard, publicGuard } from './guards'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      beforeEnter: publicGuard
    },
    {
      path: '/',
      name: 'home',
      component: BottleList
    },
    {
      path: '/add',
      name: 'add-bottle',
      component: AddBottle
    },
    {
      path: '/edit/:id',
      name: 'edit-bottle',
      component: AddBottle
    },
    {
      path: '/wine/:id',
      name: 'wine-detail',
      component: BottleDetail
    },
    {
      path: '/map',
      name: 'map',
      component: MapView
    },
    {
      path: '/region/:region',
      name: 'region',
      component: RegionView
    },
    {
      path: '/tags/:tag',
      name: 'tag-filter',
      component: BottleList
    },
    {
      path: '/caves',
      name: 'caves',
      component: CaveList
    },
    {
      path: '/caves/new',
      name: 'cave-new',
      component: CaveEdit
    },
    {
      path: '/caves/:id',
      name: 'cave-view',
      component: CaveView
    },
    {
      path: '/caves/:id/edit',
      name: 'cave-edit',
      component: CaveEdit
    }
  ],
})

// Guard global pour protéger toutes les routes
router.beforeEach(authGuard)

export default router