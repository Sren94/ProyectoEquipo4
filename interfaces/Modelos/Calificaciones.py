from .Conexion import Conexion
from mysql.connector import Error
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class Calificacion:
    @staticmethod
    def obtener_conexion():
        from .Conexion import Conexion
        return Conexion()
    @staticmethod
    def crear_calificacion(id_estudiante, id_curso, nota):
        registrado = False
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                # Verifica existencia del estudiante y curso
                cursor.execute("SELECT id FROM Estudiantes WHERE id = %s", (id_estudiante,))
                if cursor.fetchone() is None:
                    print('Error: Estudiante no existe')
                    return False
                cursor.execute("SELECT id FROM Cursos WHERE id = %s", (id_curso,))
                if cursor.fetchone() is None:
                    print('Error: Curso no existe')
                    return False
                # Inserta la calificación
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
        connection = Conexion()
        
        if connection:
            cursor = connection.cursor(dictionary=True)
            try:
               
                print(cursor.execute("SELECT * FROM calificaciones"))
                cursos=cursor.fetchall()
                return cursos
            except Exception as e:
                print(f'Error al obtener calificaciones: {e}')
                return []
            finally:
                connection.close()
        return []

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
        resultados = []
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            consulta = (
                "SELECT cu.id AS id_curso, cu.nombre AS curso, cal.id AS id_calif, cal.nota "
                "FROM Inscripciones i "
                "JOIN Cursos cu ON i.id_curso = cu.id "
                "LEFT JOIN Calificaciones cal ON cu.id = cal.id_curso AND cal.id_estudiante = i.id_estudiante "
                "WHERE i.id_estudiante = %s AND i.estado = 'inscrito' "
                "ORDER BY cu.nombre"
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
    
    @staticmethod
    def obtener_cursos():
        conexion = Conexion()
        cursos = []
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute("SELECT id, nombre FROM Cursos ORDER BY nombre")
                cursos = cursor.fetchall()
            except Exception as e:
                print(f'Error al obtener cursos: {e}')
            finally:
                conexion.close()
        return cursos

    @staticmethod
    def obtener_materias_y_calificaciones_por_estudiante(id_estudiante):
        conexion = Conexion()
        resultados = []
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            query = """
                SELECT cu.id AS id_curso, cu.nombre AS curso, c.id AS id_calif, c.nota
                FROM Inscripciones i
                JOIN Cursos cu ON i.id_curso = cu.id
                LEFT JOIN Calificaciones c ON cu.id = c.id_curso AND c.id_estudiante = i.id_estudiante
                WHERE i.id_estudiante = %s AND i.estado = 'inscrito'
                ORDER BY cu.nombre
            """
            try:
                cursor.execute(query, (id_estudiante,))
                resultados = cursor.fetchall()
            except Exception as e:
                print(f'Error al obtener materias y calificaciones por estudiante: {e}')
            finally:
                conexion.close()
        return resultados

    @staticmethod
    def agregar_calificacion(id_estudiante, id_curso, calificacion):
        conexion = Conexion()
        id_insertado = None
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute(
                    "INSERT INTO Calificaciones (id_estudiante, id_curso, nota) VALUES (%s, %s, %s)",
                    (id_estudiante, id_curso, calificacion)
                )
                conexion.commit()
                id_insertado = cursor.lastrowid
            except Exception as e:
                print(f'Error al agregar calificación: {e}')
            finally:
                cursor.close()
                conexion.close()
        return id_insertado

    @staticmethod
    def actualizar_calificacion_por_id(id_calif, calificacion):
        conexion = Conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute(
                    "UPDATE Calificaciones SET nota=%s WHERE id=%s",
                    (calificacion, id_calif)
                )
                conexion.commit()
            except Exception as e:
                print(f'Error al actualizar calificación por ID: {e}')
            finally:
                cursor.close()
                conexion.close()

    @staticmethod
    def eliminar_calificacion_por_id(id_calif):
        conexion = Conexion()
        eliminado = False
        if conexion:
            cursor = conexion.cursor()
            try:
                cursor.execute("DELETE FROM Calificaciones WHERE id=%s", (id_calif,))
                conexion.commit()
                eliminado = cursor.rowcount > 0
            except Exception as e:
                print(f'Error al eliminar calificación por ID: {e}')
            finally:
                cursor.close()
                conexion.close()
        return eliminado
    @staticmethod
    def obtener_nombre_alumno_por_id(id_alumno):
        conexion = Conexion()
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT nombre FROM estudiantes WHERE id = %s"
        cursor.execute(query, (id_alumno,))
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()
        if resultado:
            return resultado["nombre"]
        else:
            return None

class InterfazCalificaciones(tk.Frame):
    def __init__(self, parent, callback_volver=None):
        super().__init__(parent)
        self.alumno_actual = None  # Guardar ID alumno filtrado
        self.callback_volver = callback_volver  # Función para volver al menú anterior

        filtro_frame = tk.LabelFrame(self, text="Buscar alumno por ID")
        filtro_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(filtro_frame, text="ID Alumno:").pack(side="left", padx=5)
        self.entry_id_alumno = tk.Entry(filtro_frame, width=10)
        self.entry_id_alumno.pack(side="left", padx=5)

        self.label_nombre_alumno = tk.Label(filtro_frame, text="")
        self.label_nombre_alumno.pack(side="left", padx=10)

        tk.Button(filtro_frame, text="Buscar", command=self.mostrar_materias_por_alumno).pack(side="left", padx=5)

        self.tree_materias = ttk.Treeview(self, columns=("Curso", "Calificación"), show="headings", height=15)
        self.tree_materias.heading("Curso", text="Curso")
        self.tree_materias.heading("Calificación", text="Calificación")
        self.tree_materias.pack(fill="both", expand=True, padx=5, pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=5)

        tk.Button(btn_frame, text="Agregar Calificación", command=self.agregar).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Editar Calificación", command=self.editar).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Eliminar Calificación", command=self.eliminar).pack(side="left", padx=5)

        if self.callback_volver:
            tk.Button(btn_frame, text="Volver", command=self.callback_volver).pack(side="right", padx=5)

        self.tree_materias.bind("<Double-1>", self.editar_calificacion_en_tabla)

    def mostrar_materias_por_alumno(self):
        try:
            id_est = int(self.entry_id_alumno.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese un ID válido")
            self.label_nombre_alumno.config(text="")
            return

        nombre = Calificacion.obtener_nombre_alumno_por_id(id_est)
        if not nombre:
            messagebox.showinfo("Información", f"No se encontró alumno con ID {id_est}")
            self.label_nombre_alumno.config(text="")
            return

        self.label_nombre_alumno.config(text=f"Nombre: {nombre}")
        resultados = Calificacion.obtener_materias_y_calificaciones_por_estudiante(id_est)

        if not resultados:
            messagebox.showinfo("Información", f"No se encontraron cursos para el alumno con ID {id_est}")
            return

        self.alumno_actual = id_est
        for item in self.tree_materias.get_children():
            self.tree_materias.delete(item)

        for r in resultados:
            nota = r["nota"] if r["nota"] is not None else "-"
            self.tree_materias.insert("", "end", iid=r["id_calif"] if r["id_calif"] else f"nuevo_{r['id_curso']}",
                                      values=(r["curso"], nota))

    def agregar(self):
        if not self.alumno_actual:
            messagebox.showwarning("Aviso", "Primero busque un alumno por ID")
            return
        self.abrir_formulario()

    def editar(self):
        seleccionado = self.tree_materias.selection()
        if not seleccionado:
            messagebox.showwarning("Aviso", "Seleccione una calificación para editar")
            return
        id_calif = seleccionado[0]
        valores = self.tree_materias.item(id_calif, "values")
        self.abrir_formulario(id_calif, valores)

    def eliminar(self):
        seleccionado = self.tree_materias.selection()
        if not seleccionado:
            messagebox.showwarning("Aviso", "Seleccione una calificación para eliminar")
            return
        id_calif = seleccionado[0]
        if str(id_calif).startswith("nuevo_"):
            messagebox.showinfo("Información", "Esta materia no tiene calificación para eliminar")
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar esta calificación?"):
            Calificacion.eliminar_calificacion(id_calif)
            self.mostrar_materias_por_alumno()

    def abrir_formulario(self, id_calif=None, valores=None):
        form = tk.Toplevel(self)
        form.title("Formulario Calificación")

        cursos = Calificacion.obtener_cursos()

        tk.Label(form, text="Curso:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        cb_curso = ttk.Combobox(form, state="readonly", values=[c[1] for c in cursos])
        cb_curso.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="Calificación:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        calif_entry = tk.Entry(form)
        calif_entry.grid(row=1, column=1, padx=5, pady=5)

        if valores:
            curso_nombre, calificacion = valores
            cb_curso.set(curso_nombre)
            calif_entry.insert(0, calificacion)

        def guardar():
            curso_sel = cb_curso.get()
            try:
                calif_val = float(calif_entry.get())
            except ValueError:
                messagebox.showerror("Error", "La calificación debe ser un número válido")
                return
            if not curso_sel:
                messagebox.showerror("Error", "Seleccione un curso")
                return

            id_curso = next((c[0] for c in cursos if c[1] == curso_sel), None)
            if id_curso is None:
                messagebox.showerror("Error", "Error interno: no se encontró curso")
                return

            if id_calif and not str(id_calif).startswith("nuevo_"):
                Calificacion.actualizar_calificacion(id_calif, calif_val)
            else:
                Calificacion.agregar_calificacion(self.alumno_actual, id_curso, calif_val)

            self.mostrar_materias_por_alumno()
            form.destroy()

        tk.Button(form, text="Guardar", command=guardar).grid(row=2, column=0, columnspan=2, pady=10)

        form.transient(self)
        form.grab_set()
        self.wait_window(form)

    def editar_calificacion_en_tabla(self, event):
        region = self.tree_materias.identify("region", event.x, event.y)
        if region != "cell":
            return
        columna = self.tree_materias.identify_column(event.x)
        if columna != "#2":
            return
        fila = self.tree_materias.identify_row(event.y)
        if not fila:
            return

        x, y, width, height = self.tree_materias.bbox(fila, columna)
        valor_actual = self.tree_materias.set(fila, "Calificación")

        entry_edit = tk.Entry(self.tree_materias)
        entry_edit.place(x=x, y=y, width=width, height=height)
        entry_edit.insert(0, valor_actual)
        entry_edit.focus()

        def guardar_edicion(event=None):
            nuevo_valor = entry_edit.get().strip()
            if nuevo_valor == "":
                messagebox.showerror("Error", "La calificación no puede estar vacía")
                return
            try:
                calif_num = float(nuevo_valor)
            except ValueError:
                messagebox.showerror("Error", "La calificación debe ser un número válido")
                return

            id_calif = fila
            if str(id_calif).startswith("nuevo_"):
                id_curso = int(id_calif.replace("nuevo_", ""))
                Calificacion.agregar_calificacion(self.alumno_actual, id_curso, calif_num)
            else:
                Calificacion.actualizar_calificacion(id_calif, calif_num)

            entry_edit.destroy()
            self.mostrar_materias_por_alumno()

        entry_edit.bind("<Return>", guardar_edicion)
        entry_edit.bind("<FocusOut>", lambda e: entry_edit.destroy())


    @staticmethod
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
                calificaciones = Calificacion.listar_calificaciones()
                for calif in calificaciones:
                    print(calif)
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
                resultados = Calificacion.calificaciones_por_alumno(id_estudiante)
                for res in resultados:
                    print(res)
            elif opcion == '7':
                id_curso = input("ID Curso: ")
                resultados = Calificacion.calificaciones_por_curso(id_curso)
                for res in resultados:
                    print(res)
            elif opcion == '8':
                break
            else:
                print("Opción no válida.")

if __name__ == '__main__':
    Calificacion.menu_calificaciones()
