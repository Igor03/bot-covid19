import pyodbc

class connection_factory:

    sqlserver_conn = pyodbc.connect('Driver={};'
                            'Server={};'
                            'Database={};'                            
                            'Trusted_Connection=yes'.format('{SQL Server}',
                            'DESKTOP-7D1BM7H',
                            'covid_19')).cursor()

    postgres_conn = None

    def __init__(self):
        super().__init__()
    
    def get_connection(self, database):
        if database.lower() == 'sqlserver':
            return self.sqlserver_conn
        elif database.lower() == 'postgres':
            return self.postgres_conn
        else:
            raise(Exception('Unknown database'))
