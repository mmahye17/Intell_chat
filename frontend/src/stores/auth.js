import { reactive } from 'vue'

export const authStore = reactive({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('token') || '',

  setAuth(user, token) {
    this.user = user
    this.token = token
    localStorage.setItem('user', JSON.stringify(user))
    localStorage.setItem('token', token)
  },

  clearAuth() {
    this.user = null
    this.token = ''
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  },

  isLoggedIn() {
    return !!this.token
  },
})
