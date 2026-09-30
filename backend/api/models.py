from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class User(AbstractUser):
    ROLE_CHOICES=[('candidate','Candidate'),('recruiter','Recruiter'),('admin','Admin')]
    role=models.CharField(max_length=20,choices=ROLE_CHOICES,default='candidate')
    phone=models.CharField(max_length=30,blank=True)

class Skill(models.Model):
    name=models.CharField(max_length=100,unique=True)
    def __str__(self): return self.name

class CandidateProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='candidate_profile')
    location=models.CharField(max_length=120,blank=True); education=models.CharField(max_length=255,blank=True)
    experience=models.CharField(max_length=120,blank=True); projects=models.TextField(blank=True)
    certifications=models.TextField(blank=True); career_interests=models.CharField(max_length=255,blank=True)
    preferred_location=models.CharField(max_length=120,blank=True); preferred_work_mode=models.CharField(max_length=30,blank=True)
    skills=models.ManyToManyField(Skill,through='CandidateSkill',blank=True)
    def __str__(self): return self.user.get_full_name() or self.user.username

class CandidateSkill(models.Model):
    STATUS=[('VERIFIED','Verified'),('SELF_DECLARED','Self-Declared'),('PENDING','Assessment Pending')]
    candidate=models.ForeignKey(CandidateProfile,on_delete=models.CASCADE)
    skill=models.ForeignKey(Skill,on_delete=models.CASCADE)
    status=models.CharField(max_length=20,choices=STATUS,default='SELF_DECLARED')
    class Meta: unique_together=('candidate','skill')

class Company(models.Model):
    name=models.CharField(max_length=200); description=models.TextField(blank=True); website=models.URLField(blank=True)
    location=models.CharField(max_length=120,blank=True); verified=models.BooleanField(default=False)
    def __str__(self): return self.name

class RecruiterProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='recruiter_profile'); company=models.ForeignKey(Company,on_delete=models.CASCADE,related_name='recruiters')

class Job(models.Model):
    EMP=[('FULL_TIME','Full Time'),('PART_TIME','Part Time'),('CONTRACT','Contract')]
    MODE=[('WFO','WFO'),('HYBRID','Hybrid'),('REMOTE','Remote')]
    title=models.CharField(max_length=200); company=models.ForeignKey(Company,on_delete=models.CASCADE,related_name='jobs')
    location=models.CharField(max_length=120); salary_min=models.DecimalField(max_digits=10,decimal_places=2); salary_max=models.DecimalField(max_digits=10,decimal_places=2)
    experience=models.CharField(max_length=80); employment_type=models.CharField(max_length=30,choices=EMP,default='FULL_TIME'); work_mode=models.CharField(max_length=20,choices=MODE,default='WFO')
    industry=models.CharField(max_length=100,default='Technology'); description=models.TextField(); responsibilities=models.TextField(); qualifications=models.TextField()
    hiring_stages=models.JSONField(default=list); expected_timeline=models.CharField(max_length=100,default='2-3 weeks'); application_fee=models.DecimalField(max_digits=10,decimal_places=2,default=1000)
    refund_conditions=models.CharField(max_length=255,default='Eligible after attending the hiring process'); deadline=models.DateField(null=True,blank=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True); is_open=models.BooleanField(default=True)
    required_skills=models.ManyToManyField(Skill,related_name='jobs',blank=True)
    def __str__(self): return self.title

class Internship(models.Model):
    role=models.CharField(max_length=200); company=models.ForeignKey(Company,on_delete=models.CASCADE,related_name='internships'); skills=models.ManyToManyField(Skill,blank=True)
    location=models.CharField(max_length=120); work_mode=models.CharField(max_length=20); stipend=models.DecimalField(max_digits=10,decimal_places=2); duration=models.CharField(max_length=80); paid=models.BooleanField(default=True); conversion_info=models.CharField(max_length=255,blank=True); is_open=models.BooleanField(default=True)

class Assessment(models.Model):
    CATEGORY=[('Python','Python'),('JavaScript','JavaScript'),('React','React'),('SQL','SQL'),('HTML/CSS','HTML/CSS'),('Aptitude','Aptitude')]
    title=models.CharField(max_length=200); category=models.CharField(max_length=50,choices=CATEGORY); duration_minutes=models.PositiveIntegerField(default=15)
class Question(models.Model):
    assessment=models.ForeignKey(Assessment,on_delete=models.CASCADE,related_name='questions'); text=models.TextField(); options=models.JSONField(default=list); answer=models.PositiveIntegerField()
class AssessmentResult(models.Model):
    candidate=models.ForeignKey(CandidateProfile,on_delete=models.CASCADE); assessment=models.ForeignKey(Assessment,on_delete=models.CASCADE); score=models.PositiveIntegerField(); total=models.PositiveIntegerField(); submitted_at=models.DateTimeField(auto_now_add=True)

class Resume(models.Model):
    candidate=models.ForeignKey(CandidateProfile,on_delete=models.CASCADE,related_name='resumes'); name=models.CharField(max_length=150); data=models.JSONField(default=dict); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
class Verification(models.Model):
    candidate=models.ForeignKey(CandidateProfile,on_delete=models.CASCADE,related_name='verifications'); verification_type=models.CharField(max_length=50); status=models.CharField(max_length=30,default='Pending'); notes=models.CharField(max_length=255,blank=True)

class Application(models.Model):
    STATUS=[('APPLIED','Applied'),('SHORTLISTED','Shortlisted'),('ON_HOLD','On Hold'),('REJECTED','Rejected'),('SELECTED','Selected'),('NO_SHOW','No-Show')]
    candidate=models.ForeignKey(CandidateProfile,on_delete=models.CASCADE,related_name='applications'); job=models.ForeignKey(Job,on_delete=models.CASCADE,related_name='applications'); match_percent=models.PositiveIntegerField(default=0); matched_skills=models.JSONField(default=list); missing_skills=models.JSONField(default=list); priority_level=models.CharField(max_length=20,default='NORMAL'); status=models.CharField(max_length=20,choices=STATUS,default='APPLIED'); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['candidate','job'],name='unique_candidate_job')]

class ApplicationPayment(models.Model):
    STATUS=[('PENDING','Pending'),('SUCCESS','Success'),('FAILED','Failed'),('REFUNDED','Refunded')]
    candidate=models.ForeignKey(CandidateProfile,on_delete=models.CASCADE); job=models.ForeignKey(Job,on_delete=models.CASCADE); application=models.OneToOneField(Application,on_delete=models.CASCADE,related_name='payment',null=True,blank=True); order_id=models.CharField(max_length=100,unique=True); payment_id=models.CharField(max_length=100,blank=True); amount=models.DecimalField(max_digits=10,decimal_places=2); currency=models.CharField(max_length=10,default='INR'); status=models.CharField(max_length=20,choices=STATUS,default='PENDING'); payment_method=models.CharField(max_length=50,blank=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
class Refund(models.Model):
    STATUS=[('NOT_ELIGIBLE','Not Eligible'),('PENDING','Pending'),('ELIGIBLE','Eligible'),('INITIATED','Initiated'),('PROCESSED','Processed'),('FAILED','Failed')]
    application=models.OneToOneField(Application,on_delete=models.CASCADE,related_name='refund'); candidate=models.ForeignKey(CandidateProfile,on_delete=models.CASCADE); payment=models.ForeignKey(ApplicationPayment,on_delete=models.CASCADE); amount=models.DecimalField(max_digits=10,decimal_places=2); refund_id=models.CharField(max_length=100,blank=True); status=models.CharField(max_length=20,choices=STATUS,default='PENDING'); reason=models.CharField(max_length=255,blank=True); initiated_at=models.DateTimeField(null=True,blank=True); completed_at=models.DateTimeField(null=True,blank=True)
class Interview(models.Model):
    STATUS=[('SCHEDULED','Scheduled'),('ATTENDED','Attended'),('NO_SHOW','No-Show'),('CANCELLED','Cancelled'),('COMPLETED','Completed')]
    application=models.ForeignKey(Application,on_delete=models.CASCADE,related_name='interviews'); interview_type=models.CharField(max_length=50,default='Technical'); date=models.DateField(); time=models.TimeField(); location=models.CharField(max_length=255,blank=True); meeting_link=models.URLField(blank=True); status=models.CharField(max_length=20,choices=STATUS,default='SCHEDULED')
class Notification(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications'); message=models.CharField(max_length=255); read=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True)
class SavedJob(models.Model):
    candidate=models.ForeignKey(CandidateProfile,on_delete=models.CASCADE); job=models.ForeignKey(Job,on_delete=models.CASCADE); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: unique_together=('candidate','job')
class Message(models.Model):
    sender=models.ForeignKey(User,on_delete=models.CASCADE,related_name='sent_messages'); recipient=models.ForeignKey(User,on_delete=models.CASCADE,related_name='received_messages'); body=models.TextField(); read=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True)
class Report(models.Model):
    reporter=models.ForeignKey(User,on_delete=models.CASCADE); target_type=models.CharField(max_length=30); target_id=models.PositiveIntegerField(); reason=models.CharField(max_length=100); details=models.TextField(blank=True); status=models.CharField(max_length=30,default='OPEN'); created_at=models.DateTimeField(auto_now_add=True)
