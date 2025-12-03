🎵 FastAPI Spotify Manager API

![alt text](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white) ![alt text](https://img.shields.io/badge/FastAPI-0.109%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)

![alt text](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white) ![alt text](https://img.shields.io/badge/Tests-Pytest-yellow?style=for-the-badge)

Una API RESTful moderna y asíncrona construida con FastAPI que actúa como intermediario inteligente entre tus usuarios y la API de Spotify. Permite gestionar perfiles de usuarios locales, autenticarse vía OAuth2 con Spotify, buscar música y gestionar favoritos y seguidos en tiempo real.

🚀 Características Principales

Gestión de Usuarios (CRUD): Creación, lectura, actualización y borrado de usuarios con validaciones estrictas (edad, formato de nombres, etc.).
Integración Spotify OAuth2: Flujo completo de autenticación (Authorization Code Flow) para actuar en nombre del usuario.
Búsqueda Asíncrona: Consultas de Artistas y Canciones utilizando httpx para alto rendimiento.
Favoritos: Guardado de Artistas y Canciones favoritas en el perfil del usuario (con persistencia de metadatos de Spotify).
Funcionalidad Social: Endpoint para Seguir (Follow) artistas o usuarios en Spotify y verificar el estado de seguimiento.
Arquitectura Limpia: Separación por Capas (Routes, Services, Models, Auth).
Manejo de Errores Robusto: Respuestas HTTP estandarizadas y mensajes de error descriptivos.

🛠️ Stack Tecnológico

Framework: FastAPI
Validación de Datos: Pydantic V2
Cliente HTTP: Httpx (Async)
Testing: Pytest & Unittest Mock
Config: Pydantic Settings (.env)

📦 Estructura del Proyecto

El proyecto sigue una arquitectura modular para facilitar la escalabilidad:
code
Bash
.
├── app
│   ├── database       # Base de datos en memoria (Fake DB)
│   ├── models         # Modelos de datos y esquemas Pydantic
│   ├── routes         # Endpoints de la API (Controllers)
│   ├── services       # Lógica de negocio
│   ├── spotify        # Cliente de bajo nivel y Autenticación
│   ├── errors.py      # Excepciones personalizadas
│   └── settings.py    # Configuración de entorno
├── tests              # Tests unitarios y de integración
├── .env               # Variables de entorno (No subir al repo)
├── .gitignore
├── main.py            # Punto de entrada de la aplicación
└── README.md

⚙️ Instalación y Configuración

1. Prerrequisitos
Python 3.10 o superior.
Una cuenta de Spotify for Developers.

2. Clonar el repositorio

git clone https://github.com/tu-usuario/ApiRest_JC.git
cd ApiRest_JC

3. Crear entorno virtual

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

4. Instalar dependencias
pip install fastapi uvicorn[standard] httpx pydantic-settings pytest pytest-asyncio

5. Configurar Spotify Dashboard
Ve a tu Dashboard de Spotify y crea una App.
Obtén el Client ID y Client Secret.
En "Edit Settings", añade la siguiente Redirect URI:
Importante: Debe ser exacta, localhost puede dar problemas con cookies.
http://127.0.0.1:8000/users/auth/callback

6. Configurar Variables de Entorno
Crea un archivo .env en la raíz del proyecto:

SPOTIFY_CLIENT_ID="pega_tu_client_id_aqui"
SPOTIFY_CLIENT_SECRET="pega_tu_client_secret_aqui"
SPOTIFY_REDIRECT_URI="http://127.0.0.1:8000/users/auth/callback"
ENVIRONMENT="development"
LOG_LEVEL="INFO"

▶️ Ejecución

Levanta el servidor de desarrollo:
uvicorn main:app --reload --host 127.0.0.1 --port 8000

La API estará disponible en: http://127.0.0.1:8000

📖 Documentación de la API

FastAPI genera documentación interactiva automáticamente. Una vez iniciada la app, visita:
Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
Flujo de Uso Básico
Crear Usuario: POST /users/
Login en Spotify: Abre en el navegador http://127.0.0.1:8000/spotify/auth/{user_id}/login.
Autorizar: Acepta los permisos en Spotify. Serás redirigido y verás un JSON de éxito.
Usar la API: Ahora puedes añadir favoritos (POST /users/{id}/favorites/artists) o seguir artistas (PUT /spotify/me/following).

🧪 Testing

El proyecto incluye una suite de tests completa usando pytest. Los tests de integración con Spotify utilizan Mocks, por lo que no requieren credenciales reales ni conexión a internet.
Ejecutar tests:
pytest -v

🛡️ Manejo de Errores

La API implementa un manejador global de excepciones (main.py) que transforma errores de Python en respuestas HTTP JSON estandarizadas:
404 Not Found: Cuando no existe un usuario o un recurso en Spotify.
401 Unauthorized: Cuando el token de Spotify ha expirado o no existe.
422 Validation Error: Cuando los datos de entrada (edad, nombre) no cumplen las reglas.
502 Bad Gateway: Errores de comunicación con la API externa.

📝 Licencia
Este proyecto está bajo la Licencia MIT. Siéntete libre de usarlo y modificarlo.

Hecho con ❤️ y 🐍 Python para la Universidad Europea.
