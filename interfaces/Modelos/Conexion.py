# db_config.py

import mysql.connector
from mysql.connector import Error

def Conexion():
    """
    Establece y devuelve una conexión a la base de datos MySQL.
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1103',
            database='facultad'
        )
        if connection.is_connected():
            print('Conexión exitosa a la base de datos')
        return connection
    except Error as e:
        print(f'Error al conectar a MySQL: {e}')
        return None
