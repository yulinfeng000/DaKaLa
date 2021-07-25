import axios from "axios"
import cookies from "../cookies"
import https from "https"

const BASE_URL = process.env.REACT_APP_BASE_URL
  ? process.env.REACT_APP_BASE_URL
  : undefined

const Axios = axios.create({
  baseURL: BASE_URL,
  httpsAgent: new https.Agent({
    rejectUnauthorized: false,
  }),
})

//request interceptor
Axios.interceptors.request.use((config) => {
  const token = cookies.get("token")
  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`
  }
  return config
})

//response interceptor
Axios.interceptors.response.use((resp) => {
  if (resp.headers["content-type"] === "application/json") {
    if (resp.status !== 200 || resp.data.code !== 200)
      return Promise.reject(resp.data)

    return resp.data
  }
  return resp
})

export default Axios
