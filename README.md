# Fumbld AI (Source Available Upon Request)

<p align="center">
<img src="https://github.com/ant-cantu/fumbld-ai/blob/main/source/static/img/fumbld-small-logo.png?raw=true" height="50%" width="75%">
</p>

## About Fumbld AI

Fumbld AI is a Flask web application that helps fantasy football managers make informed start/sit decisions. It connects to your Yahoo Fantasy leagues, analyzes your roster with current statistics, and uses OpenAI to provide weekly recommendations.

***

### 💻 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white&logoWidth=20)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white&logoWidth=20)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black&logoWidth=20)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white&logoWidth=20)

### 🧩 Frameworks

![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white&logoWidth=20)

### 🔌 APIs

![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white&logoWidth=20)
![Yahoo! Sports](https://img.shields.io/badge/Yahoo!%20Sports-6001D2?style=for-the-badge&logo=yahoo&logoColor=white&logoWidth=20)

### 📚 Libraries & Extensions

![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-CA1F2C?style=for-the-badge&logo=sqlalchemy&logoColor=white&logoWidth=20)
![WTForms](https://img.shields.io/badge/WTForms-000000?style=for-the-badge&logo=formspree&logoColor=white&logoWidth=20)
![Flask-Login](https://img.shields.io/badge/Flask--Login-000000?style=for-the-badge&logo=flask&logoColor=white&logoWidth=20)
![Werkzeug](https://img.shields.io/badge/Werkzeug-FF6F00?style=for-the-badge)

***

## The application follows a straightforward workflow:
1. **User Authentication** – Manage user accounts and sessions with Flask‑Login.
2. **Yahoo Integration** – Authorize access to your fantasy league using Yahoo's OAuth flow and store tokens securely with SQLAlchemy.
3. **Roster Analysis** – Retrieves current league data and stores roster information in the user’s database to reduce the number of API calls.
4. **AI Recommendations** – Sends aggregated data to OpenAI’s API to generate lineup recommendations, displaying the suggested roster in a table along with the rationale behind each selection.
5. **Dashboard Display** – Present the AI's suggestions in a clean web interface.

## Features
- User registration and authentication using **Flask-Login**
- Yahoo Fantasy Sports integration with OAuth2
- AI insights powered by **OpenAI GPT**
- Dashboard to view your roster and AI recommendations
- Google reCAPTCHA for form protection

## Source Code:
> To protect the source code, it is available upon request to prospective employers only.

## Preview

### Home Page
![image](https://github.com/user-attachments/assets/e3a126f3-9d89-4da2-95b5-ed2179e4b9ae)

### Login Page
![image](https://github.com/user-attachments/assets/6dc2fd9a-1048-4e4a-b884-f43b13bb8c49)

### Registration Page
![image](https://github.com/user-attachments/assets/eb267dab-fc82-4a31-8703-8306256192ae)

### Dashboard - Main
![image](https://github.com/user-attachments/assets/2f2bd647-2a59-4665-8bc4-78fea9dddeb9)

### Dashboard - Fumbld AI
![image](https://github.com/user-attachments/assets/55f1e272-92f9-4539-bdab-34b0d9e18e28)

### Dashboard - Settings (Work In Progress)
![image](https://github.com/user-attachments/assets/7454ecff-2be9-46fb-9d0a-8c75fc13206f)