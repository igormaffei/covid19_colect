from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from covid19.models import *
import csv

class Command(BaseCommand):
    help = 'Importa planilhas CSV para o modelo do Covid-19'

    def add_arguments(self, parser):
        parser.add_argument('file_names', nargs='+', type=None)

    def handle(self, *args, **options):
        for file_name in options['file_names']:
            with open(file_name, mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        print(f'Column names : {", ".join(row)}')
                        line_count += 1

                    self.import_row(row)
                    line_count += 1
                print(f'Processed {line_count} lines.')

    def import_row(self, row):
        try:
            image = Image()
            if (row['age']):
                image.age = row['age']
            if (row['sex']):
                image.gender = row['sex']

            image.disease = self.get_deseases(row['finding'])

            if (row['survival']):
                image.survival = row['survival'] == 'Y' if 1 else 0
            image.image_type = self.get_image_type(row['modality'])
            image.view_type = self.get_view_type(row['view'])
            image.original_image = row['original_image']

            if (row['resize_image']):
                image.resized_image = row['resize_image']

            image.image_source = self.get_soruce(row['Dataset_origin'])
            image.save()

            self.stdout.write(
                self.style.SUCCESS('{} - {}: {}'.format(
                    row['Dataset_origin'],
                    row['finding'],
                    row['original_image'])
                ))
        except Exception as ex:
            self.stdout.write(
                self.style.ERROR('{} - {}: {} - ERROR {}'.format(
                    row['Dataset_origin'],
                    row['finding'],
                    row['original_image'],
                    ex)
                ))

    def get_deseases(self, name):
        desease = DiseaseType.objects.filter(Q(disease_name__iexact=name))
        if desease.exists():
            return desease[0]
        else:
            desease = DiseaseType()
            desease.disease_name = name
            desease.save()
            return desease

    def get_image_type(self, name):
        image_type = ImageType.objects.filter(Q(desc_image_type__iexact=name))
        if image_type.exists():
            return image_type[0]
        else:
            return ImageType.objects.get(id=1)

    def get_view_type(self, name):
        view_type = ViewType.objects.filter(Q(desc_view_type__iexact=name))
        if view_type.exists():
            return view_type[0]
        else:
            return None

    def get_soruce(self, name):
        source = ImageSource.objects.filter(Q(desc_source__iexact=name))
        if source.exists():
            return source[0]
        else:
            return ImageSource.objects.get(id=1)




