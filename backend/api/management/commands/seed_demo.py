from django.core.management.base import BaseCommand
from api.models import *
from django.contrib.auth import get_user_model
from datetime import date,timedelta
U=get_user_model()

class Command(BaseCommand):
 def handle(self,*args,**kwargs):
  # Reset the development database so seed_demo produces only clean demo data.
  from django.core.management import call_command
  self.stdout.write('Resetting existing database data...')
  call_command('flush', interactive=False, verbosity=0)
  skill_names=['Python','Django','SQL','REST','Git','JavaScript','React','HTML/CSS','Java','Aptitude','PostgreSQL','Docker','AWS','C#','Communication','Testing','Cypress','OWASP','MySQL','Data Structures','Marketing','SEO','Sales','Excel','Healthcare','Figma','Product Management','Machine Learning','Pandas','Power BI']
  skills={n:Skill.objects.get_or_create(name=n)[0] for n in skill_names}
  companies=[]
  for name,loc in [('NovaTech Systems','Hyderabad'),('BlueOrbit Labs','Bengaluru'),('FinEdge','Pune'),('HealthStack','Hyderabad'),('CloudCraft','Hyderabad'),('GrowthLoop','Mumbai'),('CareBridge','Chennai'),('DesignMint','Bengaluru')]:
   companies.append(Company.objects.get_or_create(name=name,defaults={'location':loc,'description':f'{name} builds technology products and digital platforms.','verified':True})[0])
  jobs=[
   ('Junior Software Engineer',companies[0],['Python','Django','SQL','REST','Git'],'HITEC City','Technology',500000,800000),
   ('React Developer',companies[1],['JavaScript','React','HTML/CSS','Git'],'Bengaluru','Technology',550000,900000),
   ('Backend Engineer',companies[2],['Python','Django','PostgreSQL','Docker'],'Pune','Technology',650000,1000000),
   ('QA Automation Engineer',companies[3],['JavaScript','Cypress','SQL','Testing'],'Gachibowli','Technology',500000,850000),
   ('Security Engineer',companies[4],['Python','OWASP','Git','AWS'],'Financial District','Cybersecurity',700000,1200000),
   ('Java Developer',companies[0],['Java','SQL','REST'],'Madhapur','Technology',550000,900000),
   ('Data Analyst',companies[2],['SQL','Python','Communication'],'Pune','Analytics',500000,850000),
   ('Full Stack Developer',companies[1],['JavaScript','React','Python','SQL'],'Bengaluru','Technology',650000,1100000),
   ('Cloud Intern',companies[4],['AWS','Python','Git'],'Kondapur','Cloud',180000,300000),
   ('Graduate Engineer Trainee',companies[3],['Aptitude','Java','SQL'],'Hyderabad','Technology',400000,650000),
   ('Digital Marketing Associate',companies[5],['Marketing','SEO','Communication'],'Madhapur','Marketing',450000,850000),
   ('Sales Development Executive',companies[5],['Sales','Communication','Excel'],'Hyderabad','Sales',400000,750000),
   ('Healthcare Operations Analyst',companies[6],['Healthcare','Excel','Communication'],'Chennai','Healthcare',450000,800000),
   ('Product Designer',companies[7],['Figma','Product Management','Communication'],'Bengaluru','Design',550000,950000),
   ('AI / ML Engineer',companies[0],['Python','Machine Learning','Pandas','SQL'],'Raidurg','Artificial Intelligence',800000,1400000),
  ]
  for title,c,ss,loc,industry,smin,smax in jobs:
   j,_=Job.objects.get_or_create(title=title,company=c,defaults={'location':loc,'salary_min':smin,'salary_max':smax,'experience':'0–2 years','employment_type':'FULL_TIME','work_mode':'HYBRID','industry':industry,'description':f'Build and improve real-world products at {c.name}.','responsibilities':'Design, implement, test and document features.','qualifications':'B.Tech/BE or equivalent; strong fundamentals.','hiring_stages':['Assessment','Technical Interview','HR'],'expected_timeline':'2–3 weeks','deadline':date.today()+timedelta(days=30)})
   for field,value in [('location',loc),('industry',industry),('salary_min',smin),('salary_max',smax)]: setattr(j,field,value)
   j.save(update_fields=['location','industry','salary_min','salary_max'])
   j.required_skills.set([skills[x] for x in ss])
  for i,c in enumerate(companies[:5]):
   ins,_=Internship.objects.get_or_create(role=['Software Engineering Intern','Frontend Intern','Data Intern','QA Intern','Cloud Intern'][i],company=c,defaults={'location':c.location,'work_mode':'Hybrid','stipend':15000,'duration':'3 months','paid':True,'conversion_info':'Performance-based full-time conversion may be considered.'}); ins.skills.set([skills[x] for x in ['Python','Git','SQL']])
  for cat,qs in {'Python':['What is a Python list?','Which keyword defines a function?','What does len() return?','Which type is immutable?','What is a dictionary?','What is PEP8?','What is a tuple?','What is exception handling?','What is a virtual environment?','What is list comprehension?'],'SQL':['What does SELECT do?','What is a primary key?','What is JOIN?','What is GROUP BY?','What is an index?','What is normalization?','What is WHERE?','What is HAVING?','What is COUNT?','What is a foreign key?'],'JavaScript':['What is let?','What is const?','What is a promise?','What is DOM?','What is map()?','What is async/await?','What is closure?','What is JSON?','What is an event?','What is destructuring?']}.items():
   a,_=Assessment.objects.get_or_create(title=f'{cat} Fundamentals',category=cat,defaults={'duration_minutes':15})
   if not a.questions.exists():
    for idx,q in enumerate(qs): Question.objects.create(assessment=a,text=q,options=['Option A','Option B','Option C','Option D'],answer=0)
  for email,role,pwd in [('candidate@example.com','candidate','Candidate@123'),('recruiter@example.com','recruiter','Recruiter@123'),('admin@example.com','admin','Admin@123')]:
   u,_=U.objects.get_or_create(username=email,defaults={'email':email,'role':role,'first_name':role.title()}); u.role=role; u.set_password(pwd); u.is_staff=role=='admin'; u.is_superuser=role=='admin'; u.save()
   if role=='candidate':
    p,_=CandidateProfile.objects.get_or_create(user=u,defaults={'location':'Hyderabad','education':'B.Tech Information Technology','experience':'Fresher','preferred_work_mode':'Hybrid'}); [CandidateSkill.objects.get_or_create(candidate=p,skill=skills[x],defaults={'status':'SELF_DECLARED'}) for x in ['Python','SQL','Git']]
   if role=='recruiter': RecruiterProfile.objects.get_or_create(user=u,company=companies[0])
  self.stdout.write(self.style.SUCCESS('Demo data created: 15 jobs, 5 internships, 8 companies, 3 demo accounts.'))
