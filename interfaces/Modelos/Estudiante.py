# student.py

from Conexion import Conexion

class Estudiante:
    @staticmethod
    def crear_estudiante(nombre, apellido, fecha_nacimiento, telefono, correo):
        creado=False
        """
        Crea un nuevo estudiante en la base de datos.
        """
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor()
            query = """
            INSERT INTO Estudiantes (nombre, apellido, fecha_nacimiento, telefono, correo)
            VALUES (%s, %s, %s, %s, %s)
            """
            try:
                cursor.execute(query, (nombre, apellido, fecha_nacimiento, telefono, correo))
                conexion.commit()
                creado=True
                print('Estudiante creado')
            except Exception as e:
                print(f'Error al crear estudiante: {e}')
            finally:
                conexion.close()
            return creado

    @staticmethod
    def mostrar_estudiante(estudiante_id):
        """
        Lee los datos de un estudiante por su ID.
        """
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            query = "SELECT * FROM Estudiantes WHERE id = %s"
            try:
                cursor.execute(query, (estudiante_id,))
                Estudiante = cursor.fetchone()
                return Estudiante
            except Exception as e:
                print(f'Error al leer estudiante: {e}')
            finally:
                conexion.close()

    @staticmethod
    def actualizar_estudiante(telefono, correo,estudiante_id):
        """
        Actualiza los datos de un estudiante.
        """
        actualizado=False
        conexion =Conexion()
        if conexion:
            cursor = conexion.cursor()
            query = """
            UPDATE Estudiantes
            SET telefono = %s, correo = %s
            WHERE id = %s
            """
            try:
                cursor.execute(query, (telefono, correo, estudiante_id))
                conexion.commit()
                print('Estudiante actualizado exitosamente')
                actualizado=True
            except Exception as e:
                print(f'Error al actualizar estudiante: {e}')
            finally:
                conexion.close()
        return actualizado

    @staticmethod
    def eliminar_estudiante(id_estudiante):
        """
        Elimina un estudiante de la base de datos y retorna True si se eliminó, False en caso contrario.
        """
        eliminado = False
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor()
            consulta = "DELETE FROM Estudiantes WHERE id = %s"
            try:
                cursor.execute(consulta, (id_estudiante,))
                conexion.commit()
                if cursor.rowcount > 0:
                    print('Estudiante eliminado exitosamente')
                    eliminado = True
                else:
                    print('No se encontró estudiante para eliminar')
            except Exception as e:
                print(f'Error al eliminar estudiante: {e}')
            finally:
                conexion.close()
        return eliminado
    @staticmethod
    def listar_estudiantes():
        """
        Lista todos los estudiantes registrados.
        """
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            consulta = "SELECT * FROM Estudiantes"
            try:
                cursor.execute(consulta)
                lista=cursor.fetchall()
                for estudiante in lista:
                    print(estudiante)
                return lista
            
            except Exception as e:
                print(f'Error al listar estudiantes: {e}')
            finally:
                conexion.close()
def estudiante_main():
    """
    Menú interactivo para gestionar CRUD de estudiantes.
    """
    while True:
        print("\n--- Gestión de Estudiantes ---")
        print("1. Crear Estudiante")
        print("2. Leer Estudiante")
        print("3. Actualizar Estudiante")
        print("4. Eliminar Estudiante")
        print("5. Listar Alumnos")
        print("6. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            nombre = input("Nombre: ")
            apellido = input("Apellido: ")
            fecha_nacimiento = input("Fecha de nacimiento (YYYY-MM-DD): ")
            telefono = input("Teléfono: ")
            correo = input("Correo: ")
            Estudiante.crear_estudiante(nombre, apellido, fecha_nacimiento, telefono, correo)

        elif opcion == '2':
            estudiante_id = input("ID del estudiante a leer: ")
            estudiante = Estudiante.mostrar_estudiante(estudiante_id)
            if estudiante:
                print(estudiante)
            else:
                print("Estudiante no encontrado")

        elif opcion == '3':
            estudiante_id = input("ID del estudiante a actualizar: ")
            telefono = input("Nuevo teléfono: ")
            correo = input("Nuevo correo: ")
            Estudiante.actualizar_estudiante(telefono, correo,estudiante_id)

        elif opcion == '4':
            estudiante_id = input("ID del estudiante a eliminar: ")
            eliminado=Estudiante.eliminar_estudiante(estudiante_id)
            if eliminado:
                print("Alumno eliminado")
            else:
                print("Alumno no eliminado")
        elif opcion=='5':
            Estudiante.listar_estudiantes()
        elif opcion == '6':
            print("Saliendo del módulo de estudiantes...")
            break

        else:
            print("Opción no válida, inténtalo de nuevo.")

if __name__ == "__main__":
    estudiante_main()