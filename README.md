# VoteCollege — Online Student Election System

A secure, web-based election management platform built with **Django** and **SQLite**, designed for college-level student elections.

---

## Project Objective

VoteCollege enables institutions to conduct transparent, tamper-resistant student elections entirely online. Students register, get verified by an administrator, and cast votes per position — all through a modern glassmorphic UI. Results are published only when the election authority decides, ensuring integrity.

---

## Features

- **Student Registration & Authentication** — Custom user model with Student ID and department fields
- **Admin Verification Workflow** — Students must be verified by an admin before voting; prevents unauthorised participation
- **One-Vote-Per-Position Enforcement** — Database-level unique constraint prevents duplicate votes
- **Election Open/Close Control** — Admin toggles `is_open`; optional `start_time` / `end_time` fields auto-open and auto-close voting
- **Controlled Result Publication** — Results visible to students only after the admin sets `results_published = True`
- **Interactive Charts** — Doughnut (vote share) + Bar chart (vote count) per position using Chart.js
- **Dashboard Statistics** — Total voters, votes cast, candidates, and live participation percentage with progress bar
- **Audit Log** — Every login, logout, failed login, registration, and vote is recorded with username, action, detail, and IP address
- **Admin Portal** — Full Django admin with colour-coded audit log badges and bulk student-verification actions

---

## Technologies Used

| Layer        | Technology                     |
|--------------|--------------------------------|
| Backend      | Python 3.11, Django 5.2        |
| Database     | SQLite 3                       |
| Frontend     | HTML5, CSS3 (glassmorphism)    |
| Charts       | Chart.js (CDN)                 |
| Auth         | Django `AbstractUser`          |
| Media        | Pillow (candidate photos)      |

---

## Installation Steps

### Prerequisites
- Python 3.10+
- pip

### 1. Clone / extract the project
```bash
unzip Votes-main.zip
cd Votes-main/votes
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply database migrations
```bash
python manage.py migrate
```

### 5. Create a superuser (admin account)
```bash
python manage.py createsuperuser
```

### 6. Run the development server
```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## Usage Guide

1. Log in to the admin panel at `/admin/` and add **Positions** and **Candidates**.
2. Set `ElectionStatus` → `is_open = True` (and optionally set `start_time` / `end_time`).
3. Students register at `/register/`, then an admin verifies them in the Student list.
4. Verified students visit `/dashboard/`, cast votes per position.
5. When voting ends, admin sets `results_published = True`; students can then view results with live charts.
6. Review the **Audit Log** in admin for a full security trail.

---

## Project Structure

```
votes/
├── election/
│   ├── models.py       # Student, Candidate, Vote, ElectionStatus, AuditLog
│   ├── views.py        # All page logic + audit logging
│   ├── admin.py        # Admin configuration
│   ├── forms.py        # Registration form
│   ├── urls.py         # URL routing
│   └── migrations/     # Database schema history
├── templates/
│   └── election/
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html   # Stats cards + participation bar
│       ├── vote.html
│       └── results.html     # Doughnut + Bar charts
├── static/css/style.css
├── voting_system/       # Django project settings
└── manage.py
```

---

## Security Features

- CSRF protection on all forms (Django default)
- Password hashing via Django's `AbstractUser`
- Admin verification gate before voting is allowed
- Audit log captures IP address of every action
- Vote immutability — admin cannot modify or add votes
- Results hidden until explicitly published

---

## For Viva — "Why is your project unique?"

> "VoteCollege provides secure online voting with student authentication, admin-controlled verification, vote-duplication prevention via database constraints, automatic election scheduling with start/end times, visual result analytics (pie + bar charts), a full security audit log capturing login times, vote times, and IP addresses, and controlled result publication — all built using Django and SQLite."
