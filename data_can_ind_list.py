import pytz
import requests
import pandas as pd
import datetime as dt
import numpy as np
import sys
from zoneinfo import ZoneInfo
from time import sleep
from googleapiclient.http import MediaFileUpload
from Google import Create_Service
from pydrive.auth import GoogleAuth
import glob
import os
from os import getcwd
from bs4 import BeautifulSoup

now = dt.datetime.now()
now_panama = dt.datetime.now(pytz.timezone('US/Central'))
# FILE_PATH_1 = r'C:/Users/ruejose/Desktop/JOSE/python/data_tribunal/'
FILE_PATH_1 = r'C:/Users/ruejose/PycharmProjects/pythonProject/joseProjects/webscrapping/data_tribunal/'
URL = "https://candidatoslp.te.gob.pa/api/File/"

tribunal_api_dic = {'circunscripcion':["1", "3 8 9", "2 8-2", "4 8 9 1", "4 8 9 2", "4 8 9 3", "4 8 9 4", "4 8 9 5", "4 8 9 6", "4 8 9 7", "4 8 9 8", "4 8 9 9"],
                    'Cargo':["Presidente", "Alcalde", "Diputado", "Representante", "Representante", "Representante", "Representante", "Representante", "Representante", "Representante", "Representante", "Representante"],
                    'Provincia':"Panama",
                    'Distrito':["",	"San Miguelito", "San Miguelito", "San Miguelito", "San Miguelito", "San Miguelito", "San Miguelito", "San Miguelito", "San Miguelito", "San Miguelito", "San Miguelito", "San Miguelito"],
                    'Corregimiento':["", "", "", "AMELIA DENIS DE ICAZA", "BELISARIO PORRAS", "JOSE DOMINGO ESPINAR", "MATEO ITURRALDE", "VICTORIANO LORENZO", "ARNULFO ARIAS",	"BELISARIO FRIAS", "OMAR TORRIJOS", "RUFINA ALFARO"]
                    }

df_tribunal_api = pd.DataFrame(tribunal_api_dic)
circunscripcion_list = tribunal_api_dic["circunscripcion"]
candidatos_result = []

def download_data_candidatos():
    for i in circunscripcion_list:
        request_i = requests.get(URL + i + ".json")
        response_i = request_i.json()
        candidatos_response = response_i['candidatos']
        candidatos_response_fecha_actualizacion = response_i["fechaActualizacion"]
        candidatos_response_circunscripcion = response_i["circunscripcion"]
        for i in candidatos_response:
            candidatos_dict = i
            candidatos_dict["fechaActualizacionTE"] = candidatos_response_fecha_actualizacion
            # candidatos_dict["fechaDescarga"] = now_panama.strftime('%d/%m/%Y %H:%M')
            candidatos_dict["fechaDescarga"] = now_panama.strftime('%Y-%m-%d %H:%M')
            candidatos_dict["circunscripcion"] = candidatos_response_circunscripcion
            candidatos_result.append(candidatos_dict)

    # Create dataframe based on result dictionary
    df_candidatos = pd.DataFrame(candidatos_result)

    # Clean dataframe
    df_candidatos['firmasAceptadas'] = df_candidatos['firmasAceptadas'].str.replace(',', '')
    new_fechaTribunal = df_candidatos['fechaActualizacionTE'].str.split(":", n=1, expand=True)
    df_candidatos['fechaActualizacionTE'] = new_fechaTribunal[0] + ":00 a.m."
    # Join dataframa with extra data TE api
    df_candidatos = df_candidatos.join(df_tribunal_api.set_index('circunscripcion'), on=['circunscripcion'], how='left')
    df_candidatos.drop(["totalLista","candidatoCabezaLista","cabezaLista","curul"],axis=1, inplace=True)

    # Create sort ID based on download data
    df_candidatos_sort = df_candidatos[['independienteId']].copy()
    df_candidatos_sort.insert(0, 'Sort_ID', range(0, 0 + len(df_candidatos)))

    # create Diputados DF to join with listas
    df_candidatos_diputados = df_candidatos[(df_candidatos['Cargo']=='Diputado')].copy()
    df_candidatos_diputados.drop(["firmasAceptadas", "nombreCompleto", "porcentaje"], axis=1, inplace=True)

    return df_candidatos, df_candidatos_sort,df_candidatos_diputados

def download_data_listas(df_candidatos_sort, df_candidatos_diputados):

    UR_listas = "https://candidatoslp.te.gob.pa/home/listaConNombre/2/8/2/"
    # clear
    dic_url_diputados = {
        'url_document': ["25002904/'Zulay%20Leyset%20Rodriguez%20Lu'", "25002039/'Angel%20Santos%20Ortega%20Gonzalez'",
                         "25002955/'Jean%20Marcel%20Chery%20Ramos'",
                         "25002224/'Juan%20Antonio%20Tejada%20Pinillo'", "25002845/'Juan%20Estrada%20Muir'",
                         # "25002271/'Hector%20Emilio%20Rodriguez%20Ure%C3%B1a'",
                         "25003030/'Raul%20Antonio%20Pati%C3%B1o%20Samaniego'",
                         "25003278/'Franklin%20Amilcar%20Ortiz%20Cano'"],
        'circunscripcion': "2 8-2",
        'lista': ["LISTA_ZULAY", "LISTA_VAMOS", "LISTA_RADIX",
                  "LISTA_JUAN_ANTONIO_TEJADA", "LISTA_JUAN_ESTRADA",
                  # "LISTA_HECTOR_RODRIGUEZ",
                  "LISTA_RAUL_ANTONIO", "LISTA_FRANKLIN_AMILCAR"],
        'lista_id': ['25002904', '25002039', '25002955', '25002224', '25002845',
                     # '25002271',
                    '25003030', '25003278']

        }

    url_document_list = dic_url_diputados["url_document"]
    lista_list = dic_url_diputados["lista"]
    lista_id_list = dic_url_diputados["lista_id"]
    circunscripcion_list = dic_url_diputados["circunscripcion"]

    nombrecompleto = []
    firmasAceptadas = []
    porcentaje = []
    lista = []
    lista_id = []
    circunscripcion = []
    sort_id_list = []
    data = {}

    for i, j, k in zip(url_document_list, lista_list, lista_id_list):
        html_request = requests.get(UR_listas + i).text
        # print(html_request)
        soup = BeautifulSoup(html_request, 'lxml')

        candidatos_cards = soup.find_all('div', class_="col-6 col-sm-5")
        firmas_cards = soup.find_all('div', class_="col-12")
        index = 1
        sort_id = 0
        lista_j = j
        lista_id_k = k
        circunscripcion_k = "2 8-2"

        for candidatos in candidatos_cards:
            candidatos_name = candidatos.find('div').text
            nombrecompleto.append(candidatos_name)
            lista.append(lista_j)
            lista_id.append(lista_id_k)
            circunscripcion.append(circunscripcion_k)
            sort_id_list.append(sort_id)
            sort_id += 1

        for firmas in firmas_cards:
            firmas_num = firmas.find('h5')
            if firmas_num:
                if (index % 2) == 0:
                    porcentaje.append(firmas_num.text)
                else:
                    firmasAceptadas.append(firmas_num.text)
                index += 1


        data['nombreCompleto'] = nombrecompleto
        data['firmasAceptadas'] = firmasAceptadas
        data['porcentaje'] = porcentaje
        data['lista'] = lista
        data['lista_id'] = lista_id
        # data['circunscripcion'] = circunscripcion
        data['sort_id'] = sort_id_list

        df_listas = pd.DataFrame(data)

    df_candidatos_diputados = df_candidatos_diputados.join(df_candidatos_sort.set_index('independienteId'), on=['independienteId'], how='left')
    df_candidatos_diputados.rename(columns={'independienteId':'lista_id','Sort_ID':'Sort_ID_lista'}, inplace = True)
    df_listas['lista_id'] = df_listas['lista_id'].astype('str')
    df_listas['firmasAceptadas'] = df_listas['firmasAceptadas'].str.replace(',', '')
    df_candidatos_diputados['lista_id'] = df_candidatos_diputados['lista_id'].astype('str')
    df_diputados_listas = df_listas.join(df_candidatos_diputados.set_index('lista_id'), on = ['lista_id'], how = 'left' )
    df_diputados_listas['sort_id'] = df_diputados_listas['sort_id'].astype('str')
    df_diputados_listas['Sort_ID_lista'] = df_diputados_listas['Sort_ID_lista'].astype('int').astype('str')
    # df_diputados_listas = df_candidatos_diputados


    df_diputados_listas['independienteId'] = np.where( df_diputados_listas['sort_id'] == '0',
                                                       df_diputados_listas['lista_id'],
                                                       df_diputados_listas[['lista_id', 'sort_id']].agg('-'.join,axis=1).str.upper())

    df_diputados_listas['cedula'] = df_diputados_listas['cedula'].astype('str')
    df_diputados_listas['cedula'] = np.where( df_diputados_listas['sort_id'] == '0',
                                                       df_diputados_listas['cedula'],
                                                       df_diputados_listas[['cedula', 'sort_id']].agg('-'.join,axis=1).str.upper())

    df_diputados_listas['Sort_ID'] = np.where( df_diputados_listas['sort_id'] == '0',
                                                       df_diputados_listas['Sort_ID_lista'],
                                                       df_diputados_listas[['Sort_ID_lista', 'sort_id']].agg('.'.join,axis=1).str.upper())

    df_diputados_listas.drop(["lista_id", "sort_id","Sort_ID_lista"], axis=1, inplace=True)
    # df_diputados_listas.insert(0, 'independienteId', df_diputados_listas['independienteId'])
    df_diputados_complete = df_diputados_listas[['independienteId','nombreCompleto', 'cedula', 'firmasAceptadas',
                             'porcentaje', 'fechaActualizacionTE', 'fechaDescarga', 'circunscripcion',
                             'Cargo', 'Provincia', 'Distrito', 'Corregimiento', 'lista']]

    df_diputados_sort= df_diputados_listas[['independienteId', 'Sort_ID','lista']]

    df_diputados_complete.to_csv(FILE_PATH_1 + '\\df_diputados_complete.csv', index=False, encoding='latin1')
    df_diputados_sort.to_csv(FILE_PATH_1 + '\\df_diputados_sort.csv', index=False, encoding='latin1')


    return df_diputados_complete, df_diputados_sort

def merge_candidatos_listas(df_candidatos, df_candidatos_sort, df_diputados_complete, df_diputados_sort):
    df_candidatos_todo = pd.concat([df_candidatos, df_diputados_complete], ignore_index=True)
    df_candidatos_todo['independienteId'] = df_candidatos_todo['independienteId'].astype('str')
    df_candidatos_todo['Cargo'] = df_candidatos_todo['Cargo'].astype('str')
    df_candidatos_todo['dupl_independienteId'] = df_candidatos_todo.duplicated(['independienteId'], keep = False)
    # df_candidatos_todo['dupl_independienteId_2'] = not (df_candidatos_todo['cedula'].is_unique)
    # df_candidatos_todo['dupl_independienteId'] = df_candidatos_todo['cedula'].duplicated().any()
    # df_candidatos_todo['dupl_independienteId_2'] = not(df_candidatos_todo['cedula'].is_unique)
    # df_candidatos_todo['lista_bool'] = (df_candidatos_todo['lista'].notnull())
    # df_candidatos_todo = df_candidatos_todo[(df_candidatos_todo['dupl_independienteId']) &
    #                                         (~(df_candidatos_todo['lista'].notnull())) &
    #                                         (df_candidatos_todo['Cargo']=='Diputado')]
    df_candidatos_todo['filter'] = np.where((df_candidatos_todo['dupl_independienteId']) &
                                            (~(df_candidatos_todo['lista'].notnull())) &
                                            (df_candidatos_todo['Cargo']=='Diputado'),
                                            False, True)
    df_candidatos_todo = df_candidatos_todo[(df_candidatos_todo['filter'])]
    df_candidatos_todo.drop(["dupl_independienteId", "filter",'lista'], axis=1, inplace=True)

    df_candidatos_todo_sort = pd.concat([df_candidatos_sort, df_diputados_sort], ignore_index=True)
    df_candidatos_todo_sort['independienteId'] = df_candidatos_todo_sort['independienteId'].astype('str')
    df_candidatos_todo_sort['Sort_ID'] = df_candidatos_todo_sort['Sort_ID'].astype('float')
    df_candidatos_todo_sort = df_candidatos_todo_sort.drop_duplicates(['independienteId'], keep='last')
    df_candidatos_todo_sort = df_candidatos_todo_sort.sort_values(['Sort_ID'], ascending=[True])

    return df_candidatos_todo, df_candidatos_todo_sort


def read_write_data_candidatos(df_candidatos_todo,df_candidatos_todo_sort):

    # Read CSV with old data
    df_candidatos_csv = pd.read_csv(FILE_PATH_1 + 'data_candidatos_all.csv', encoding='latin1')
    # df_candidatos_csv.drop(["Sort_ID","firmasDiarias"], axis=1, inplace=True)
    df_candidatos_csv.drop(["Sort_ID","firmasDiarias", "lista"], axis=1, inplace=True)

    # Concat two dataframes, add new with old data
    df_candidatos_all = pd.concat([df_candidatos_todo, df_candidatos_csv], ignore_index=True)

    # Join candidatos all with candidatos sort to get sort ID
    df_candidatos_todo_sort['independienteId'] = df_candidatos_todo_sort['independienteId'].astype('str')
    df_candidatos_all['independienteId'] = df_candidatos_all['independienteId'].astype('str')
    df_candidatos_all = df_candidatos_all.join(df_candidatos_todo_sort.set_index('independienteId'), on=['independienteId'],
                                               how='left')


    # Clean complete dataframe
    df_candidatos_all['firmasAceptadas'] = df_candidatos_all['firmasAceptadas'].apply(pd.to_numeric, errors='coerce')
    df_candidatos_all['fechaDescarga'] = pd.to_datetime(df_candidatos_all['fechaDescarga'],dayfirst=True,format='mixed')
    df_candidatos_all['fechaDescarga'] = pd.to_datetime(df_candidatos_all['fechaDescarga'], format='%Y-%m-%d %H:%M')



    # Create group ID based on group of two columns
    df_candidatos_all = df_candidatos_all.sort_values(
        ['independienteId', 'fechaDescarga'], ascending=[False, True])
    df_candidatos_all['candidato_index'] = df_candidatos_all.groupby(['independienteId']).cumcount()
    df_candidatos_all['candidato_index_previous'] = df_candidatos_all['candidato_index'] - 1

    # First change int to str to create index keys
    df_candidatos_all['independienteId'] = df_candidatos_all['independienteId'].astype('str')
    df_candidatos_all['candidato_index'] = df_candidatos_all['candidato_index'].astype('str')
    df_candidatos_all['candidato_index_previous'] = df_candidatos_all['candidato_index_previous'].astype('str')
    df_candidatos_all['candidatos_key'] = df_candidatos_all[['independienteId', 'candidato_index']].agg('-'.join,
                                                                                                        axis=1).str.upper()
    df_candidatos_all['candidatos_key_previous'] = df_candidatos_all[
        ['independienteId', 'candidato_index_previous']].agg('-'.join, axis=1).str.upper()

    # create df copy for previous row value, rename columns to join
    df_candidatos_all_previous = df_candidatos_all[['candidatos_key', 'firmasAceptadas']].copy()
    df_candidatos_all_previous.rename(
        columns={'candidatos_key': 'candidatos_key_previous', 'firmasAceptadas': 'firmasAceptadas_previous'},
        inplace=True)

    # Join df all with df previous row
    df_candidatos_final = df_candidatos_all.join(df_candidatos_all_previous.set_index('candidatos_key_previous'),
                                                 on=['candidatos_key_previous'], how='left')

    # create Firmas diarias, clean data and substraction
    df_candidatos_final['firmasAceptadas_previous'].fillna(df_candidatos_final['firmasAceptadas'], inplace=True)
    df_candidatos_final['firmasDiarias_1'] = np.where(df_candidatos_final['candidato_index'] == '0',
                                                      df_candidatos_final['firmasAceptadas'] ,
                                                      (df_candidatos_final['firmasAceptadas'] - df_candidatos_final['firmasAceptadas_previous']))


    # Re-order columns, sort rows and erase useless columns
    df_candidatos_final.insert(4, 'firmasDiarias', df_candidatos_final['firmasDiarias_1'])
    df_candidatos_final = df_candidatos_final.sort_values(
        ['Sort_ID', 'fechaDescarga'], ascending=[True, True])
    df_candidatos_final.drop(
        ["candidato_index", "candidato_index_previous", "candidatos_key", "candidatos_key_previous",
         "firmasAceptadas_previous", "firmasDiarias_1"], axis=1, inplace=True)

    # create csv based on output csv
    df_candidatos_final.to_csv(FILE_PATH_1 + '\\data_candidatos_all.csv', index=False, encoding='latin1')

    return df_candidatos_final

def upload_data_candidatos():
    secrets_file = os.path.normpath('C:/Users/ruejose/PycharmProjects/pythonProject/joseProjects/webscrapping/client_secret.json')
    GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = secrets_file

    # CLIENT_SECRET_FILE = 'client_secret.json'
    CLIENT_SECRET_FILE = secrets_file
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    folder_id = '1mb4PHSpfIOpnxF-opZTVX4aaj0jX6J16'
    file_names = ['data_candidatos_all.csv']
    mime_types = ['text/csv']

    for file_name, mime_type in zip(file_names,mime_types):
        file_id = '1J2L-MWavAtbdgvqtHq8fS9kQ_ctCsWVQ'
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        # replace the file
        media = MediaFileUpload('C:/Users/ruejose/PycharmProjects/pythonProject/joseProjects/webscrapping/data_tribunal/{0}'.format(file_name),
                                mimetype=mime_type)
        service.files().update(
            fileId =file_id,
            media_body= media,
        ).execute()



# download data candidatos tribunal
df_candidatos, df_candidatos_sort, df_candidatos_diputados = download_data_candidatos()
print("download candidatos data successful")
sleep(10)

# download data diputado listas hidden
df_diputados_complete, df_diputados_sort = download_data_listas(df_candidatos_sort, df_candidatos_diputados)
print("download hidden diputados listas data successful")
sleep(10)

# merge candidatos and listas together
df_candidatos_todo, df_candidatos_todo_sort = merge_candidatos_listas(df_candidatos, df_candidatos_sort, df_diputados_complete, df_diputados_sort)
sleep(10)

# Merge all data with new download
df_candidatos_final = read_write_data_candidatos(df_candidatos_todo, df_candidatos_todo_sort)
print("Create complete data successful")
sleep(20)

# Upload data to drive
upload_data_candidatos()
print("Upload complete data successful")



# df_candidatos_final = read_write_data_candidatos(df_candidatos, df_candidatos_sort)
# print("Create complete data successful")





# new merge old and new data function

# df_listas = download_data_listas(df_candidatos_sort, df_candidatos_diputados)
# pd.set_option('display.max_columns', None)
# print(df_listas)
# print(df_listas.dtypes)
# print(df_candidatos_final)
# print(df_candidatos_final.dtypes)
# df_candidatos_final.to_csv(FILE_PATH_1 + '\\df_candidatos_final_todo.csv', index=False, encoding='latin1')

# print(df_candidatos_todo_sort)
# print(df_candidatos_todo_sort.dtypes)
# df_candidatos_todo_sort.to_csv(FILE_PATH_1 + '\\df_candidatos_todo_sort.csv', index=False, encoding='latin1')

# print(df_candidatos_sort)
# print(df_candidatos_sort.dtypes)
#
#
# print(df_diputados_complete)
# print(df_diputados_complete.dtypes)


