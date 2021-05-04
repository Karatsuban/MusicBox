#coding:utf-8

import py_midicsv as pm


def transforme(nom):
    if ".csv" not in nom:
        input_name = nom+".csv"
    else:
        input_name = nom
        
    output_name = input_name.replace(".csv", "-modif.csv")

    file = open(input_name, 'r')
    lines = file.readlines()
    file.close()

    liste_piste_1 = []
    liste_copy = []
    end_of_file = None

    for line in lines:
        if "End_of_file" in line:
            end_of_file = line
        else:
            line = line.split(", ")
            if int(line[0]) < 2:
                liste_piste_1.append(", ".join(line))
            if int(line[0]) > 2:
                line[0] = '2'
                liste_copy.append([int(line[1]),", ".join(line)])

    liste_copy.sort()

    file = open(output_name, 'w')
    for line in liste_piste_1:
        file.write(line)

    for line in liste_copy:
        file.write(line[1])

    file.write(end_of_file)
    file.close()
    
    midi_object = pm.csv_to_midi(output_name)

    output_name = output_name.replace(".csv", ".mid")
    print("Fichier écrit sous le nom ", output_name)
    
    with open(output_name, "wb") as output_file:
        midi_writer = pm.FileWriter(output_file)
        midi_writer.write(midi_object)

input_name = input("Entrez le nom du fichier dont il faut passer toutes les pistes sur la piste 2 : ")
transforme(input_name)
