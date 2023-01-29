# Ejecuta intento de trabajar con ventanas en HD, solo disponible en Windows
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# Importaciones de librerias
import tkinter as tk
from client.app_gui import Frame, barra_menu

def main():
    root = tk.Tk()
    root.title("Procesador de retenciones")
    root.iconbitmap("img/logo.ico")
    root.resizable(0,0)

    app = Frame(root = root)
    barra_menu(root, app)

    app.mainloop()

if __name__ == '__main__':
    main()
    