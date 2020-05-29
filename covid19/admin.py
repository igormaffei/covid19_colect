from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(ImageType)
admin.site.register(ImageSource)
admin.site.register(ViewType)
admin.site.register(DiseaseType)
admin.site.register(Reason)
admin.site.unregister(Image)
admin.site.register(Image, ImageAdmin)
admin.site.register(ImageApproved)