# PetPal Backend — Resumen del proyecto y diagnóstico

Documento generado a partir del análisis de la migración desde `Pet-Care-app/` (Flask) hacia esta API REST, y de los problemas observados en local durante el desarrollo.

---

## 1. Qué se construyó en `PetPal-backend/`

### Stack

| Componente | Tecnología |
|------------|------------|
| Framework | FastAPI + Uvicorn |
| Base de datos | PostgreSQL (driver `psycopg` v3) |
| ORM | SQLAlchemy 2.x |
| Migraciones | Alembic (configurado, seed manual incluido) |
| Validación | Pydantic v2 |
| Autenticación | JWT (`python-jose`) + bcrypt |
| Imágenes | Cloudinary (opcional en local) |
| Config | `pydantic-settings` + `.env` |

### Estructura de carpetas

```
PetPal-backend/
├── app/
│   ├── main.py              # App FastAPI, CORS, routers
│   ├── config.py            # Settings desde .env
│   ├── database.py          # Engine SQLAlchemy + get_db
│   ├── models.py            # 11 modelos ORM
│   ├── dependencies.py      # JWT auth + verificación de ownership
│   ├── utils.py             # pet_to_out, cálculo de edad
│   ├── routers/
│   │   ├── auth.py          # register, login, me, reset password
│   │   ├── species.py       # especies y razas
│   │   ├── pets.py          # CRUD mascotas (multipart)
│   │   ├── gallery.py       # fotos por mascota
│   │   ├── logs.py          # diario por mascota
│   │   └── trackers.py      # trackers de salud + gráfico peso
│   ├── schemas/             # DTOs Pydantic por dominio
│   ├── services/
│   │   ├── auth.py          # hash/verify password, JWT
│   │   └── cloudinary.py    # upload/delete imágenes
│   └── seed/
│       ├── breeds.py        # ~170 razas perro + ~45 gato
│       └── seed_db.py       # create_all + seed inicial
├── alembic/                 # Migraciones Alembic
├── requirements.txt
├── .env.example
└── README.md
```

### Modelos de base de datos (11 tablas)

Migrados desde el Flask original, con mejoras:

- `User` — usuarios con `pw_hash` (255 chars)
- `Species`, `Breed` — catálogo de especies/razas
- `Pet` — datos generales de mascota
- `Photo` — galería (+ campo `public_id` para Cloudinary)
- `Log` — diario
- `WeightTracker`, `VaccineTracker`, `InternalDewormingTracker`, `ExternalDewormingTracker`, `MedicationTracker`

**Mejoras respecto a Flask:**

- Foreign keys con `ondelete=CASCADE` consistentes
- `CheckConstraint` de sexo (`M`/`F`) a nivel de tabla
- Ownership verificado en `dependencies.get_owned_pet()` (corregido vs bug del Flask)

### Endpoints API (`/api/...`)

#### Auth (`routers/auth.py`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/register` | Registro → devuelve JWT |
| POST | `/auth/login` | Login → devuelve JWT |
| GET | `/auth/me` | Usuario autenticado |
| POST | `/auth/forgot-password` | Token de reset (dev: en respuesta) |
| POST | `/auth/reset-password` | Cambiar contraseña |
| DELETE | `/auth/me` | Eliminar cuenta |

#### Especies (`routers/species.py`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/species` | Listar especies |
| GET | `/species/{id}/breeds` | Razas por especie |

#### Mascotas (`routers/pets.py`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/pets` | Mascotas del usuario |
| POST | `/pets` | Crear (multipart/form-data) |
| GET | `/pets/{id}` | Detalle |
| PUT | `/pets/{id}` | Actualizar (JSON) |
| POST | `/pets/{id}/photo` | Foto de perfil |
| DELETE | `/pets/{id}` | Eliminar |

#### Galería, logs, trackers

- `/pets/{id}/photos` — GET, POST, DELETE
- `/pets/{id}/logs` — CRUD
- `/pets/{id}/trackers/{tipo}` — listar, crear, eliminar
- `/pets/{id}/trackers/weight/chart` — datos para gráfico

#### Health

- `GET /api/health` → `{ "status": "ok" }`

Docs interactivas: **http://localhost:8000/docs**

### Autenticación y seguridad

1. **Registro/login** generan un JWT con `user_id` en el claim `sub`.
2. Rutas protegidas usan `HTTPBearer` en `dependencies.get_current_user()`.
3. Rutas por mascota usan `get_owned_pet()` — verifica `pet.user_id == current_user.id`.
4. Contraseñas hasheadas con **bcrypt** directo (no `passlib`, por compatibilidad con Python 3.14).
5. Operaciones destructivas usan **DELETE**, no GET (a diferencia del Flask original).

### Cloudinary

- Configuración opcional vía `CLOUDINARY_*` en `.env`.
- Si no está configurado: crear mascota **sin foto** funciona; con foto devuelve error 400 claro.
- Galería requiere Cloudinary para subir imágenes.

### Variables de entorno (`.env`)

```env
DATABASE_URL=postgresql+psycopg://postgres:PASSWORD@localhost:5432/petpal
SECRET_KEY=...
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
FRONTEND_URL=http://localhost:3000
```

### Cómo arrancar en local

```powershell
cd D:\Programming\PetPal\PetPal-backend
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

Primera vez:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.seed.seed_db
```

---

## 2. Cronología de lo que pasó en esta conversación

| Momento | Qué ocurrió |
|---------|-------------|
| **Inicio** | Se crearon `PetPal-backend` y `PetPal-frontend` separados del Flask original |
| **Primer arranque local** | Backend + frontend funcionaron; registro con `demo@example.com` OK |
| **Problema mascota nueva** | Usuario reportó que agregar mascota fallaba |
| **Diagnóstico mascota** | Causa: Cloudinary no configurado + campo foto vacío enviado al backend |
| **Fix mascota** | Backend rechaza foto sin Cloudinary con mensaje claro; frontend omite foto vacía |
| **Problema registro** | Usuario reporta que register/login dejó de funcionar |
| **Diagnóstico registro** | API funciona por curl/PowerShell; falla desde navegador |
| **Causa raíz registro** | CORS + backend apagado + frontend en puerto distinto + errores al arrancar servidores |
| **Fixes aplicados** | CORS ampliado, regex localhost, `.env` con ruta absoluta, mensajes de error en frontend |
| **Problemas persistentes** | Múltiples instancias de uvicorn, procesos huérfanos en :8000, frontend no arrancado |

---

## 3. ¿Por qué register/login funcionaba y luego dejó de hacerlo?

### Conclusión principal

**Los cambios en “registrar mascota nueva” NO modificaron el código de auth** (`routers/auth.py`, `services/auth.py`, schemas de auth). El registro dejó de funcionar en el **navegador** por problemas de **entorno local** que coincidieron en el tiempo con el fix de mascotas, no por un bug introducido en login/register.

```
┌─────────────────────────────────────────────────────────────┐
│  Fix mascota (Cloudinary, FormData)                         │
│       ↓                                                     │
│  NO tocó /api/auth/register ni /api/auth/login             │
│       ↓                                                     │
│  Pero sí hubo reinicios de servidores, cambios CORS,        │
│  y el frontend pasó a otro puerto → registro “roto”         │
└─────────────────────────────────────────────────────────────┘
```

### Causas identificadas (orden de probabilidad)

#### Causa 1 — CORS: frontend en puerto distinto al permitido

**Síntoma:** Register/login fallan en el navegador con error de red o “Failed to fetch”; la API responde bien desde PowerShell/curl.

**Qué pasó:**

- `.env` original solo tenía `CORS_ORIGINS=http://localhost:3000`
- Cuando el puerto 3000 estaba ocupado, Next.js usó **3001 o 3002**
- El navegador bloquea la petición antes de llegar al backend (preflight OPTIONS → “Disallowed CORS origin”)

**Evidencia en conversación:**

```
Origin: http://localhost:3002 → Disallowed CORS origin
Origin: http://localhost:3000 → access-control-allow-origin: http://localhost:3000
```

**Fix aplicado:**

- Ampliar `CORS_ORIGINS` a puertos 3000–3003
- Añadir `allow_origin_regex=r"http://localhost:\d+"` en `main.py`
- Cargar `.env` con ruta absoluta en `config.py` (evita que uvicorn arrancado desde otra carpeta ignore el `.env`)

---

#### Causa 2 — Backend no estaba corriendo (comando mal escrito)

**Síntoma:** “Cannot reach the API” o página que no carga datos.

**Qué pasó:** En terminal apareció:

```powershell
.\.venv\Scripts\activateuvicorn app.main:app --reload --port 8000
#              ^^^^^^^^^^^^^^ pegado — PowerShell no lo reconoce
```

El backend **nunca arrancó** desde esa terminal. El frontend seguía abierto pero sin API detrás.

**Comando correcto:**

```powershell
cd D:\Programming\PetPal\PetPal-backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

O en una línea:

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

---

#### Causa 3 — Múltiples instancias de backend en el puerto 8000

**Síntoma:** CORS parcialmente arreglado en código pero sigue fallando en navegador.

**Qué pasó:**

- Varios reinicios dejaron procesos uvicorn huérfanos
- El proceso que respondía en `:8000` a veces era una **instancia antigua** sin los cambios de CORS
- Matar solo el proceso “padre” del reloader no siempre mata el worker hijo

**Solución:** Cerrar todas las terminales con backend (Ctrl+C) y arrancar **una sola** instancia nueva.

---

#### Causa 4 — Frontend apagado o caché `.next` corrupta

**Síntoma:** Error `ENOENT: ... .next\server\app\dashboard\page.js`

**Qué pasó:** Servidor Next.js detenido a mitad de compilación o varias instancias en conflicto.

**Solución:**

```powershell
cd D:\Programming\PetPal\PetPal-frontend
Remove-Item -Recurse -Force .next -ErrorAction SilentlyContinue
npm run dev
```

---

#### Causa 5 — Email ya registrado (confundido con “no funciona”)

**Síntoma:** Register falla con mensaje poco claro.

**Qué pasó:** Durante pruebas se crearon usuarios (`demo@example.com`, `test@example.com`, etc.). Reintentar el mismo email devuelve **409 Conflict** — “Email already registered”. Eso es comportamiento correcto, no un bug.

---

### Lo que SÍ cambió con el fix de mascota (y NO afecta auth)

| Archivo | Cambio | ¿Afecta login/register? |
|---------|--------|-------------------------|
| `app/routers/pets.py` | Validación Cloudinary, parse fechas | No |
| `app/services/cloudinary.py` | `is_configured()`, mensajes de error | No |
| `PetPal-frontend/src/app/pets/new/page.tsx` | FormData, errores en UI | No |
| `PetPal-frontend/src/lib/api.ts` | Mejor manejo errores fetch | Solo mensajes más claros |
| `app/services/auth.py` | `passlib` → `bcrypt` directo | Sí, pero **antes** del problema de mascota; probado OK |
| `app/config.py` + `main.py` | CORS ampliado | Sí, intento de **arreglar** el registro, no romperlo |

---

## 4. Cómo verificar que todo funciona (checklist)

### Backend

```powershell
# 1. Health check
Invoke-RestMethod http://localhost:8000/api/health
# Esperado: status = ok

# 2. Register directo (email nuevo)
$body = '{"username":"test","email":"nuevo@example.com","password":"password123"}'
Invoke-RestMethod -Uri http://localhost:8000/api/auth/register -Method POST -Body $body -ContentType "application/json"
# Esperado: access_token

# 3. CORS desde tu puerto de frontend (ej. 3002)
curl.exe -X OPTIONS http://localhost:8000/api/auth/register `
  -H "Origin: http://localhost:3002" `
  -H "Access-Control-Request-Method: POST" `
  -H "Access-Control-Request-Headers: content-type" -v
# Esperado: access-control-allow-origin en la respuesta
```

### Frontend + backend juntos

1. Terminal 1: backend en `:8000`
2. Terminal 2: `npm run dev` en frontend
3. Abrir la URL que muestre Next.js (anotar el puerto)
4. `/register` con email **nuevo**
5. Debe redirigir a `/dashboard`

### Crear mascota (sin Cloudinary)

1. Login
2. `/pets/new`
3. Nombre + sexo + especie
4. **Dejar foto vacía**
5. Register Pet → debe funcionar

---

## 5. Problemas conocidos pendientes

| Problema | Estado | Workaround |
|----------|--------|------------|
| Subir foto sin Cloudinary | Error 400 esperado | Dejar foto vacía o configurar Cloudinary |
| CORS en puerto distinto a localhost | Parcialmente resuelto | Reiniciar backend tras cambiar `.env` |
| Procesos huérfanos en :8000 | Manual | Cerrar terminales y arrancar de nuevo |
| Python 3.14 + dependencias | Resuelto | `psycopg[binary]`, `bcrypt` directo, pydantic ≥2.11 |
| Alembic sin migración inicial generada | Pendiente | `seed_db.py` usa `create_all` por ahora |

---

## 6. Comandos de referencia rápida

```powershell
# === BACKEND ===
cd D:\Programming\PetPal\PetPal-backend
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000

# === FRONTEND ===
cd D:\Programming\PetPal\PetPal-frontend
npm run dev

# === Limpiar caché frontend ===
Remove-Item -Recurse -Force .next
npm run dev

# === Ver docs API ===
start http://localhost:8000/docs
```

---

## 7. Relación con el proyecto Flask original

| Aspecto | Flask (`Pet-Care-app/`) | FastAPI (`PetPal-backend/`) |
|---------|-------------------------|-------------------------------|
| Renderizado | Server-side Jinja2 | API JSON + frontend Next.js |
| Auth | Sesiones filesystem | JWT |
| DB | SQLite | PostgreSQL |
| Fotos | `static/uploads/` local | Cloudinary |
| Ownership | Bug en `owned_pet()` | Corregido en `get_owned_pet()` |
| Deletes | GET (inseguro) | DELETE |

El Flask original **no fue modificado**; sigue en `Pet-Care-app/` como referencia.

---

*Última actualización: junio 2026 — basado en sesión de desarrollo y debugging local.*
