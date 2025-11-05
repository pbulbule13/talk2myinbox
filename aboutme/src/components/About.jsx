import { useState } from 'react'
import './About.css'

function About({ about }) {
  const [isExpanded, setIsExpanded] = useState(true)

  const getIcon = (iconName) => {
    const icons = {
      brain: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"></path>
          <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"></path>
        </svg>
      ),
      code: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="16 18 22 12 16 6"></polyline>
          <polyline points="8 6 2 12 8 18"></polyline>
        </svg>
      ),
      'trending-up': (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
          <polyline points="17 6 23 6 23 12"></polyline>
        </svg>
      )
    }
    return icons[iconName] || icons.code
  }

  return (
    <section id="about" className="about">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">{about?.title || 'About Me'}</h2>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="collapse-btn"
            aria-label={isExpanded ? 'Collapse section' : 'Expand section'}
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className={`collapse-icon ${isExpanded ? 'expanded' : ''}`}
            >
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
        </div>

        {isExpanded && (
          <div className="about-content slide-down">
            <div className="about-description">
              <p>{about?.description}</p>
            </div>

            {about?.highlights && about.highlights.length > 0 && (
              <div className="highlights-grid">
                {about.highlights.map((highlight, index) => (
                  <div key={index} className="highlight-card">
                    <div className="highlight-icon">
                      {getIcon(highlight.icon)}
                    </div>
                    <h3 className="highlight-title">{highlight.title}</h3>
                    <p className="highlight-description">{highlight.description}</p>
                  </div>
                ))}
              </div>
            )}

            {about?.skills && about.skills.length > 0 && (
              <div className="skills-section">
                <h3 className="skills-title">Key Skills & Technologies</h3>
                <div className="skills-grid">
                  {about.skills.map((skill, index) => (
                    <div key={index} className="skill-tag">
                      {skill}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  )
}

export default About
