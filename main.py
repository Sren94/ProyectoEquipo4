import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

def conectar_bd():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="facultad"
    )

def obtener_estudiantes():
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre FROM estudiantes ORDER BY nombre")
    estudiantes = cursor.fetchall()
    cursor.close()
    conexion.close()
    return estudiantes

def obtener_cursos():
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre FROM cursos ORDER BY nombre")
    cursos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return cursos

def obtener_materias_y_calificaciones_por_estudiante(id_estudiante):
    conexion = conectar_bd()
    cursor = conexion.cursor(dictionary=True)
    query = """
        SELECT cu.id AS id_curso, cu.nombre AS curso, c.id AS id_calif, c.nota
        FROM cursos cu
        LEFT JOIN calificaciones c ON cu.id = c.id_curso AND c.id_estudiante = %s
        ORDER BY cu.nombre
    """
    cursor.execute(query, (id_estudiante,))
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    return resultados

def agregar_calificacion(id_estudiante, id_curso, calificacion):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO calificaciones (id_estudiante, id_curso, nota) VALUES (%s, %s, %s)",
        (id_estudiante, id_curso, calificacion)
    )
    conexion.commit()
    id_insertado = cursor.lastrowid
    cursor.close()
    conexion.close()
    return id_insertado

def actualizar_calificacion(id_calif, calificacion):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE calificaciones SET nota=%s WHERE id=%s",
        (calificacion, id_calif)
    )
    conexion.commit()
    cursor.close()
    conexion.close()

def eliminar_calificacion(id_calif):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM calificaciones WHERE id=%s", (id_calif,))
    conexion.commit()
    cursor.close()
    conexion.close()


class InterfazCalificaciones(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.alumno_actual = None  # Guardar ID alumno filtrado

        filtro_frame = tk.LabelFrame(self, text="Buscar alumno por ID")
        filtro_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(filtro_frame, text="ID Alumno:").pack(side="left", padx=5)
        self.entry_id_alumno = tk.Entry(filtro_frame, width=10)
        self.entry_id_alumno.pack(side="left", padx=5)
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

        # Bind para editar calificación con doble clic en la tabla
        self.tree_materias.bind("<Double-1>", self.editar_calificacion_en_tabla)

    def mostrar_materias_por_alumno(self):
        try:
            id_est = int(self.entry_id_alumno.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese un ID válido")
            return
        resultados = obtener_materias_y_calificaciones_por_estudiante(id_est)
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
            eliminar_calificacion(id_calif)
            self.mostrar_materias_por_alumno()

    def abrir_formulario(self, id_calif=None, valores=None):
        form = tk.Toplevel(self)
        form.title("Formulario Calificación")

        cursos = obtener_cursos()

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
                actualizar_calificacion(id_calif, calif_val)
            else:
                # Insertar nueva calificación para el alumno actual
                agregar_calificacion(self.alumno_actual, id_curso, calif_val)
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
                agregar_calificacion(self.alumno_actual, id_curso, calif_num)
            else:
                actualizar_calificacion(id_calif, calif_num)

            entry_edit.destroy()
            self.mostrar_materias_por_alumno()

        entry_edit.bind("<Return>", guardar_edicion)
        entry_edit.bind("<FocusOut>", lambda e: entry_edit.destroy())

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gestión de Calificaciones")
    root.geometry("600x500")
    app = InterfazCalificaciones(root)
    app.pack(fill="both", expand=True)
    root.mainloop()
