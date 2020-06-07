from selenium import webdriver
from corona_tracker import covid_data_tracker
from confirmed_country import confirmed_country

if __name__ == '__main__':
    cf = connection_factory()    
    driver = webdriver.Firefox()
    # Atualizando lista de paises com casos confirmados
    confirmed_country(cf.get_connection('sqlserver'), driver).update_known_countries()
    # Atualizando dados de paises com casos confirmados
    covid_data_tracker(cf.get_connection('sqlserver'), driver).update_data()
