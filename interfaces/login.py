from .Modelos import Conexion as Conexion
from tkinter import messagebox, ttk
import bcrypt
import tkinter as tk
from .Modelos.Cursos import Curso  
from .Modelos.Estudiante import Estudiante  # Para abrir la interfaz de estudiantes

# Clase para la interfaz de Cursos (con botón Regresar)
class InterfazCursos:
    def __init__(self, root, callback_volver):
        self.root = root
        self.callback_volver = callback_volver
        self.root.title("Gestión de Cursos")
        self.root.geometry("800x500")

        # Pestañas
        tabs = ttk.Notebook(root)
        self.tab_cursos = tk.Frame(tabs, bg="#f0ece8")
        self.tab_inscripciones = tk.Frame(tabs)
        tabs.add(self.tab_cursos, text="Cursos")
        tabs.add(self.tab_inscripciones, text="Inscripciones")
        tabs.pack(fill="both", expand=True)

        # ----- Formulario -----
        form_frame = tk.Frame(self.tab_cursos, bg="#f0ece8")
        form_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(form_frame, text="Nombre del curso:", bg="#f0ece8").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_nombre = tk.Entry(form_frame)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Créditos:", bg="#f0ece8").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_creditos = tk.Entry(form_frame)
        self.entry_creditos.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Descripción del curso:", bg="#f0ece8").grid(row=0, column=2, rowspan=2, sticky="n", padx=10, pady=5)
        self.txt_descripcion = tk.Text(form_frame, width=40, height=4)
        self.txt_descripcion.grid(row=0, column=3, rowspan=2, padx=5, pady=5)

        # ----- Botones -----
        botones_frame = tk.Frame(form_frame, bg="#f0ece8")
        botones_frame.grid(row=2, column=0, columnspan=4, pady=10)

        btn_crear = tk.Button(botones_frame, text="Crear", width=15, command=self.crear_curso)
        btn_crear.pack(side="left", padx=10)

        btn_actualizar = tk.Button(botones_frame, text="Actualizar", width=15, command=self.actualizar_curso)
        btn_actualizar.pack(side="left", padx=10)

        btn_eliminar = tk.Button(botones_frame, text="Eliminar", width=15, command=self.eliminar_curso)
        btn_eliminar.pack(side="left", padx=10)

        btn_regresar = tk.Button(botones_frame, text="Regresar", width=15, command=self.regresar)
        btn_regresar.pack(side="left", padx=10)

        # ----- Tabla de cursos -----
        tabla_frame = tk.Frame(self.tab_cursos)
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = ("id", "nombre", "descripcion", "creditos")
        self.tree = ttk.Treeview(tabla_frame, columns=columnas, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("descripcion", text="Descripcion")
        self.tree.heading("creditos", text="Creditos")

        self.tree.column("id", width=100)
        self.tree.column("nombre", width=200)
        self.tree.column("descripcion", width=250)
        self.tree.column("creditos", width=100)

        self.tree.pack(fill="both", expand=True)

        # Al seleccionar un item en la tabla
        self.tree.bind("<<TreeviewSelect>>", self.cargar_curso_seleccionado)

        # Cargar cursos desde BD al iniciar
        self.cargar_cursos()

    def cargar_cursos(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Obtener cursos desde la base de datos
        cursos = Curso.lista_cursos()
        if cursos:
            for curso in cursos:
                self.tree.insert("", "end", values=(curso["id"], curso["nombre"], curso["descripcion"], curso["creditos"]))

    def crear_curso(self):
        nombre = self.entry_nombre.get().strip()
        descripcion = self.txt_descripcion.get("1.0", tk.END).strip()
        creditos = self.entry_creditos.get().strip()
        if not nombre or not creditos:
            messagebox.showwarning("Validación", "Nombre y créditos son obligatorios.")
            return
        creado = Curso.crear_curso(nombre, descripcion, creditos)
        if creado:
            messagebox.showinfo("Éxito", "Curso creado correctamente.")
            self.limpiar_campos()
            self.cargar_cursos()
        else:
            messagebox.showerror("Error", "No se pudo crear el curso.")

    def cargar_curso_seleccionado(self, event):
        seleccion = self.tree.selection()
        if seleccion:
            item = self.tree.item(seleccion[0])
            id_, nombre, descripcion, creditos = item["values"]
            self.curso_seleccionado_id = id_
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, nombre)
            self.txt_descripcion.delete("1.0", tk.END)
            self.txt_descripcion.insert(tk.END, descripcion)
            self.entry_creditos.delete(0, tk.END)
            self.entry_creditos.insert(0, creditos)
        else:
            self.curso_seleccionado_id = None

    def actualizar_curso(self):
        if not hasattr(self, 'curso_seleccionado_id') or self.curso_seleccionado_id is None:
            messagebox.showwarning("Selección", "Seleccione un curso para actualizar.")
            return
        nombre = self.entry_nombre.get().strip()
        descripcion = self.txt_descripcion.get("1.0", tk.END).strip()
        creditos = self.entry_creditos.get().strip()
        if not nombre or not creditos:
            messagebox.showwarning("Validación", "Nombre y créditos son obligatorios.")
            return
        actualizado = Curso.actualizar_curso(self.curso_seleccionado_id, nombre, descripcion, creditos)
        if actualizado:
            messagebox.showinfo("Éxito", "Curso actualizado correctamente.")
            self.limpiar_campos()
            self.cargar_cursos()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el curso.")

    def eliminar_curso(self):
        if not hasattr(self, 'curso_seleccionado_id') or self.curso_seleccionado_id is None:
            messagebox.showwarning("Selección", "Seleccione un curso para eliminar.")
            return
        confirm = messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este curso?")
        if confirm:
            eliminado = Curso.eliminar_curso(self.curso_seleccionado_id)
            if eliminado:
                messagebox.showinfo("Éxito", "Curso eliminado correctamente.")
                self.limpiar_campos()
                self.cargar_cursos()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el curso.")

    def limpiar_campos(self):
        self.entry_nombre.delete(0, tk.END)
        self.txt_descripcion.delete("1.0", tk.END)
        self.entry_creditos.delete(0, tk.END)
        self.curso_seleccionado_id = None
        self.tree.selection_remove(self.tree.selection())

    def regresar(self):
        self.root.destroy()
        self.callback_volver()


# Luis Rene y Cintia
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

        # Botón para módulo de calificaciones (sin funcionalidad por ahora)
        boton_calificaciones = tk.Button(panel, text="Módulo de Gestión de Calificaciones", width=40, height=2)
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


if __name__ == "__main__":
    SuperAdminLogin()
