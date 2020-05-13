from django.contrib.auth.models import User
from django.db import models

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

