import { useState } from 'react'
import './Projects.css'

function ProjectCard({ project }) {
  return (
    <div className="project-card">
      <div className="project-header">
        <h4 className="project-name">{project.name}</h4>
        <div className="project-links">
          {project.githubUrl && (
            <a
              href={project.githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="project-link"
              title="View on GitHub"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
            </a>
          )}
          {project.liveUrl && (
            <a
              href={project.liveUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="project-link"
              title="View Live Demo"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                <polyline points="15 3 21 3 21 9"></polyline>
                <line x1="10" y1="14" x2="21" y2="3"></line>
              </svg>
            </a>
          )}
        </div>
      </div>

      <p className="project-description">{project.description}</p>

      {project.technologies && project.technologies.length > 0 && (
        <div className="project-tech">
          {project.technologies.map((tech, index) => (
            <span key={index} className="tech-badge">{tech}</span>
          ))}
        </div>
      )}

      {project.highlights && project.highlights.length > 0 && (
        <ul className="project-highlights">
          {project.highlights.map((highlight, index) => (
            <li key={index}>{highlight}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

function ProjectCategory({ category }) {
  const [isExpanded, setIsExpanded] = useState(true)

  return (
    <div className="project-category">
      <div className="category-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div>
          <h3 className="category-title">{category.name}</h3>
          <p className="category-description">{category.description}</p>
        </div>
        <button
          className="category-toggle"
          aria-label={isExpanded ? 'Collapse category' : 'Expand category'}
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className={`toggle-icon ${isExpanded ? 'expanded' : ''}`}
          >
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
      </div>

      {isExpanded && (
        <div className="projects-grid slide-down">
          {category.projects && category.projects.length > 0 ? (
            category.projects.map((project, index) => (
              <ProjectCard key={index} project={project} />
            ))
          ) : (
            <p className="no-projects">No projects yet in this category.</p>
          )}
        </div>
      )}
    </div>
  )
}

function Projects({ projects }) {
  const [mainExpanded, setMainExpanded] = useState(true)

  return (
    <section id="projects" className="projects">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Projects</h2>
          <button
            onClick={() => setMainExpanded(!mainExpanded)}
            className="collapse-btn"
            aria-label={mainExpanded ? 'Collapse section' : 'Expand section'}
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className={`collapse-icon ${mainExpanded ? 'expanded' : ''}`}
            >
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
        </div>

        {mainExpanded && (
          <div className="projects-content slide-down">
            {projects?.categories && projects.categories.length > 0 ? (
              <div className="categories-container">
                {projects.categories.map((category, index) => (
                  <ProjectCategory key={category.id || index} category={category} />
                ))}
              </div>
            ) : (
              <p className="no-projects">No project categories configured yet.</p>
            )}
          </div>
        )}
      </div>
    </section>
  )
}

export default Projects
