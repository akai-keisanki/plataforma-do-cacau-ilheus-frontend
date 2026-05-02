<script setup>
  const { token, signIn, getSession } = useAuth()
  const { setToken }= useAuthState()

  const email = ref('email')
  const password = ref('password')
  const user_data = ref(await getSession())

  async function login() {
    await signIn(
      {
        email: email.value,
        password: password.value
      },
      { redirect: false }
    )

    console.log('logged in')

    user_data.value = await getSession()
  }
</script>

<template>
  <input type=email v-model=email />
  <input type=password v-model=password />
  <button @click=login()>login</button>

  {{ user_data }}
</template>

<style scoped>
</style>
