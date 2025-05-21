import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import simpledialog
import mysql.connector
from datetime import datetime
from interfaces.login import SuperAdminLogin

class Estudiante:
    def __init__(self,  callback_volver=None):
        self.callback_volver = callback_volver
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="facultad"
        )
        self.cursor = self.conn.cursor()

        self.root = tk.Tk()
        self.root.title("Gestión de Estudiantes - MySQL")
        self.root.geometry("750x550")
        self.root.config(bg="#2C3E50")  # Fondo oscuro azul/gris

        self.estilo = ttk.Style(self.root)
        self.estilo.theme_use("clam")  # Tema ttk para más personalización
        
        # Estilos para Treeview
        self.estilo.configure("Treeview",
                              background="#34495E",
                              foreground="white",
                              rowheight=25,
                              fieldbackground="#34495E",
                              font=("Segoe UI", 10))
        self.estilo.map("Treeview", background=[("selected", "#1ABC9C")], foreground=[("selected", "black")])
        
        # Estilo para botones
        self.estilo.configure("TButton",
                              background="#1ABC9C",
                              foreground="white",
                              font=("Segoe UI", 10, "bold"),
                              padding=6)
        self.estilo.map("TButton",
                        background=[('active', '#16A085'), ('!disabled', '#1ABC9C')],
                        foreground=[('active', 'white')])

        self.crear_interfaz()
        self.mostrar_estudiantes()
        self.root.mainloop()

    def crear_interfaz(self):
        # Frame del formulario con fondo ligeramente más claro
        frame_form = tk.Frame(self.root, bg="#34495E", padx=15, pady=15)
        frame_form.pack(pady=10, fill="x", padx=10)

        labels = [
            ("ID", 0),
            ("Nombre*", 1),
            ("Apellido*", 2),
            ("Fecha Nacimiento* (YYYY-MM-DD)", 3),
            ("Teléfono", 4),
            ("Correo", 5)
        ]
        for text, row in labels:
            lbl = tk.Label(frame_form, text=text, bg="#34495E", fg="white", font=("Segoe UI", 10, "bold"))
            lbl.grid(row=row, column=0, sticky="w", pady=3)
        
        self.entry_id = tk.Entry(frame_form, state="readonly", bg="#d2f9ff", fg="black", font=("Segoe UI", 10))
        self.entry_id.grid(row=0, column=1, pady=3, sticky="ew")

        self.entry_nombre = tk.Entry(frame_form, bg="#d2f9ff", fg="black", font=("Segoe UI", 10))
        self.entry_nombre.grid(row=1, column=1, pady=3, sticky="ew")

        self.entry_apellido = tk.Entry(frame_form, bg="#d2f9ff", fg="black", font=("Segoe UI", 10))
        self.entry_apellido.grid(row=2, column=1, pady=3, sticky="ew")

        self.entry_fecha_nacimiento = tk.Entry(frame_form, bg="#d2f9ff", fg="black", font=("Segoe UI", 10))
        self.entry_fecha_nacimiento.grid(row=3, column=1, pady=3, sticky="ew")

        self.entry_telefono = tk.Entry(frame_form, bg="#d2f9ff", fg="black", font=("Segoe UI", 10))
        self.entry_telefono.grid(row=4, column=1, pady=3, sticky="ew")

        self.entry_correo = tk.Entry(frame_form, bg="#d2f9ff", fg="black", font=("Segoe UI", 10))
        self.entry_correo.grid(row=5, column=1, pady=3, sticky="ew")

        # Expandir columnas para que los entry se ajusten
        frame_form.grid_columnconfigure(1, weight=1)

        # Botones con ttk para estilo moderno
        frame_buttons = tk.Frame(self.root, bg="#2C3E50")
        frame_buttons.pack(pady=10, fill="x", padx=10)

        botones = [
            ("Agregar", self.agregar_estudiante),
            ("Actualizar", self.actualizar_estudiante),
            ("Eliminar", self.eliminar_estudiante),
            ("Limpiar", self.limpiar_campos),
            ("Regresar", self.regresar)
        ]

        for i, (text, cmd) in enumerate(botones):
            btn = ttk.Button(frame_buttons, text=text, command=cmd)
            btn.grid(row=0, column=i, padx=5, sticky="ew")
            frame_buttons.grid_columnconfigure(i, weight=1)

        # Tabla de estudiantes
        self.tree = ttk.Treeview(self.root,
                                 columns=("ID", "Nombre", "Apellido", "Fecha Nacimiento", "Teléfono", "Correo"),
                                 show="headings", style="Treeview")
        columnas = [("ID", 50), ("Nombre", 120), ("Apellido", 120), ("Fecha Nacimiento", 120), ("Teléfono", 100), ("Correo", 150)]
        for col, ancho in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=ancho, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_estudiante)


    def validar_fecha(self, fecha_str):
        try:
            datetime.strptime(fecha_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def agregar_estudiante(self):
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        fecha_nacimiento = self.entry_fecha_nacimiento.get().strip()
        telefono = self.entry_telefono.get().strip()
        correo = self.entry_correo.get().strip()

        if not nombre or not apellido or not fecha_nacimiento:
            messagebox.showwarning("Campos requeridos", "Los campos Nombre, Apellido y Fecha de Nacimiento son obligatorios")
            return
        
        if not self.validar_fecha(fecha_nacimiento):
            messagebox.showwarning("Formato inválido", "La fecha de nacimiento debe tener formato YYYY-MM-DD")
            return
        
        if correo:
            self.cursor.execute("SELECT id FROM estudiantes WHERE correo = %s", (correo,))
            if self.cursor.fetchone():
                messagebox.showwarning("Correo duplicado", "El correo electrónico ya está registrado")
                return

        self.cursor.execute(
            "INSERT INTO estudiantes (nombre, apellido, fecha_nacimiento, telefono, correo) VALUES (%s, %s, %s, %s, %s)",
            (nombre, apellido, fecha_nacimiento, telefono if telefono else None, correo if correo else None)
        )
        self.conn.commit()
        self.limpiar_campos()
        self.mostrar_estudiantes()
        messagebox.showinfo("Éxito", "Estudiante agregado correctamente")

    def mostrar_estudiantes(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.cursor.execute("SELECT id, nombre, apellido, fecha_nacimiento, telefono, correo FROM estudiantes")
        for row in self.cursor.fetchall():
            self.tree.insert("", tk.END, values=row)

    def seleccionar_estudiante(self, event):
        item = self.tree.selection()
        if item:
            datos = self.tree.item(item[0], "values")
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, datos[0])
            self.entry_id.config(state="readonly")

            self.entry_nombre.config(state="normal")
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, datos[1])
            self.entry_nombre.config(state="readonly")

            self.entry_apellido.config(state="normal")
            self.entry_apellido.delete(0, tk.END)
            self.entry_apellido.insert(0, datos[2])
            self.entry_apellido.config(state="readonly")

            self.entry_fecha_nacimiento.config(state="normal")
            self.entry_fecha_nacimiento.delete(0, tk.END)
            self.entry_fecha_nacimiento.insert(0, datos[3])
            self.entry_fecha_nacimiento.config(state="readonly")

            self.entry_telefono.delete(0, tk.END)
            self.entry_telefono.insert(0, datos[4] if datos[4] else "")
            self.entry_correo.delete(0, tk.END)
            self.entry_correo.insert(0, datos[5] if datos[5] else "")

    def actualizar_estudiante(self):
        id_estudiante = self.entry_id.get()
        if not id_estudiante:
            messagebox.showwarning("Seleccionar", "Selecciona un estudiante primero")
            return

        telefono = self.entry_telefono.get().strip()
        correo = self.entry_correo.get().strip()

        if correo:
            self.cursor.execute("SELECT id FROM estudiantes WHERE correo = %s AND id != %s", (correo, id_estudiante))
            if self.cursor.fetchone():
                messagebox.showwarning("Correo duplicado", "El correo electrónico ya está registrado por otro estudiante")
                return

        self.cursor.execute("""
            UPDATE estudiantes
            SET telefono = %s, correo = %s
            WHERE id = %s
        """, (telefono if telefono else None, correo if correo else None, id_estudiante))
        self.conn.commit()
        self.limpiar_campos()
        self.mostrar_estudiantes()
        messagebox.showinfo("Actualizado", "Estudiante actualizado correctamente")

    def eliminar_estudiante(self):
        id_estudiante = self.entry_id.get()
        if not id_estudiante:
            messagebox.showwarning("Seleccionar", "Selecciona un estudiante primero")
            return
        confirm = messagebox.askyesno("Confirmar eliminación", "¿Seguro que quieres eliminar este estudiante?")
        if confirm:
            self.cursor.execute("DELETE FROM estudiantes WHERE id = %s", (id_estudiante,))
            self.conn.commit()
            self.limpiar_campos()
            self.mostrar_estudiantes()
            messagebox.showinfo("Eliminado", "Estudiante eliminado correctamente")

    def limpiar_campos(self):
        self.entry_id.config(state="normal")
        self.entry_id.delete(0, tk.END)
        self.entry_id.config(state="readonly")

        self.entry_nombre.config(state="normal")
        self.entry_nombre.delete(0, tk.END)

        self.entry_apellido.config(state="normal")
        self.entry_apellido.delete(0, tk.END)

        self.entry_fecha_nacimiento.config(state="normal")
        self.entry_fecha_nacimiento.delete(0, tk.END)

        self.entry_telefono.delete(0, tk.END)
        self.entry_correo.delete(0, tk.END)
    
    def regresar(self):
        self.root.destroy()
        if self.callback_volver:
            self.callback_volver()
