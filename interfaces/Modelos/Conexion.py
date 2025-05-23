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
            password='',
<<<<<<< HEAD

=======
>>>>>>> 314ddcd81bfe8fa6f9352912c1df79d5728c959d
            database='facultad'
        )
        if connection.is_connected():
            print('Conexión exitosa a la base de datos')
        return connection
    except Error as e:
        print(f'Error al conectar a MySQL: {e}')
        return None
