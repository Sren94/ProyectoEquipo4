import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import bcrypt
from datetime import datetime
from .Modelos import Conexion as Conexion
from .Modelos.Cursos import Curso  
from .Modelos.Estudiante import Estudiante
from .Modelos.Inscripcion import Inscripcion

# Clase para la interfaz de Calificaciones
class InterfazCalificaciones(tk.Frame):
    def __init__(self, parent, callback_volver=None):
        super().__init__(parent)
        self.callback_volver = callback_volver
        self.alumno_actual = None  # Guardar ID alumno filtrado

        filtro_frame = tk.LabelFrame(self, text="Buscar alumno por ID")
        filtro_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(filtro_frame, text="ID Alumno:").pack(side="left", padx=5)
        self.entry_id_alumno = tk.Entry(filtro_frame, width=10)
        self.entry_id_alumno.pack(side="left", padx=5)

        # Label para mostrar nombre del alumno
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
        
        if callback_volver:
            tk.Button(btn_frame, text="Regresar", command=self.regresar).pack(side="right", padx=5)

        # Bind para editar calificación con doble clic en la tabla
        self.tree_materias.bind("<Double-1>", self.editar_calificacion_en_tabla)

    def regresar(self):
        if self.callback_volver:
            self.callback_volver()

    def mostrar_materias_por_alumno(self):
        try:
            id_est = int(self.entry_id_alumno.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese un ID válido")
            self.label_nombre_alumno.config(text="")  # Limpia el label si error
            return

        nombre = self.obtener_nombre_alumno_por_id(id_est)
        if not nombre:
            messagebox.showinfo("Información", f"No se encontró alumno con ID {id_est}")
            self.label_nombre_alumno.config(text="")
            return

        self.label_nombre_alumno.config(text=f"Nombre: {nombre}")

        resultados = self.obtener_materias_y_calificaciones_por_estudiante(id_est)
        if not resultados:
            messagebox.showinfo("Información", f"No se encontraron cursos para el alumno con ID {id_est}")
            return
        self.alumno_actual = id_est

        # Limpiar Treeview materias
        for item in self.tree_materias.get_children():
            self.tree_materias.delete(item)

        # Insertar filas con id_calif guardado en el 'iid' para fácil referencia
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
            self.eliminar_calificacion(id_calif)
            self.mostrar_materias_por_alumno()

    def abrir_formulario(self, id_calif=None, valores=None):
        form = tk.Toplevel(self)
        form.title("Formulario Calificación")

        cursos = self.obtener_cursos()

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
                # Actualizar calificación existente
                self.actualizar_calificacion(id_calif, calif_val)
            else:
                # Insertar nueva calificación para el alumno actual
                self.agregar_calificacion(self.alumno_actual, id_curso, calif_val)
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
        if columna != "#2":  # Solo columna Calificación editable
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
                self.agregar_calificacion(self.alumno_actual, id_curso, calif_num)
            else:
                self.actualizar_calificacion(id_calif, calif_num)

            entry_edit.destroy()
            self.mostrar_materias_por_alumno()

        entry_edit.bind("<Return>", guardar_edicion)
        entry_edit.bind("<FocusOut>", lambda e: entry_edit.destroy())

    # Métodos de conexión a BD (simplificados para el ejemplo)
    def obtener_nombre_alumno_por_id(self, id_est):
        connection = Conexion.Conexion()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = "SELECT nombre, apellido FROM estudiantes WHERE id = %s"
                cursor.execute(query, (id_est,))
                result = cursor.fetchone()
                if result:
                    return f"{result['nombre']} {result['apellido']}"
                return None
            except Exception as e:
                print(f"Error al obtener nombre alumno: {e}")
                return None
            finally:
                connection.close()
        return None

    def obtener_materias_y_calificaciones_por_estudiante(self, id_est):
        connection = Conexion.Conexion()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT c.id AS id_curso, c.nombre AS curso, cal.id AS id_calif, cal.nota
                FROM cursos c
                LEFT JOIN calificaciones cal ON c.id = cal.id_curso AND cal.id_estudiante = %s
                WHERE c.id IN (SELECT id_curso FROM inscripciones WHERE id_estudiante = %s AND estado = 'inscrito')
                """
                cursor.execute(query, (id_est, id_est))
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener materias: {e}")
                return None
            finally:
                connection.close()
        return None

    def obtener_cursos(self):
        connection = Conexion.Conexion()
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT id, nombre FROM cursos"
                cursor.execute(query)
                return cursor.fetchall()
            except Exception as e:
                print(f"Error al obtener cursos: {e}")
                return []
            finally:
                connection.close()
        return []

    def agregar_calificacion(self, id_est, id_curso, nota):
        connection = Conexion.Conexion()
        if connection:
            try:
                cursor = connection.cursor()
                query = "INSERT INTO calificaciones (id_estudiante, id_curso, nota) VALUES (%s, %s, %s)"
                cursor.execute(query, (id_est, id_curso, nota))
                connection.commit()
                return True
            except Exception as e:
                print(f"Error al agregar calificación: {e}")
                return False
            finally:
                connection.close()
        return False

    def actualizar_calificacion(self, id_calif, nota):
        connection = Conexion.Conexion()
        if connection:
            try:
                cursor = connection.cursor()
                query = "UPDATE calificaciones SET nota = %s WHERE id = %s"
                cursor.execute(query, (nota, id_calif))
                connection.commit()
                return True
            except Exception as e:
                print(f"Error al actualizar calificación: {e}")
                return False
            finally:
                connection.close()
        return False

    def eliminar_calificacion(self, id_calif):
        connection = Conexion.Conexion()
        if connection:
            try:
                cursor = connection.cursor()
                query = "DELETE FROM calificaciones WHERE id = %s"
                cursor.execute(query, (id_calif,))
                connection.commit()
                return True
            except Exception as e:
                print(f"Error al eliminar calificación: {e}")
                return False
            finally:
                connection.close()
        return False

# Clase para la interfaz de Cursos (con botón Regresar)
class InterfazCursos:
    def __init__(self, root, callback_volver):
        self.root = root
        self.callback_volver = callback_volver
        self.root.title("Gestión de Cursos e Inscripciones")
        self.root.geometry("800x550")

        # Pestañas
        tabs = ttk.Notebook(root)
        self.tab_cursos = tk.Frame(tabs, bg="#f0ece8")
        self.tab_inscripciones = tk.Frame(tabs)
        tabs.add(self.tab_cursos, text="Cursos")
        tabs.add(self.tab_inscripciones, text="Inscripciones")
        tabs.pack(fill="both", expand=True)

        self._crear_pestana_cursos()
        self._crear_pestana_inscripciones()

    # ... (resto del código de InterfazCursos igual que antes)
    # (Mantén todos los métodos existentes de InterfazCursos aquí)

# Clase para el login y panel de superadmin
class SuperAdminLogin:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Login Superadmin")
        self.ventana.geometry("300x200")

        self.label_usuario = tk.Label(self.ventana, text="Usuario:")
        self.label_usuario.pack(pady=5)

        self.entry_usuario = tk.Entry(self.ventana)
        self.entry_usuario.pack(pady=5)

        self.label_contrasena = tk.Label(self.ventana, text="Contraseña:")
        self.label_contrasena.pack(pady=5)

        self.entry_contrasena = tk.Entry(self.ventana, show="*")
        self.entry_contrasena.pack(pady=5)

        self.boton_login = tk.Button(self.ventana, text="Iniciar Sesión", command=self.iniciar_sesion)
        self.boton_login.pack(pady=10)

        self.ventana.mainloop()

    def mostrar_panel_bienvenida(self, usuario):
        panel = tk.Tk()
        panel.title("Panel de Bienvenida")
        panel.geometry("400x300")

        label_bienvenida = tk.Label(panel, text=f"Bienvenido, {usuario}", font=("Arial", 14))
        label_bienvenida.pack(pady=10)

        # Botón que abre la interfaz de gestión de estudiantes
        boton_estudiantes = tk.Button(panel, text="Módulo de Gestión de Estudiantes", width=40, height=2,
                                     command=lambda: self.abrir_gestion_estudiantes(panel))
        boton_estudiantes.pack(pady=5)

        # Botón que abre la interfaz de gestión de cursos
        boton_cursos = tk.Button(panel, text="Módulo de Gestión de Cursos e Inscripciones", width=40, height=2,
                                command=lambda: self.abrir_gestion_cursos(panel))
        boton_cursos.pack(pady=5)

        # Botón para módulo de calificaciones
        boton_calificaciones = tk.Button(panel, text="Módulo de Gestión de Calificaciones", width=40, height=2,
                                       command=lambda: self.abrir_gestion_calificaciones(panel))
        boton_calificaciones.pack(pady=5)

    def login_superadmin(self, usuario, contrasena):
        connection = Conexion.Conexion()
        if connection:
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT contrasena_hash FROM administradores
            WHERE usuario = %s AND rol = 'superadmin'
            """
            try:
                cursor.execute(query, (usuario,))
                result = cursor.fetchone()
                if result and bcrypt.checkpw(contrasena.encode(), result['contrasena_hash'].encode()):
                    return True
                else:
                    return False
            except Exception as e:
                print(f'Error al verificar el inicio de sesión: {e}')
            finally:
                connection.close()
        return False

    def iniciar_sesion(self):
        usuario = self.entry_usuario.get()
        contrasena = self.entry_contrasena.get()
        if self.login_superadmin(usuario, contrasena):
            self.usuario_actual = usuario
            messagebox.showinfo("Éxito", "Inicio de sesión exitoso.")
            self.mostrar_panel_bienvenida(usuario)
            self.ventana.destroy()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas o usuario no es superadmin.")

    def abrir_gestion_estudiantes(self, ventana_actual):
        ventana_actual.destroy()

        def volver_a_bienvenida():
            self.mostrar_panel_bienvenida(self.usuario_actual)

        Estudiante(callback_volver=volver_a_bienvenida)

    def abrir_gestion_cursos(self, ventana_actual):
        ventana_actual.destroy()

        def volver_a_bienvenida():
            self.mostrar_panel_bienvenida(self.usuario_actual)

        root_cursos = tk.Tk()
        InterfazCursos(root_cursos, callback_volver=volver_a_bienvenida)
        root_cursos.mainloop()

    def abrir_gestion_calificaciones(self, ventana_actual):
        ventana_actual.destroy()

        def volver_a_bienvenida():
            self.mostrar_panel_bienvenida(self.usuario_actual)

        root_calificaciones = tk.Tk()
        root_calificaciones.title("Gestión de Calificaciones")
        root_calificaciones.geometry("600x400")
        
        # Crear el frame de calificaciones dentro de la ventana
        frame_calificaciones = InterfazCalificaciones(root_calificaciones, callback_volver=volver_a_bienvenida)
        frame_calificaciones.pack(fill="both", expand=True, padx=10, pady=10)
        
        root_calificaciones.mainloop()

if __name__ == "__main__":
    SuperAdminLogin()