from django.contrib import admin
from .models import *
for m in [User,Skill,CandidateProfile,CandidateSkill,Company,RecruiterProfile,Job,Internship,Assessment,Question,AssessmentResult,Resume,Verification,Application,ApplicationPayment,Refund,Interview,Notification,SavedJob,Message,Report]:
    admin.site.register(m)
