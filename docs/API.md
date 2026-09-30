# Core API surface

Authentication: `/api/auth/register/`, `/api/auth/login/`, `/api/auth/refresh/`
Jobs: `/api/jobs/`, `/api/jobs/{id}/`, `/api/jobs/{id}/match/`
Applications: `/api/applications/`, `/api/applications/fee-preview/`, `/api/applications/create-order/`, `/api/applications/verify-payment/`
Recruiter: `/api/recruiter/jobs/`, `/api/applications/{id}/action/`, `/api/applications/{id}/outcome/`
Interviews: `/api/interviews/`, `/api/interviews/{id}/attendance/`
Refunds: `/api/refunds/`, `/api/refunds/{application_id}/initiate/`
Assessments: `/api/assessments/`, `/api/assessments/{id}/`, `/api/assessments/{id}/submit/`
Resume: `/api/resumes/`
Internships: `/api/internships/`
AI fallback: `/api/ai/assistant/`
Admin: `/api/admin/companies/`
Webhook: `/api/payments/webhook/`
