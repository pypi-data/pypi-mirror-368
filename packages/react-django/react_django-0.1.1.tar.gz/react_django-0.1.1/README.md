# Full-Stack Django + Vite + React + TailwindCSS Scaffold

- **Start Project:**
  - Creating it Globally for Windows ----> 
    - py -m pip install react-django

  - Creating it Globally for Linux/macOS: ----> 
    - python3 -m pip install react-django


  - run this in your terminal
   - react_django


  

This project is a **one-command scaffold** for creating a fully integrated **Django backend** and **Vite + React + TailwindCSS frontend** inside a single repository.  
It automatically configures **development** and **production** environments, including database settings, static files, and environment-based React/Django integration.

---

## 📦 Features

- **Frontend:**
  - [Vite](https://vitejs.dev/) with [React](https://reactjs.org/)
  - [TailwindCSS](https://tailwindcss.com/) styling
  - Auto-generated `vite.config.js` and `index.css`
  - Environment-aware server settings from `config.json`
  - Fonts and theme variables preconfigured

- **Backend:**
  - [Django](https://www.djangoproject.com/) REST API
  - [Django REST Framework](https://www.django-rest-framework.org/)
  - CORS support via `django-cors-headers`
  - Token-based authentication
  - Whitenoise for static file serving
  - Environment-aware settings from `config.json`
  - SQLite (dev) / PostgreSQL (production)

- **Extras:**
  - Single root directory for both frontend and backend
  - Auto-creation of `config.json` for easy environment switching
  - Django templates configured to serve Vite in dev and built static files in production

---

## 🛠 Requirements

Before running the script, make sure you have:

- **Python 3.8+**  
- **Node.js 18+ & npm**  
- **pip** (comes with Python)  
- **PostgreSQL** (only needed in production)

---

## 🚀 Usage

### 1️⃣ Clone or Download
```bash
git clone https://github.com/ISAAC-EDZORDZI-FIAVOR/Django_React_Template
cd yourrepo


After running the script, you'll get a structure like:

    your-project/
    │── account/                  # Django app
    │── core/                     # Django project
    │── dist/                     # Built React files (production)
    │── env/                      # Python virtual environment
    │── media/                    # User-uploaded files
    │── node_modules/             # Frontend dependencies
    │── src/                      # React source code
    │── static/                   # Django static files (collected)
    │── template/                 # Django templates
    │── config.json               # Environment configuration
    │── requirements.txt          # Python dependencies
    │── vite.config.js            # Vite config linked to config.json
    │── manage.py
    │── package.json
    │── index.css
