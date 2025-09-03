#### Waqas. , AFeeF
---

# **Still Missed Children - Web Application**

**A Multi-Level, Centralized, Asynchronous Architecture for Handling the SMC Process**

---

## **Setup Instructions**

### 1. Clone the Repository

```bash
git clone https://github.com/<USERNAME>/<REPO>.git
cd <REPO>
```

### 2. Install Python

* Ensure **Python 3.12+** is installed.

### 3. Create a Virtual Environment

```bash
python -m venv env
```
One Environemnt for Both FastAPI and Django is Ok. Don't Duplicate

### 4. Activate the Virtual Environment

```bash
# Windows
env\Scripts\activate

# macOS/Linux
source env/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## **6. Database Setup**

#### Run Migrations

Navigate to the project directory where `manage.py` is located:

```
smc_tracker/          # Django project root
├── smc_tracker/      # Project settings, ASGI, WSGI, urls.py
├── apps/             # Your Django apps
├── static/           # Static files (CSS, JS, images)
├── templates/        # HTML templates
├── media/            # Uploaded files
└── manage.py         # Django management script
```



```bash
cd smc_tracker
python manage.py makemigrations
python manage.py migrate
```

#### Create Superuser

```bash
python manage.py createsuperuser
```

**Credentials:**

* **Username:** `stillmissedchildren`
* **Email:** `administrator@eoc.gov.pk`
* **Password:** `stillmissedchildren`

---

## **7. Configure Environment & Network**

* Update the environment **(.env)** or settings file to point to the **FastAPI backend**:

  ```
  IP_ADDRESS:8001
  ```
* In `apiConfig.js` (located in `smc_tracker/static/`), update the backend API URL to the FastAPI IP and port `8001`.
* Ensure **ports 8000 (Django) and 8001 (FastAPI)** are publicly accessible.

---

## **8. Static & Media Files**

Collect static files:

```bash
python manage.py collectstatic
```

* Serve static and media files via **NGINX** or **cloud storage** in production for performance and security.

---

## **9. Allowed Hosts**

Update `ALLOWED_HOSTS` in `settings.py` located in smc_tracker/smc_tracker:

```python
ALLOWED_HOSTS = ['<SERVER_IP>:8000']
```

* Later, replace with your **SMC website URL** when deploying.

---

## **10. Running the Project**


### Production Server with Uvicorn (ASGI)

```bash
cd smc_tracker
uvicorn smc_tracker.asgi:application --host 0.0.0.0 --port 8000 --workers 8
```

* **--host 0.0.0.0** → Accessible externally
* **--port 8000** → Django server port
* **--workers 8** → Number of worker processes (adjust according to CPU cores)

> Use **NGINX** or another reverse proxy for serving static files and handling HTTPS in production.

---


