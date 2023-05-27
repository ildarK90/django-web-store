import csv
import simplejson as json
from pprint import pprint
import urllib.request
import codecs
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse


def read(file):
    with open(file, 'r', ) as file:
        data = json.load(file)
        return data


# def read_right(file):
#     with open(file, 'r') as file:
#         data = json.loads(file.read())
#         return data

def multijson():
    testmodel = 'csv_source\\testmodel.json'
    deserialized = read(testmodel)
    new_data = []
    for i in range(500):
        for notebook in deserialized:
            new_data.append(notebook['fields'])

    with open("csv_result\\data_testmodel.json", "w") as write_file:
        json.dump(new_data, write_file, ensure_ascii=False, encoding='utf-8')


def json_to_csv(modelname):
    models_files = {
        'category': 'files/category.json',
        'notebook': 'files/notebook.json',
        'smartphones': 'files/smartphones.json',
        'testmodel': 'csv_source\\data_testmodel.json'
    }

    with open(models_files[modelname]) as file:
        src = json.loads(file)
    csv_filename = 'csv_result\\' + str(modelname) + '.' + 'csv'
    for i in src:
        with open(csv_filename, "a") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(
                (i.values())
            )


def file_to_csv(json_file, name):
    filename = name[:name.rfind('.')]
    json_file = json_file.read()
    json_file = str(json_file.decode('utf-8'))
    json_file = json.loads(json_file)
    for i in json_file:
        path = f"csv_result\\{filename}.csv"
        print(path)
        # print(i)
        with open(path, "a") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(
                (i.values())
            )

def normal_json(file, name,rounds=1):
    filename = name[:name.rfind('.')]
    # json_file = json.load(file)
    json_file = file.read()
    # f = codecs.open(json_file,'r',encoding='utf-8')
    json_file = str(json_file.decode('utf-8'))
    print(json_file)
    json_file = json.loads(json_file)
    json_data = []
    for i in range(rounds):
        for product in json_file:
            json_data.append(product['fields'])
    print(json_data)
    # json_file = json.loads(json_file)
    # print(json_file)
    # for i in json_file:
    #     path = f"csv_result\\{filename}.csv"
    #     print(path)
    #     # print(i)
    #     with open(path, "a") as csv_file:
    #         writer = csv.writer(csv_file)
    #         writer.writerow(
    #             (i.values())
    #         )
    path = f"json_result\\{filename}.json"
    with open(path ,"w",encoding='utf-8') as write_file:
        json.dump(json_data, write_file, ensure_ascii=False, encoding='utf-8')


def del_id(file):
    json_file = file.read()
    # f = codecs.open(json_file,'r',encoding='utf-8')
    json_file = str(json_file.decode('utf-8'))
    json_file = json.loads(json_file)
    for i in json_file:
        print(i)
        print(i['id'])
        i.pop('id')
    path = f"json_result\\notebook_edited.json"
    with open(path ,"w") as write_file:
        json.dump(json_file, write_file, ensure_ascii=False, encoding='utf-8')

def download_csv(modeladmin, request, queryset):
    # if not request.user.is_staff:
    #     raise PermissionDenied
    opts = queryset.model._meta
    model = queryset.model
    response = HttpResponse(content_type='text/csv')
    # force download.
    response['Content-Disposition'] = 'attachment;filename=export.csv'
    # the csv writer
    with open('output_file_name', 'w+',encoding='utf-8',errors='replace',  newline='') as file:  #encoding='utf-8'
        writer = csv.writer(file)
        field_names = [field.name for field in opts.fields]
    # Write a first row with header information
        writer.writerow(field_names)
    # Write data rows
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
    return response
download_csv.short_description = "Download selected as csv"