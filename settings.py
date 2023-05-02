# Libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import psycopg2
from psycopg2 import sql
from datetime import date


# Settings
main_url = 'https://www.olx.ua'
months = {1: 'січня', 2: 'лютого', 3: 'березня', 4: 'квітня', 5: 'травня', 6: 'червня', 7: 'липня', 8: 'серпня',
          9: 'вересня', 10: 'жовтня', 11: 'листопада', 12: 'грудня'}


# Selenium settings
options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-popup-blocking')
options.add_argument('--headless')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)

