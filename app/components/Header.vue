<script setup>
  const { getSession, status } = useAuth()
  const api = useApi()

  import { computedAsync } from '@vueuse/core'

  const user_name = computedAsync(async () => {
    const session = await getSession()
    const resp = await api.get(`user/${ session.id }`)
    return resp.data.name
  })
  
  const isLoggedIn = computed(() => status.value === 'authenticated')
</script>

<template>
  <header>
    <div v-if="isLoggedIn">
      logged in as {{ user_name }}
    </div>
    <NuxtLink to="/login">login</NuxtLink>
  </header>
</template>
