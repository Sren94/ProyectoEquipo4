from .Conexion import Conexion
class Inscripcion:
    @staticmethod
    def crear_inscripcion(id_estudiante, id_curso, estado):
        """
        Crea una nueva inscripción para un estudiante en un curso.
        Retorna True si se registra, False en caso de error o si ya existe una inscripción activa.
        """
        registrado = False
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                # Verificar existencia de estudiante y curso
                cursor.execute("SELECT id FROM Estudiantes WHERE id = %s", (id_estudiante,))
                if cursor.fetchone() is None:
                    print('Error: Estudiante no existe')
                    return False
                
                cursor.execute("SELECT id FROM Cursos WHERE id = %s", (id_curso,))
                if cursor.fetchone() is None:
                    print('Error: Curso no existe')
                    return False
                
                
                cursor.execute(
                    "SELECT id FROM Inscripciones WHERE id_estudiante = %s AND id_curso = %s AND estado = 'inscrito'",
                    (id_estudiante, id_curso)
                )
                if cursor.fetchone() is not None:
                    print('Error: Ya existe una inscripción activa para este estudiante en el curso')
                    return False
                
                
                consulta = (
                    "INSERT INTO Inscripciones (id_estudiante, id_curso, estado, fecha_inscripcion) "
                    "VALUES (%s, %s, %s, CURRENT_DATE)"
                )
                cursor.execute(consulta, (id_estudiante, id_curso, estado))
                conexion.commit()
                print('Inscripción creada exitosamente')
                registrado = True
            except Exception as e:
                print(f'Error al crear inscripción: {e}')
            finally:
                conexion.close()
        return registrado

    @staticmethod
    def leer_inscripcion(id_inscripcion):
        """
        Devuelve la inscripción con el ID dado.
        """
        resultado = None
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM Inscripciones WHERE id = %s", (id_inscripcion,))
                resultado = cursor.fetchone()
            except Exception as e:
                print(f'Error al leer inscripción: {e}')
            finally:
                conexion.close()
        return resultado

    @staticmethod
    def actualizar_inscripcion(id_inscripcion, estado):
        """
        Actualiza el estado de una inscripción.
        Retorna True si se actualiza, False en caso contrario.
        """
        actualizado = False
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute(
                    "UPDATE Inscripciones SET estado=%s WHERE id=%s",
                    (estado, id_inscripcion)
                )
                conexion.commit()
                if cursor.rowcount > 0:
                    print('Inscripción actualizada exitosamente')
                    actualizado = True
                else:
                    print('No se encontró inscripción para actualizar')
            except Exception as e:
                print(f'Error al actualizar inscripción: {e}')
            finally:
                conexion.close()
        return actualizado

    @staticmethod
    def eliminar_inscripcion(id_inscripcion):
        """
        Elimina una inscripción y retorna True si se eliminó, False en caso contrario.
        """
        eliminado = False
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute(
                    "DELETE FROM Inscripciones WHERE id=%s",
                    (id_inscripcion,)
                )
                conexion.commit()
                if cursor.rowcount > 0:
                    print('Inscripción eliminada exitosamente')
                    eliminado = True
                else:
                    print('No se encontró inscripción para eliminar')
            except Exception as e:
                print(f'Error al eliminar inscripción: {e}')
            finally:
                conexion.close()
        return eliminado

    @staticmethod
    def inscripciones_por_estudiante(id_estudiante):
        """
        Devuelve una lista de inscripciones de un estudiante.
        """
        resultados = []
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT * FROM Inscripciones WHERE id_estudiante = %s",
                    (id_estudiante,)
                )
                resultados = cursor.fetchall()
            except Exception as e:
                print(f'Error al obtener inscripciones por estudiante: {e}')
            finally:
                conexion.close()
        return resultados

    @staticmethod
    def inscripciones_por_curso(id_curso):
        """
        Devuelve una lista de inscripciones de un curso.
        """
        resultados = []
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT * FROM Inscripciones WHERE id_curso = %s",
                    (id_curso,)
                )
                resultados = cursor.fetchall()
            except Exception as e:
                print(f'Error al obtener inscripciones por curso: {e}')
            finally:
                conexion.close()
        return resultados
##########################
    @staticmethod
    def lista_inscripciones():
        """
        Devuelve una lista con todas las inscripciones registradas en la base de datos.
        """
        resultados = []
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM Inscripciones")
                resultados = cursor.fetchall()
            except Exception as e:
                print(f'Error al obtener todas las inscripciones: {e}')
            finally:
                conexion.close()
        return resultados
    
    @staticmethod
    def baja(id_estudiante, id_curso):
        """
        Cambia el estado de una inscripción activa (estado 'inscrito') a 'baja'
        para el estudiante y curso especificados.
        """
        exito = False
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute(
                    """
                    UPDATE Inscripciones
                    SET estado = %s, fecha_inscripcion= NOW()
                    WHERE id_estudiante = %s AND id_curso = %s AND estado = %s
                    """,
                    ("baja", id_estudiante, id_curso, "inscrito")
                )
                if cursor.rowcount > 0:
                    conexion.commit()
                    exito = True
            except Exception as e:
                print(f'Error al dar de baja la inscripción: {e}')
            finally:
                conexion.close()
        return exito



def menu_inscripciones():
    while True:
        print("---Gestión de Inscripciones ---")
        print("1. Crear Inscripción")
        print("2. Leer Inscripción")
        print("3. Actualizar Inscripción")
        print("4. Eliminar Inscripción")
        print("5. Inscripciones por Estudiante")
        print("6. Inscripciones por Curso")
        print("7. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            id_estudiante = input("ID Estudiante: ")
            id_curso = input("ID Curso: ")
            estado = input("Estado (inscrito/baja): ")
            Inscripcion.crear_inscripcion(id_estudiante, id_curso, estado)
        elif opcion == '2':
            id_inscripcion = input("ID de la inscripción: ")
            print(Inscripcion.leer_inscripcion(id_inscripcion))
        elif opcion == '3':
            id_inscripcion = input("ID de la inscripción: ")
            estado = input("Nuevo estado: ")
            Inscripcion.actualizar_inscripcion(id_inscripcion, estado)
        elif opcion == '4':
            id_inscripcion = input("ID de la inscripción: ")
            Inscripcion.eliminar_inscripcion(id_inscripcion)
        elif opcion == '5':
            id_estudiante = input("ID Estudiante: ")
            inscripciones = Inscripcion.inscripciones_por_estudiante(id_estudiante)
            for ins in inscripciones:
                print(ins)
        elif opcion == '6':
            id_curso = input("ID Curso: ")
            inscripciones = Inscripcion.inscripciones_por_curso(id_curso)
            for ins in inscripciones:
                print(ins)
        elif opcion == '7':
            break
        else:
            print("Opción no válida.")

    

if __name__ == '__main__':
    menu_inscripciones()