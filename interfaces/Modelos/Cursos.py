from .Conexion import Conexion

class Curso:
    @staticmethod
    def crear_curso(nombre, descripcion,creditos):
        conexion = Conexion()
        creado=False
        if conexion:
            cursor = conexion.cursor()
            query = """INSERT INTO cursos (nombre, descripcion,creditos) VALUES (%s, %s,%s)"""
            try:
                cursor.execute(query, (nombre, descripcion,creditos))
                conexion.commit()
                print('Curso creado exitosamente')
                creado=True
            except Exception as e:
                print(f'Error al crear curso: {e}')
            finally:
                conexion.close()
        return creado

    @staticmethod
    def lista_cursos():
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            query = "SELECT * FROM cursos"
            try:
                cursor.execute(query)
                cursos = cursor.fetchall()
                for curso in cursos:
                    print(curso)
                return cursos
            except Exception as e:
                print(f'Error al listar cursos: {e}')
            finally:
                conexion.close()
    def actualizar_curso(curso_id, nombre, descripcion,creditos):
        conexion = Conexion()
        actualizado=True
        if conexion:
            cursor = conexion.cursor()
            query = """UPDATE cursos SET nombre = %s, descripcion = %s,creditos=%s WHERE id = %s"""
            try:
                cursor.execute(query, (nombre, descripcion,creditos, curso_id))
                conexion.commit()
                print('Curso actualizado exitosamente')
                actualizado=True
            except Exception as e:
                print(f'Error al actualizar curso: {e}')
            finally:
                conexion.close()
        return actualizado

    @staticmethod
    def eliminar_curso(curso_id):
        conexion = Conexion()
        eliminado=False
        if conexion:
            cursor = conexion.cursor()
            query = "DELETE FROM cursos WHERE id = %s"
            try:
                cursor.execute(query, (curso_id,))
                conexion.commit()
                print('Curso eliminado exitosamente')
                eliminado=True
            except Exception as e:
                print(f'Error al eliminar curso: {e}')
            finally:
                conexion.close()
        return eliminado
    @staticmethod
    def curso_por_alumno(estudiante_id=None):
        """
        Lista los cursos en los que está inscrito un estudiante.
        Retorna una lista de diccionarios con los datos para mostrar en la tabla.
        Si no se proporciona estudiante_id, retorna todos los registros.
        """
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            query = (
            "SELECT i.id_estudiante as 'ID Estudiante', "
            "       i.id_curso as 'ID Curso', "
            "       i.estado as 'Estado', "
            "       i.fecha_inscripcion as 'Fecha' "
            "FROM Inscripciones i "
            "JOIN Cursos c ON i.id_curso = c.id "
        )
            params = ()
        
            if estudiante_id:
                query += "WHERE i.id_estudiante = %s"
                params = (estudiante_id,)
            
            try:
                cursor.execute(query, params)
                inscripciones = cursor.fetchall()
            
                # Formatear la fecha para cada registro
                for insc in inscripciones:
                    if insc['Fecha']:
                        insc['Fecha'] = insc['Fecha'].strftime('%Y-%m-%d')
                    else:
                        insc['Fecha'] = ''
            
                return inscripciones if inscripciones else []
            except Exception as e:
                print(f'Error al obtener cursos por alumno: {e}')
                return []
            finally:
                conexion.close()
# Cursos.py - Método principal del módulo cursos
def curso_main():
    while True:
        print("\n--- Gestión de Cursos ---")
        print("1. Crear Curso")
        print("2. Listar Cursos")
        print("3. Actualizar Curso")
        print("4. Eliminar Curso")
        print("5. Cursos Por Estudiante")
        print("6. Salir")
        
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            nombre = input("Nombre del curso: ")
            descripcion = input("Descripción del curso: ")
            creditos=input("Creditos del curso: ")
            Curso.crear_curso(nombre, descripcion,creditos)
        elif opcion == '2':
            Curso.lista_cursos()
        elif opcion == '3':
            curso_id=input("Id del curso: ")
            descripcion=input("Descripcion del curso: ")
            nombre=input("Nombre del curso")
            creditos=input("Creditos del curso: ")
            Curso.actualizar_curso(curso_id,descripcion,nombre,creditos)
        elif opcion=='4':
            curso_id=input("Id del curso: ")
            Curso.eliminar_curso(curso_id)
        elif opcion=='5':
            estudiante_id=input("Id del alumno: ")
            Curso.curso_por_alumno(estudiante_id)
        elif opcion=='6':
            print('Saliendo...')
            break
        else:
            print("Opción no válida, inténtalo de nuevo.")

if __name__ == "__main__":
   curso_main()


