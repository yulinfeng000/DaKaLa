export const setKV = (key, value) => {
  localStorage.setItem(key, value)
}

export function getKV(key) {
  return localStorage.getItem(key)
}

export const setItem = (key, value, ttl) => {
  let expire = undefined
  if (ttl) expire = new Date().getTime() + ttl

  localStorage.setItem(key, JSON.stringify({ value, expire }))
}

export function getItem(key) {
  const res = localStorage.getItem(key)
  if (res) {
    let v = JSON.parse(res)
    if (v.expire && Number.isFinite(v.expire)) {
      const now = new Date().getTime()
      if (now - v.expire < 0) return v.value
      else {
        removeItem(key)
        return null
      }
    } else return v.value
  }
  return null
}

export const removeItem = (key) => {
  localStorage.removeItem(key)
}
