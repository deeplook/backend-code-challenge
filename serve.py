import configparser

from app import app


config_path = 'config.ini'
config = configparser.ConfigParser()
config.read(config_path)
debug = config.getboolean('SERVICE', 'debug')
port = config.getint('SERVICE', 'port')

app.run(debug=debug, host='0.0.0.0', port=port)
