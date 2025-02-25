DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'transfermarkt',
    'user': 'tarik',
    'password': 'admin',

    # Optional parameters
    'echo': True,  # Set to True to log SQL queries
    # 'pool_size': 5,  # Number of connections to keep open
    #'max_overflow': 10,  # Max number of extra connections to create
    #'pool_timeout': 30,  # Seconds to wait for a connection
    
    # Additional settings you might want to add
    # 'ssl_mode': None,  # 'require', 'verify-full', etc.
    #'application_name': 'transfermarkt_scraper'  # Identifier in DB logs
}