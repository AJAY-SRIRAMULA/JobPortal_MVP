# JOBPORTAL — React + Django + MySQL MVP

A responsive career and hiring marketplace implementing the supplied JobPortal specification, including Job DNA, explainable matching, Application Quality Gate, first-three ₹1,000 / 4th+ ₹5,000 application pricing, Priority/Normal applications, Razorpay TEST MODE payment verification and refund workflow, assessments, resume builder, interviews, internships, analytics, notifications, messaging, reports and admin verification.

## Prerequisites
- Python 3.11/3.12/3.13 (Python 3.13 may require `pip install "setuptools<81"` because the Razorpay SDK currently imports `pkg_resources`)
- Node.js + npm
- MySQL Server + Workbench
- Git
- Razorpay TEST MODE API credentials

## 1. Database
Create a MySQL database:
```sql
CREATE DATABASE jobportal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```
Edit `.env` with your MySQL password and Razorpay TEST credentials. Never commit `.env`.

Then:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```
Backend: http://127.0.0.1:8000
Admin: http://127.0.0.1:8000/admin/

## 3. Frontend
In another terminal:
```bash
cd frontend
npm install
npm run dev
```
Frontend: http://localhost:5173 (Vite may choose 5174/5175 if the port is busy; Django CORS allows 5173–5175)

## Demo accounts
- Candidate: candidate@example.com / Candidate@123
- Recruiter: recruiter@example.com / Recruiter@123
- Admin: admin@example.com / Admin@123

Change these credentials for any non-demo environment.

## Razorpay TEST MODE
The frontend uses Razorpay Checkout. Django creates the order and calculates the amount; React never supplies the trusted fee. Django verifies the returned signature before creating the application. Refunds are initiated by an authorized admin through the backend Razorpay Refund API. The Razorpay secret stays in `.env`.

## Critical demo flow
1. Candidate registers/logs in.
2. Search a seeded job.
3. Open Job DNA and Application Quality Gate.
4. First three successful applications calculate ₹1,000 and become PRIORITY.
5. Fourth successful application calculates ₹5,000 and becomes NORMAL.
6. Recruiter reviews, shortlists/rejects and schedules interviews.
7. Recruiter records attendance and hiring outcome.
8. Selected or rejected after confirmed attendance becomes refund eligible.
9. Admin initiates the real Razorpay TEST refund.
10. No-show becomes NOT_ELIGIBLE.

## Security
- JWT access/refresh tokens
- Backend role enforcement
- Server-side fee calculation
- Razorpay signature verification
- Webhook signature validation hook
- ORM-based database access
- Environment variables for secrets
- No card/CVV/UPI PIN storage

## Notes
This repository is intentionally an MVP: advanced AI uses a useful rule-based fallback, messaging is database-backed, and analytics are database-driven. Add an AI API key later through `AI_API_KEY` if desired.

For Razorpay webhook testing on localhost, expose `/api/payments/webhook/` through a secure tunnel or deploy the backend to a reachable HTTPS environment, then configure the Razorpay webhook URL and secret in the dashboard.


## UI / Product Upgrade Pack

This version keeps the existing Django + MySQL + JWT + Razorpay Test Mode flow and adds:
- Distinct Candidate and Recruiter login entry points.
- Competitive job discovery filters: keyword, location, work mode, employment, experience, industry and salary range.
- Saved jobs and saved-search alert UI.
- Company transparency directory with verification status and open-role count.
- Job DNA, Hiring Process Transparency, Application Quality Gate and explainable skill matching.
- Candidate dashboard with application funnel and skill-gap bar charts.
- Verified Skill Passport, profile editor and resume-file attachment section.
- Smart Resume Builder with saved versions and print/PDF workflow.
- Recruiter pipeline search/filtering, fee visibility, shortlist/reject, interview scheduling and attendance.
- Interview calendar, candidate notifications, application/refund tracking and admin Razorpay refund initiation.
- Internship filters and expanded non-technology seed roles.
- Messaging and Career AI surfaces.
- Responsive visual system, illustrations, cards, badges, meters, charts and mobile layouts.

### Razorpay UPI note

The application still uses the real Razorpay Checkout/Test Mode integration. The checkout configuration requests UPI when the Razorpay account has UPI enabled. Razorpay's current documentation supports UPI in Checkout, but the methods displayed in a merchant's checkout depend on the payment methods enabled for that account. If UPI is absent from your Test Mode checkout, enable/activate UPI in the Razorpay dashboard rather than adding a fake UPI flow. Cards, netbanking and wallets remain available where enabled.

### Demo portals

- Candidate: `candidate@example.com` / `Candidate@123`
- Recruiter: `recruiter@example.com` / `Recruiter@123`
- Admin: `admin@example.com` / `Admin@123`

Run the existing `python manage.py seed_demo` command after pulling the upgraded source if you want the additional diversified demo jobs/skills.
