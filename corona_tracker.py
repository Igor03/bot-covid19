from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import json
import datetime
import connection_factory

class covid_data_tracker():
    
    base_select_qry = '''select id, 'https://bing.com/covid/local/'+country_name_search search_url
                        from covid_19..country
                        where id not in (select country_id from covid_19..country_situation 
                                    where convert(date, search_date) = convert(date, getdate()))'''

    base_insert_qry = ''' insert into covid_19..country_situation (
            country_id, active_cases,
            recovered_cases, fatal_cases,
            search_date
        ) values (
            {}, {}, {}, {}, getdate()
        )'''

    def __init__(self, conn, driver):
        self.driver = driver
        self.conn = conn
        super().__init__()
    

    def update_data(self):
        for country in self.conn.execute(self.base_select_qry).fetchall():
            country_id = country[0]
            country_url = country[1]
        
            # Tentando realizar requisicao para o portal    
            try:
                self.driver.get(country_url)
            except TimeoutException:
                self.driver.get(country_url) 

            # Esperando um elemento especifico renderizar
            WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'infoTile')))
            time.sleep(1)

            # Capturando as numeros globais 
            active_cases = self.driver.execute_script('return document.getElementsByClassName("infoTileData")[1].children[0].children[2].innerText.split("\\n")[0]')
            recovered_cases = self.driver.execute_script('return document.getElementsByClassName("infoTileData")[1].children[1].children[2].innerText.split("\\n")[0]')
            fatal_cases = self.driver.execute_script('return document.getElementsByClassName("infoTileData")[1].children[2].children[2].innerText.split("\\n")[0]')

            active_cases = active_cases.replace('.', '')
            recovered_cases = recovered_cases.replace('.', '')
            fatal_cases = fatal_cases.replace('.', '')

            active_cases = 0 if active_cases == '-' else active_cases
            recovered_cases = 0 if recovered_cases == '-' else recovered_cases
            fatal_cases = 0 if fatal_cases == '-' else fatal_cases

            self.conn.execute(self.base_insert_qry.format(country_id, active_cases, recovered_cases, fatal_cases))
            self.conn.commit()