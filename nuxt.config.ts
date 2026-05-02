// https://nuxt.com/docs/api/configuration/nuxt-config

const API_URL = 'http://localhost:5000'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: [
    '@nuxt/eslint',
    '@sidebase/nuxt-auth'
  ],
  runtimeConfig: {
    public: {
      baseURL: API_URL
    }
  },
  auth: {
    isEnabled: true,
    baseURL: API_URL,
    provider: {
      type: 'local',
      endpoints: {
        signIn: { path: '/user/login', method: 'post' },
        getSession: { path: '/user', method: 'get' }
      },
      pages: {
        login: '/login'
      },
      token: {
        signInResponseTokenPointer: '/access_token',
        type: 'Bearer',
        headerName: 'Authorization',
        maxAgeInSeconds: 60 * 60 * 24
      }
    }
  },
  components: {
    dirs: [
      {
        path: '~/components/global',
        global: true
      },
      "~/components"
    ]
  },
  css: ['@/assets/styles/global.css']
})
