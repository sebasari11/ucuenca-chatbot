
# UCALMA – Chatbot de Salud Mental

UCALMA es un chatbot conversacional inteligente enfocado en la salud mental y la prevención de la ciberadicción. Desarrollado con **FastAPI**, utiliza **PostgreSQL** para persistencia, **FAISS** para búsqueda semántica, y se integra con múltiples APIs de IA como **Gemini**, **DeepSeek** y otros modelos de lenguaje.

## 🚀 Características Principales

- 🤖 **Chatbot Inteligente**: Respuestas contextuales basadas en recursos de salud mental
- 🔍 **Búsqueda Semántica**: Utiliza FAISS para encontrar información relevante
- 📚 **Gestión de Recursos**: Procesamiento de PDFs, URLs y texto
- 👥 **Sistema de Usuarios**: Roles diferenciados (admin, user, invited)
- 🔐 **Autenticación JWT**: Sistema seguro de login y registro
- 🐳 **Docker Ready**: Despliegue fácil con Docker y Docker Compose
- 📊 **API REST**: Documentación automática con Swagger/OpenAPI

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.13** - Lenguaje principal
- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional
- **SQLAlchemy** - ORM asíncrono
- **Alembic** - Migraciones de base de datos

### IA y Machine Learning
- **FAISS** - Búsqueda de similitud vectorial
- **Sentence Transformers** - Embeddings de texto
- **Google Gemini** - Modelo de lenguaje
- **DeepSeek** - API de IA alternativa
- **NLTK** - Procesamiento de lenguaje natural

### Utilidades
- **PyMuPDF** - Procesamiento de PDFs
- **JWT** - Autenticación de tokens
- **Pydantic** - Validación de datos
- **Uvicorn** - Servidor ASGI

## 📁 Estructura del Proyecto

```
ucuenca-chatbot/
├── app/
│   ├── alembic/              # Migraciones de base de datos
│   ├── api/
│   │   ├── deps.py          # Dependencias de FastAPI
│   │   └── routes/          # Rutas de la API
│   ├── core/
│   │   ├── config.py        # Configuración de la aplicación
│   │   ├── database.py      # Configuración de BD
│   │   ├── security.py      # Autenticación y JWT
│   │   └── logging.py       # Sistema de logs
│   ├── faiss_index/         # Motor de búsqueda semántica
│   ├── src/
│   │   ├── users/           # Gestión de usuarios y roles
│   │   ├── resources/       # Procesamiento de PDFs y URLs
│   │   ├── chunks/          # Vectorización de textos
│   │   └── chats/           # Sesiones de conversación
│   └── utils/
│       ├── nlp.py           # Procesamiento de lenguaje natural
│       └── pdf_reader.py    # Lectura de PDFs
├── resources/               # Archivos PDF de salud mental
├── requirements.txt         # Dependencias de Python
├── Dockerfile              # Configuración de Docker
├── docker-compose.yml      # Orquestación de servicios
└── README.md              # Este archivo
```

## 🔐 Sistema de Roles

| Rol | Permisos | Descripción |
|-----|----------|-------------|
| **admin** | Acceso completo | Puede invitar usuarios, cargar recursos, gestionar el sistema |
| **user** | Acceso parcial | Puede interactuar con el chatbot y consultar recursos |
| **invited** | Acceso restringido | Solo lectura y chat básico |

## 🚀 Despliegue Rápido

### Opción 1: Docker Compose (Recomendado)

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/sebasari11/ucuenca-chatbot.git
   cd ucuenca-chatbot
   ```

2. **Configura las variables de entorno:**
   ```bash
   cp env.example .env
   # Edita .env con tus configuraciones
   ```

3. **Ejecuta con Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Accede a la aplicación:**
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Opción 2: Desarrollo Local

1. **Prepara el entorno:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # o
   venv\Scripts\activate     # Windows
   ```

2. **Instala dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura la base de datos PostgreSQL**

4. **Ejecuta migraciones:**
   ```bash
   alembic upgrade head
   ```

5. **Inicia el servidor:**
   ```bash
   uvicorn app.main:app --reload
   ```

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Base de Datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ucuenca_chatbot
DB_USER=postgres
DB_PASSWORD=tu_password_seguro

# APIs de IA
DEEPSEEK_API_KEY=tu_api_key_deepseek
GEMINI_API_KEY=tu_api_key_gemini

# Seguridad
SECRET_KEY=tu_clave_secreta_muy_larga
ALGORITHM=HS256

# Aplicación
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=*
```

### Configuración de Base de Datos

1. **Instala PostgreSQL**
2. **Crea la base de datos:**
   ```sql
   CREATE DATABASE ucuenca_chatbot;
   ```
3. **Ejecuta las migraciones:**
   ```bash
   alembic upgrade head
   ```

## 📡 Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/health` | Estado del sistema |
| `POST` | `/users/login` | Autenticación de usuarios |
| `POST` | `/users/register` | Registro de usuarios |
| `GET` | `/resources` | Lista de recursos disponibles |
| `POST` | `/resources/upload` | Cargar nuevo recurso |
| `POST` | `/chats/query` | Consulta al chatbot |
| `GET` | `/chats/sessions` | Historial de conversaciones |

## 🧠 Funcionamiento del Chatbot

1. **Recepción de Consulta**: El usuario envía una pregunta
2. **Análisis de Intención**: Clasifica el tipo de consulta (informativa, empática, reflexiva)
3. **Búsqueda Semántica**: Utiliza FAISS para encontrar información relevante en los recursos
4. **Generación de Respuesta**: 
   - Si encuentra información local, la contextualiza
   - Si no, utiliza APIs externas (Gemini, DeepSeek)
5. **Respuesta Contextual**: Devuelve una respuesta personalizada y útil

## 🐳 Docker

### Comandos Útiles

```bash
# Construir imagen
docker build -t ucuenca-chatbot .

# Ejecutar con Docker Compose
docker-compose up -d

# Ver logs
docker-compose logs -f app

# Ejecutar migraciones
docker-compose exec app alembic upgrade head

# Acceder al contenedor
docker-compose exec app bash

# Parar servicios
docker-compose down
```

### Estructura de Docker

- **app**: Servicio principal de FastAPI
- **db**: Base de datos PostgreSQL
- **Volumes**: Persistencia de datos y recursos

## 🔧 Desarrollo

### Estructura de Módulos

- **`app/src/users/`**: Gestión de usuarios, autenticación, roles
- **`app/src/resources/`**: Carga y procesamiento de PDFs/URLs
- **`app/src/chunks/`**: Vectorización y almacenamiento de texto
- **`app/src/chats/`**: Gestión de conversaciones y sesiones
- **`app/faiss_index/`**: Motor de búsqueda semántica
- **`app/core/`**: Configuración central y utilidades

### Agregar Nuevos Recursos

1. Coloca archivos PDF en `resources/`
2. Usa el endpoint `/resources/upload` para procesarlos
3. Los chunks se vectorizan automáticamente

### Extender el Chatbot

- Modifica `app/src/chats/service.py` para lógica de conversación
- Ajusta `app/faiss_index/manager.py` para búsqueda personalizada
- Configura nuevos modelos en `app/core/config.py`

## 🐛 Troubleshooting

### Problemas Comunes

1. **Error de conexión a BD:**
   ```bash
   docker-compose logs db
   # Verifica variables de entorno
   ```

2. **Migraciones fallidas:**
   ```bash
   docker-compose exec app alembic current
   docker-compose exec app alembic upgrade head
   ```

3. **Recursos no cargan:**
   - Verifica permisos del directorio `resources/`
   - Revisa logs: `docker-compose logs app`

4. **APIs de IA no funcionan:**
   - Verifica las API keys en `.env`
   - Revisa la conectividad a internet

## 📊 Monitoreo

- **Health Check**: `GET /health`
- **Logs**: `docker-compose logs -f app`
- **Métricas**: Integración con FastAPI metrics

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Desarrollado por **Universidad de Cuenca** – Facultad de Ingeniería.

## 📬 Contacto

- **Desarrollador**: Sebastián Arias
- **LinkedIn**: [sebasari11](https://www.linkedin.com/in/sebasari11/)
- **Email**: sebasari11@gmail.com
- **Repositorio**: [https://github.com/sebasari11/ucuenca-chatbot](https://github.com/sebasari11/ucuenca-chatbot)

---

⭐ **¡Dale una estrella al proyecto si te resulta útil!**