# FastAPI Project 🚀

## 📌 Setup Instructions

Follow the steps below to run the project locally:

---

## 1️⃣ Create Virtual Environment

```bash
python -m venv venv
```

---

## 2️⃣ Activate Virtual Environment

### On Windows:

```bash
.\venv\Scripts\activate
```

### On macOS/Linux:

```bash
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

### Option 1: Install manually

```bash
pip install fastapi uvicorn sqlalchemy
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart email-validator
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

### Option 2 (Recommended): Install from requirements file

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Run the Application

```bash
uvicorn main:app --reload
```

---

## 🌐 API Docs

Once the server is running, open:

* Swagger UI: http://127.0.0.1:8000/docs
* ReDoc: http://127.0.0.1:8000/redoc

---

## 📂 Project Structure

```
app/
 ├── api/
 ├── models/
 ├── repository/
 ├── schemas/
 ├── services/
 ├── database.py
 └── db_utils.py

main.py
requirements.txt
```

---

## ⚠️ Notes

* Make sure `.env` file is configured properly (if used)
* Do NOT commit `venv/` or `.env` to GitHub
* Always activate the virtual environment before running the project

---

## ✅ Requirements

* Python 3.8+
* pip

---


