<script setup>

const { token, signIn, getSession } = useAuth()
const { setToken } = useAuthState()

const email = ref('')
const name = ref('')
const password = ref('')
const phone_number = ref('')
const cpf_or_cnpj = ref('')
const birthday = ref('')
const user_data = ref(await getSession())

const isLoginMode = ref(true)
const errorMessage = ref('')

async function login() {
  errorMessage.value = ''
  try {
    const result = await signIn(
      {
        email: email.value,
        password: password.value
      },
      { redirect: false }
    )

    if (!result || result.error) {
      errorMessage.value = 'E-mail ou senha incorretos!'
      console.log('Erro retornado pelo Auth:', result?.error)
    } else {
      console.log('Login efetuado com sucesso!')
      user_data.value = await getSession()
    }

  } catch (error) {
    console.error('Erro crítico no catch:', error)
    errorMessage.value = 'Falha na conexão com o servidor.'
  }
}

async function handleLogon() {
  errorMessage.value = ''
  try {
    await $fetch('/api/user/logon', {
      method: 'POST',
      body: {
        name: name.value,
        email: email.value,
        password: password.value,
        phone_number: phone_number.value,
        cpf_or_cnpj: cpf_or_cnpj.value,
        birthday: birthday.value,
        roles: ["CLIENT"]
      }
    })

    alert('Conta criada com sucesso! Faça o seu login.')
    isLoginMode.value = true
  } catch (error) {
    console.error(error)
    errorMessage.value = 'Erro ao criar conta. Tente novamente.'
  }
}
</script>

<template>

  <div class="d-flex flex-column min-vh-100">
    <nav class="navbar
                navbar-dark
                header-cacau
                shadow-sm">
      <div class="container">
        <span class="navbar-brand
        fw-bold">Conexão Cacau</span>
      </div>
    </nav>

    <main class="flex-grow-1
                d-flex flex-column
                align-items-center
                justify-content-center
                p-3">

      <div class="card shadow border-0 p-4 mb-4"
                  style="width: 100%;
                  max-width: 400px;
                  border-radius: 12px;">
        <h3 class="text-center fw-bold mb-3">
          {{ isLoginMode ? 'Entrar' : 'Cadastrar' }}
        </h3>

        <div v-if="errorMessage" class="alert alert-danger py-2 small fw-bold mb-3 text-center text-danger" role="alert">
        {{ errorMessage }}
        </div>

        <form @submit.prevent="isLoginMode ? login() : handleLogon()">

          <div v-if="!isLoginMode">
            <div class="mb-3">
              <label class="form-label
                            small
                            fw-bold
                            text-muted">
                            Nome Completo</label>
              <input v-model="name" type="text"
                     class="form-control"
                     placeholder="Nome" required />
            </div>

            <div class="mb-3">
              <label class="form-label small
                            fw-bold
                            text-muted">
                            Telefone</label>
              <input v-model="phone_number" type="text"
                     class="form-control"
                     placeholder="Telefone" required />
            </div>

            <div class="mb-3">
             <label class="form-label small 
                           fw-bold 
                           text-muted">
                           CPF ou CNPJ</label>
             <input v-model="cpf_or_cnpj" type="text" class="form-control" placeholder="01234567899" required />
            </div>

            <div class="mb-3">
              <label class="form-label small 
                            fw-bold 
                            text-muted">
                            Data de Nascimento</label>
              <input v-model="birthday" type="date" class="form-control" required />
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label small fw-bold text-muted">E-mail</label>
            <input v-model="email" type="email"
                   class="form-control"
                   placeholder="seuemail@exemplo.com" required />
          </div>

          <div class="mb-4">
            <label class="form-label small fw-bold text-muted">Senha</label>
            <input v-model="password" type="password" class="form-control" placeholder="Senha" required />
          </div>

          <button type="submit" class="btn btn-cacau w-100 fw-bold py-2 shadow-sm">
            {{ isLoginMode ? 'Entrar' : 'Criar Conta' }}
          </button>

          <div class="text-center mt-3">
            <span @click="isLoginMode = !isLoginMode" class="text-decoration-underline text-secondary small style-toggle">
              {{ isLoginMode ? 'Não tem conta? Cadastre-se!' : 'Já tem conta? Faça Login' }}
            </span>
          </div>
        </form>

      </div>
      <div v-if="user_data" class="card shadow-sm border-0 p-3 text-start"
                            style="width: 100%;
                            max-width: 400px;
                            border-radius: 12px;">
        <h6 class="fw-bold text-muted mb-2 small">Sessão Ativa (user_data):</h6>
        <pre class="bg-light p-2 rounded text-dark small mb-0" style="white-space: pre-wrap;">{{ user_data }}</pre>
      </div>
    </main>
  </div>

</template>

<style scoped>

.style-toggle {
  cursor: pointer;
}

.alert-custom {
  color: #721c24 !important;
  -webkit-text-fill-color: #721c24 !important;
}

</style>