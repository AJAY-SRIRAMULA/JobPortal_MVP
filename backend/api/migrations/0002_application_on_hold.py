from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies=[('api','0001_initial')]
    operations=[
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.CharField(choices=[('APPLIED','Applied'),('SHORTLISTED','Shortlisted'),('ON_HOLD','On Hold'),('REJECTED','Rejected'),('SELECTED','Selected'),('NO_SHOW','No-Show')],default='APPLIED',max_length=20),
        ),
    ]
