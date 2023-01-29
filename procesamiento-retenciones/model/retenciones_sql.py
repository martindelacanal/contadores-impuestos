from .conexion_db import ConexionDB
from tkinter import E, messagebox
import csv
import pandas as pd


def crear_tabla(archivo, nombre_tabla, opcion=None):
    if archivo != '':
        con = ConexionDB()
        # Carga de archivo CSV a la tabla nombre_tabla
        # si la tabla existe, la reemplaza; si no existe, la crea
        try:
            # if(nombre_tabla != 'purgar'):                           ##################################### PadronIntermediarios
            df = pd.read_csv(archivo, sep=';', encoding='utf-8')
            # else:                                                   ##################################### PadronIntermediarios
            #     df = pd.read_csv(archivo, sep=']', encoding='ANSI') ##################################### PadronIntermediarios
            
            # if(nombre_tabla == 'purgar'): #####################################SIRTAC
            #     df["nombre6"] = df["nombre6"].astype('string') #####################################SIRTAC
            #     df["nombre6"] = '*' + df["nombre6"] #####################################SIRTAC
            if(opcion == 1):
                df["cuit"] = df["cuit"].replace({'-':''}, regex=True)
                df["cuit"] = df["cuit"].astype('int64')
            df.to_sql(nombre_tabla, con.conexion, if_exists='replace', index=False)
            if(nombre_tabla != 'purgar'):
                messagebox.showinfo('Carga exitosa', 'El archivo fue cargado exitosamente.')
        except:
            messagebox.showerror('Error', 'La tabla no pudo ser creada.')
        con.cerrar()

def borrar_tabla(nombre_tabla):
    conexion = ConexionDB()
    conexion.cursor.execute(f"DROP TABLE IF EXISTS {nombre_tabla}")
    conexion.cerrar()

def listar(nombre_tabla, id=None):
    columnas = []
    try:
        conexion = ConexionDB()
        if id is None:
            data = conexion.cursor.execute(f"SELECT * FROM {nombre_tabla}")
        else:
            data = conexion.cursor.execute(f"SELECT * FROM {nombre_tabla} WHERE id_impuesto = {id}")
        lista = conexion.cursor.fetchall()
        for column in data.description:
            columnas.append(column[0])
        conexion.cerrar()
    except:
        lista = []
    return lista, columnas

def eliminar_filas_purgarcomercios():
    conexion = ConexionDB()
    ############## PadronIntermediarios
    # purgar_temporal = pd.read_sql("SELECT SUBSTRING(nombre,3,11) as cuit,SUBSTRING(nombre,58,1) as retencion FROM purgar", conexion.conexion)
    # purgar_temporal["cuit"] = purgar_temporal["cuit"].astype('int64')
    # purgar_temporal.to_sql("purgar", conexion.conexion, if_exists='replace', index=False)
    ##############
    conexion.cursor.execute("DELETE FROM purgar WHERE purgar.cuit NOT IN (SELECT cuit FROM comercios)")
    comercios = pd.read_sql("SELECT * FROM comercios", conexion.conexion)
    purgar = pd.read_sql("SELECT * FROM purgar", conexion.conexion) ############################# SIRTAC y RGS
    # purgar = pd.read_sql("SELECT cuit,retencion FROM purgar", conexion.conexion) ############## PadronIntermediarios
    result = pd.merge(comercios, purgar, how="inner", on=["cuit"])
    result.to_sql('purgar_final', conexion.conexion, if_exists='replace', index=False)
    conexion.cerrar()

def exportar_tabla_csv(tabla, nombre_archivo, id=None):
    try:
        conexion = ConexionDB()
        if(id is None):
            conexion.cursor.execute(f"SELECT * FROM {tabla}")
        else:
            conexion.cursor.execute(f"SELECT * FROM impuestos WHERE id_impuesto = {id}")
        data = conexion.cursor.fetchall()
        conexion.cerrar()
        with open(f'./ARCHIVOS_EXPORTADOS/{nombre_archivo}.csv', 'w', encoding='utf-8', newline= '') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow([i[0] for i in conexion.cursor.description])
            writer.writerows(data)
        messagebox.showinfo('Exportación exitosa', f'El archivo "{nombre_archivo}.csv"\nfue exportado exitosamente.')
    except:
        messagebox.showerror('Error', 'El archivo no pudo ser exportado.')

def existe_tabla(nombre_tabla):
    conexion = ConexionDB()
    conexion.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{nombre_tabla}'")
    existe = conexion.cursor.fetchone()
    conexion.cerrar()
    if existe is None:
        return False
    else:
        return True

def cargar_tabla_impuestos(archivo, id_tabla):
    if archivo != '':
        if (existe_tabla('impuestos')):
            borrar_datos_impuestoantiguo(id_tabla)
        
        con = ConexionDB()
        try:
            # si la tabla existe, le agrega los datos al final; si no existe, la crea
            df = pd.read_csv(archivo, sep=';', encoding='utf-8')
            df["alicuota"] = df["alicuota"].replace({',':'.'}, regex=True)
            df["alicuota"] = df["alicuota"].astype(float)
            df.insert(0, "id_impuesto", id_tabla, allow_duplicates=False)
            df.to_sql('impuestos', con.conexion, if_exists='append', index=False)
            messagebox.showinfo('Carga exitosa', 'El archivo fue cargado exitosamente.')
        except:
            messagebox.showerror('Error', 'La tabla no pudo ser creada.')
        con.cerrar()

def borrar_datos_impuestoantiguo(id_tabla):
    conexion = ConexionDB()
    conexion.cursor.execute(f"DELETE FROM impuestos WHERE id_impuesto = {id_tabla}")
    conexion.cerrar()

def crear_archivo_inserts(id_tabla):
    if (existe_tabla('contratos')):
        try:
            with open(f"./ARCHIVOS_EXPORTADOS/inserts_impuesto_{id_tabla}.txt", "w", encoding='utf-8') as f:
                conexion = ConexionDB()
                if (id_tabla==14) or (id_tabla==15) :
                    conexion.cursor.execute(f"SELECT a.agreement, a.account, a.tax, b.alicuota AS amount, a.account_destination FROM contratos AS a, (SELECT * FROM impuestos WHERE id_impuesto = {id_tabla}) AS b WHERE a.cuit=b.cuit AND a.id = b.id_pdv and a.tax = {id_tabla} and a.cuit in (SELECT cuit FROM (SELECT * FROM impuestos WHERE id_impuesto = {id_tabla}));")
                else:
                    conexion.cursor.execute(f"SELECT a.agreement, a.account, a.tax, b.alicuota AS amount, a.account_destination FROM contratos AS a, (SELECT * FROM impuestos WHERE id_impuesto = {id_tabla}) AS b WHERE a.cuit=b.cuit AND a.id = b.id_pdv AND b.alicuota >=0.1 and a.tax = {id_tabla} and a.cuit in (SELECT cuit FROM (SELECT * FROM impuestos WHERE id_impuesto = {id_tabla}));")
                data = conexion.cursor.fetchall()
                conexion.cerrar()
                for row in data:
                    f.write(f"insert into agreements_taxes_pre_process values (NULL, {row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]});\n")
            messagebox.showinfo('Exportación exitosa', f'El archivo "inserts_impuesto_{id_tabla}.txt"\nfue exportado exitosamente.')                    
        except:
            messagebox.showerror('Error', 'El archivo no pudo ser exportado.')
    else:
        messagebox.showerror('Error', 'Debe cargar la tabla de contratos.')


