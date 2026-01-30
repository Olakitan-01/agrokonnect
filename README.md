AgroKonnect Backend 🌾
AgroKonnect is a robust Python-based API service that connects buyers and farmers directly. It handles everything from marketplace listings and real-time chat to secure authentication and password recovery.

🎯 Purpose
The main goal is to empower farmers by removing middlemen, providing a direct channel to sell produce, and giving buyers access to fresh farm-to-table goods.

✨ Core Features
Secure Authentication:

JWT-based login and registration.

Password Management: Full "Forgot Password" and "Reset Password" workflows.

Direct Marketplace: Endpoints for listing agricultural products, categories, and inventory.

Real-time Chat: Direct messaging between buyers and farmers for negotiations and inquiries.

Interactive API Docs: Built-in Swagger UI for easy endpoint testing.

🛠 Tech Stack
Language: Python 3.x

Framework: (Django)

API Documentation: Swagger / OpenAPI

Database: ( SQLite)

🚀 Getting Started
Clone the repository

Bash
git clone https://github.com/your-username/agrokonnect-backend.git
cd agrokonnect-backend
Install dependencies

Bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
Set up Environment Variables Create a .env file for your DATABASE_URL, SECRET_KEY, and EMAIL_SETTINGS (for password resets).

Run Migrations & Start Server

Bash
python manage.py migrate
python manage.py runserver

📑 API Documentation (Swagger)
The project comes with built-in interactive documentation. Once the server is running, you can view the available endpoints and test them directly in your browser:

👉 http://localhost:8000/docs (or /swagger)

Key Endpoints:
POST /auth/forgot-password - Trigger a reset email.

POST /auth/reset-password - Update password with token.

GET /marketplace - Browse all farm produce.

POST /chat/message - Send a message to a farmer.