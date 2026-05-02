<script setup>
const name = ref('test')

const api = useApi()

console.log(api)

import { computedAsync } from '@vueuse/core'

const response = computedAsync(async () => {
  const resp = await api.get('/user/search', {params: {name: name.value}})
  return resp.data
})

</script>

<template>
<HelloWorld />
<input v-model=name />
resp: {{ response }}
</template>

<style scoped>
</style>
