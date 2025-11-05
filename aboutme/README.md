# AI/ML Engineer Portfolio

A beautiful, production-grade portfolio application showcasing AI/ML engineering projects and expertise. Built with React, featuring a clean, professional design with collapsible sections and full configurability.

## Features

- **Single-page application** with smooth scrolling navigation
- **Collapsible sections** for better content organization
- **Fully configurable** via JSON - no code changes needed
- **Project categorization** (Machine Learning, Artificial Intelligence, etc.)
- **Responsive design** that works on all devices
- **Light, professional color scheme** with beautiful gradients
- **GitHub & Live URL links** for each project
- **Easy deployment** to GitHub Pages

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Your Content

Edit the `public/config.json` file to add your personal information, projects, and details:

```json
{
  "personal": {
    "name": "Your Name",
    "title": "Seasonal AI/ML Engineer",
    "photo": "/path-to-your-photo.jpg",
    "email": "your.email@example.com",
    "linkedin": "https://linkedin.com/in/yourprofile",
    "github": "https://github.com/yourusername"
  },
  "about": { ... },
  "projects": { ... }
}
```

### 3. Add Your Photo

Place your photo in the `public` folder and update the path in `config.json`:

```json
"photo": "/your-photo.jpg"
```

### 4. Run Development Server

```bash
npm run dev
```

Visit `http://localhost:5173` to see your portfolio.

### 5. Build for Production

```bash
npm run build
```

## How to Update Your Portfolio

### Adding a New Project

1. Open `public/config.json`
2. Find the appropriate category (`machine-learning` or `artificial-intelligence`)
3. Add a new project object:

```json
{
  "name": "Your Project Name",
  "description": "Brief description of the project",
  "technologies": ["Python", "TensorFlow", "FastAPI"],
  "githubUrl": "https://github.com/yourusername/project",
  "liveUrl": "https://your-demo.com",
  "highlights": [
    "Key achievement 1",
    "Key achievement 2",
    "Key achievement 3"
  ]
}
```

### Adding a New Category

To add a new project category (e.g., "Data Engineering"):

```json
{
  "id": "data-engineering",
  "name": "Data Engineering",
  "description": "Data pipeline and infrastructure projects",
  "projects": [...]
}
```

### Updating About Me Section

Edit the `about` section in `config.json`:

```json
"about": {
  "title": "About Me",
  "description": "Your bio...",
  "skills": ["Skill 1", "Skill 2", ...],
  "highlights": [...]
}
```

### Updating Personal Information

Edit the `personal` section:

```json
"personal": {
  "name": "Your Name",
  "title": "Your Title",
  "photo": "/your-photo.jpg",
  "email": "email@example.com",
  "linkedin": "https://linkedin.com/in/profile",
  "github": "https://github.com/username"
}
```

## Deployment

### GitHub Pages (Automatic)

This portfolio is configured to automatically deploy to GitHub Pages when you push to the `main` or `develop` branch.

#### Setup:

1. Go to your GitHub repository settings
2. Navigate to **Pages** section
3. Under **Source**, select **GitHub Actions**
4. Push your code to trigger deployment

```bash
git add .
git commit -m "Initial portfolio setup"
git push origin main
```

Your portfolio will be available at: `https://yourusername.github.io/aboutme/`

### Manual Deployment

```bash
npm run deploy
```

## Updating from Any Project

You can update this portfolio from any other GitHub project by:

1. **Cloning this repository**:
   ```bash
   git clone https://github.com/pbulbule13/aboutme.git
   cd aboutme
   ```

2. **Making your changes** to `public/config.json`

3. **Committing and pushing**:
   ```bash
   git add public/config.json
   git commit -m "Update project information"
   git push
   ```

4. **Or use GitHub's web interface**:
   - Navigate to `public/config.json` on GitHub
   - Click the "Edit" (pencil) icon
   - Make your changes
   - Commit directly to the repository

## Configuration Reference

### Personal Section
- `name`: Your full name
- `title`: Your professional title
- `photo`: Path to your profile photo
- `email`: Your email address
- `linkedin`: LinkedIn profile URL
- `github`: GitHub profile URL

### About Section
- `title`: Section title
- `description`: Your bio/description
- `skills`: Array of your key skills
- `highlights`: Array of highlight objects with `icon`, `title`, and `description`

### Projects Section
- `categories`: Array of project categories
  - Each category has: `id`, `name`, `description`, and `projects` array
  - Each project has: `name`, `description`, `technologies`, `githubUrl`, `liveUrl`, `highlights`

## Technology Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **CSS3** - Styling with custom properties
- **GitHub Pages** - Hosting
- **GitHub Actions** - CI/CD

## Project Structure

```
aboutme/
├── public/
│   └── config.json          # Your portfolio data
├── src/
│   ├── components/
│   │   ├── Header.jsx       # Navigation header
│   │   ├── Hero.jsx         # Hero section with photo
│   │   ├── About.jsx        # About me section
│   │   ├── Projects.jsx     # Projects showcase
│   │   └── Footer.jsx       # Footer
│   ├── App.jsx              # Main app component
│   ├── main.jsx             # Entry point
│   └── index.css            # Global styles
├── .github/
│   └── workflows/
│       └── deploy.yml       # GitHub Pages deployment
└── package.json
```

## Tips

1. **Keep descriptions concise** - Users can expand sections to see more details
2. **Use high-quality images** - Your photo should be at least 400x400px
3. **Update regularly** - Keep your projects and information current
4. **Test locally** - Always run `npm run dev` to preview changes before pushing
5. **Commit often** - Make small, incremental updates with clear commit messages

## Support

If you encounter any issues:
- Check that `config.json` is valid JSON
- Ensure all URLs are properly formatted
- Verify that your photo path is correct
- Check the browser console for errors

## License

Feel free to use this portfolio template for your personal use.

---

Built with React and passion for AI/ML
