from django.urls import path
from .views import *
urlpatterns=[
 path('me/',MeView.as_view()), path('dashboard/',DashboardView.as_view()),
 path('jobs/',JobListView.as_view()), path('companies/',CompanyListView.as_view()), path('jobs/<int:pk>/',JobDetailView.as_view()), path('jobs/<int:pk>/match/',JobMatchView.as_view()), path('recruiter/jobs/',RecruiterJobListCreateView.as_view()),
 path('applications/',ApplicationListView.as_view()), path('applications/fee-preview/',FeePreviewView.as_view()), path('applications/create-order/',CreateOrderView.as_view()), path('applications/verify-payment/',VerifyPaymentView.as_view()), path('applications/<int:pk>/action/',RecruiterActionView.as_view()),
 path('payments/webhook/',WebhookView.as_view()), path('refunds/',RefundListView.as_view()), path('refunds/<int:application_id>/initiate/',RefundInitiateView.as_view()),
 path('interviews/',InterviewListCreateView.as_view()), path('interviews/<int:pk>/attendance/',InterviewAttendanceView.as_view()), path('applications/<int:pk>/outcome/',HiringOutcomeView.as_view()),
 path('assessments/',AssessmentListView.as_view()), path('assessments/<int:pk>/',AssessmentDetailView.as_view()), path('assessments/<int:pk>/submit/',AssessmentSubmitView.as_view()),
 path('resumes/',ResumeListCreateView.as_view()), path('resumes/upload/',ResumeUploadView.as_view()), path('saved-jobs/',SavedJobListView.as_view()), path('resumes/<int:pk>/',ResumeDetailView.as_view()), path('internships/',InternshipListView.as_view()),
 path('notifications/',NotificationView.as_view()), path('ai/assistant/',AiAssistantView.as_view()), path('messages/',MessageView.as_view()), path('reports/',ReportView.as_view()), path('admin/companies/',AdminCompaniesView.as_view()), path('admin/companies/<int:pk>/',AdminCompaniesView.as_view()),
]
