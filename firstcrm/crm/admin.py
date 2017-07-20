from django.contrib import admin

# Register your models here.
from crm import models


admin.site.register(models.School)
admin.site.register(models.UserProfile)
admin.site.register(models.Customer)
admin.site.register(models.CustomerTrackRecord)
admin.site.register(models.Course)
admin.site.register(models.ClassList)
admin.site.register(models.CourseRecord)
admin.site.register(models.StudyRecord)
