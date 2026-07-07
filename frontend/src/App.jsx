import { useState, useEffect } from 'react'
import URLList from './components/URLList'
import AddURLForm from './components/AddURLForm'

const API_BASE = '/api'

function App() {
  const [urls, setUrls] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchUrls = async () => {
    try {
      const res = await fetch(`${API_BASE}/urls`)
      const data = await res.json()
      setUrls(data)
    } catch (err) {
      console.error('Failed to fetch URLs:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUrls()
    const interval = setInterval(fetchUrls, 15000)
    return () => clearInterval(interval)
  }, [])

  const handleAdd = async (url, name) => {
    const res = await fetch(`${API_BASE}/urls`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, name: name || null }),
    })
    if (res.ok) {
      fetchUrls()
    }
  }

  const handleDelete = async (id) => {
    const res = await fetch(`${API_BASE}/urls/${id}`, { method: 'DELETE' })
    if (res.ok) {
      fetchUrls()
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-center mb-8">Uptime Monitor</h1>
        <AddURLForm onAdd={handleAdd} />
        {loading ? (
          <p className="text-center text-gray-400 mt-8">Loading...</p>
        ) : (
          <URLList urls={urls} onDelete={handleDelete} />
        )}
      </div>
    </div>
  )
}

export default App
