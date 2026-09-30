import os,hmac,hashlib
from decimal import Decimal
from datetime import datetime, timedelta
import razorpay
from django.conf import settings
from django.db import transaction
from django.db.models import Q,Count,Avg
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *

client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET)) if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET else None

def tokens(user):
    r=RefreshToken.for_user(user); return {'access':str(r.access_token),'refresh':str(r)}
def profile(user):
    if user.role=='candidate': return CandidateProfile.objects.get_or_create(user=user)[0]
    return None
def match_for(candidate,job):
    have=set(candidate.skills.values_list('name',flat=True)); req=set(job.required_skills.values_list('name',flat=True)); matched=sorted(have&req); missing=sorted(req-have); pct=round(len(matched)/len(req)*100) if req else 100
    return pct,matched,missing

class RegisterView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        d=request.data; username=d.get('username') or d.get('email'); email=d.get('email'); password=d.get('password'); role=d.get('role','candidate')
        if role not in ['candidate','recruiter']:
            return Response({'detail':'Only candidate or recruiter accounts can be created here.'},400)
        if not username or not email or not password:return Response({'detail':'username/email/password required'},400)
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():return Response({'detail':'User already exists'},400)
        u=User.objects.create_user(username=username,email=email,password=password,first_name=d.get('first_name',''),last_name=d.get('last_name',''),role=role,phone=d.get('phone',''))
        if role=='candidate': CandidateProfile.objects.create(user=u)
        elif role=='recruiter':
            company=Company.objects.create(name=f"{u.first_name or u.username} Company")
            RecruiterProfile.objects.create(user=u,company=company)
        return Response({'user':UserSerializer(u).data,**tokens(u)},201)
class LoginView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        u=authenticate(username=request.data.get('username') or request.data.get('email'),password=request.data.get('password'))
        if not u:return Response({'detail':'Invalid credentials'},401)
        requested_role=request.data.get('role')
        if requested_role and requested_role != u.role:
            return Response({'detail':f'This login is for {requested_role} accounts. Use the correct portal.'},403)
        return Response({'user':UserSerializer(u).data,**tokens(u)})

class MeView(APIView):
    def get(self,request):
        data=UserSerializer(request.user).data
        if request.user.role=='candidate':
            p=profile(request.user); data['profile']={'location':p.location,'education':p.education,'experience':p.experience,'projects':p.projects,'certifications':p.certifications,'career_interests':p.career_interests,'preferred_location':p.preferred_location,'preferred_work_mode':p.preferred_work_mode,'skills':[{'name':x.skill.name,'status':x.status} for x in p.candidateskill_set.select_related('skill')]}
        return Response(data)
    def put(self,request):
        u=request.user; p=profile(u)
        for f in ['first_name','last_name','email','phone']:
            if f in request.data:setattr(u,f,request.data[f])
        u.save()
        if p:
            for f in ['location','education','experience','projects','certifications','career_interests','preferred_location','preferred_work_mode']:
                if f in request.data:setattr(p,f,request.data[f])
            p.save()
            if 'skills' in request.data:
                for name in request.data['skills']:
                    s,_=Skill.objects.get_or_create(name=str(name).strip())
                    CandidateSkill.objects.get_or_create(candidate=p,skill=s,defaults={'status':'SELF_DECLARED'})
        return Response(UserSerializer(u).data)

class JobListView(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        qs=Job.objects.filter(is_open=True).select_related('company').prefetch_related('required_skills').order_by('-created_at')
        q=request.GET.get('keyword') or request.GET.get('q')
        loc=request.GET.get('location'); mode=request.GET.get('work_mode'); industry=request.GET.get('industry')
        exp=request.GET.get('experience'); jt=request.GET.get('job_type'); company=request.GET.get('company')
        skill=request.GET.get('skill'); min_salary=request.GET.get('min_salary'); max_salary=request.GET.get('max_salary')
        freshness=request.GET.get('freshness')
        if q:qs=qs.filter(Q(title__icontains=q)|Q(description__icontains=q)|Q(company__name__icontains=q)|Q(required_skills__name__icontains=q))
        if loc:qs=qs.filter(location__icontains=loc)
        if mode:qs=qs.filter(work_mode=mode)
        if industry:qs=qs.filter(industry__icontains=industry)
        if exp:qs=qs.filter(experience__icontains=exp)
        if jt:qs=qs.filter(employment_type=jt)
        if company:qs=qs.filter(company__name__icontains=company)
        if skill:qs=qs.filter(required_skills__name__icontains=skill)
        if min_salary:
            try:qs=qs.filter(salary_max__gte=Decimal(min_salary))
            except:pass
        if max_salary:
            try:qs=qs.filter(salary_min__lte=Decimal(max_salary))
            except:pass
        if freshness=='RECENT':
            qs=qs.filter(created_at__gte=timezone.now()-timedelta(days=7))
        return Response(JobSerializer(qs.distinct(),many=True).data)

class JobDetailView(APIView):
    permission_classes=[AllowAny]
    def get(self,request,pk):
        try:
            job=Job.objects.select_related('company').prefetch_related('required_skills').get(pk=pk)
            return Response(JobSerializer(job).data)
        except Job.DoesNotExist:
            return Response({'detail':'Job not found'},404)
    def put(self,request,pk):
        if request.user.role!='recruiter':return Response({'detail':'Recruiter only'},403)
        job=Job.objects.get(pk=pk)
        for f in ['title','location','experience','employment_type','work_mode','industry','description','responsibilities','qualifications','expected_timeline','refund_conditions','deadline','is_open']:
            if f in request.data:setattr(job,f,request.data[f])
        job.save(); return Response(JobSerializer(job).data)
    def patch(self,request,pk):
        if request.user.role!='recruiter':return Response({'detail':'Recruiter only'},403)
        job=Job.objects.select_related('company').get(pk=pk)
        if job.company_id != request.user.recruiter_profile.company_id:return Response({'detail':'You can only manage jobs for your company.'},403)
        if 'is_open' in request.data:
            job.is_open=bool(request.data.get('is_open'))
            job.save(update_fields=['is_open','updated_at'])
        return Response(JobSerializer(job).data)

class JobMatchView(APIView):
    def get(self,request,pk):
        p=profile(request.user); job=Job.objects.get(pk=pk); pct,matched,missing=match_for(p,job)
        return Response({'match_percent':pct,'matched_skills':matched,'missing_skills':missing,'recommended_skills':missing[:5],'explanation':f'{len(matched)} of {len(matched)+len(missing)} required skills matched.'})

class FeePreviewView(APIView):
    def get(self,request):
        p=profile(request.user); count=Application.objects.filter(candidate=p).count(); fee=1000 if count<3 else 5000; return Response({'successful_application_count':count,'next_application_number':count+1,'fee':fee,'currency':'INR','priority':count<3})

class CreateOrderView(APIView):
    def post(self,request):
        p=profile(request.user); job=Job.objects.get(pk=request.data.get('job_id'))
        if not job.is_open:return Response({'detail':'Job is closed'},400)
        if Application.objects.filter(candidate=p,job=job).exists():return Response({'detail':'You have already applied for this job.'},409)
        count=Application.objects.filter(candidate=p).count(); amount=1000 if count<3 else 5000
        if not client:return Response({'detail':'Razorpay is not configured. Add test credentials to backend/.env.'},503)
        try:
            order=client.order.create({'amount':amount*100,'currency':'INR','receipt':f'job-{job.id}-cand-{p.id}-{timezone.now().timestamp()}','notes':{'job_id':str(job.id),'candidate_id':str(p.id)}})
        except Exception:
            return Response({'detail':'Unable to create the Razorpay test order. Please try again.'},502)
        ApplicationPayment.objects.create(candidate=p,job=job,order_id=order['id'],amount=amount,status='PENDING')
        return Response({'order_id':order['id'],'amount':amount,'amount_paise':amount*100,'currency':'INR','key_id':settings.RAZORPAY_KEY_ID})
class VerifyPaymentView(APIView):
    @transaction.atomic
    def post(self,request):
        p=profile(request.user); order_id=request.data.get('razorpay_order_id'); payment_id=request.data.get('razorpay_payment_id'); signature=request.data.get('razorpay_signature')
        try: rec=ApplicationPayment.objects.select_for_update().get(order_id=order_id,candidate=p)
        except ApplicationPayment.DoesNotExist:return Response({'detail':'Payment order not found'},404)
        if rec.status=='SUCCESS' and rec.application:return Response({'application':ApplicationSerializer(rec.application).data,'duplicate':True})
        if not order_id or not payment_id or not signature or not client:
            rec.status='FAILED'; rec.save(); return Response({'detail':'Incomplete payment verification details.'},400)
        try:
            client.utility.verify_payment_signature({'razorpay_order_id':order_id,'razorpay_payment_id':payment_id,'razorpay_signature':signature})
            payment=client.payment.fetch(payment_id)
            if payment.get('order_id') != order_id or int(payment.get('amount',-1)) != int(rec.amount * 100) or payment.get('currency') != rec.currency:
                raise ValueError('Payment details do not match the application order.')
        except Exception:
            rec.status='FAILED'; rec.save(); return Response({'detail':'Payment verification failed. The payment details did not match the application order.'},400)
        if Application.objects.filter(candidate=p,job=rec.job).exists(): rec.status='FAILED'; rec.save(); return Response({'detail':'Already applied; no duplicate charge.'},409)
        count=Application.objects.filter(candidate=p).count(); pct,matched,missing=match_for(p,rec.job); priority='PRIORITY' if count<3 else 'NORMAL'
        app=Application.objects.create(candidate=p,job=rec.job,match_percent=pct,matched_skills=matched,missing_skills=missing,priority_level=priority)
        rec.application=app; rec.payment_id=payment_id; rec.status='SUCCESS'; rec.save()
        Notification.objects.create(user=request.user,message=f'Application submitted for {rec.job.title}.')
        return Response({'application':ApplicationSerializer(app).data,'payment_status':'SUCCESS'})
class ApplicationListView(APIView):
    def get(self,request):
        if request.user.role=='candidate': qs=Application.objects.filter(candidate=profile(request.user)).select_related('job__company').prefetch_related('job__required_skills').order_by('-created_at')
        elif request.user.role=='recruiter':
            company=request.user.recruiter_profile.company
            qs=Application.objects.filter(job__company=company).select_related('candidate__user','job__company').prefetch_related('candidate__candidateskill_set__skill').order_by('-created_at')
        else: qs=Application.objects.all().select_related('candidate__user','job__company')
        priority=request.GET.get('priority'); st=request.GET.get('status'); q=request.GET.get('q')
        if priority=='true':qs=qs.filter(priority_level='PRIORITY')
        if st:qs=qs.filter(status=st)
        if q:qs=qs.filter(Q(candidate__user__username__icontains=q)|Q(candidate__user__first_name__icontains=q)|Q(job__title__icontains=q))
        return Response(ApplicationSerializer(qs,many=True).data)
class RecruiterActionView(APIView):
    def patch(self,request,pk):
        if request.user.role!='recruiter':return Response({'detail':'Recruiter only'},403)
        app=Application.objects.select_related('job__company').get(pk=pk)
        if app.job.company_id != request.user.recruiter_profile.company_id:return Response({'detail':'You can only manage applications for your company.'},403)
        action=request.data.get('action')
        if action not in ['SHORTLISTED','REJECTED','ON_HOLD']:return Response({'detail':'Invalid action'},400)
        app.status=action; app.save(); Notification.objects.create(user=app.candidate.user,message=f'Your application for {app.job.title} is {action.lower().replace('_',' ')}.')
        return Response(ApplicationSerializer(app).data)

class InterviewListCreateView(APIView):
    def get(self,request):
        if request.user.role=='candidate':
            qs=Interview.objects.filter(application__candidate=profile(request.user))
        elif request.user.role=='recruiter':
            qs=Interview.objects.filter(application__job__company=request.user.recruiter_profile.company)
        else:
            qs=Interview.objects.all()
        return Response([{'id':i.id,'application_id':i.application_id,'job':i.application.job.title,'candidate':i.application.candidate.user.get_full_name() or i.application.candidate.user.username,'date':i.date,'time':i.time,'type':i.interview_type,'location':i.location,'meeting_link':i.meeting_link,'status':i.status} for i in qs.order_by('date','time')])
    def post(self,request):
        if request.user.role!='recruiter':return Response({'detail':'Recruiter only'},403)
        app=Application.objects.select_related('job__company').get(pk=request.data['application_id'])
        if app.job.company_id != request.user.recruiter_profile.company_id:return Response({'detail':'You can only schedule interviews for your company.'},403)
        i=Interview.objects.create(application=app,interview_type=request.data.get('interview_type','Technical'),date=request.data['date'],time=request.data['time'],location=request.data.get('location',''),meeting_link=request.data.get('meeting_link',''))
        Notification.objects.create(user=app.candidate.user,message=f'Interview scheduled for {app.job.title} on {i.date} at {i.time}.'); return Response({'id':i.id,'status':i.status},201)
class InterviewAttendanceView(APIView):
    def patch(self,request,pk):
        if request.user.role!='recruiter':return Response({'detail':'Recruiter only'},403)
        i=Interview.objects.select_related('application__job__company').get(pk=pk)
        if i.application.job.company_id != request.user.recruiter_profile.company_id:return Response({'detail':'You can only update interviews for your company.'},403)
        s=request.data.get('status')
        if s not in dict(Interview.STATUS):return Response({'detail':'Invalid interview status'},400)
        i.status=s; i.save(); app=i.application
        if s=='ATTENDED':
            app.status=app.status if app.status in ['SELECTED','REJECTED'] else 'SHORTLISTED'
        elif s=='NO_SHOW':app.status='NO_SHOW'
        app.save(); self._refund_state(app)
        return Response({'status':i.status,'application_status':app.status})
    def _refund_state(self,app):
        try:pay=app.payment
        except ApplicationPayment.DoesNotExist:return
        r,_=Refund.objects.get_or_create(application=app,defaults={'candidate':app.candidate,'payment':pay,'amount':pay.amount,'status':'PENDING'})
        if app.status in ['SELECTED','REJECTED']:
            r.status='ELIGIBLE'; r.reason='Candidate attended hiring process and hiring outcome recorded.'; r.save()
        elif app.status=='NO_SHOW':r.status='NOT_ELIGIBLE'; r.reason='Candidate did not attend required hiring process.'; r.save()

class HiringOutcomeView(APIView):
    def patch(self,request,pk):
        if request.user.role!='recruiter':return Response({'detail':'Recruiter only'},403)
        app=Application.objects.select_related('job__company').get(pk=pk)
        if app.job.company_id != request.user.recruiter_profile.company_id:return Response({'detail':'You can only update applications for your company.'},403)
        outcome=request.data.get('outcome')
        if outcome not in ['SELECTED','REJECTED','ON_HOLD']:return Response({'detail':'Invalid outcome'},400)
        attended=Interview.objects.filter(application=app,status__in=['ATTENDED','COMPLETED']).exists()
        if not attended:
            return Response({'detail':'Mark an interview as attended before recording a hiring outcome.'},400)
        app.status=outcome; app.save()
        pay=getattr(app,'payment',None)
        if pay:
            r,_=Refund.objects.get_or_create(application=app,defaults={'candidate':app.candidate,'payment':pay,'amount':pay.amount})
            if outcome in ['SELECTED','REJECTED']:
                r.status='ELIGIBLE'; r.reason='Eligible after attended hiring process and final hiring outcome.'
            else:
                r.status='PENDING'; r.reason='Application is on hold; refund remains pending until a final hiring outcome is recorded.'
            r.save()
        Notification.objects.create(user=app.candidate.user,message=f'Your application for {app.job.title} is {outcome.lower().replace('_',' ')}.')
        return Response(ApplicationSerializer(app).data)

class RefundListView(APIView):
    def get(self,request):
        if request.user.role=='candidate':
            qs=Refund.objects.filter(candidate=profile(request.user))
        elif request.user.role=='recruiter':
            qs=Refund.objects.filter(application__job__company=request.user.recruiter_profile.company)
        else:
            qs=Refund.objects.all()
        return Response([{'id':r.id,'application_id':r.application_id,'job':r.application.job.title,'amount':r.amount,'status':r.status,'reason':r.reason,'refund_id':r.refund_id} for r in qs.select_related('application__job')])
class RefundInitiateView(APIView):
    def post(self,request,application_id):
        if request.user.role!='admin':return Response({'detail':'Admin only'},403)
        r=Refund.objects.select_related('payment','application').get(application_id=application_id)
        if r.status not in ['ELIGIBLE','FAILED']:return Response({'detail':f'Refund is {r.status}'},400)
        if not client:return Response({'detail':'Razorpay is not configured'},503)
        if not r.payment.payment_id:return Response({'detail':'Payment ID missing'},400)
        try:
            result=client.payment.refund(r.payment.payment_id,{'amount':int(r.amount*100),'notes':{'application_id':str(r.application_id)}})
            r.refund_id=result['id']; r.status='PROCESSED' if result.get('status') in ['processed','completed'] else 'INITIATED'; r.initiated_at=timezone.now(); r.completed_at=timezone.now() if r.status=='PROCESSED' else None; r.save(); r.payment.status='REFUNDED'; r.payment.save(); return Response({'refund_id':r.refund_id,'status':r.status})
        except Exception as e:r.status='FAILED'; r.reason=str(e)[:240]; r.save(); return Response({'detail':'Refund request failed'},502)

class AssessmentListView(APIView):
    def get(self,request):return Response(AssessmentSerializer(Assessment.objects.all(),many=True).data)
class AssessmentDetailView(APIView):
    def get(self,request,pk):
        a=Assessment.objects.get(pk=pk); return Response({'id':a.id,'title':a.title,'category':a.category,'duration_minutes':a.duration_minutes,'questions':[{'id':q.id,'text':q.text,'options':q.options} for q in a.questions.all()]})
class AssessmentSubmitView(APIView):
    def post(self,request,pk):
        a=Assessment.objects.get(pk=pk); answers=request.data.get('answers',{}); qs=list(a.questions.all()); score=sum(1 for q in qs if int(answers.get(str(q.id),-1))==q.answer); r=AssessmentResult.objects.create(candidate=profile(request.user),assessment=a,score=score,total=len(qs)); return Response({'score':score,'total':len(qs),'percentage':round(score/len(qs)*100) if qs else 0,'result_id':r.id})

class ResumeListCreateView(APIView):
    def get(self,request):return Response(ResumeSerializer(Resume.objects.filter(candidate=profile(request.user)),many=True).data)
    def post(self,request):
        d=request.data.copy(); d.pop('candidate',None); r=Resume.objects.create(candidate=profile(request.user),**d); return Response(ResumeSerializer(r).data,201)

class ResumeUploadView(APIView):
    def post(self,request):
        p=profile(request.user); uploaded=request.FILES.get('file')
        if not uploaded:return Response({'detail':'Please choose a PDF, DOC or DOCX file.'},400)
        ext=uploaded.name.lower().rsplit('.',1)[-1] if '.' in uploaded.name else ''
        if ext not in {'pdf','doc','docx'}:return Response({'detail':'Only PDF, DOC and DOCX resume files are supported.'},400)
        if uploaded.size > 5*1024*1024:return Response({'detail':'Resume file must be 5 MB or smaller.'},400)
        path=default_storage.save(f'resumes/{request.user.id}/{uploaded.name}',uploaded)
        data={'file_name':uploaded.name,'file_path':path,'file_url':default_storage.url(path),'file_size':uploaded.size,'file_type':ext}
        r=Resume.objects.create(candidate=p,name=request.data.get('name') or uploaded.name,data=data)
        return Response(ResumeSerializer(r).data,201)
class ResumeDetailView(APIView):
    def put(self,request,pk):
        r=Resume.objects.get(pk=pk,candidate=profile(request.user)); r.name=request.data.get('name',r.name); r.data=request.data.get('data',r.data); r.save(); return Response(ResumeSerializer(r).data)

class InternshipListView(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        qs=Internship.objects.filter(is_open=True).select_related('company').prefetch_related('skills'); q=request.GET.get('q'); loc=request.GET.get('location'); mode=request.GET.get('work_mode'); paid=request.GET.get('paid')
        if q:qs=qs.filter(Q(role__icontains=q)|Q(company__name__icontains=q))
        if loc:qs=qs.filter(location__icontains=loc)
        if mode:qs=qs.filter(work_mode=mode)
        if paid in ['true','false']:qs=qs.filter(paid=paid=='true')
        return Response(InternshipSerializer(qs,many=True).data)

class DashboardView(APIView):
    def get(self, request):

        # =========================
        # CANDIDATE DASHBOARD
        # =========================
        if request.user.role == 'candidate':
            p = profile(request.user)

            apps = Application.objects.filter(candidate=p)
            results = AssessmentResult.objects.filter(candidate=p)
            interviews = Interview.objects.filter(
                application__candidate=p
            )
            refunds = Refund.objects.filter(candidate=p)

            return Response({
                'applications': apps.count(),
                'priority_applications': apps.filter(
                    priority_level='PRIORITY'
                ).count(),
                'shortlisted': apps.filter(
                    status='SHORTLISTED'
                ).count(),
                'interviews': interviews.count(),
                'selected': apps.filter(
                    status='SELECTED'
                ).count(),
                'rejected': apps.filter(
                    status='REJECTED'
                ).count(),
                'no_shows': apps.filter(
                    status='NO_SHOW'
                ).count(),
                'average_match': round(
                    apps.aggregate(
                        v=Avg('match_percent')
                    )['v'] or 0
                ),
                'assessment_results': results.count(),
                'refunds': refunds.count()
            })

        # =========================
        # RECRUITER DASHBOARD
        # =========================
        if request.user.role == 'recruiter':

            # Get the company assigned to the logged-in recruiter
            recruiter = request.user.recruiter_profile
            company = recruiter.company

            # IMPORTANT:
            # Only applications belonging to jobs
            # posted by this recruiter's company
            apps = Application.objects.filter(
                job__company_id=company.id
            )

            # Only interviews belonging to this recruiter's company
            interviews = Interview.objects.filter(
                application__job__company_id=company.id
            )

            return Response({
                'total_applications': apps.count(),

                'priority_applications': apps.filter(
                    priority_level='PRIORITY'
                ).count(),

                'shortlisted': apps.filter(
                    status='SHORTLISTED'
                ).count(),

                'interviews': interviews.count(),

                'selected': apps.filter(
                    status='SELECTED'
                ).count(),

                'rejected': apps.filter(
                    status='REJECTED'
                ).count(),

                'no_shows': apps.filter(
                    status='NO_SHOW'
                ).count()
            })

        # =========================
        # ADMIN DASHBOARD
        # =========================
        return Response({
            'users': User.objects.count(),
            'candidates': User.objects.filter(
                role='candidate'
            ).count(),
            'companies': Company.objects.count(),
            'jobs': Job.objects.count(),
            'internships': Internship.objects.count(),
            'applications': Application.objects.count(),
            'payments': ApplicationPayment.objects.count(),
            'refunds': Refund.objects.count(),
            'assessments': Assessment.objects.count(),
            'reports': Report.objects.count()
        })
class SavedJobListView(APIView):
    def get(self,request):
        p=profile(request.user)
        rows=SavedJob.objects.filter(candidate=p).select_related('job__company')
        return Response([{'id':x.id,'job_id':x.job_id,'job':JobSerializer(x.job).data,'created_at':x.created_at} for x in rows])
    def post(self,request):
        p=profile(request.user)
        try:j=Job.objects.get(pk=request.data.get('job_id'),is_open=True)
        except Job.DoesNotExist:return Response({'detail':'Job not found'},404)
        x,_=SavedJob.objects.get_or_create(candidate=p,job=j)
        return Response({'id':x.id,'job_id':j.id,'saved':True},201)
    def delete(self,request):
        p=profile(request.user); jid=request.data.get('job_id')
        SavedJob.objects.filter(candidate=p,job_id=jid).delete()
        return Response({'saved':False})

class CompanyListView(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        qs=Company.objects.all().prefetch_related('jobs')
        q=request.GET.get('q')
        if q: qs=qs.filter(Q(name__icontains=q)|Q(location__icontains=q)|Q(description__icontains=q))
        return Response(CompanySerializer(qs,many=True).data)

class NotificationView(APIView):
    def get(self,request):return Response([{'id':n.id,'message':n.message,'read':n.read,'created_at':n.created_at} for n in request.user.notifications.order_by('-created_at')[:50]])
class MessageView(APIView):
    def get(self,request):
        qs=Message.objects.filter(Q(sender=request.user)|Q(recipient=request.user)).select_related('sender','recipient'); return Response([{'id':m.id,'sender':m.sender.username,'recipient':m.recipient.username,'body':m.body,'read':m.read,'created_at':m.created_at} for m in qs.order_by('-created_at')])
    def post(self,request):
        to=User.objects.get(id=request.data['recipient_id']); m=Message.objects.create(sender=request.user,recipient=to,body=request.data['body']); return Response({'id':m.id},201)
class ReportView(APIView):
    def post(self,request):
        r=Report.objects.create(reporter=request.user,target_type=request.data.get('target_type','job'),target_id=request.data['target_id'],reason=request.data['reason'],details=request.data.get('details','')); return Response({'id':r.id,'status':r.status},201)
class AdminCompaniesView(APIView):
    def get(self,request):
        if request.user.role!='admin':return Response({'detail':'Admin only'},403)
        return Response(CompanySerializer(Company.objects.all(),many=True).data)
    def patch(self,request,pk):
        if request.user.role!='admin':return Response({'detail':'Admin only'},403)
        c=Company.objects.get(pk=pk); c.verified=bool(request.data.get('verified',c.verified)); c.save(); return Response(CompanySerializer(c).data)
class RecruiterJobListCreateView(APIView):
    def get(self,request):
        if request.user.role not in ['recruiter','admin']: return Response({'detail':'Recruiter only'},403)
        qs=Job.objects.filter(company=request.user.recruiter_profile.company) if request.user.role=='recruiter' else Job.objects.all()
        qs=qs.select_related('company').prefetch_related('required_skills').order_by('-created_at')
        return Response(JobSerializer(qs,many=True).data)
    def post(self,request):
        if request.user.role!='recruiter': return Response({'detail':'Recruiter only'},403)
        try: company=request.user.recruiter_profile.company
        except RecruiterProfile.DoesNotExist: return Response({'detail':'Recruiter company profile missing'},400)
        d=request.data
        company_name=str(d.get('company_name') or '').strip()
        if company_name:
            company.name=company_name
            company.save(update_fields=['name'])
        title=str(d.get('title') or '').strip()
        description=str(d.get('description') or '').strip()
        if not title or not description:
            return Response({'detail':'Job title and description are required.'},400)
        try:
            salary_min=Decimal(str(d.get('salary_min',400000)))
            salary_max=Decimal(str(d.get('salary_max',700000)))
        except Exception:
            return Response({'detail':'Salary must contain valid numbers.'},400)
        if salary_min < 0 or salary_max < 0 or salary_min > salary_max:
            return Response({'detail':'Please enter a valid salary range.'},400)
        deadline=d.get('deadline') or None
        try:
            j=Job.objects.create(company=company,title=title,location=str(d.get('location') or 'Hyderabad').strip(),salary_min=salary_min,salary_max=salary_max,experience=str(d.get('experience') or '0–2 years').strip(),employment_type=d.get('employment_type','FULL_TIME'),work_mode=d.get('work_mode','HYBRID'),industry=str(d.get('industry') or 'Technology').strip(),description=description,responsibilities=str(d.get('responsibilities') or '').strip(),qualifications=str(d.get('qualifications') or '').strip(),hiring_stages=d.get('hiring_stages') or ['Assessment','Technical Interview','HR'],expected_timeline=str(d.get('expected_timeline') or '2–3 weeks').strip(),refund_conditions=str(d.get('refund_conditions') or 'Eligible after attending the hiring process').strip(),deadline=deadline)
            names=d.get('required_skills') or []
            if isinstance(names,str):
                names=[x.strip() for x in names.split(',') if x.strip()]
            j.required_skills.set([Skill.objects.get_or_create(name=str(x).strip())[0] for x in names if str(x).strip()])
            return Response(JobSerializer(j).data,201)
        except Exception as exc:
            return Response({'detail':f'Could not publish the job: {exc}'},400)

class AiAssistantView(APIView):
    def post(self,request):
        p=profile(request.user); q=(request.data.get('message') or '').lower(); skills=list(p.skills.values_list('name',flat=True));
        if 'skill' in q or 'gap' in q:
            return Response({'reply':f'Your current skill passport includes {", ".join(skills) or "no declared skills"}. Open a job to see exact matched and missing skills.'})
        if 'resume' in q:
            return Response({'reply':'Keep your resume ATS-friendly: lead with role-relevant skills, measurable project outcomes, education, certifications and a concise summary.'})
        if 'interview' in q:
            return Response({'reply':'Prepare around the Job DNA: required skills, hiring stages, project examples, fundamentals and your top missing skills.'})
        if 'job' in q or 'career' in q:
            return Response({'reply':'Start with jobs where your match is strongest, then close the highest-impact skill gaps through assessments and projects.'})
        return Response({'reply':'I can help with career guidance, job explanations, skill gaps, resumes and interview preparation. Ask me about one of these topics.'})

class WebhookView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        secret=settings.RAZORPAY_WEBHOOK_SECRET
        if secret:
            sig=request.headers.get('X-Razorpay-Signature',''); body=request.body; expected=hmac.new(secret.encode(),body,hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig,expected):return Response({'detail':'Invalid webhook signature'},400)
        return Response({'received':True})
