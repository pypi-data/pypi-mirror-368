#!/usr/bin/env python3
import os
import json
import subprocess
import shutil
from pathlib import Path
import platform
import sys
    

def main():
   
    def run_command(command, cwd=None):
        print(f"\n[Running]: {command}")
        result = subprocess.run(command, shell=True, cwd=cwd)
        if result.returncode != 0:
            print("[Error] Command failed.")
            exit(1)


    

    def check_command(cmd_names):
        for name in cmd_names:
            if not shutil.which(name):
                print(f"[Error] Required command '{name}' is not installed or not in PATH.")
                sys.exit(1)

    # Check npm
    check_command(["npm"])

    # Decide python command based on OS
    if platform.system() == "Windows":
        if shutil.which("py"):
            python_cmd = "py"
        elif shutil.which("python"):
            python_cmd = "python"
        else:
            print("[Error] Python is not installed or not in PATH.")
            sys.exit(1)
    else:
        if shutil.which("python3"):
            python_cmd = "python3"
        elif shutil.which("python"):
            python_cmd = "python"
        else:
            print("[Error] Python is not installed or not in PATH.")
            sys.exit(1)
       


    def write_file(filepath, content):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)


    project_name = input("Enter your project name: ").strip()
    if not project_name:
        print("[Error] Project name cannot be empty.")
        exit(1)

    base_path = Path.cwd() / project_name
    frontend_path = base_path

    # Step 1: Create Vite + React Project
    run_command(f"npm create vite@latest {project_name} -- --template react")

    # Step 2: Install Tailwind CSS + Plugin
    run_command("npm install tailwindcss @tailwindcss/vite", cwd=frontend_path)

    # Step 3: Create config.json
    config_json = {
        "ENV": "development",
        "development": {
            "DEBUG": True,
            "DB_NAME": "db.sqlite3",
            "DB_USER": "dev_user",
            "DB_PASS": "dev_pass",
            "DOMAIN": "localhost",
            "HOST": "localhost",
            "PORT": "5175",
            "BACKEND_PORT": "8000",
            "SECRET_KEY": "django-insecure-)l2$^ac%*f9@+d^!)j0j(5#n2ef^nn$uz&aitb$boey6+9l$jv",
            "JWT_SECRET": "dev_jwt_secret"
        },
        "production": {
            "DEBUG": False,
            "DB_NAME": "db.sqlite3",
            "DB_USER": "dev_user",
            "DB_PASS": "dev_pass",
            "DOMAIN": "thesis-tracking-system.onrender.com",
            "HOST": "thesis-tracking-system.onrender.com",
            "ALLOWED_HOSTS": ["thesis-tracking-system.onrender.com"],
            "PORT": "5175",
            "BACKEND_PORT": "8000",
            "SECRET_KEY": "django-insecure-)l2$^ac%*f9@+d^!)j0j(5#n2ef^nn$uz&aitb$boey6+9l$jv",
            "JWT_SECRET": "prod_jwt_secret",
            "DATABASE_URL": "postgresql://thesisdbuser:qLRN2ZVsysqcYtPQKi74NOigVkDcdYh0@dpg-d0hnol3uibrs73diaebg-a/thesisdb"
        }
    }
    write_file(frontend_path / "config.json", json.dumps(config_json, indent=4))

    # Step 4: Write vite.config.js
    vite_config = '''
    import { defineConfig } from "vite";
    import react from "@vitejs/plugin-react";
    import tailwindcss from '@tailwindcss/vite'
    import fs from "node:fs";
    import Path from "node:path";

    const configPath = Path.resolve("./config.json");
    const config = JSON.parse(fs.readFileSync(configPath, "utf-8"));
    const { ENV, [ENV]: { HOST, PORT } } = config;

    export default defineConfig({
    base: "/static/",
    plugins: [tailwindcss(), react()],
    server: {
        host: HOST,
        port: parseInt(PORT, 10),
        cors: true,
        origin: `http://${HOST}:${PORT}`,
        headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept",
        },
    },
    build: {
        outDir: "dist",
        publicDir: "public",
        chunkSizeWarningLimit: 26000,
        rollupOptions: {
        output: {
            manualChunks: false,
            inlineDynamicImports: true,
            entryFileNames: "[name].js",
            assetFileNames: "[name].[ext]",
        },
        },
    },
    });
    '''
    write_file(frontend_path / "vite.config.js", vite_config)

    # Step 5: Write index.css
    index_css = '''
    @import "tailwindcss";

    @font-face {
    font-family: poppinsRegular;
    src:  url("/fonts/PoppinsRegular.ttf") format('truetype')
    }
    @font-face {
    font-family: poppinsMedium;
    src: url("/fonts/PoppinsMedium.ttf") format('truetype')
    }
    @font-face {
    font-family: poppinsSemiBold;
    src:  url("/fonts/PoppinsSemiBold.ttf") format('truetype')
    }
    @font-face {
    font-family: poppinsBold;
    src:  url("/fonts/PoppinsBold.ttf") format('truetype')
    }
    @font-face {
    font-family: poppinsBlack;
    src:  url("/fonts/PoppinsBlack.ttf") format('truetype')
    }

    @theme {
    --color-custom-green: #096537;
    --color-custom-red: #e4161d;
    --font-poppinsRegular: poppinsRegular;
    --font-poppinsMedium: poppinsMedium;
    --font-poppinsSemiBold: poppinsSemiBold;
    --font-poppinsBold: poppinsBold;
    --font-poppinsBlack: poppinsBlack;
    }
    '''
    write_file(frontend_path / "src/index.css", index_css)

    # Step 5: Backend Setup (Django in same root)
    # Create virtualenv and activate
    venv_cmd = f"{python_cmd} -m venv env"
    run_command(venv_cmd, cwd=base_path)
    if os.name == 'nt':
        activate_cmd = f"{base_path / 'env/Scripts/activate'}"
    else:
        activate_cmd = f"source {base_path}/env/bin/activate"

    # Install packages
    requirements = '''asgiref==3.8.1
    dj-database-url==2.3.0
    Django==5.1.2
    django-cors-headers==4.6.0
    djangorestframework==3.15.2
    et_xmlfile==2.0.0
    gunicorn==23.0.0
    numpy==2.2.2
    openpyxl==3.1.5
    packaging==25.0
    pandas==2.2.3
    pillow==11.0.0
    psycopg2-binary==2.9.10
    python-dateutil==2.9.0.post0
    pytz==2025.1
    six==1.17.0
    sqlparse==0.5.1
    typing_extensions==4.13.2
    tzdata==2024.2
    whitenoise==6.9.0
    XlsxWriter==3.2.5
    '''
    write_file(base_path / "requirements.txt", requirements)

    # pip install
    run_command(f"{activate_cmd} && pip install -r requirements.txt", cwd=base_path)

    # Create Django project & app in root
    run_command(f"{activate_cmd} && django-admin startproject core .", cwd=base_path)
    
    if platform.system() == "Windows":
        run_command(f"{activate_cmd} && py manage.py startapp account", cwd=base_path)
    else:
        run_command(f"{activate_cmd} && {python_cmd} manage.py startapp account", cwd=base_path)

    # Overwrite core/settings.py
    settings_path = base_path / "core/settings.py"
    settings_content = '''

    from pathlib import Path
    import os
    import json
    import dj_database_url

    BASE_DIR = Path(__file__).resolve().parent.parent

    with open(BASE_DIR / "config.json") as f:
        config = json.load(f)

    ENV = config.get("ENV", "development")
    env_config = config[ENV]

    SECRET_KEY = env_config.get("SECRET_KEY", "change-me")
    DEBUG = env_config.get("DEBUG", True)
    ALLOWED_HOSTS = env_config.get("ALLOWED_HOSTS", ["*"])


    # Custom user model
    AUTH_USER_MODEL = 'account.User'

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
        'rest_framework.authtoken',
        'corsheaders',
        'whitenoise',
        'account',
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]


    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.TokenAuthentication',
        ],
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ]
    }

    ROOT_URLCONF = 'core.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [BASE_DIR / "template"],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'core.wsgi.application'

    if ENV == 'production':
        DATABASES = {
            'default': dj_database_url.parse(env_config.get("DATABASE_URL"))
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / env_config.get("DB_NAME", "db.sqlite3")
            }
        }

    AUTH_PASSWORD_VALIDATORS = [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    ]

    LANGUAGE_CODE = 'en-us'
    TIME_ZONE = 'UTC'
    USE_I18N = True
    USE_TZ = True

    STATIC_URL = '/static/'
    STATICFILES_DIRS = [ BASE_DIR / "dist" ]
    STATIC_ROOT = BASE_DIR / "static"
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / "media"

    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

    CORS_ALLOW_ALL_ORIGINS = True

    '''
    write_file(settings_path, settings_content)

    # Create urls.py
    urls_path = base_path / "core/urls.py"
    urls_content = '''
    from django.contrib import admin
    from django.urls import path, include, re_path
    from django.conf.urls.static import static
    from django.views.static import serve
    from django.conf import settings
    from .views import home

    urlpatterns = [
        # Admin route
        path('admin/', admin.site.urls),
        
        # API routes
        path('api/account/', include('account.urls', namespace='account')),
        
        # Static and media file serving
        re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
        
        # Catch-all route for React frontend - EXCLUDE API ROUTES
        re_path(r"^(?!api/).*$", home),  # CHANGED: Added negative lookahead
    ]

    # Add media file serving in development mode
    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    '''
    write_file(urls_path, urls_content)

    # Create urls.views.py
    views_path = base_path / "core/views.py"
    views_content = '''
    from django.shortcuts import render
    from django.conf import settings
    import json
    from pathlib import Path
    import logging

    logger = logging.getLogger(__name__)

    def home(request):
        # Resolve the path to config.json
        config_path = Path(settings.BASE_DIR) / "config.json"
        try:
            with open(config_path) as config_file:
                config_data = json.load(config_file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Error loading config.json: {e}")

        # Get the current environment
        env = config_data.get("ENV", "development")
        env_config = config_data.get(env, {})

        # Log the active environment
        logger.info(f"Running in {env} environment with host {env_config.get('HOST')} and port {env_config.get('PORT')}")

        # Pass environment-specific values to the template
        context = {
            "debug": settings.DEBUG,
            "host": env_config.get("HOST", "127.0.0.1"),
            "port": env_config.get("PORT", "8000"),
        }
        return render(request, "base.html", context)
    '''
    write_file(views_path, views_content)


    # Create base.html in template folder
    template_path = base_path / "template/base.html"
    base_html = '''{% load static %}
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="icon" type="image/svg+xml" href="{% static '/images/logo.png' %}" />
        <title>YOUR PROJECT NAME HERE</title>
        {% if debug %}
        <script type="module" src="http://{{host}}:{{port}}/static/@vite/client"></script>
        <script type="module">
        import RefreshRuntime from "http://{{host}}:{{port}}/static/@react-refresh";
        RefreshRuntime.injectIntoGlobalHook(window),
            (window.$RefreshReg$ = () => {});
        window.$RefreshSig$ = () => (type) => type;
        window.__vite_plugin_react_preamble_installed__ = true;
        </script>
        <script type="module" src="http://{{host}}:{{port}}/static/src/main.jsx"></script>
        {% else %}
        <script type="module" crossorigin src="{% static 'index.js' %}"></script>
        <link rel="stylesheet" href="{% static 'index.css' %}" />
        {% endif %}
    </head>
    <body>
        <div id="root"></div>
    </body>
    </html>
    '''
    write_file(template_path, base_html)

    print("\n✅ Project scaffold completed with backend in root directory and fully connected to React build.")

if __name__ == "__main__":
    main()
