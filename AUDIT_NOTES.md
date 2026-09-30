# JobPortal final audit notes

This package preserves the existing UI and product flows. The audit focused on authentication, authorization, payments, refunds, database integrity, API/frontend route alignment, and Python source compilation.

## Fixes included
- Candidate/recruiter/admin login routing preserved and login requests do not send stale JWT access tokens.
- CORS allows Vite ports 5173, 5174 and 5175 on localhost/127.0.0.1.
- Public registration cannot create an admin account. Admin accounts must be created through Django admin.
- Razorpay payment verification validates signature, payment/order relationship, amount and currency before creating an application.
- Razorpay order creation returns a controlled 502 instead of leaking provider exceptions.
- Recruiters can only shortlist/reject applications belonging to their own company.
- Recruiters can only create/update interviews and hiring outcomes for their own company's applications.
- Recruiters only see their company's interviews/refunds through the corresponding API views.
- Invalid interview statuses are rejected server-side.
- No database migration was changed by this audit.
- All backend Python files compile successfully.

## Important security note
The previous working archive contained local database/Razorpay credentials in `backend/.env`. This final archive intentionally does **not** contain those secrets. Use `backend/.env.example` to create your local `.env` and enter your own credentials. Because the old credentials were included in an uploaded archive, regenerate/rotate the Razorpay TEST secret before using it for anything beyond local testing.

## What was not falsely claimed as live-verified
A source-code archive cannot prove connectivity to your personal MySQL server or Razorpay merchant account without accessing those services. The final local verification must therefore be performed with your own `.env`, MySQL database and Razorpay TEST credentials. The application code keeps the real Razorpay order, signature verification and refund APIs; it does not replace them with fake payment/refund logic.
