import './Footer.css'

function Footer({ personal }) {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="footer">
      <div className="container footer-content">
        <div className="footer-section">
          <h3 className="footer-title">{personal?.name || 'Your Name'}</h3>
          <p className="footer-subtitle">{personal?.title || 'AI/ML Engineer'}</p>
        </div>

        <div className="footer-section">
          <h4 className="footer-heading">Connect</h4>
          <div className="footer-links">
            {personal?.github && (
              <a href={personal.github} target="_blank" rel="noopener noreferrer" className="footer-link">
                GitHub
              </a>
            )}
            {personal?.linkedin && (
              <a href={personal.linkedin} target="_blank" rel="noopener noreferrer" className="footer-link">
                LinkedIn
              </a>
            )}
            {personal?.email && (
              <a href={`mailto:${personal.email}`} className="footer-link">
                Email
              </a>
            )}
          </div>
        </div>

        <div className="footer-section">
          <h4 className="footer-heading">Quick Links</h4>
          <div className="footer-links">
            <button onClick={() => document.getElementById('about').scrollIntoView({ behavior: 'smooth' })} className="footer-link-btn">
              About
            </button>
            <button onClick={() => document.getElementById('projects').scrollIntoView({ behavior: 'smooth' })} className="footer-link-btn">
              Projects
            </button>
            <button onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} className="footer-link-btn">
              Back to Top
            </button>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <div className="container">
          <p className="copyright">
            © {currentYear} {personal?.name || 'Your Name'}. Built with React & passion for AI/ML.
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
