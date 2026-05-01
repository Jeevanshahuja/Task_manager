# 🗂️ Task Manager Web Application

A full-stack Task Manager web application built using Flask, HTML, CSS, and MySQL, designed to manage projects and tasks efficiently with role-based access control.

---

## 🚀 Live Demo
[https://your-app.up.railway.app](https://taskmanager-production-78de.up.railway.app/auth)

---

## 📌 Features

- User Authentication (Signup & Login)
- Role-Based Access (Admin & Member)
- Admin Dashboard (Create & Manage Projects)
- Task Assignment to Members
- Member Dashboard (View Assigned Tasks)
- Task Status Update
- Secure Password Hashing
- Session Management

---

## 🛠️ Tech Stack

Frontend:
- HTML
- CSS

Backend:
- Flask (Python)

Database:
- MySQL

Deployment:
- Railway
- Gunicorn

---



## 🗄️ Database Schema

Users Table:
- id
- username
- email
- password_hash
- role

Projects Table:
- id
- name
- description
- created_by
- created_at

Tasks Table:
- id
- project_id
- title
- description
- assigned_to
- due_date
- status
- created_by

---



## 🌐 Deployment

- Hosted on Railway
- Uses Gunicorn as WSGI server
- MySQL database hosted on Railway

---



## 🧠 How It Works

1. Users sign up and log in
2. Admins create projects and assign tasks
3. Members view assigned tasks
4. Members update task status
5. Data is stored in MySQL database

---



## 🚀 Future Improvements

- JWT Authentication
- Email notifications
- Advanced analytics dashboard
- Improved UI/UX

---

