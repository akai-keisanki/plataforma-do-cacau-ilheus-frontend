// https://nuxt.com/docs/api/configuration/nuxt-config

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: [
    '@nuxt/eslint',
    '@sidebase/nuxt-auth'
  ],
  runtimeConfig: {
    public: {
      baseURL: '/api'
    }
  },
  auth: {
    isEnabled: true,
    baseURL: '/api',
    provider: {
      type: 'local',
      endpoints: {
        signIn: { path: '/user/login', method: 'post' },
        getSession: { path: '/user/', method: 'get' }
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
  css: ['@/assets/styles/global.css'],
  routeRules: {
    '/api/**': { 
      proxy: 'http://127.0.0.1:5000/**',
    },
  }
})
