
---

# Still Missed Children (SMC) - FastAPI
**A Multi-Level-Centralized-Asynchronous Architecture for Handling the SMC Process**

A **RESTful API** built with **FastAPI** for managing the SMC for the Polio Program.

---

## **Setup Instructions**

### 1. Clone the Repository

```bash
git clone https://github.com/<USERNAME>/<REPO>.git
cd <REPO>
```

### 2. Install Python

* Ensure **Python 3.12.7** is installed.

### 3. Create a Virtual Environment

```bash
python -m venv env
```

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

### 6. Set Up Database

* Ensure **PostgreSQL 17** is installed and running.
* Create a new database for the application.
* Configure the `.env` file with your database URL:

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
```

#### **Database Connection Settings**

* **Core connections (pool\_size)**: 1024 (allows more than 1000 concurrent connections per worker)
* **Extra connections (max\_overflow)**: 256

> ⚠️ **Important:** The total number of connections across all workers should not exceed your PostgreSQL `max_connections`. Adjust `pool_size` if needed.

### 7. Configure CORS (Cross-Origin Requests)

* Update `allow_origins` in your FastAPI app:

```python
allow_origins=[
    "http://<SERVER_IP>:8000"  # Add server IP when deploying
]
```

### 8. Run the API

* Recommended command for production with multiple workers:

```bash
uvicorn smc_tracker.asgi:application --host 0.0.0.0 --port 8000 --workers 16
```

### 9. Notes

* **Do not modify** the extra configuration in `.env`; only update the `DATABASE_URL`.
* Ensure that the database connection settings match your PostgreSQL server limits.
* For production deployment, consider using **Gunicorn with Uvicorn workers** for better process management.

---
