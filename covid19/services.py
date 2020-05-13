import csv

from django.db.models import Q

from covid19.models import *

def get_deseases(name):
    desease = DiseaseType.objects.filter(Q(disease_name__iexact=name))
    if desease.exists():
        return desease[0]
    else:
        desease = DiseaseType()
        desease.disease_name = name
        desease.save()
        return desease

def get_view_type(name):
    view_type = ViewType.objects.filter(Q(view_type_name__iexact=name))
    if view_type.exists():
        return view_type[0]
    else:
        return None

def get_soruce(name):
    source = ImageSource.objects.filter(Q(source_name__iexact=name))
    if source.exists():
        return source[0]
    else:
        return ImageSource.objects.get(id=1)

def import_row(row):
    image = Image()
    if (row['age']):
        image.age = row['age']
    if (row['sex']):
        image.gender = row['sex']

    image.disease = get_deseases(row['finding'])

    if (row['survival']):
        image.survival = row['survival'] == 'Y' if 1 else 0

    image.view_type = get_view_type(row['view'])
    image.original_image = row['original_image']
    image.resized_image = row['resize_image']
    image.image_source = row['Dataset_origin']
    image.save()


with open('../import/metadata_ex.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names : {", ".join(row)}')
            line_count += 1

        import_row(row)
        line_count += 1
    print(f'Processed {line_count} lines.')
