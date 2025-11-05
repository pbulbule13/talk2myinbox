import { useState, useEffect } from 'react'
import Header from './components/Header'
import Hero from './components/Hero'
import About from './components/About'
import Projects from './components/Projects'
import Footer from './components/Footer'
import './App.css'

function App() {
  const [config, setConfig] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/aboutme/config.json')
      .then(response => response.json())
      .then(data => {
        setConfig(data)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error loading config:', error)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading portfolio...</p>
      </div>
    )
  }

  if (!config) {
    return (
      <div className="error-container">
        <p>Error loading configuration. Please check config.json file.</p>
      </div>
    )
  }

  return (
    <div className="App">
      <Header personal={config.personal} />
      <main>
        <Hero personal={config.personal} />
        <About about={config.about} />
        <Projects projects={config.projects} />
      </main>
      <Footer personal={config.personal} />
    </div>
  )
}

export default App
