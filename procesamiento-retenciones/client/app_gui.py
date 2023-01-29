from msilib.schema import RadioButton
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from turtle import window_width
from model.retenciones_sql import crear_tabla, borrar_tabla, listar, eliminar_filas_purgarcomercios, exportar_tabla_csv, existe_tabla, cargar_tabla_impuestos, crear_archivo_inserts
# import os
# import errno

def barra_menu(root, app):
    barra_menu = tk.Menu(root)
    root.config(menu = barra_menu)
    
    menu_ingresar = tk.Menu(barra_menu, tearoff = 0)
    barra_menu.add_cascade(label = 'Cargar', menu = menu_ingresar)
    menu_ingresar.add_command(label= 'Tabla de impuestos', command = lambda: app.cargar_tabla_impuestos())
    menu_ingresar.add_command(label= 'Comercios de PVS', command = lambda: crear_tabla(archivo=filedialog.askopenfilename(initialdir = "/", title = "Seleccione el archivo", filetypes = {("Archivos CSV", "*.csv")}),nombre_tabla='comercios'))
    menu_ingresar.add_command(label= 'Contratos de impuestos', command = lambda: crear_tabla(archivo=filedialog.askopenfilename(initialdir = "/", title = "Seleccione el archivo", filetypes = {("Archivos CSV", "*.csv")}),nombre_tabla='contratos'))

    menu_purgar = tk.Menu(barra_menu, tearoff = 0)
    barra_menu.add_cascade(label = 'Purgar', menu = menu_purgar)
    menu_purgar.add_command(label= 'Depurar padrones', command= lambda: app.show_frame(Frame_1))

    menu_procesamiento = tk.Menu(barra_menu, tearoff = 0)
    barra_menu.add_cascade(label = 'Procesamiento', menu = menu_procesamiento)
    menu_procesamiento.add_command(label= 'Carga de retenciones/percepciones', command= lambda: app.show_frame(Frame_2))

    menu_ayuda = tk.Menu(barra_menu, tearoff = 0)
    barra_menu.add_cascade(label = 'Ayuda', menu = menu_ayuda)
    menu_ayuda.add_command(label= 'Instrucciones', command= lambda: app.show_frame(Frame_3))


class Frame(tk.Frame):
    def __init__(self, root=None):
        super().__init__(root)
        self.root = root
        self.pack()
        self.config(bg='white')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        contenedor_principal = tk.Frame(self, bg='white')
        contenedor_principal.grid(padx=40, pady=50, sticky='nsew')
        # try:
        #     os.mkdir('ARCHIVOS_EXPORTADOS')
        # except OSError as e:
        #     if e.errno != errno.EEXIST:
        #         raise

        self.todos_los_frames = dict()
        for F in (Frame_1, Frame_2, Frame_3):
            frame = F(contenedor_principal, self)
            self.todos_los_frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        
        self.show_frame(Frame_3)
        
    
    def show_frame(self, contenedor_llamado):
        frame = self.todos_los_frames[contenedor_llamado]
        frame.tkraise()
    
    def cargar_tabla_impuestos(self):
        frame2 = self.todos_los_frames[Frame_2]
        frame2.nueva_tabla()


class Frame_1(tk.Frame):
    
    def __init__(self, container, controller):
        super().__init__(container)
        self.configure(bg='white')
        self.campos_gui()
        self.deshabilitar_botones()
    
    def campos_gui(self):
        
        #Labels
        self.label_archivo = tk.Label(self, text = 'Archivo:', bg='white')
        self.label_archivo.grid(row = 0, column = 0, padx=10, pady=10)
        self.label_archivo.config(font = ('Arial', 11, 'bold'))

        self.label_archivo_exportar = tk.Label(self, text = 'Nombre del archivo a exportar:', bg='white')
        self.label_archivo_exportar.grid(row = 1, column = 0, padx=10, pady=10)
        self.label_archivo_exportar.config(font = ('Arial', 11, 'bold'))

        self.label_guiones = tk.Label(self, text = '¿CUIT contiene guiones?:', bg='white')
        self.label_guiones.grid(row = 2, column = 0, padx=10, pady=10)
        self.label_guiones.config(font = ('Arial', 11, 'bold'))

        #Entrys de cada campo
        self.mi_archivo = tk.StringVar()
        self.entry_archivo = tk.Entry(self, textvariable = self.mi_archivo)
        self.entry_archivo.grid(row = 0, column = 1, padx=10, pady=10, columnspan = 3)
        self.entry_archivo.config(width=50, font = ('Arial', 11, 'italic'), state = 'disabled')

        self.mi_archivo_exportar = tk.StringVar()
        self.entry_archivo_exportar = tk.Entry(self, textvariable = self.mi_archivo_exportar)
        self.entry_archivo_exportar.grid(row = 1, column = 1, padx=10, pady=10, columnspan = 3)
        self.entry_archivo_exportar.config(width=50, font = ('Arial', 11))

        #Opciones
        self.opcion = tk.IntVar()
        self.opcion.set(2)
        self.RadioButton_1 = tk.Radiobutton(self, text = 'SI', variable = self.opcion, value = 1, bg='white')
        self.RadioButton_2 = tk.Radiobutton(self, text = 'NO', variable = self.opcion, value = 2, bg='white')
        self.RadioButton_1.grid(row = 2, column = 1)
        self.RadioButton_2.grid(row = 2, column = 2)
        self.RadioButton_1.config(font = ('Arial', 11, 'bold'))
        self.RadioButton_2.config(font = ('Arial', 11, 'bold'))

        #Botones
        self.boton_cargar = tk.Button(self, text = 'Cargar', command = self.cargar_archivo)
        self.boton_cargar.config(width=20, font=('Arial', 12, 'bold'), fg='#FFFFFF', bg='#2C95C5', cursor='hand2', activebackground='#1F698A') 
        self.boton_cargar.grid(row=3, column=0, padx=10, pady=10)
        
        self.boton_purgar = tk.Button(self, text = 'Purgar', command = self.purgar)
        self.boton_purgar.config(width=20, font=('Arial', 12, 'bold'), fg='#FFFFFF', bg='#2C95C5', cursor='hand2', activebackground='#1F698A') 
        self.boton_purgar.grid(row=3, column=1, padx=10, pady=10)
        
        self.boton_cancelar = tk.Button(self, text = 'Cancelar', command = self.deshabilitar_botones)
        self.boton_cancelar.config(width=20, font=('Arial', 12, 'bold'), fg='#FFFFFF', bg='#2C95C5', cursor='hand2', activebackground='#1F698A') 
        self.boton_cancelar.grid(row=3, column=2, padx=10, pady=10)

    def habilitar_botones(self):
        self.boton_cargar.config(state = 'disabled')
        self.boton_purgar.config(state = 'normal')
        self.boton_cancelar.config(state = 'normal')

        self.entry_archivo_exportar.config(state = 'normal')
        self.entry_archivo_exportar.focus()

    def deshabilitar_botones(self):
        self.mi_archivo.set('')
        self.mi_archivo_exportar.set('')

        self.boton_cargar.config(state = 'normal')
        self.boton_purgar.config(state = 'disabled')
        self.boton_cancelar.config(state = 'disabled')

        self.entry_archivo_exportar.config(state = 'disabled')

    def cargar_archivo(self):
        try:
            self.dir_archivo = filedialog.askopenfilename(initialdir = "/", title = "Seleccione el archivo", filetypes = {("Archivos CSV", "*.csv")})
            self.mi_archivo.set(self.dir_archivo)
            if self.dir_archivo != '':
                self.habilitar_botones()
        except:
            messagebox.showerror('Error', 'No se pudo cargar el archivo.')
    
    def purgar(self):
        if (self.mi_archivo_exportar.get() != '') and (existe_tabla('comercios')):
            crear_tabla(archivo=self.dir_archivo, nombre_tabla='purgar', opcion = self.opcion.get())
            eliminar_filas_purgarcomercios()
            exportar_tabla_csv(tabla='purgar_final', nombre_archivo=self.mi_archivo_exportar.get())
            borrar_tabla('purgar')
            borrar_tabla('comercios')
            borrar_tabla('purgar_final')
            self.deshabilitar_botones()
        else:
            if(self.mi_archivo_exportar.get() == ''):
                messagebox.showerror('Error', 'Debe ingresar el nombre del archivo a exportar.')
            else:
                messagebox.showerror('Error', 'Debe ingresar la tabla de comercios de PVS.')


class Frame_2(tk.Frame):
    
    def __init__(self, container, controller):
        super().__init__(container)
        self.configure(bg='white')
        self.tabla_retenciones()
        self.campos_gui()

    def campos_gui(self):
        #Botones
        # self.boton_nuevo = tk.Button(self, text = 'Cargar tabla impuestos', command = self.nueva_tabla)
        # self.boton_nuevo.config(width=20, font=('Arial', 12, 'bold'), fg='#FFFFFF', bg='#2C95C5', cursor='hand2', activebackground='#1F698A') 
        # self.boton_nuevo.grid(row=0, column=0, padx=10, pady=10)
        
        self.boton_cargar = tk.Button(self, text = 'Cargar padrón', command = self.cargar_archivo)
        self.boton_cargar.config(width=20, font=('Arial', 12, 'bold'), fg='#FFFFFF', bg='#2C95C5', cursor='hand2', activebackground='#1F698A') 
        self.boton_cargar.grid(row=3, column=0, padx=10, pady=10)
        
        self.boton_consultar = tk.Button(self, text = 'Consultar', command = self.consultar)
        self.boton_consultar.config(width=20, font=('Arial', 12, 'bold'), fg='#FFFFFF', bg='#2C95C5', cursor='hand2', activebackground='#1F698A') 
        self.boton_consultar.grid(row=3, column=1, padx=10, pady=10)
        
        self.boton_generartxt = tk.Button(self, text = 'Generar txt', command = self.generartxt)
        self.boton_generartxt.config(width=20, font=('Arial', 12, 'bold'), fg='#FFFFFF', bg='#2C95C5', cursor='hand2', activebackground='#1F698A') 
        self.boton_generartxt.grid(row=3, column=2, padx=10, pady=10)

    def tabla_retenciones(self):
        self.lista_retenciones, self.names = listar(nombre_tabla='retenciones')
        self.tabla = ttk.Treeview(self, columns = self.names, show = 'headings')
        self.tabla.place(x=0, y=0, relwidth=1)
        
        # Espacio
        self.label_archivo = tk.Label(self, text = '', bg='white')
        self.label_archivo.grid(row = 1, column = 4, pady=100)

        # Scrollbars
        self.yscrollbar = tk.Scrollbar(self, orient="vertical", command=self.tabla.yview)
        self.xscrollbar = tk.Scrollbar(self, orient="horizontal", command=self.tabla.xview)
        self.yscrollbar.grid(row=1, column=4, rowspan= 2, sticky='ns')
        self.xscrollbar.grid(row=2, column=0, columnspan = 4, sticky='ew')
        self.tabla.configure(xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)

        # Headers
        for i in range(len(self.names)):
            self.tabla.heading(self.names[i], text=self.names[i])
            
        # Rows
        for i in range(len(self.lista_retenciones)):
            self.tabla.insert('', 'end', values=self.lista_retenciones[i])

    def nueva_tabla(self):
        try:
            self.dir_archivo = filedialog.askopenfilename(initialdir = "/", title = "Seleccione el archivo", filetypes = {("Archivos CSV", "*.csv")})
            crear_tabla(archivo=self.dir_archivo, nombre_tabla='retenciones')
            self.tabla_retenciones()
        except:
            messagebox.showerror('Error', 'No se pudo cargar el archivo.')
    
    def cargar_archivo(self):
        try:
            self.id_tabla = self.tabla.item(self.tabla.selection())['values'][0]
            self.dir_archivo = filedialog.askopenfilename(initialdir = "/", title = "Seleccione el archivo", filetypes = {("Archivos CSV", "*.csv")})
            cargar_tabla_impuestos(self.dir_archivo, self.id_tabla)
        except:
            messagebox.showerror('Error', 'Seleccione un registro.')
        
    def consultar(self):
        if (existe_tabla('impuestos')):
            try:
                self.id_tabla = self.tabla.item(self.tabla.selection())['values'][0]
                self.Ventana = tk.Toplevel()
                self.Ventana.title(f'Consulta id: {self.id_tabla}')
                self.Ventana.configure(bg='white')
                self.Ventana.resizable(0,0)

                # Agregar tabla
                self.lista_impuestos, self.names = listar('impuestos', self.id_tabla)
                self.tabla_ventana = ttk.Treeview(self.Ventana, columns = self.names, show = 'headings')
                self.tabla_ventana.grid(row = 0, column = 0, columnspan = 4, sticky='nsew')

                # Scrollbars
                self.yscrollbar_ventana = tk.Scrollbar(self.Ventana, orient="vertical", command=self.tabla_ventana.yview)
                self.xscrollbar_ventana = tk.Scrollbar(self.Ventana, orient="horizontal", command=self.tabla_ventana.xview)
                self.yscrollbar_ventana.grid(row=0, column=10, rowspan= 3, sticky='ns')
                self.xscrollbar_ventana.grid(row=2, column=0, columnspan = 5, sticky='ew')
                self.tabla_ventana.configure(xscrollcommand=self.xscrollbar_ventana.set, yscrollcommand=self.yscrollbar_ventana.set)

                # Headers
                for i in range(len(self.names)):
                    self.tabla_ventana.heading(self.names[i], text=self.names[i])

                # Rows
                for i in range(len(self.lista_impuestos)):
                    self.tabla_ventana.insert('', 'end', values=self.lista_impuestos[i])

                # Botones
                self.boton_descargar_ventana = tk.Button(self.Ventana, text = 'Descargar CSV', command = lambda: exportar_tabla_csv(tabla='impuestos', nombre_archivo=f'consulta_impuesto_{self.id_tabla}', id=self.id_tabla))
                self.boton_descargar_ventana.config(width=20, font=('Arial', 12, 'bold'), fg='#FFFFFF', bg='#2C95C5', cursor='hand2', activebackground='#1F698A')
                self.boton_descargar_ventana.grid(row=4, column=0, pady=10)


            except:
                messagebox.showerror('Error', 'Seleccione un registro.')
        else:
            messagebox.showerror('Error', 'Todavía no se ha cargado ningún archivo.')


    def generartxt(self):
        try:
            self.id_tabla = self.tabla.item(self.tabla.selection())['values'][0]
            crear_archivo_inserts(self.id_tabla)
        except:
            messagebox.showerror('Error', 'Seleccione un registro.')


class Frame_3(tk.Frame):
    
    def __init__(self, container, controller):
        super().__init__(container)
        self.configure(bg='white')
        self.explicacion()

    def explicacion(self):
        self.label_explicacion = tk.Label(self, text = 'Instrucciones:', bg='white', justify='left')
        self.label_explicacion.grid(row = 0, column = 0, pady=10)
        self.label_explicacion.config(font = ('Arial', 12, 'bold'))

        self.label_explicacion = tk.Label(self, text = '1) Seleccione la pestaña "Cargar" para cargar las tablas (impuestos, comercios y contratos).\n2) Seleccione la pestaña "Purgar" si desea reducir los padrones originales,\n    tomando solo los CUIT de comercios de PVS.\n    El proceso de reducción puede demorar, un cartel le avisará cuando finalice.\n3) Seleccione la pestaña "Procesamiento" para generar los inserts.\n    Con el botón "Cargar padrón" (luego de seleccionar una fila) cargue una tabla para ese impuesto.', bg='white', justify='left')
        self.label_explicacion.grid(row = 1, column = 0, pady=10)
        self.label_explicacion.config(font = ('Arial', 11))

        self.label_explicacion = tk.Label(self, text = 'ACLARACIONES:\n• Todos los archivos a subir deben estar en formato CSV.\n• Los archivos CSV deben tener en la primer fila los nombres de sus columnas en minúscula.\n• El separador de cada campo debe ser ; (punto y coma).\n• La tabla de comercios y la tabla a purgar deben tener una columna llamada cuit.\n  Si Excel no abre la tabla a purgar, abrir con bloq de notas y agregar nombre de columnas a mano.\n• Si al menos uno de los CUIT tiene guiones o no sabe, indique la opción SI antes de purgar.\n• Para más informacion consulte el manual adjunto con este programa.', bg='white', justify='left')
        self.label_explicacion.grid(row = 3, column = 0, pady=10)
        self.label_explicacion.config(font = ('Arial', 11))