import time
import os
import warnings

# Install and import necessary libraries
try:
    import selenium
except ImportError:
    os.system("pip install selenium")
    time.sleep(10)
    import selenium
try:
    import undetected_chromedriver as uc
except ImportError:
    os.system("pip install undetected_chromedriver")
    time.sleep(10)
    import undetected_chromedriver as uc
try:
    import pandas as pd
except ImportError:
    os.system("pip install pandas")
    time.sleep(10)
    import pandas as pd
try:
    import glob
except ImportError:
    os.system("pip install glob")
    time.sleep(10)
    import glob
try:
    import googleapiclient
except ImportError:
    os.system("pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    time.sleep(10)
    import googleapiclient
try:
    import pydrive
except ImportError:
    os.system("pip install pydrive")
    time.sleep(10)
    import pydrive


# import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
# from time import sleep
from googleapiclient.http import MediaFileUpload
from Google import Create_Service
from pydrive.auth import GoogleAuth
# import glob
# import os
from os import getcwd
# import pandas as pd

print(os.getcwd())
file_path = os.getcwd()
download_path = file_path + '\\downloads'
# print(download_path)
pd.set_option('display.max_columns', 34)
# list_of_files = glob.glob(f'{download_path}\*')
# print(list_of_files)


def test_uc():
    # Options to specificy download folder and where the chrome driver is located in the computer
    # chromeOptions = uc.ChromeOptions()

    # chromeOptions.add_experimental_option('prefs', {
    #     'download.default_directory': 'C:\\Users\\ruejose\\Desktop\\data_firmas\\downloads'})
    #
    # # driver = webdriver.Chrome(executable_path='C:/Users/ruejose/PycharmProjects/pythonProject/joseProjects/webscrapping/chromedriver.exe',chrome_options=chromeOptions)
    # driver = uc.Chrome(
    #     getcwd() + '/chromedriver.exe',
    #     chrome_options=chromeOptions)

    # second try
    options = uc.ChromeOptions()
    # profile = "C:\\Users\\ruejose\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
    profile = "C:\\Users\\mskor\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1"
    options.add_argument(f"user-data-dir={profile}")
    driver = uc.Chrome(options=options, use_subprocess= True)
    url = "https://reporteslp.te.gob.pa/sindep/login"
    driver.get(url)

    raise

    # specifying URL and credentials
    driver = uc.Chrome(use_subprocess=True)
    # wait = WebDriverWait(driver, 20)
    driver.implicitly_wait(10)
    url = "https://reporteslp.te.gob.pa/sindep/login"
    driver.get(url)
    password = "Cgw6mrio7qh"
    username = "8-908-1305"

    #   login into website
    driver.implicitly_wait(10)
    driver.find_element(By.NAME,"username").send_keys(username)
    driver.find_element(By.NAME,"password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR,"input[type=\"submit\" i]").click()
    driver.get("https://reporteslp.te.gob.pa/sindep/")
    print("logged in succesfully")
    sleep(15)

def download_data_tribunal():
    # Options to specificy download folder and where the chrome driver is located in the computer
    chromeOptions = webdriver.ChromeOptions()
    # chromeOptions = Options()
    # chromeOptions.add_argument('disable-infobars')
    # chromeOptions.add_argument(r"--user-data-dir=C:\Users\ruejose\AppData\Local\Google\Chrome\User Data")
    # chromeOptions.add_argument(r"--profile-directory=C:\Users\ruejose\AppData\Local\Google\Chrome\User Data\Default")
    # chromeOptions.add_experimental_option('prefs',{'download.default_directory':'C:\\Users\\ruejose\\Desktop\\JOSE\\python\\data_tribunal'})
    chromeOptions.add_experimental_option('prefs', {
        'download.default_directory': 'C:\\Users\\ruejose\\PycharmProjects\\pythonProject\\joseProjects\\webscrapping\\data_tribunal'})

    # driver = webdriver.Chrome(executable_path='C:/Users/ruejose/PycharmProjects/pythonProject/joseProjects/webscrapping/chromedriver.exe',chrome_options=chromeOptions)
    driver = webdriver.Chrome(
        getcwd()+'/chromedriver.exe',
        chrome_options=chromeOptions)

    # specifying URL and credentials
    driver.implicitly_wait(10)
    url = "https://reporteslp.te.gob.pa/sindep/login"
    driver.get(url)
    password = "Cgw6mrio7qh"
    username = "8-908-1305"

    #   login into website
    driver.implicitly_wait(10)
    driver.find_element(By.NAME,"username").send_keys(username)
    driver.find_element(By.NAME,"password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR,"input[type=\"submit\" i]").click()
    driver.get("https://reporteslp.te.gob.pa/sindep/")
    print("logged in succesfully")
    sleep(15)
    driver.implicitly_wait(10)

    #   Select Cargo Alcalde in first dropdown
    element = driver.find_element(By.ID,"cargo")
    drp = Select(element)
    drp.select_by_value("3")
    sleep(15)
    driver.implicitly_wait(10)

    #   Select "aceptadas" en las options para descargar
    element_1 = driver.find_element(By.CSS_SELECTOR,"body > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > select:nth-child(2)")
    drp_1 = Select(element_1)
    drp_1.select_by_visible_text('Aceptadas')
    sleep(15)
    driver.implicitly_wait(10)

    #   click on download csv or excel download button
    # driver.find_element(By.CSS_SELECTOR,".btn.d-flex.aling-items-center.rounded-3.mx-1").click()
    driver.find_element(By.CSS_SELECTOR, "button[class ='btn d-flex aling-items-center rounded-3']").click()
    sleep(30)

def transform_data_tribunal():
    # FILE_PATH_1 = r'C:/Users/ruejose/Desktop/JOSE/python/data_tribunal/'
    # FILE_PATH_1 = r'C:/Users/ruejose/PycharmProjects/pythonProject/joseProjects/webscrapping/data_tribunal/'

    # get the latest file downloaded
    # list_of_files = glob.glob(r'C:\Users\ruejose\PycharmProjects\pythonProject\joseProjects\webscrapping\data_tribunal\*')
    list_of_files = glob.glob(f'{download_path}\*')
    latest_file = max(list_of_files, key=os.path.getctime)
    # df_data_tribunal_raw_header = pd.read_csv(latest_file, index_col=None, header=None)
    df_data_tribunal_raw_header = pd.read_excel(latest_file, engine='openpyxl',index_col=None, header=7)
    # print(df_data_tribunal_raw_header)

    # erase 5 first rows with description and use first row as headers
    # df_data_tribunal_raw = df_data_tribunal_raw_header.iloc[5:, :]
    # df_data_tribunal_raw.columns = df_data_tribunal_raw.iloc[0]
    # df_data_tribunal_raw = df_data_tribunal_raw[1:]



    # take only columns we need and change name

    df_data_tribunal = df_data_tribunal_raw_header[
        ['Provincia', 'Distrito', 'Corregimiento', 'Centro de votación', 'Fecha de firma', 'Sexo', 'Edad', 'Oficina',
         'Activista']]
    df_data_tribunal.rename(columns={'Provincia': 'provincia',
                                     'Distrito': 'distrito',
                                     'Corregimiento': 'corregimiento_orig',
                                     'Centro de votación': 'centro_de_votacion',
                                     'Fecha de firma': 'fecha_firma',
                                     'Sexo': 'sexo',
                                     'Edad': 'edad',
                                     'Oficina': 'metodo',
                                     'Activista': 'activista'}, inplace=True)

    # post new file in the folder
    df_data_tribunal.to_csv(FILE_PATH_1 + '\\data_tribunal.csv', index=False, encoding='latin1')

def upload_refreshed_data():
    secrets_file = os.path.normpath('C:/Users/ruejose/PycharmProjects/pythonProject/joseProjects/webscrapping/client_secret.json')
    GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = secrets_file

    # CLIENT_SECRET_FILE = 'client_secret.json'
    CLIENT_SECRET_FILE = secrets_file
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    folder_id = '1mb4PHSpfIOpnxF-opZTVX4aaj0jX6J16'
    file_names = ['data_tribunal.csv']
    mime_types = ['text/csv']

    for file_name, mime_type in zip(file_names,mime_types):
        file_id = '1d8BMhIF1BvDbvMGUMgYbV_wIL0Z827PY'
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        # # upload the file
        # media = MediaFileUpload('C:/Users/ruejose/PycharmProjects/pythonProject/joseProjects/webscrapping/data_tribunal/{0}'.format(file_name),mimetype= mime_type )
        #
        # service.files().create(
        #     body=file_metadata,
        #     media_body= media,
        #     fields='id'
        # ).execute()

        # replace the file
        media = MediaFileUpload('C:/Users/ruejose/PycharmProjects/pythonProject/joseProjects/webscrapping/data_tribunal/{0}'.format(file_name),
                                mimetype=mime_type)
        service.files().update(
            fileId =file_id,
            media_body= media,
        ).execute()

if __name__ == "__main__":
    test_uc()
    raise

download_data_tribunal()
sleep(30)
transform_data_tribunal()
sleep(30)
upload_refreshed_data()

