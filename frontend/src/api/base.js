export const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export async function request(path, options = {}) {
  const token = localStorage.getItem('hms_token')
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {})
    },
    ...options
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.message || 'Request failed')
  return data
}

export async function requestFile(path, options = {}) {
  const token = localStorage.getItem('hms_token')
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {})
    },
    ...options
  })

  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.message || 'Request failed')
  }

  const blob = await res.blob()
  const disposition = res.headers.get('Content-Disposition') || ''
  const match = /filename=([^;]+)/i.exec(disposition)
  const filename = match ? match[1].replace(/"/g, '') : 'download'
  return { blob, filename }
}
