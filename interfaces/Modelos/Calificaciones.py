# Módulo de Calificaciones 
from .Conexion import Conexion
from mysql.connector import Error

class Calificacion:
    @staticmethod
    def crear_calificacion(id_estudiante, id_curso, nota):
        """
        Registra una calificación, verificando que existan el estudiante y el curso.
        Retorna True si se registró, False en caso de error.
        """
        registrado = False
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor()
            # Verificar existencia de estudiante y curso
            try:
                cursor.execute("SELECT id FROM Estudiantes WHERE id = %s", (id_estudiante,))
                if cursor.fetchone() is None:
                    print('Error: Estudiante no existe')
                    return False
                cursor.execute("SELECT id FROM Cursos WHERE id = %s", (id_curso,))
                if cursor.fetchone() is None:
                    print('Error: Curso no existe')
                    return False
                # Insertar calificación
                consulta = "INSERT INTO Calificaciones (id_estudiante, id_curso, nota) VALUES (%s, %s, %s)"
                cursor.execute(consulta, (id_estudiante, id_curso, nota))
                conexion.commit()
                print('Calificación registrada exitosamente')
                registrado = True
            except Error as e:
                print(f'Error al registrar calificación: {e.msg}')
            except Exception as e:
                print(f'Error inesperado al registrar calificación: {e}')
            finally:
                conexion.close()
        return registrado

    @staticmethod
    def leer_calificacion(id_estudiante, id_curso):
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            consulta = "SELECT * FROM Calificaciones WHERE id_estudiante=%s AND id_curso=%s"
            try:
                cursor.execute(consulta, (id_estudiante, id_curso))
                return cursor.fetchone()
            except Exception as e:
                print(f'Error al leer calificación: {e}')
            finally:
                conexion.close()

    @staticmethod
    def listar_calificaciones():
        conexion =Conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            consulta = "SELECT * FROM Calificaciones"
            try:
                cursor.execute(consulta)
                lista_calificaiones=cursor.fetchall()
                for cal in lista_calificaiones:
                    print(cal)
                return lista_calificaiones
            except Exception as e:
                print(f'Error al listar calificaciones: {e}')
            finally:
                conexion.close()

    @staticmethod
    def actualizar_calificacion(id_estudiante, id_curso, nota):
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor()
            consulta = """UPDATE Calificaciones SET nota=%s WHERE id_estudiante=%s AND id_curso=%s"""
            try:
                cursor.execute(consulta, (nota, id_estudiante, id_curso))
                conexion.commit()
                print('Calificación actualizada exitosamente')
            except Exception as e:
                print(f'Error al actualizar calificación: {e}')
            finally:
                conexion.close()

    @staticmethod
    def eliminar_calificacion(id_estudiante, id_curso):
        """
        Elimina una calificación de la base de datos y retorna True si se eliminó, False en caso contrario.
        """
        eliminado = False
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor()
            consulta = "DELETE FROM Calificaciones WHERE id_estudiante=%s AND id_curso=%s"
            try:
                cursor.execute(consulta, (id_estudiante, id_curso))
                conexion.commit()
                if cursor.rowcount > 0:
                    print('Calificación eliminada exitosamente')
                    eliminado = True
                else:
                    print('No se encontró calificación para eliminar')
            except Exception as e:
                print(f'Error al eliminar calificación: {e}')
            finally:
                conexion.close()
        return eliminado


    @staticmethod
    def calificaciones_por_alumno(id_estudiante):
        """
        Devuelve una lista de todas las calificaciones de un estudiante.
        """
        resultados = []
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            consulta = (
                "SELECT c.id AS id_curso, c.nombre AS curso, cal.nota, cal.fecha_registro "
                "FROM Calificaciones cal "
                "JOIN Cursos c ON cal.id_curso = c.id "
                "WHERE cal.id_estudiante = %s"
            )
            try:
                cursor.execute(consulta, (id_estudiante,))
                resultados = cursor.fetchall()
            except Exception as e:
                print(f'Error al obtener calificaciones por alumno: {e}')
            finally:
                conexion.close()
        return resultados

    @staticmethod
    def calificaciones_por_curso(id_curso):
        """
        Devuelve una lista de diccionarios con las calificaciones de un curso.
        """
        resultados = []
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                cursor.execute(
                    """
                    SELECT cal.id_estudiante, e.nombre AS estudiante, cal.nota, cal.fecha_registro
                    FROM Calificaciones cal
                    JOIN Estudiantes e ON cal.id_estudiante = e.id
                    WHERE cal.id_curso = %s
                    """, (id_curso,)
                )
                resultados = cursor.fetchall()
            except Exception as e:
                print(f'Error al obtener calificaciones por curso: {e}')
            finally:
                conexion.close()
        return resultados


def menu_calificaciones():
    while True:
        print("\n--- Gestión de Calificaciones ---")
        print("1. Registrar Calificación")
        print("2. Leer Calificación")
        print("3. Listar Calificaciones")
        print("4. Actualizar Calificación")
        print("5. Eliminar Calificación")
        print("6. Calificaciones por Alumno")
        print("7. Calificaciones por Curso")
        print("8. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            id_estudiante = input("ID Estudiante: ")
            id_curso = input("ID Curso: ")
            nota = input("Nota: ")
            Calificacion.crear_calificacion(id_estudiante, id_curso, nota)
        elif opcion == '2':
            id_estudiante = input("ID Estudiante: ")
            id_curso = input("ID Curso: ")
            print(Calificacion.leer_calificacion(id_estudiante, id_curso))
        elif opcion == '3':
            Calificacion.listar_calificaciones()
        elif opcion == '4':
            id_estudiante = input("ID Estudiante: ")
            id_curso = input("ID Curso: ")
            nota = input("Nueva Nota: ")
            Calificacion.actualizar_calificacion(id_estudiante, id_curso, nota)
        elif opcion == '5':
            id_estudiante = input("ID Estudiante: ")
            id_curso = input("ID Curso: ")
            Calificacion.eliminar_calificacion(id_estudiante, id_curso)
        elif opcion == '6':
            id_estudiante = input("ID Estudiante: ")
            print( Calificacion.calificaciones_por_alumno(id_estudiante))
        elif opcion == '7':
            id_curso = input("ID Curso: ")
            print(Calificacion.calificaciones_por_curso(id_curso))
        elif opcion == '8':
            break
        else:
            print("Opción no válida.")

if __name__ == '__main__':
    menu_calificaciones()
