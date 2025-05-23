from .Modelos import Conexion as Conexion
from tkinter import messagebox, ttk
import bcrypt
import tkinter as tk
from .Modelos.Cursos import Curso  
from .Modelos.Estudiante import Estudiante
from .Modelos.Inscripcion import Inscripcion
from .Modelos.Calificaciones import Calificacion
from datetime import datetime
import csv

# Clase para la interfaz de Calificaciones
class InterfazCalificaciones:
    def __init__(self, root, callback_volver):
        self.root = root
        self.callback_volver = callback_volver
        self.root.title("Gestión de Calificaciones")
        self.root.geometry("600x500")
        
        self.alumno_actual = None  # Guardar ID alumno filtrado

        # Frame superior con botón de regreso
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=5, pady=5)
        tk.Button(top_frame, text="Regresar", command=self.regresar).pack(side="left")

        # Frame de filtro
        filtro_frame = tk.LabelFrame(self.root, text="Buscar alumno por ID")
        filtro_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(filtro_frame, text="ID Alumno:").pack(side="left", padx=5)
        self.entry_id_alumno = tk.Entry(filtro_frame, width=10)
        self.entry_id_alumno.pack(side="left", padx=5)

        # Label para mostrar nombre del alumno
        self.label_nombre_alumno = tk.Label(filtro_frame, text="")
        self.label_nombre_alumno.pack(side="left", padx=10)

        tk.Button(filtro_frame, text="Buscar", command=self.mostrar_materias_por_alumno).pack(side="left", padx=5)

        # Treeview para mostrar materias y calificaciones
        self.tree_materias = ttk.Treeview(self.root, columns=("Curso", "Calificación"), show="headings", height=15)
        self.tree_materias.heading("Curso", text="Curso")
        self.tree_materias.heading("Calificación", text="Calificación")
        self.tree_materias.pack(fill="both", expand=True, padx=5, pady=5)

        # Frame de botones
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", pady=5)

        tk.Button(btn_frame, text="Agregar Calificación", command=self.agregar).pack(side="left", padx=5)

        # Bind para editar calificación con doble clic en la tabla
        self.tree_materias.bind("<Double-1>", self.editar_calificacion_en_tabla)

    def regresar(self):
        self.root.destroy()
        if self.callback_volver:
            self.callback_volver()

    def mostrar_materias_por_alumno(self):
        try:
            id_est = int(self.entry_id_alumno.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese un ID válido")
            self.label_nombre_alumno.config(text="")  # Limpia el label si error
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
                Calificacion.eliminar_calificacion(id_calif)
                self.mostrar_materias_por_alumno()

    def abrir_formulario(self, id_calif=None, valores=None):
        form = tk.Toplevel(self.root)
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
                # Actualizar calificación existente
                Calificacion.actualizar_calificacion(id_calif, calif_val)
            else:
                # Insertar nueva calificación para el alumno actual
                Calificacion.agregar_calificacion(self.alumno_actual, id_curso, calif_val)
            self.mostrar_materias_por_alumno()
            form.destroy()

        tk.Button(form, text="Guardar", command=guardar).grid(row=2, column=0, columnspan=2, pady=10)

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
                Calificacion.agregar_calificacion(self.alumno_actual, id_curso, calif_num)
            else:
                Calificacion.actualizar_calificacion(id_calif, calif_num)

            entry_edit.destroy()
            self.mostrar_materias_por_alumno()

        entry_edit.bind("<Return>", guardar_edicion)
        entry_edit.bind("<FocusOut>", lambda e: entry_edit.destroy())

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

    # ----------- Pestaña Cursos -----------
    def _crear_pestana_cursos(self):
        # Formulario
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

        # Botones
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

        # Tabla de cursos
        tabla_frame = tk.Frame(self.tab_cursos)
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = ("id", "nombre", "descripcion", "creditos")
        self.tree_cursos = ttk.Treeview(tabla_frame, columns=columnas, show="headings")
        self.tree_cursos.heading("id", text="ID")
        self.tree_cursos.heading("nombre", text="Nombre")
        self.tree_cursos.heading("descripcion", text="Descripcion")
        self.tree_cursos.heading("creditos", text="Creditos")

        self.tree_cursos.column("id", width=100)
        self.tree_cursos.column("nombre", width=200)
        self.tree_cursos.column("descripcion", width=250)
        self.tree_cursos.column("creditos", width=100)

        self.tree_cursos.pack(fill="both", expand=True)

        self.tree_cursos.bind("<<TreeviewSelect>>", self.cargar_curso_seleccionado)

        self.cargar_cursos()

    def cargar_cursos(self):
        for item in self.tree_cursos.get_children():
            self.tree_cursos.delete(item)
        cursos = Curso.lista_cursos()
        if cursos:
            for curso in cursos:
                self.tree_cursos.insert("", "end", values=(curso["id"], curso["nombre"], curso["descripcion"], curso["creditos"]))

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
        seleccion = self.tree_cursos.selection()
        if seleccion:
            item = self.tree_cursos.item(seleccion[0])
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
        self.tree_cursos.selection_remove(self.tree_cursos.selection())

    # ----------- Pestaña Inscripciones -----------
    def _crear_pestana_inscripciones(self):
        # Etiquetas y entradas
        tk.Label(self.tab_inscripciones, text="Id del estudiante:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry_id_est = tk.Entry(self.tab_inscripciones)
        self.entry_id_est.grid(row=0, column=1, pady=10)

        tk.Label(self.tab_inscripciones, text="Id del curso:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.entry_id_curso = tk.Entry(self.tab_inscripciones)
        self.entry_id_curso.grid(row=1, column=1, pady=10)

        # Botones
        btn_inscribir = tk.Button(self.tab_inscripciones, text="Inscribir", command=self.inscribir)
        btn_inscribir.grid(row=2, column=0, pady=10)

        btn_baja = tk.Button(self.tab_inscripciones, text="Dar de baja", command=self.dar_baja)
        btn_baja.grid(row=2, column=1, pady=10)

        # Tabla de inscripciones
        columns = ("ID Estudiante", "ID de curso", "Estado", "Fecha")
        self.tree_inscripciones = ttk.Treeview(self.tab_inscripciones, columns=columns, show="headings")
        for col in columns:
            self.tree_inscripciones.heading(col, text=col)
            self.tree_inscripciones.column(col, width=150)
        self.tree_inscripciones.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.cargar_inscripciones()

    def cargar_inscripciones(self):
        for item in self.tree_inscripciones.get_children():
            self.tree_inscripciones.delete(item)
        inscripciones = Inscripcion.lista_inscripciones()  
        if inscripciones:
            for ins in inscripciones:
                self.tree_inscripciones.insert("", "end", values=(
                    ins["id_estudiante"], ins["id_curso"], ins["estado"], ins["fecha_inscripcion"]
                ))

    def inscribir(self):
        id_estudiante = self.entry_id_est.get().strip()
        id_curso = self.entry_id_curso.get().strip()
        if not id_estudiante or not id_curso:
            messagebox.showwarning("Validación", "Debe ingresar ambos ID de estudiante y curso.")
            return

        inscripciones = Inscripcion.lista_inscripciones()

        for ins in inscripciones:
            if ins["id_estudiante"] == id_estudiante and ins["id_curso"] == id_curso:
                if ins["estado"].strip().lower() == "inscrito":
                    messagebox.showwarning("Ya inscrito", "El estudiante ya está inscrito en este curso.")
                    return

        for ins in inscripciones:
            if ins["id_estudiante"] == id_estudiante and ins["id_curso"] == id_curso:
                if ins["estado"].strip().lower() == "baja":
                    if Inscripcion.actualizar_estado(id_estudiante, id_curso, "inscrito"):
                        messagebox.showinfo("Éxito", "Estudiante reinscrito correctamente.")
                        self.cargar_inscripciones()
                    else:
                        messagebox.showerror("Error", "No se pudo reinscribir al estudiante.")
                    return

        if Inscripcion.crear_inscripcion(id_estudiante, id_curso, "inscrito"):
            messagebox.showinfo("Éxito", "Estudiante inscrito correctamente.")
            self.cargar_inscripciones()
        else:
            messagebox.showerror("Error", "No se pudo inscribir al estudiante.")

    def dar_baja(self):
        id_estudiante = self.entry_id_est.get().strip()
        id_curso = self.entry_id_curso.get().strip()
        if not id_estudiante or not id_curso:
            messagebox.showwarning("Validación", "Debe ingresar ambos ID de estudiante y curso.")
            return
        if Inscripcion.baja(id_estudiante, id_curso):
            messagebox.showinfo("Éxito", "Estudiante dado de baja correctamente")
            self.cargar_inscripciones()
        else:
            messagebox.showerror("Error", "No se pudo dar de baja al estudiante")

    # ----------- Botón Regresar -----------
    def regresar(self):
        if self.callback_volver:
            self.callback_volver()
        self.root.destroy()

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
        
        # Botón para resumen general
        boton_resumen = tk.Button(panel, text="Módulo de Base de Datos y Reportes", width=40, height=2,
                                command=self.mostrar_resumen_general)
        boton_resumen.pack(pady=5)

    def mostrar_resumen_general(self):
        # Verificar si la ventana ya existe
        if hasattr(self, 'resumen_window'):
            try:
                if self.resumen_window.winfo_exists():
                    self.resumen_window.lift()
                    return
            except tk.TclError:
                pass  # La ventana fue destruida
    
    # Crear nueva ventana
        self.resumen_window = tk.Toplevel()
        self.resumen_window.title("Resumen General del Sistema")
        self.resumen_window.geometry("900x650")
    
    # Frame superior para el botón de regresar
        top_frame = tk.Frame(self.resumen_window)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Botón para regresar al menú principal
        btn_regresar = tk.Button(top_frame, text="Regresar al Menú", 
                            command=self._cerrar_resumen)
        btn_regresar.pack(side=tk.LEFT)
    
    # Notebook (pestañas)
        notebook = ttk.Notebook(self.resumen_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Pestaña de Alumnos
        tab_alumnos = ttk.Frame(notebook)
        self._crear_tabla_resumen(tab_alumnos, "Estudiantes", 
                            ["ID", "Nombre", "Apellido", "Email", "Teléfono"],
                            Estudiante.lista_estudiantes())
    
    # Pestaña de Cursos
        tab_cursos = ttk.Frame(notebook)
        self._crear_tabla_resumen(tab_cursos, "Cursos",
                            ["ID", "Nombre", "Descripción", "Créditos"],
                            Curso.lista_cursos())
    
    # Pestaña de Inscripciones
        tab_inscripciones = ttk.Frame(notebook)
        self._crear_tabla_resumen(tab_inscripciones, "Inscripciones",
                            ["ID Estudiante", "ID Curso", "Estado", "Fecha"],
                            Inscripcion.lista_inscripciones())
    
    # Pestaña de Calificaciones
        tab_calificaciones = ttk.Frame(notebook)
        self._crear_tabla_resumen(tab_calificaciones, "Calificaciones",
                            ["ID", "ID Estudiante", "ID Curso", "Calificación"],
                            Calificacion.listar_calificaciones())
    # Pestaña de cursos por alumno
        tab_cursos_por_alumno = ttk.Frame(notebook)
        self._crear_tabla_resumen(tab_cursos_por_alumno, "cursos por alumno",
                    ["ID Estudiante", "ID Curso", "Estado", "Fecha"],
                    Curso.curso_por_alumno())
    
        tab_Calificaciones_por_curso = ttk.Frame(notebook)
        self._crear_tabla_resumen(tab_Calificaciones_por_curso, "Calificaciones por curso",
                    ["ID", "ID Estudiante", "ID Curso", "nota"],
                    Calificacion.calificaciones_por_curso())
        
    
    # Añadir pestañas
        notebook.add(tab_alumnos, text="Alumnos")
        notebook.add(tab_cursos, text="Cursos")
        notebook.add(tab_inscripciones, text="Inscripciones")
        notebook.add(tab_calificaciones, text="Calificaciones")
        notebook.add(tab_cursos_por_alumno, text="Cursos por alumno")
        notebook.add(tab_Calificaciones_por_curso, text="Calificacion por alumno")
    
    # Botón para exportar a CSV
        btn_frame = tk.Frame(self.resumen_window)
        btn_frame.pack(fill=tk.X, pady=5)
    
        btn_exportar = tk.Button(btn_frame, text="Exportar a CSV", 
                           command=self.exportar_resumen_a_csv)
        btn_exportar.pack(side=tk.RIGHT, padx=10)
    
    # Configurar manejo de cierre
        self.resumen_window.protocol("WM_DELETE_WINDOW", self._cerrar_resumen)

    def _cerrar_resumen(self):
        """Cierra la ventana de resumen y regresa al menú principal"""
        if hasattr(self, 'resumen_window'):
            self.resumen_window.destroy()
            del self.resumen_window
        # Opcional: hacer visible la ventana principal si está oculta
        if hasattr(self, 'panel'):
            self.panel.deiconify()
    
    def _crear_tabla_resumen(self, parent, title, columns, data):
        tk.Label(parent, text=f"Resumen de {title}", font=('Arial', 12, 'bold')).pack(pady=5)
        
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")
        
        # Insertar datos
        if data:
            for item in data:
                tree.insert("", "end", values=tuple(item.values()))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def exportar_resumen_a_csv(self):
        import csv
        from datetime import datetime
        
        # Obtener todos los datos
        estudiantes = Estudiante.lista_estudiantes()
        cursos = Curso.lista_cursos()
        inscripciones = Inscripcion.lista_inscripciones()
        calificaciones = Calificacion.listar_calificaciones()
        cursos_por_alumno=Curso.curso_por_alumno()
        calificacion_por_alumno=Calificacion.calificaciones_por_alumno()
        
        
        # Crear nombre de archivo con fecha
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resumen_sistema_{fecha}.csv"
        
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Escribir sección de estudiantes
                writer.writerow(["ESTUDIANTES"])
                writer.writerow(["ID", "Nombre", "Apellido","telefono", "correo"])
                for est in estudiantes:
                    writer.writerow([est['id'], est['nombre'], est['apellido'], est['telefono'], est['correo']])
                
                writer.writerow([])  # Línea en blanco
                
                # Escribir sección de cursos
                writer.writerow(["CURSOS"])
                writer.writerow(["ID", "Nombre", "Descripción", "Créditos"])
                for cur in cursos:
                    writer.writerow([cur['id'], cur['nombre'], 
                                    cur['descripcion'], cur['creditos']])
                
                writer.writerow([])  # Línea en blanco
                
                # Escribir sección de inscripciones
                writer.writerow(["INSCRIPCIONES"])
                writer.writerow(["ID Estudiante", "ID Curso", "Estado", "Fecha"])
                for ins in inscripciones:
                    writer.writerow([ins['id_estudiante'], ins['id_curso'], 
                                   ins['estado'], ins['fecha_inscripcion']])
                
                writer.writerow([])  # Línea en blanco
                
                # Escribir sección de calificaciones
                writer.writerow(["CALIFICACIONES"])
                writer.writerow(["ID", "ID Estudiante", "ID Curso", "Calificación"])
                for cal in calificaciones:
                    writer.writerow([cal['id'], cal['id_estudiante'], 
                                   cal['id_curso'], cal['nota']])
                        # Escribir sección de cursos por alumno
                writer.writerow(["CURSOS POR ALUMNO"])
                writer.writerow(["ID Estudiante", "ID Curso", "Nombre Curso", "Estado", "Fecha Inscripción"])
                for curso in cursos_por_alumno:
                    writer.writerow([
                    curso.get('id_estudiante', ''),
                    curso.get('id_curso', ''),
                    curso.get('nombre_curso', curso.get('nombre', '')),  # Por si usa diferente nombre
                    curso.get('estado', ''),
                curso.get('fecha_inscripcion', '')
                    ])
        
                writer.writerow([])  # Línea en blanco
        
        # Escribir sección de calificaciones por alumno
                writer.writerow(["CALIFICACIONES POR ALUMNO"])
                writer.writerow(["ID Estudiante", "ID Curso", "Nombre Curso", "Nota", "Fecha Registro"])
                for calif in calificacion_por_alumno:
                    writer.writerow([
                        calif.get('id_estudiante', ''),
                        calif.get('id_curso', ''),
                        calif.get('nombre_curso', calif.get('nombre', '')),  # Por si usa diferente nombre
                        calif.get('nota', ''),
                        calif.get('fecha_registro', '')])
            
            messagebox.showinfo("Éxito", f"Resumen exportado correctamente a {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el resumen: {str(e)}")
    def cerrar_resumen(self):
        if hasattr(self, 'resumen_window'):
            self.resumen_window.destroy()
            del self.resumen_window

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
        InterfazCalificaciones(root_calificaciones, callback_volver=volver_a_bienvenida)
        root_calificaciones.mainloop()

if __name__ == "__main__":
    SuperAdminLogin()