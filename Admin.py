from Conexion import Conexion
import bcrypt


def crear_admin(usuario, contrasena, rol='admin'):
    """
    Crea un administrador o superadmin en la base de datos.
    - usuario: Nombre de usuario del administrador.
    - contrasena: Contraseña del administrador.
    - rol: Tipo de administrador ('admin' o 'superadmin').
    """
    connection = Conexion()
    if connection:
        cursor = connection.cursor()
        contrasena_hash = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()
        query = """
        INSERT INTO Administradores (usuario, contrasena_hash, rol)
        VALUES (%s, %s, %s)
        """
        try:
            cursor.execute(query, (usuario, contrasena_hash, rol))
            connection.commit()
            print(f'Administrador {rol} creado exitosamente.')
        except Exception as e:
            print(f'Error al crear el administrador: {e}')
        finally:
            connection.close()

def login_superadmin(usuario, contrasena):
    """
    Verifica las credenciales del superadmin.
    - usuario: Nombre de usuario del superadmin.
    - contrasena: Contraseña proporcionada.
    - return: True si el inicio de sesión es exitoso, False en caso contrario.
    """
    connection = Conexion()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT contrasena_hash FROM Administradores
        WHERE usuario = %s AND rol = 'superadmin'
        """
        try:
            cursor.execute(query, (usuario,))
            result = cursor.fetchone()
            if result and bcrypt.checkpw(contrasena.encode(), result['contrasena_hash'].encode()):
                print('Inicio de sesión exitoso')
                return True
            else:
                print('Credenciales incorrectas o usuario no es superadmin')
                return False
        except Exception as e:
            print(f'Error al verificar el inicio de sesión: {e}')
        finally:
            connection.close()
    return False
def admin_main():
    while True:
        print("Gestión de Administradores ---")
        print("1. Crear Superadmin")
        print("2. Crear Admin")
        print("3. Login Superadmin")
        print("4. Salir")
        opcion = input('Seleccione una opción: ')

        if opcion == '1':
            usuario = input('Usuario Superadmin: ')
            contrasena = input('Contraseña: ')
            crear_admin(usuario, contrasena, rol='superadmin')
        elif opcion == '2':
            usuario = input('Usuario Admin: ')
            contrasena = input('Contraseña: ')
            crear_admin(usuario, contrasena)
        elif opcion == '3':
            usuario = input('Usuario: ')
            contrasena = input('Contraseña: ')
            if login_superadmin(usuario, contrasena):
                print('Bienvenido al sistema de gestión académica')
            else:
                print('Acceso denegado')
        elif opcion == '4':
            print('Saliendo...')
            break
        else:
            print('Opción no válida, intente de nuevo.')

if __name__ == '__main__':
    admin_main()
