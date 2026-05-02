import axios from 'axios'
import { useRuntimeConfig } from '#app'

export const useApi = () => {
  const { token } = useAuth()
  const config = useRuntimeConfig()

  return axios.create({
    baseURL: config.public.baseURL,
    headers: {
      Authorization: `${token.value}`
    }
  })
}
