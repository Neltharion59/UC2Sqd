import os
from os import listdir
from os.path import isfile, join
from utilities import file_exists


def provide_use_cases():
    input_path = "Input_UCs"
    input_dataset_files = [x.replace('.txt', '') for x in listdir(input_path) if isfile(join(input_path, x)) and '.txt' in x]

    for file_name in input_dataset_files:
        output_file_name = 'Output_Pumls/{0}.puml'.format(file_name)

        if file_exists(output_file_name):
            continue

        input_file_name = 'Input_UCs/{0}.txt'.format(file_name)

        with open(input_file_name, 'r', encoding='utf-8') as uc_file:
            use_case = uc_file.read()
            yield file_name, use_case


def collect_puml(file_name, plant_uml_string, error_message):
    output_string = plant_uml_string

    if len(error_message) > 0:
        output_string = '[Error]' + error_message
        print('[UC2Sqd] Converting {0} failed, because: {1}'.format(file_name, error_message))

    file_path = 'Output_Pumls/{0}.puml'.format(file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w+', encoding='utf-8') as puml_file:
        puml_file.write(output_string)
        puml_file.flush()
        os.fsync(puml_file)
