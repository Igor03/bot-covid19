import requests
import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import connection_factory


class confirmed_country:

    api_base_url = r'https://restcountries.eu/rest/v2/name/{}'
    bing_base_url = r'https://bing.com/covid/{}'

    # Consultas sql
    known_countries_qry = "select country_name_search from covid_19..country"   
    base_insert_qry = '''
        insert into covid_19..country (country_name, 
            country_name_search, 
            region, subregion, 
            population, last_search)
        values(
            '{}', '{}', '{}', '{}', {}, getdate()
        )
    '''     

    def __init__(self, conn, driver):
        self.conn = conn
        self.driver = driver
        super().__init__()
            

    def update_known_countries(self):

        self.driver.get(self.bing_base_url.format(''))
        WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'infoTileData')))        
        
        time.sleep(1)
        
        for country in self._get_unknown_countries():
            
            self.driver.get("https://bing.com/covid/local/{}".format(country))
            WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'infoTile')))
            time.sleep(1)

            country_name_fant = self.driver.execute_script('return document.getElementsByClassName("locationTitle")[0].innerText')
            # country_name_fant = country_name_fant
            request_url = self.api_base_url.format(self._validate(country))

            response = requests.request("GET", request_url)
            if response.status_code != 200:
                print(request_url)
                continue
            
            response = json.loads(response.text)
        
            region = response[0]['region']
            subregion = response[0]['subregion']
            population = response[0]['population']

            insert = self.base_insert_qry.format(country_name_fant, country, region, subregion, population)
            self.conn.execute(insert)
            self.conn.commit()         

    def _get_unknown_countries(self):
        countries = []
        known_countries = []  
        [known_countries.append(c[0]) for c in self.conn.execute(self.known_countries_qry).fetchall()]
        self.driver.find_element_by_xpath("//div[@id='main']/div/div/div[2]/div/div/div[2]/div[2]/div[2]/div/div").click()
        time.sleep(1)
        areas = self.driver.execute_script('return document.getElementsByClassName("areas")[0].children.length')
        for i in range(int(areas)):
            country_name = self.driver.execute_script('return document.getElementsByClassName("areas")[0].children[{}].children[0].id'.format(i))
            if country_name not in known_countries:
                countries.append(country_name)
        print(countries)
        return countries

    # Adaptando nome de paises para requisicoes a API
    def _validate(self, country_name):
        if country_name == 'South Korea':
            return 'South Korean'
        elif country_name == 'Vatican City':
            return 'Vatican'
        elif country_name == 'Macao SAR':
            return 'Macao'
        elif country_name == 'Congo (DRC)':
            return 'Congo'
        elif country_name == 'unitedstates':
            return 'usa'
        elif country_name == 'unitedkingdom':
            return 'uk'
        else:
            return country_name.replace('mainland', '')