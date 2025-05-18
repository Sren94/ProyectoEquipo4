from .Modelos import Conexion as Conexion
from tkinter import messagebox
import bcrypt
import tkinter as tk

#Luis Rene y Cintia
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
        self.ventana.destroy()
        panel = tk.Tk()
        panel.title("Panel de Bienvenida")
        panel.geometry("400x300")

        label_bienvenida = tk.Label(panel, text=f"Bienvenido, {usuario}", font=("Arial", 14))
        label_bienvenida.pack(pady=10)

        botones = ["Módulo de Gestión de Estudiantes", "Módulo de Gestión de Cursos e Inscripciones", "Módulo de Gestión de Calificaciones"]
        for texto in botones:
            boton = tk.Button(panel, text=texto, width=40, height=2)
            boton.pack(pady=5)

    def login_superadmin(self, usuario, contrasena):
        connection =Conexion.Conexion()
        if connection:
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT contrasena_hash FROM Administradores
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
            messagebox.showinfo("Éxito", "Inicio de sesión exitoso.")
            self.mostrar_panel_bienvenida(usuario)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas o usuario no es superadmin.")


if __name__ == "__main__":
    SuperAdminLogin()
