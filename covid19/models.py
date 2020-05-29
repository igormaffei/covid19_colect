from django.contrib.auth.models import User
from django.db import models
from django.contrib import admin
from django.utils.html import mark_safe
from django.http import HttpResponse

#Constantes
GENDER_TYPE = (
        ('M','Masculino'),
        ('F','Feminino'),
    )

YESNO_TYPE = (
        (0,'Não'),
        (1,'Sim'),
    )

# Tipo da Imagem
# Ex: (TC ou RAIO-X)
class ImageType(models.Model):
    desc_image_type = models.CharField(max_length=100, unique=True,verbose_name='Descição do Tipo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.desc_image_type

# Origem da Imagem
# Ex:(DataSet X, Y ou Z, ou próprio site)
class ImageSource(models.Model):
    desc_source = models.CharField(max_length=60, unique=True,verbose_name='Descição da Fonte')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.desc_source

# Tipo de Visualização da Imagem
# EX: (LA, LE)
class ViewType(models.Model):
    desc_view_type = models.CharField(max_length=45, unique=True,verbose_name='Tipo de Visualização')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.desc_view_type

# Doenças Encontrada na Imagem
# EX: (Covid19, Pneoumonia comum, Normal-Saudável)
class DiseaseType(models.Model):
    disease_name = models.CharField(max_length=100, unique=True,verbose_name='Nome da Doença')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.disease_name

# Razão de Recusa de aprovação de uma imagem.
# EX: ( Não é um TC ou RAIo-X válido, não é uma pessoa, foto inválida)
class Reason(models.Model):
    desc_reason = models.CharField(max_length=255, unique=True,verbose_name='Descrição da Razão de Recusa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.desc_reason

#Imagem candidata a entrar no DataSet para treinamento
class Image(models.Model):
    gender = models.CharField(max_length=1,blank=True, null=True,
                              verbose_name='Sexo do Paciente',
                              choices=GENDER_TYPE)
    age = models.IntegerField(blank=True, null=True,verbose_name='Idade do Paciente')
    survival = models.IntegerField(blank=True, null=True,verbose_name='Paciente Sobreviveu')
    original_image = models.ImageField(upload_to="images/origin",
                                       unique=True,
                                       verbose_name='Imagem')
    resized_image = models.CharField(max_length=500,
                                     unique=True,
                                     blank=True, null=True,
                                     verbose_name='Imagem Modificada',
                                     editable=False)
    image_type = models.ForeignKey(ImageType,
                                   on_delete=models.CASCADE,
                                   related_name='ImageType')
    view_type = models.ForeignKey(ViewType,
                                  blank=True, null=True,
                                  on_delete=models.CASCADE,
                                  related_name='ViewType')

    disease = models.ForeignKey(DiseaseType,
                                on_delete=models.CASCADE,
                                related_name='Disease')

    image_source = models.ForeignKey(ImageSource,
                                     on_delete=models.CASCADE,
                                     related_name='ImageSource')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def image_tag(self):
        return mark_safe('<img src="images/origin/%s" width="150" height="150" />' % (self.original_image))
    image_tag.short_description = 'Image'

# Indica se uma determinada imagem foi aprovada e motivo da não aprovação.
class ImageApproved(models.Model):
    image = models.ForeignKey(Image,
                              on_delete=models.CASCADE,
                              related_name='Image')
    reason = models.ForeignKey(Reason,
                               on_delete=models.CASCADE,
                              related_name='Reason', verbose_name='Razão/Motivo')
    user = models.ForeignKey(User,
                             related_name='UserApprove',
                             on_delete=models.CASCADE,
                             verbose_name='Usuário')
    valid = models.IntegerField(verbose_name='Válido', default=0, choices=YESNO_TYPE)
    obs = models.CharField(max_length=500, blank=True, null=True, verbose_name='Observação')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    exclude = ['user', ]

    def __str__(self):
        return self.image.original_image

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

class DiseaseListFilter(admin.SimpleListFilter):
    """
    This filter is an example of how to combine two different Filters to work together.
    """
    # Human-readable title which will be displayed in the right admin sidebar just above the filter
    # options.
    title = 'disease Types'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'disease'

    # Custom attributes
    related_filter_parameter = 'disease__id__exact'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        list_of_questions = []
        queryset = DiseaseType.objects.order_by('disease_name')
        if self.related_filter_parameter in request.GET:
            queryset = queryset.filter(id=request.GET[self.related_filter_parameter])
        for disease in queryset:
            list_of_questions.append(
                (disease.id, disease.disease_name)
            )
        return sorted(list_of_questions, key=lambda tp: tp[1])

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value to decide how to filter the queryset.
        if self.value():
            return queryset.filter(id=self.value())
        return queryset


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    actions = ['download_csv','download_images']
    list_display = ('image_tag','original_image', 'disease', 'view_type','image_source', )
    list_filter = ('disease', DiseaseListFilter)
    readonly_fields = ['image_tag']

    def download_csv(self, request, queryset):
        import csv
        from io import StringIO

        f = StringIO()
        writer = csv.writer(f)
        writer.writerow(['original_image', 'disease', 'view_type', 'image_source'])
        for s in queryset:
            writer.writerow([s.original_image, s.disease, s.view_type, s.image_source])

        f.seek(0)
        response = HttpResponse(f, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=images.csv'
        return response

    download_csv.short_description = "Download CSV"

    def download_images(self, request, queryset):
        import zipfile
        import os
        from io import BytesIO

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for s in queryset:
                filename = os.path.join(BASE_DIR,("images/origin/%s" % s.original_image))
                zip_file.write(filename, arcname=os.path.basename(filename))

        zip_buffer.seek(0)
        resp = HttpResponse(zip_buffer, content_type='application/zip')
        resp['Content-Disposition'] = 'attachment; filename = images.zip'
        return resp

    download_images.short_description = "Download images as ZIP"