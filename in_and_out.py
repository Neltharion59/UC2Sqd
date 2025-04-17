def provide_use_cases():
    for i in range(12):
        file_name = 'UseCase{0}'.format(i)
        with open('Input_UCs/{0}.txt'.format(file_name), 'r', encoding='utf-8') as uc_file:
            use_case = uc_file.read()
            yield file_name, use_case


def collect_puml(file_name, plant_uml_string, error_message):
    output_string = plant_uml_string

    if len(error_message) > 0:
        output_string = '[Error]' + error_message
        print('[UC2Sqd] Converting {0} failed, because: {1}'.format(file_name, error_message))

    with open('Output_Pumls/{0}.puml'.format(file_name), 'w+', encoding='utf-8') as puml_file:
        puml_file.write(output_string)
