from datetime import date

from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'phone'
        ]


class CompanySerializer(serializers.ModelSerializer):
    job_count = serializers.IntegerField(
        source='jobs.count',
        read_only=True
    )

    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'description',
            'website',
            'location',
            'verified',
            'job_count'
        ]


class JobSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    required_skills = serializers.SerializerMethodField()
    job_freshness = serializers.SerializerMethodField()
    salary = serializers.SerializerMethodField()
    hiring_signal = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'company',
            'location',
            'salary_min',
            'salary_max',
            'salary',
            'experience',
            'employment_type',
            'work_mode',
            'industry',
            'description',
            'responsibilities',
            'qualifications',
            'hiring_stages',
            'expected_timeline',
            'application_fee',
            'refund_conditions',
            'deadline',
            'created_at',
            'updated_at',
            'is_open',
            'required_skills',
            'job_freshness',
            'hiring_signal'
        ]

    def get_required_skills(self, obj):
        return list(
            obj.required_skills.values_list(
                'name',
                flat=True
            )
        )

    def get_salary(self, obj):
        return (
            f'₹{obj.salary_min / 100000:.1f}–'
            f'₹{obj.salary_max / 100000:.1f} LPA'
        )

    def get_job_freshness(self, obj):
        from django.utils.timezone import now

        today = now().date()
        days = (now() - obj.created_at).days

        # Recruiter manually closed the job
        if not obj.is_open:
            return 'Closed'

        deadline = obj.deadline

        # Convert string deadline to a Python date if necessary
        if isinstance(deadline, str):
            try:
                deadline = date.fromisoformat(
                    deadline.strip()
                )
            except (ValueError, TypeError):
                deadline = None

        # Only perform date comparisons when deadline
        # is actually a date
        if isinstance(deadline, date):

            if deadline <= today:
                return 'Closed'

            if (deadline - today).days <= 7:
                return 'Closing Soon'

        # Recently posted
        if days <= 7:
            return 'Recently Posted'

        return 'Active'

    def get_hiring_signal(self, obj):
        return (
            'Verified company'
            if obj.company.verified
            else 'Company profile available'
        )


class InternshipSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Internship
        fields = '__all__'

    def get_skills(self, obj):
        return list(
            obj.skills.values_list(
                'name',
                flat=True
            )
        )


class AssessmentSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(
        source='questions.count',
        read_only=True
    )

    class Meta:
        model = Assessment
        fields = [
            'id',
            'title',
            'category',
            'duration_minutes',
            'question_count'
        ]


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ['candidate']


class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    candidate = serializers.StringRelatedField()
    refund_status = serializers.SerializerMethodField()
    payment = serializers.SerializerMethodField()
    interview = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id',
            'candidate',
            'job',
            'match_percent',
            'matched_skills',
            'missing_skills',
            'priority_level',
            'status',
            'created_at',
            'refund_status',
            'payment',
            'interview'
        ]

    def get_refund_status(self, obj):
        try:
            return obj.refund.status
        except Refund.DoesNotExist:
            return 'PENDING'

    def get_payment(self, obj):
        try:
            p = obj.payment

            return {
                'amount': str(p.amount),
                'currency': p.currency,
                'status': p.status,
                'payment_id': p.payment_id,
                'order_id': p.order_id,
                'method': p.payment_method
            }

        except ApplicationPayment.DoesNotExist:
            return None

    def get_interview(self, obj):
        i = obj.interviews.order_by(
            '-date',
            '-time'
        ).first()

        if not i:
            return None

        return {
            'id': i.id,
            'date': i.date,
            'time': i.time,
            'type': i.interview_type,
            'location': i.location,
            'meeting_link': i.meeting_link,
            'status': i.status
        }