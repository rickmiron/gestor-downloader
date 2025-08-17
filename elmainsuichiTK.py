import tkinter as tk
from tkinter import ttk
from threading import Thread,Lock,Event#,Condition
#import multiprocessing
import time
from tkinter import filedialog
from utils import Downloader,LazyUrl,get_max_range,_set_max_range,_set_resolution,get_resolution,Session
import requests
import os
#import importlib.util
from tkinter import messagebox
from PIL import Image
from PIL.ImageTk import PhotoImage
import base64
from io import BytesIO
import pickle
import types
import sqlite3
from queue import Queue,Empty
from http.cookiejar import MozillaCookieJar
from m3u8_tools import M3u8_stream
import ffmpegx
import traceback
import PyTaskbar
from ctypes import WinDLL
import faulthandler
import comtypes.client
from urllib.parse import unquote
import shutil
faulthandler.enable()
#gris,azul,verde,rojo,naranja
def itemconf(canvas:tk.Canvas,idm:int,titulo:str):
    canvas.itemconfig(idm,text=titulo)
def itemconfill(canvas:tk.Canvas,idm:int,color:str):
    canvas.itemconfig(idm,fill=color)
def itemconfimg(canvas:tk.Canvas,idm:int,photo:PhotoImage):
    if photo:
        canvas.itemconfig(idm,image=photo,state=tk.NORMAL)
def itemconfimx(i,canvas:tk.Canvas,idm:int,photo:PhotoImage):
    #print('itemfimx',i)
    if photo:
        canvas.itemconfig(idm,image=photo)
def fondo(imm:BytesIO):
    img=Image.open(imm)
    fondo = Image.new("RGB", (94,64), (0, 0, 0))
    fondo.paste(img, ((94 - img.width) // 2, (64 - img.height) // 2))
    return PhotoImage(fondo)
COLORES=(('#C0C0C0','#7C7C7C'),('#0A97F5','#06629F'),('#48B74B','#2E7630'),('#FF0000','#A50000'),('#FF7F27',"#C14D00"))
class Tarea:
    def __init__(self, url:str):
        self.imaok=False
        self.color0=0
        self.color1=0
        self.url=url
        self.titulo=url
        self.proges=''
        self.veloci=''
        self.peso=''
        self.cerrar=False
        self.posirecta:int=None
        self.ubicacion=''
        self.namefile=''
        self.namecla=Downloader.encontrar_subclase_por_url(url)
        self.descri=''
        self.listex=[]
        self.single=False
class Marco:
    def __init__(self,ima:int,recta:int,titulo:int,recta2:int,proges:int,veloci:int,peso:int,icon:int,rectall:int):
        self.ima=ima
        self.recta=recta
        self.titulo=titulo
        self.recta2=recta2
        self.proges=proges
        self.veloci=veloci
        self.peso=peso
        self.icon=icon
        self.rectall=rectall

class DraggableRectangleApp:
    def __init__(self, root:tk.Tk):
        self.root=root
        root.protocol('WM_DELETE_WINDOW',self.pedidocierra)
        
        self.locks_comprobador={None:Lock()}
        self.pho=[None]
        
        self.codedic={}
        self.iniciado=False
        self.pideurl=True
        self.sessionmaster:requests.Session = None
        self.nmaximo=2000
        self.ondic={None:False}
        #self.colalock=Lock()
        self.lockrun=Lock()
        self.runstop=0
        #self.condition = Condition(self.colalock)
        self.listafter:list[str]=[]
        self.event = Event()
        self.colalista:list[tuple[int,str]]=[]
        estilo = ttk.Style()
        estilo.theme_use("default")

        estilo.configure("TButton", padding=6, font=("Segoe UI", 10))
        estilo.configure("SwitchOn.TButton", background="#4CAF50", foreground="white")
        estilo.configure("SwitchOff.TButton", background="#D32F2F", foreground="white")
        estilo.configure("Vista.TButton", padding=4, background="#e0e0e0")
        estilo.configure("VistaActiva.TButton", background="#2196F3", foreground="white")
        estilo.map("Vista.TButton", background=[("active", "#c0c0c0")])
        estilo.map("VistaActiva.TButton", background=[("active", "#1976D2")])
        estilo.map("SwitchOn.TButton", background=[("active", "#388E3C")])
        estilo.map("SwitchOff.TButton", background=[("active", "#C62828")])

        self.rutas:dict[str,str]={}
        Downloader._getdix=self.getruta
        Downloader._settitle=self.settitulo
        Downloader.addtarea=self.insertalo
        self.colaurlby:Queue[tuple[int,str]]=Queue(maxsize=20)
        self.guardando=True
        self.home = os.path.dirname(__file__)
        conn = sqlite3.connect(self.home+'\\xmhimageshmx.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS images 
                            (url TEXT PRIMARY KEY, image BLOB)''')
        conn.commit()
        print('sqlite3.threadsafety',sqlite3.threadsafety)
        conn.close()
        

        self.elementosmostrados=7
        self.ntareas:dict[str,int]={None:1}
        
        self.parteciya=8192#1024*8
        self.canom=None
        self.caindpro=False
        self.lcanvas=[]
        
        self.nombreactual:str=None
        self.dichilostarea:dict[str,list[Thread]]={None:[]}

        self.imgnone=tk.PhotoImage(width=94, height=64)
        self.imgnone.put(("pink",), to=(0, 0, 94, 64))


        barra_menu = tk.Menu(root)
        root.config(menu=barra_menu)

        # Crear un menú desplegable llamado "Archivo"
        menu_archivo = tk.Menu(barra_menu, tearoff=0)
        menu_archivo.add_command(label="Carga Cookies", command=self.addcookie)
        # Añadir el menú "Archivo" a la barra de menú
        barra_menu.add_cascade(label="Redes", menu=menu_archivo)
        
        menu_editar = tk.Menu(barra_menu, tearoff=0)
        menu_editar.add_command(label="Cargar Plugin", command=self.cargar_elmodulo)
        menu_editar.add_command(label="Guardar", command=self.guardar)
        menu_editar.add_command(label="Configuracion", command=lambda: self.configuracion(root))
        
        barra_menu.add_cascade(label="Opciones", menu=menu_editar)
        self.frameed=ttk.Frame(root)
        self.frameed.pack(side=tk.TOP, fill=tk.X, pady=10, padx=10)
        self.suich=ttk.Button(self.frameed,style="SwitchOff.TButton",width=6,text='O|I ALL',command=self.on_off)
        self.suich.pack(side=tk.LEFT, padx=3)
        self.suichuni=ttk.Button(self.frameed,style="SwitchOff.TButton",width=3,text='O|I',command=self.on_offuni)
        self.suichuni.pack(side=tk.LEFT, padx=5)
        self.actsel=ttk.Button(self.frameed,text='EDITAR',command=self.edita)
        self.actsel.pack(side=tk.LEFT, padx=3)
        self.boreini=ttk.Button(self.frameed,text='REINICIAR',command=self.reinicio)
        
        self.boelim=ttk.Button(self.frameed,text='ELIMINAR',command=self.eliminar)

        self.bocopia=ttk.Button(self.frameed,text='COPIAR URL',command=self.copiau)


        frame=ttk.Frame(root)
        canvasboton = tk.Canvas(frame, height=40, bg="#f0f0f0", highlightbackground="#ccc")
        canvasboton.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        self.active_canvas = True
        def on_mousewheelx(event):
            if self.active_canvas:
                canvasboton.xview_scroll(-1 * (event.delta // 120), "units")

        def set_active_canvas(event):
            self.active_canvas = False

        def clear_active_canvas(event):
            self.active_canvas = True

        scrollbar_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=canvasboton.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        canvasboton.configure(xscrollcommand=scrollbar_x.set)
        self.frame_botones_vista = ttk.Frame(canvasboton)
        canvasboton.create_window((0, 0), window=self.frame_botones_vista, anchor="nw")
        self.frame_botones_vista.bind("<Configure>", lambda e: canvasboton.configure(scrollregion=canvasboton.bbox("all")))

        bnon=ttk.Button(self.frame_botones_vista,text='None',style="VistaActiva.TButton",command=lambda: self.cambiaventana(None))
        bnon.pack(side=tk.LEFT, padx=2)
        frame.pack(side=tk.TOP, fill=tk.X, pady=10, padx=10)
        self.botones:dict[str,ttk.Button]={None:bnon}
        
        self.framecan=ttk.Frame(root)
        self.canvasvacio = tk.Canvas(self.framecan,width=0,bg='blue')
        self.canvasvacio.pack(side=tk.LEFT, fill=tk.Y)
        self.canvas = tk.Canvas(self.framecan, bg="red")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.framecan, orient="vertical", command=self.fun_moverbarra)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvasvacio.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.bind("<Enter>", set_active_canvas)
        self.canvas.bind("<Leave>", clear_active_canvas)
        canvasboton.bind_all("<MouseWheel>", on_mousewheelx)
        
        self.ent=ttk.Entry(root,width=55, font=("Arial", 10))
        def cortar():
            self.ent.event_generate("<<Cut>>")
        def copiar():
            self.ent.event_generate("<<Copy>>")
        def pegar():
            self.ent.event_generate("<<Paste>>")
        def crear_menu(event):
            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label="Cortar", command=cortar)
            menu.add_command(label="Copiar", command=copiar)
            menu.add_command(label="Pegar", command=pegar)
            menu.post(event.x_root, event.y_root)
        self.ent.bind("<Button-3>", crear_menu)
        butt=ttk.Button(root,text='INSERTA',command=self.datonuevo)
        butt.pack(side=tk.BOTTOM)
        self.ent.pack(side=tk.BOTTOM)
        self.framecan.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.filepkl=self.home+'\\xmhvariableshmx.pkl'
        self.lock1=Lock()
        self.dichilocomprobador:dict[str,list[Thread]]={None:[]}
        self.suichi=False

        self.mover=False
        self.selecionado:set[int]=set()

        self.start_index2:dict[str,int] = {None:0}
        self.indicedeprocesamiento2:dict[str,int] = {None:0}

        self.datos2:dict[str,list[Tarea]]={None:[]}
        self.marcos:list[Marco]=[]
        self.modulos:dict[int,types.ModuleType]={}
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.yview_moveto(0)
        self.iconos:dict[str,PhotoImage]={}
        self.image_bytes_list:dict[str,BytesIO]={}
        self.photos:list[PhotoImage]=[]
        self.urlram:set[str]=set()
        self.urlran:set[str]=set()
        self.temporalima:dict[str,BytesIO]={}
        
        self.canvas.bind("<Configure>", self.modialtu)
        self.noload=False
        
        self.indicecola=0
        print('lee recupera')
        aaa=time.time()
        if os.path.exists(self.filepkl):
            self.recupera()
            Session.set_base_session(self.sessionmaster)
        else:
            self.sessionmaster=requests.Session()
        print(time.time()-aaa)
        print('fin recupera')
        #self.datosset=set([d1.url for d2 in self.datos2.values() for d1 in d2])
        self.datosset={d1.url for d2 in self.datos2.values() for d1 in d2}
        self.iniciamarcos()

        self.item_height=65
        self.altura=self.elementosmostrados*self.item_height
        self.total_items=len(self.datos2[None])
        self.regionscrol=len(self.datos2[None])*self.item_height
        self.canvasvacio.configure(scrollregion=(0, 0, 0, self.regionscrol))
        self.proporcion=self.regionscrol/(self.regionscrol-self.altura)
        self.paginas=(len(self.datos2[None])-1)//self.elementosmostrados

        self.urlsaeliminar:list[str]=[]
        Thread(target=self.colado,daemon=True).start()
        self.draw_visible_rectangles()
        self.iniciado=True
        root.update_idletasks()
        self.taskbar_progress = PyTaskbar.Progress(WinDLL('user32', use_last_error=True).GetParent(root.winfo_id()))
        self.taskbar_progress.init()
        self.taskbar_progress.setState("normal") # Set the progress bar state to normal (Available: loading, normal, warning, error)
        #self.poco()
        #for ss in self.datos2.values():
        #    for ww in ss:
        #        if hasattr(ww,'estado'):
        #            del ww.estado
        #        if not hasattr(ww,'single'):
        #            ww.single=False
    def poco(self):
        if any(os.path.exists(destino) and 536870912 > shutil.disk_usage(destino).free for destino in {ru[:2] for ru in self.rutas.values()}):
            self.taskbar_progress.setState("error")
            print('error')
        else:
            self.taskbar_progress.setState("normal")
            print('normal')
        print('elpoco')
        self.root.after(3000,self.poco)
        
    def mouse_wheel_horizon():
        pass
    def pedidocierra(self):
        #print('Pedidocierra ini')
        Thread(target=self.cerrando).start()
        #print('Pedidocierra fin')

    def cerrando(self):
        print('cerrando INI')
        self.suichi=False
        for lis in self.datos2.values():
            for ta in lis:
                if ta.color0==1:
                    ta.cerrar=True
        print('cerrando cerrar=True OK')
        for key,lish in self.dichilostarea.items():
            for h in lish:
                if h.is_alive():
                    na=h.name
                    print('cerr join ini',key,na)
                    h.join()
                    print('cerr join fin',key,na)
        print('cerrando threads closed OK')
        self.root.after(0,self.root.destroy)
        print('cerrando FIN')
        

    def modialtu(self,event=None):
        self.altura=self.canvasvacio.winfo_height()-4
        proporcion2=round((self.regionscrol-self.altura)/self.regionscrol, 4)
        self.proporcion=round(1/proporcion2, 4)

    def fun_moverbarra(self, *args):
        #print('args',args)
        if len(args)==3:
            delta=int(args[1])*(-120)
            #print(delta)
            self.update_scroll(delta)
        else:
            #print('args[1]',args[1])
            #print('self.proporcion',self.proporcion)
            delta=float(args[1])*self.proporcion
            #print('args[1])*self.proporcion',delta)
            dd=int(delta*self.paginas+0.1)*self.elementosmostrados
            #print('delta*pagina*elmetmostra',dd)
            #self.index2=dd
            #self.start_index2[self.nombreactual]=dd
            if self.start_index2[self.nombreactual]!=dd :
                self.start_index2[self.nombreactual]=dd
                self.draw_visible_rectangles()
        
        self.canvasvacio.yview(*args)
        #self.canvas.yview(*args)
        
    def settitulo(self,titulo:str,vari:int,cerrar:bool):
        #tarea.titulo=titulo
        #vari=posi
        if not vari is None and not cerrar:
            self.root.after(0,itemconf,self.canvas,self.marcos[vari].titulo,titulo)
            #self.canvas.itemconfig(self.marcos[vari].titulo,text=titulo)

    def getruta(self,na:str):
        return self.rutas[na]
    
    def addcookie(self):
        ruta_modulo= filedialog.askopenfilename(title="Seleccionar cookie formato Netscape",filetypes=[("Archivos txt", "*.txt")])
        if ruta_modulo:
            try:
                # Cargar cookies desde archivo Netscape
                cookiejar = MozillaCookieJar()
                cookiejar.load(ruta_modulo, ignore_discard=True, ignore_expires=True)
                for cookie in cookiejar:
                    self.sessionmaster.cookies.set_cookie(cookie)
                Session.set_base_session(self.sessionmaster)
                messagebox.showinfo("Realizado", "se inserto la Cookie")
            except Exception as e:
                messagebox.showinfo("Error al cargar", f"el archivo {ruta_modulo}: {e}")

    def configuracion(self,root):
        cr=tk.Toplevel(root)
        cr.title("Configuracion")
        cr.geometry("430x350+800+10")
        ttk.Label(cr,width=30,text='Cambio de ruta', font=("Arial", 10)).place(x=10, y=25)
        combo=ttk.Combobox(cr,width=30, state="readonly", values=list(self.rutas.keys()))
        combo.place(x=10, y=50)
        ruta=ttk.Entry(cr,width=30, font=("Arial", 10))
        ruta.place(x=210, y=50)
        def show_selection():
            self.rutas[combo.get()]=ruta.get()
            self.show_toast('cambio guardado')
        ttk.Button(cr,text="SAVE1", command=show_selection).place(x=210, y=100)
        def cuando_cambia(_):
            ruta.delete(0, tk.END)
            ruta.insert(0, self.rutas[combo.get()])
        combo.bind("<<ComboboxSelected>>", cuando_cambia)

        ttk.Label(cr,width=30,text='N# maximo archivo por tarea', font=("Arial", 10)).place(x=10, y=150)
        maxi=ttk.Entry(cr,width=30, font=("Arial", 10))
        maxi.place(x=210, y=150)
        maxi.insert(0,str(get_max_range()))
        def show_selection2():
            ma=maxi.get()
            if ma.isnumeric():
                _set_max_range(int(ma))
                self.show_toast('cambio guardado')
        ttk.Button(cr,text="SAVE2", command=show_selection2).place(x=210, y=200)

        ttk.Label(cr,width=30,text='resolucion de video', font=("Arial", 10)).place(x=10, y=250)
        combo1=ttk.Combobox(cr,width=10, state="readonly", values=[240,480,720,1080,1440,2160,4320])
        combo1.place(x=210, y=250)
        combo1.set(get_resolution())
        def show_selection3():
            _set_resolution(int(combo1.get()))
            self.show_toast('cambio guardado')
        ttk.Button(cr,text="SAVE3", command=show_selection3).place(x=210, y=300)

    def save_to_db(self):
        print('INI save_to_db')
        self.guardando=False
        self.noload=True
        conn = sqlite3.connect(self.home+'\\xmhimageshmx.db')
        print('sqlite3.connect')
        cursor = conn.cursor()
        items = [(k, v.getvalue()) for k, v in list(self.image_bytes_list.items())]
        cursor.executemany("INSERT OR REPLACE INTO images (url, image) VALUES (?, ?)", items)
        print('executemany')
        conn.commit()
        conn.close()
        print('close')
        self.urlram.clear()
        self.image_bytes_list.clear()
        self.guardando=True
        self.urlram.update(self.urlran)
        self.image_bytes_list.update(self.temporalima)
        self.noload=False
        self.urlran.clear()
        self.temporalima.clear()
        print("Imágenes guardadas en la base de datos")
    
    def load_from_db2(self, url:str):
        if self.noload:
            #print('RE if self.noload')
            return None#self.imgnone
        if url in self.urlram:
            #print('RE if url in self.urlram')
            return fondo(self.image_bytes_list[url])
        '''
        conn2 = sqlite3.connect(self.home+'\\xmhimageshmx.db')
        self.cursor2=conn2.cursor()

        self.cursor2.execute("SELECT image FROM images WHERE url = ?", (url,))
        result = self.cursor2.fetchone()
        '''
        conn2 = sqlite3.connect(self.home+'\\xmhimageshmx.db')
        cursor2=conn2.cursor()
        cursor2.execute("SELECT image FROM images WHERE url = ?", (url,))
        result = cursor2.fetchone()

        if result:
            bite=fondo(BytesIO(result[0]))
            conn2.close()
            return bite
        conn2.close()
        return None
    def remove_url(self, url):
        # Eliminar URL de la lista y de la base de datos
        if url in self.url_list:
            self.url_list.remove(url)
            
        self.cursor.execute("DELETE FROM images WHERE url = ?", (url,))
        self.conn.commit()
        
        # Ajustar índice si es necesario
        if self.current_index >= len(self.url_list):
            self.current_index = max(0, len(self.url_list) - 5)
        
        self.load_images()
    
    def remove_url2(self, url):
        # Eliminar URL de la lista y de la base de datos
        if url in self.url_list:
            self.url_list.remove(url)
        for url in self.urlsaeliminar:
            self.cursor.execute("DELETE FROM images WHERE url = ?", (url,))
            self.conn.commit()
        
        # Ajustar índice si es necesario
        if self.current_index >= len(self.url_list):
            self.current_index = max(0, len(self.url_list) - 5)
        
        self.load_images()

    def show_toast(self,msg:str):
        toast = tk.Toplevel()
        toast.overrideredirect(True)  # Quitar barra de título
        toast.attributes("-topmost", True)  # Mantener al frente
        toast.configure(bg="#333333")
        width, height = 300, 50
        toast.geometry(f"{width}x{height}+{(self.root.winfo_width()-300)//2 +self.root.winfo_x()}+{(self.root.winfo_height()-50)//2 +self.root.winfo_y()}")
        label = tk.Label(toast, text=msg, fg="white", bg="#333333", font=("Arial", 12))
        label.pack(expand=True, fill="both")
        toast.after(1000, toast.destroy)

    def guardar(self):
        print('guardar(self) ini')
        variguarda=[]
        variguarda.append(self.datos2)
        variguarda.append(self.codedic)
        variguarda.append(self.start_index2[self.nombreactual])
        variguarda.append(self.elementosmostrados)
        variguarda.append(self.nombreactual)
        variguarda.append(self.sessionmaster)
        variguarda.append(self.rutas)
        variguarda.append(get_max_range())
        variguarda.append(get_resolution())
        with open(self.filepkl, "wb") as archivo:
            print('with open(self.filepkl')
            pickle.dump(variguarda, archivo,protocol = -1)
        print('pickle.dump')
        self.save_to_db()
        print('self.save_to_db()')
        self.show_toast('guardado completo')
        print('guardar(self) fin')

    def recupera(self):
        with open(self.filepkl, "rb") as archivo:
            self.datos2,self.codedic,x1,x2,nn,self.sessionmaster,self.rutas,maxi,resu=pickle.load(archivo)
            _set_max_range(maxi)
            _set_resolution(resu)
            for ww in self.datos2[nn][x1:x2+x1]:
                ww.posirecta=None
            for i,v in enumerate(self.datos2[None][:x2]):
                v.posirecta=i
            for li in self.datos2.values():
                for el in li:
                    if el.color0==1:
                        el.color0=0
                        el.color1=0
            self.cargar_modulos(self.codedic)

    def cargar_modulos(self,codes:dict[str,str]):
        for na,codigo_str in codes.items():
            modulo = types.ModuleType("a")
            #code_obj = compile(codigo_str, filename=filename, mode="exec")
            #exec(compile(codigo_str, filename=na, mode="exec"), modulo.__dict__)
            exec(codigo_str, modulo.__dict__)
            self.modulos[na]=modulo
            self.cargaicono(na)
            self.agregaboton()
        Downloader.ordenaloinicio()

    def cargaiconos(self,name:list):
        if not name:
            name=Downloader.obtener_nombresubclases()
        for na in name:
            base64_image=Downloader.obtener_subclase(na).icon
            try:
                image_data = base64.b64decode(base64_image)
                image = Image.open(BytesIO(image_data))
                image = image.resize((32, 32), Image.Resampling.LANCZOS)
                self.iconos[na]=PhotoImage(image)
            except:
                self.iconos[na]=None
    def cargaicono(self,na:str):
        base64_image=Downloader.obtener_subclase(na).icon
        try:
            image_data = base64.b64decode(base64_image)
            image = Image.open(BytesIO(image_data))
            image = image.resize((32, 32), Image.Resampling.LANCZOS)
            self.iconos[na]=PhotoImage(image)
        except:
            self.iconos[na]=None

    def agregaboton(self):
        na=Downloader.obtener_ultimonombre()
        if na not in self.botones:
            self.locks_comprobador[na]=Lock()
            mi=len(na)//2
            nax=na
            if mi>5:
                nax=na[:mi]+'\n'+na[mi:]
            boton=ttk.Button(self.frame_botones_vista,text=nax, compound="left",image=self.iconos[na], style="Vista.TButton",command=lambda: self.cambiaventana(na))
            #if na not in self.datos2:
            #    self.datos2[na]=[]
            
            if self.iniciado:
                self.rutas[na]=self.home+'\\'+na
                self.datos2[na]=[]
                #self.redistribuye(na)
            self.botones[na]=boton
            self.ondic[na]=False
            self.dichilostarea[na]=[]
            self.dichilocomprobador[na]=[]
            #self.start_index2[na]=0
            #self.ntareas[na]=Downloader.obtener_subclase(na).MAX_PARALLEL
            #self.indicedeprocesamiento2[na]=0
            boton.pack(side=tk.LEFT, padx=2)

            #self.redistribuye(na)
            if not self.iniciado:
                self.start_index2[na]=0
                self.ntareas[na]=Downloader.obtener_subclase(na).MAX_PARALLEL
                self.indicedeprocesamiento2[na]=0
        else:
            self.botones[na].config(image=self.iconos[na] or '', compound=None)
        if self.iniciado:
            self.redistribuye(na)
            self.start_index2[na]=0
            self.ntareas[na]=Downloader.obtener_subclase(na).MAX_PARALLEL
            self.indicedeprocesamiento2[na]=0

    def cambiaventana(self,na:str):
        if not self.mover:
            self.botones[self.nombreactual].configure(style="Vista.TButton")
            for i in range(self.elementosmostrados if len(self.datos2[self.nombreactual])>self.start_index2[self.nombreactual]+self.elementosmostrados else len(self.datos2[self.nombreactual])-self.start_index2[self.nombreactual]):
                self.datos2[self.nombreactual][self.start_index2[self.nombreactual]+i].posirecta=None
            self.nombreactual=na


            self.total_items=len(self.datos2[na])
            self.regionscrol=len(self.datos2[na])*self.item_height
            self.canvasvacio.configure(scrollregion=(0, 0, 0, self.regionscrol))
            cero=self.regionscrol-self.altura
            self.proporcion=cero and self.regionscrol/cero
            self.paginas=(len(self.datos2[na])-1)//self.elementosmostrados


            self.botones[na].configure(style="VistaActiva.TButton")
            
            self.suichuni.configure(style="SwitchOn.TButton" if self.ondic[na] else "SwitchOff.TButton")
            self.draw_visible_rectangles()
            for i in range(self.elementosmostrados if len(self.datos2[na])>self.start_index2[na]+self.elementosmostrados else len(self.datos2[na])-self.start_index2[na]):
                self.datos2[na][self.start_index2[na]+i].posirecta=i

    def cargar_elmodulo(self):
        ruta_modulo= filedialog.askopenfilename(title="Seleccionar archivo",filetypes=[("Archivos python", "*.py")])
        if ruta_modulo:
            try:
                with open(ruta_modulo, "r", encoding="utf-8") as archivo:
                    codigo_str = archivo.read()
                modulo=types.ModuleType('a')
                exec(codigo_str, modulo.__dict__)
                #exec(compile(codigo_str, filename=na, mode="exec"), modulo.__dict__)
                na=Downloader.obtener_ultimonombre()
                Downloader.ordenalounico()
                self.modulos[na]=modulo
                self.codedic[na]=codigo_str
                self.cargaicono(na)
                self.agregaboton()
                self.draw_visible_rectangles()
                messagebox.showinfo("Realizado", "se inserto el modulo")
            except Exception as e:
                messagebox.showinfo("Error al cargar", f"el archivo {ruta_modulo}: {e}")
                traceback.print_exc()
            
    def reinicio(self):
        na=self.nombreactual
        if self.mover and self.selecionado:
            for i in list(self.selecionado):
                da=self.datos2[na][i]
                if da.color0 != 1:
                    da.listex.clear()
                    da.descri=''
                    da.color0=0
                    da.namecla=Downloader.encontrar_subclase_por_url(da.url)
                da.color1=0
            if self.caindpro:
                self.indicedeprocesamiento2[self.canom]=0
            self.canom=na
            self.caindpro=True
            self.selecionado.clear()
            self.draw_visible_rectangles()
            if self.suichi and self.ondic[na]:
                self.creahilo(na)
    def eliminar(self):
        na=self.nombreactual
        if self.mover and self.selecionado:
            indices_a_mover=list(self.selecionado)
            indices_a_mover.sort(reverse=True)
            #indices_a_mover.reverse()
            da2=self.datos2[na]
            for i in indices_a_mover:
                da2[i].cerrar=True
                link=da2[i].url
                self.urlsaeliminar.append(link)
                del da2[i]
                self.datosset.remove(link)
            self.selecionado.clear()
            if self.caindpro:
                self.indicedeprocesamiento2[self.canom]=0
            self.canom=na
            self.caindpro=True
            self.draw_visible_rectangles()
        
    def edita(self):
        self.mover=not self.mover
        '''
        print(self.photos)
        self.pho[0]=None
        self.photos.clear()
        print(self.photos)
        returdn
        '''
        if self.mover:
            bx="SwitchOn.TButton"
            self.boreini.pack(side=tk.LEFT)
            self.boelim.pack(side=tk.LEFT)
            self.bocopia.pack(side=tk.LEFT)
        else:
            bx="TButton"#"SwitchOff.TButton"
            self.boreini.pack_forget()
            self.boelim.pack_forget()
            self.bocopia.pack_forget()
            na=self.nombreactual
            if self.selecionado:
                lis=self.datos2[na]
                for i in list(self.selecionado):
                    da=lis[i]
                    da.posirecta=None
                    da.color1=0
                self.draw_visible_rectangles()
                si=self.start_index2[na]
                for i in range(self.elementosmostrados if len(lis)>si+self.elementosmostrados else len(lis)-si):
                    lis[si+i].posirecta=i
                self.selecionado.clear()
        self.actsel.config(style=bx)

    def copiau(self):
        dicnow=self.datos2[self.nombreactual]
        self.copiar_al_portapapeles(' '.join([dicnow[i].url for i in self.selecionado]))

    def on_resize(self, event):
        x1= self.canvas.winfo_width()
        for i,li in enumerate(self.marcos):
            y0=i*65 +1
            y1=y0 + 63
            med=(y0+y1)//2
            self.canvas.coords(li.recta, 98, y0, x1-5, med)
            self.canvas.coords(li.recta2, 98, med, x1-5, y1)
            self.canvas.itemconfig(li.titulo, width = x1-107)
            self.canvas.coords(li.veloci, x1-75, 32 +med)
            self.canvas.coords(li.peso, x1-7, 32 +med)
            self.canvas.coords(li.rectall, 98, y0, x1-5, y1)

    def toplay(self, index:int):
        idx=self.start_index2[self.nombreactual]+index
        if idx<len(self.datos2[self.nombreactual]):
            tarea=self.datos2[self.nombreactual][idx]
            if tarea.namefile and os.path.exists(tarea.ubicacion+'\\'+tarea.namefile):
                os.startfile(tarea.ubicacion+'\\'+tarea.namefile)
            else:
                self.show_toast('No hay el archivo')

    def copiar_al_portapapeles(self,texto):
        root.clipboard_clear()
        root.clipboard_append(texto)
        root.update()  # para que se mantenga en el clipboard tras cerra

    def detalles(self,index:int):
        idx=self.start_index2[self.nombreactual]+index
        if idx<len(self.datos2[self.nombreactual]):
            tarea=self.datos2[self.nombreactual][idx]
            descri=tarea.descri+'ERRORES EN PROCESABARRA\n\n'+''.join(tarea.listex)
            cr=tk.Toplevel(self.root)
            cr.title("Detalles")
            cr.geometry("630x350+800+10")
            tex=tk.Text(cr, height = 400, width = 350, wrap="none")
            scro=tk.Scrollbar(cr)
            scrox=tk.Scrollbar(cr,orient="horizontal")
            scro.pack(side="right", fill="y")
            scrox.pack(side="bottom", fill="x")
            #tex.place(x=10, y=25)
            tex.pack(side='right')
            tex.config(yscrollcommand=scro.set, xscrollcommand=scrox.set)
            #tex.config(xscrollcommand=scrox.set)
            scro.config(command=tex.yview)
            scrox.config(command=tex.xview)

            tex.delete('1.0','end')
            tex.insert('1.0',descri)
            
    def on_click(self,event,index:int):
        nom=self.nombreactual
        menu = tk.Menu(root, tearoff=0)
        menu.add_command(label="Copiar Url", command=lambda: self.copiar_al_portapapeles(self.datos2[nom][self.start_index2[nom]+index].url))
        menu.add_command(label="Play archivo", command=lambda: self.toplay(index))
        menu.add_command(label="Detalles", command=lambda: self.detalles(index))
        menu.tk_popup(event.x_root, event.y_root)
        #menu.post(event.x_root, event.y_root)

    def iniciamarcos(self):
        for i in range(self.elementosmostrados):
            yy1 = i * 65+1
            yy2 = yy1 + 63
            med=(yy1 + yy2)//2
            t0=self.canvas.create_image(3, yy1, anchor='nw', image=self.imgnone)
            self.canvas.tag_bind(t0,"<Button-3>", lambda event, idx=i: self.on_click(event, idx))
            self.canvas.tag_bind(t0,"<ButtonPress-1>", lambda event, idx=i: self.abrefolder(event, idx))
            r1=self.canvas.create_rectangle(98, yy1, 450,med, fill="black", outline="black")
            t1=self.canvas.create_text(102, -32+med, text='',anchor='nw', font=("Arial", 10, "bold"),width=348)
            r1b=self.canvas.create_rectangle(98, med, 450,  yy2, fill="black", outline="black")
            t2=self.canvas.create_text(134, 32+med, text='',anchor='sw', font=("Arial", 10))
            t3=self.canvas.create_text(380, 32+med, text='',anchor='se', font=("Arial", 10))
            t4=self.canvas.create_text(448, 32+med, text='',anchor='se', font=("Arial", 10))
            t5=self.canvas.create_image(102, 30+med, anchor='sw', image=None)
            rf=self.canvas.create_rectangle(98, yy1, 450,yy2, outline="", fill="")
            self.canvas.tag_bind(rf, "<ButtonPress-1>", lambda event, idx=i: self.selecciona(event, idx))
            self.canvas.tag_bind(rf, "<ButtonPress-3>",lambda event, idx=i: self.deselecciona(event, idx))
            self.canvas.bind("<Configure>", self.on_resize)
            self.marcos.append(Marco(t0,r1,t1,r1b,t2,t3,t4,t5,rf))
        tu = self.canvas.bbox("all")
        #self.altura=tu[3]+1
        self.canvas.configure(scrollregion=(tu[0]-1,tu[1],tu[2],tu[3]+1))


    def colado(self):
        #conn2 = sqlite3.connect(self.home+'\\xmhimageshmx.db')
        #self.cursor2=conn2.cursor()
        while True:
            i,url=self.colaurlby.get()
            
            aa=self.indicecola
            if not self.pideurl:
                continue
            '''
            imm=self.load_from_db2(url)
            if not self.pideurl:
                continue
            if imm is None:
                pho=self.imgnone
            else:
                #img=Image.open(imm)
                #fondo = Image.new("RGB", (94,64), (0, 0, 0))
                #fondo.paste(img, ((94 - img.width) // 2, (64 - img.height) // 2))
                #pho = PhotoImage(fondo)
                pho=fondo(imm)
            '''


            self.pho[0]=self.load_from_db2(url)
            if self.pho[0] is None:
                self.pho[0]=self.imgnone

            
            if aa==self.indicecola:
                if not self.pideurl:
                    self.photos.clear()
                    self.pho[0]=None
                    continue
                if self.pideurl:
                    self.photos.append(self.pho[0])
                    idf=self.root.after_idle(itemconfimx,i,self.canvas,self.marcos[i].ima,self.pho[0])
                    self.listafter.append(idf)
            
    def draw_visible_rectangles(self):
        #print('draw ini')
        self.pideurl=False
        
        #self.colaurlby.queue.clear()
        #print('d1')
        while True:
            try:
                self.colaurlby.get_nowait()
            except Empty:
                break
        for af in self.listafter:
            self.root.after_cancel(af)
        self.listafter.clear()

        self.photos.clear()
        self.pideurl=True
        self.indicecola=self.start_index2[self.nombreactual]
        #print('d3')
        for i,m in enumerate(self.marcos):
            actual_index = self.start_index2[self.nombreactual] + i
            if actual_index<len(self.datos2[self.nombreactual]):
                #print(i,'i1')
                tarea=self.datos2[self.nombreactual][actual_index]
                if tarea.imaok and self.guardando:
                    
                    self.colaurlby.put((i,tarea.url),block=True,timeout=5)
                    
                else:
                    self.canvas.itemconfig(m.ima,image=self.imgnone)
                #print(i,'i2')
                self.canvas.itemconfig(m.recta, fill=COLORES[tarea.color0][tarea.color1])
                '📸'
                self.canvas.itemconfig(m.titulo,text=tarea.titulo)
                self.canvas.itemconfig(m.recta2, fill=COLORES[tarea.color0][tarea.color1])
                self.canvas.itemconfig(m.peso,text=tarea.peso)
                self.canvas.itemconfig(m.veloci,text=tarea.veloci)
                self.canvas.itemconfig(m.proges,text=tarea.proges)
                imag=None if tarea.namecla is None else self.iconos[tarea.namecla]
                #print(i,'i3')
                if imag is None:
                    self.canvas.itemconfig(m.icon, state=tk.HIDDEN)
                else:
                    self.canvas.itemconfig(m.icon, image=imag,state=tk.NORMAL)
                #print(i,'i4')
            else:
                self.canvas.itemconfig(m.ima, image=self.imgnone)
                self.canvas.itemconfig(m.recta, fill='black')
                self.canvas.itemconfig(m.recta2, fill='black')
                self.canvas.itemconfig(m.titulo,text='')
                self.canvas.itemconfig(m.peso,text='')
                self.canvas.itemconfig(m.veloci,text='')
                self.canvas.itemconfig(m.proges,text='')
                self.canvas.itemconfig(m.icon, state=tk.HIDDEN)
        #print('draw fin')

    def abrefolder(self, event, index:int):
        idx=self.start_index2[self.nombreactual]+index
        if idx<len(self.datos2[self.nombreactual]):
            tarea=self.datos2[self.nombreactual][idx]

            if tarea.single:
                if tarea.ubicacion and os.path.exists(tarea.ubicacion+"\\"+tarea.namefile):
                    
                    shell = comtypes.client.CreateObject("Shell.Application")
                    ventanas = shell.Windows()
                    for i in range(ventanas.Count):
                        ventana = ventanas.Item(i)
                        try:
                            url = ventana.LocationURL
                            if url[:8]=="file:///":
                                ruta_actual = unquote(url[8:]).replace('/', '\\')
                                if ruta_actual.lower() == tarea.ubicacion.lower():
                                    item = ventana.Document.Folder.ParseName(tarea.namefile)
                                    if item:
                                        ventana.Document.SelectItem(item, 29)  # SVSI_SELECT | SVSI_FOCUSED
                                        ventana.Visible = True
                                    else:
                                        os.startfile(tarea.ubicacion)
                                    break
                        except:
                            continue
                    else:
                        os.system(f'explorer /select,"{tarea.ubicacion+"\\"+tarea.namefile}"')
                else:
                    self.show_toast('No hay la carpeta')
            else:
                if tarea.ubicacion and os.path.exists(tarea.ubicacion):
                    os.startfile(tarea.ubicacion)
                else:
                    self.show_toast('No hay la carpeta')

    def selecciona(self, event, index:int):
        if self.mover:
            idx=self.start_index2[self.nombreactual]+index
            if idx<len(self.datos2[self.nombreactual]):
                tarea=self.datos2[self.nombreactual][idx]
                if idx in self.selecionado:
                    self.selecionado.remove(idx)
                    tarea.color1=0
                else:
                    self.selecionado.add(idx)
                    tarea.color1=1
                self.canvas.itemconfig(self.marcos[index].recta, fill=COLORES[tarea.color0][tarea.color1])
                self.canvas.itemconfig(self.marcos[index].recta2, fill=COLORES[tarea.color0][tarea.color1])
    
    def deselecciona(self, event,idx):
        if self.mover and self.selecionado:
            self.reorderna(self.start_index2[self.nombreactual]+idx)
            self.selecionado.clear()
            if self.caindpro:
                self.indicedeprocesamiento2[self.canom]=0
            self.canom=self.nombreactual
            self.caindpro=True
            self.draw_visible_rectangles()

    def reorderna(self,idx):
        indices_a_mover=list(self.selecionado)
        listactual=self.datos2[self.nombreactual]
        def non3(ii:int):
            da=listactual[ii]
            da.posirecta=None
            da.color1=0
            return da
        elementos_a_mover = [non3(i) for i in indices_a_mover]
        #indices_a_mover.reverse()
        indices_a_mover.sort(reverse=True)
        for i in indices_a_mover:
            del listactual[i]
        listactual[idx:idx] = elementos_a_mover
        for i in range(self.elementosmostrados if len(listactual)>self.start_index2[self.nombreactual]+self.elementosmostrados else len(listactual)-self.start_index2[self.nombreactual]):
            listactual[self.start_index2[self.nombreactual]+i].posirecta=i
    
    def redistribuye(self,na:str):
        if self.selecionado:
            listactual=self.datos2[self.nombreactual]
            indxactual=self.start_index2[self.nombreactual]
            for i in list(self.selecionado):
                da=listactual[i]
                da.posirecta=None
                da.color1=0
            #self.draw_visible_rectangles()
            for i in range(self.elementosmostrados if len(listactual)>indxactual+self.elementosmostrados else len(listactual)-indxactual):
                listactual[indxactual+i].posirecta=i
            self.selecionado.clear()
        lista=self.datos2[None]
        listb=self.datos2[na]
        i=0
        urls=Downloader.obtener_subclase(na).URLS
        for ta in lista.copy():
            for u in urls:
                if isinstance(u,str):
                    if u in ta.url:
                        ta.namecla=na
                        listb.append(ta)
                        del lista[i]
                        break
                elif u(ta.url):
                    ta.namecla=na
                    listb.append(ta)
                    del lista[i]
                    break
            else:
                i+=1

    def datonuevo(self):
        link=self.ent.get().strip()
        self.ent.delete(0, 'end')
        if not link:
            link = self.root.clipboard_get()
        self.insertalo(link)

    def insertalo(self,link:str):
        inse=False
        ok=[]
        names=set()
        repe=[]
        for i in link.split():
            if i not in self.datosset:
                if i[:4] == 'http' or i.isnumeric():
                    if len(ok)<11:
                        ok.append(i)
                    names.add(self.datonuevook(i))
            else:
                inse=True
                repe.append(i)
        
        self.draw_visible_rectangles()
        if self.nombreactual in names:
            na=self.nombreactual
            lita=self.datos2[na]
            inx=self.start_index2[na]
            ww=self.elementosmostrados if len(lita)>inx+self.elementosmostrados else len(lita)-inx
            for i in range(ww):
                lita[inx+i].posirecta=i
        if self.suichi:
            for na in names:
                if self.ondic[na]:
                    self.creahilo(na)
        if ok:
            self.show_toast('link insertado\n'+'\n'.join(ok))
        elif inse:
            self.show_toast('link repetido')
            if len(repe)==1:
                mues=repe[0]
                lista=self.datos2[Downloader.encontrar_subclase_por_url(mues)]
                #for i,tarea in enumerate(lista):
                #    if tarea.url==mues:
                #        indice=i
                #        break

                indice = next((i for i, tarea in enumerate(lista) if tarea.url == mues), -1)
                if indice != -1:
                    indzero=(indice//7)*7
                    self.kom(indzero)
                    tarea=lista[indice]
                    self.canvas.itemconfig(self.marcos[indice-indzero].recta, fill=COLORES[tarea.color0][1])
                    self.canvas.itemconfig(self.marcos[indice-indzero].recta2, fill=COLORES[tarea.color0][1])

    def kom(self,indice):
        #self.canvas.yview_scroll(int(-1 * (delta / 120)), "units")
        lista=self.datos2[self.nombreactual]
        indiceactu=self.start_index2[self.nombreactual]
        for i in range(self.elementosmostrados if len(lista)>indiceactu+self.elementosmostrados else len(lista)-indiceactu):
            lista[indiceactu+i].posirecta=None
        self.start_index2[self.nombreactual]=indice
        self.draw_visible_rectangles()
        for i in range(self.elementosmostrados if len(lista)>indice+self.elementosmostrados else len(lista)-indice):
            lista[indice+i].posirecta=i

    def datonuevook(self,link):
        self.datosset.add(link)
        tar=Tarea(link)
        self.datos2[tar.namecla].append(tar)
        return tar.namecla

    def worker(self,page_url_queue: Queue[str|LazyUrl|M3u8_stream],lock:Lock,lista:list,filenames:dict[str|M3u8_stream,str],maxi:list,nhilos:int,ruta:str,tarea:Tarea, size:list,sizeok:list,idx:int,vivo:list,nelem:list,nphilo:int,head:dict,primaimage:list,segmenduo:list,session:requests.Session,conv):
        file_url=''
        while not tarea.cerrar:
            try:
                page_url = page_url_queue.get()
                if page_url is None:
                    page_url_queue.task_done()
                    break
                page_url_queue.task_done()
                if isinstance(page_url,LazyUrl):
                    file_url=page_url()
                    filenam:str=ruta+'\\'+str(page_url.obj.filename)
                    hea=getattr(page_url.obj, 'header', head)
                    nphilos=getattr(page_url.obj, 'nhilos', 1)
                    alter=page_url.alter
                else:
                    file_url=page_url
                    fn=filenames[page_url]
                    filenam=fn if ':\\' in fn else ruta+'\\'+fn
                    nphilos=nphilo
                    hea=head
                    alter=None
                
                if nphilos<1:
                    nphilos=1
                
                if page_url_queue.empty() and page_url_queue.unfinished_tasks==0:
                    with lock:
                        if page_url_queue.empty():
                            if maxi[0]<len(lista):
                                for li in lista[maxi[0]:]:
                                    page_url_queue.put(li)
                                maxi[0]=len(lista)
                            else:
                                for _ in range(nhilos):
                                    page_url_queue.put(None)
                
                #print('++1 WORK DOWNLOAD')
                if not file_url:
                    raise Exception('URL VOID')
                if not os.path.exists(filenam):
                    if isinstance(file_url,str):
                        if 'http' != file_url[:4]:
                            raise Exception('URL LOCAL VOID')
                        filenam=self.download_file(file_url,filenam,tarea,size,idx,nphilos,hea,session,segmenduo if maxi[0]==1 else None,alter)
                    elif isinstance(file_url,M3u8_stream):
                        filenam=file_url.download(filenam,tarea,size,sizeok,idx,segmenduo if maxi[0]==1 else None,conv,alter)
                    else:
                        raise Exception('URL NO VALID')
                    if not tarea.cerrar and isinstance(page_url,LazyUrl) and page_url.pp:
                        try:
                            page_url.pp(filenam)
                        except:
                            traceback.print_exc()
                else:
                    sizeok[idx]+=os.path.getsize(filenam)
                #print('++2 WORK DOWNLOAD')
                if not primaimage:
                    if page_url is lista[0]:
                        print('filenam',filenam)
                        tarea.namefile=filenam[len(ruta)+1:]
                        primaimage.append(filenam)
                        primaimage.append(idx)
                nelem[idx]+=1
                #print('++3 WORK NELEM[idx]+=1')
            except Exception as e:
                print('++0 WORK except Exception as e')
                if page_url_queue.empty() and page_url_queue.unfinished_tasks==0:
                    with lock:
                        if page_url_queue.empty():
                            if maxi[0]<len(lista):
                                for li in lista[maxi[0]:]:
                                    page_url_queue.put(li)
                                maxi[0]=len(lista)
                            else:
                                for _ in range(nhilos):
                                    page_url_queue.put(None)
                print('WORKER CAPTURA DE EXCEPTION')
                print(F'WORKER FALLO la descarga de un elemento {file_url}')
                #tarea.descri+=
                tarea.listex[idx]+=f'WORKER fallo la descarga de un elemento {file_url}\n'
                if e.args[0]:
                    tarea.listex[idx]+=f'{traceback.format_exc()}\n\n\n'
                    traceback.print_exc()
                if maxi[0]==1:
                    tarea.color0=3
        print('fin del worker',idx,tarea.namecla)
        vivo[idx]=False

    def procesabarra(self,tarea:Tarea):
        #tarea.descri+='inicia procesabarra\n'
        tarea.imaok=False
        tarea.color0=1
        tee=peso=''
        vari=tarea.posirecta
        #tarea.descri+='if not vari procesabarra\n'
        if not vari is None and not tarea.cerrar:
            self.root.after(0,itemconfill,self.canvas,self.marcos[vari].recta,COLORES[1][tarea.color1])
            self.root.after(0,itemconfill,self.canvas,self.marcos[vari].recta2,COLORES[1][tarea.color1])
        #tarea.descri+='out if not vari procesabarra\n'
        try:
            #tarea.descri+='try: 0 if tarea.namecla\n' 
            if tarea.namecla is None:
                tarea.namecla=Downloader.encontrar_subclase_por_url(tarea.url)
                if tarea.namecla is None:
                    raise Exception('tarea.namecla is None')
            #tarea.descri+='try: 1 if tarea.namecla\n' 
            #don=Downloader.obtener_subclase(tarea.namecla)()
            don=Downloader.obtener_subclase(tarea.namecla)()
            #tarea.descri+='don=Downloader.obtener_subclase(tarea.namecla)()\n'
            don.url=tarea.url
            #tarea.descri+='don.url=tarea.url\n'
            #print('don._tarea=tarea')
            don._tarea=tarea
            #tarea.descri+='don._tarea=tarea\n'
            print('read ini')
            tarea.descri+='Inicia read\n'
            don.read()
            print('read fin')
            tarea.descri+='Termina read\n'
            tarea.titulo=don.title
            tarea.descri+=f'URL: {tarea.url}\nTITLE: {don.title}\n'
            tarea.single=don.single
            if don.single:
                laruta=self.rutas[tarea.namecla]
            else:
                laruta=self.rutas[tarea.namecla]+'\\'+tarea.titulo
            tarea.ubicacion=laruta
            tarea.descri+=f'Ubicacion de carpeta: {laruta}\n\n\n'
            os.makedirs(laruta,exist_ok=True)
            vari=tarea.posirecta
            if not vari is None and not tarea.cerrar:
                self.root.after(0,itemconf,self.canvas,self.marcos[vari].titulo,don.title)
            #tarea.icon=don.icon
            photo=self.imgnone
            try:
                if isinstance(don.thumbnail,BytesIO):
                    #print('ini thumbanail')
                    img = Image.open(don.thumbnail)
                    biyee=BytesIO()
                    img.thumbnail((94,64),4)
                    img.save(biyee,'jpeg')
                    #self.temporalima={}
                    if self.guardando:
                        self.image_bytes_list[tarea.url] = biyee
                        self.urlram.add(tarea.url)
                        if not self.guardando:
                            self.temporalima[tarea.url] = biyee
                            self.urlran.add(tarea.url)
                    else:
                        self.temporalima[tarea.url] = biyee
                        self.urlran.add(tarea.url)
                        if self.guardando:
                            self.image_bytes_list[tarea.url] = biyee
                            self.urlram.add(tarea.url)
                    tarea.imaok=True
                    #self.image_bytes_list[link]=None



                    fondo = Image.new("RGB", (94,64), (0, 0, 0))  # negro
                    fondo.paste(img, ((94 - img.width) // 2, (64 - img.height) // 2))
                    photo = PhotoImage(fondo)#PhotoImage(img)



                    self.photos.append(photo)
                vari=tarea.posirecta
                if not vari is None and not tarea.cerrar:
                    #self.canvas.itemconfig(self.marcos[vari].ima, image=photo,state=tk.NORMAL)
                    self.root.after(0,itemconfimg,self.canvas,self.marcos[vari].ima,photo)
                #print('fin thumbanail')
            except Exception as e:
                tarea.descri+=f"Error cargando imagen: {e}\n\n\n"
                print(f"Error cargando imagen: {e}")
                #self.remove_url(url)
            
            cola=Queue()
            lock=Lock()
            tarea.descri+='URL File:\n'+'\n'.join(str(obj) for obj in don.urls)+'\n\n\n'
            if not don.urls:
                raise Exception('PROCESABARRA: URLS empty')
            
            maxi=[len(don.urls)]
            #print('maxi',maxi)
            #print('don.urls',don.urls)
            n_files=don.MAX_CORE
            tamanio=[0]*n_files
            tamaniook=[0]*n_files
            noacaba=[True]*n_files
            nelem=[0]*n_files
            segmenduo=[[],0]
            conv=['']
            for url in don.urls:
                cola.put(url)
            primaimage:list[str|int]=[]
            tarea.listex=['']*n_files
            hilocal=[Thread(target=self.worker, args=(cola,lock,don.urls,don.filenames,maxi,n_files,laruta,tarea,tamanio,tamaniook,i,noacaba,nelem,don.nphilo,don.header,primaimage,segmenduo,don.session,conv)) for i in range(n_files)]
            for t in hilocal:
                t.start()
            def memon(siz:int):
                mm=['B','KB','MB','GB','TB']
                po=0
                while siz>1023:
                    siz/=1024
                    po+=1
                return f'{siz:.1f} {mm[po]}'
            a1=time.time()
            okima=True
            pesoaguar=0
            while any(noacaba):
                if okima and not tarea.imaok and len(primaimage)>1 and nelem[primaimage[1]]>0:
                    primaimage[1]=(primaimage[1]+1)%n_files
                    try:
                        pathfile:str=primaimage[0]
                        if pathfile.split('.')[-1] in ['mp4','ts','mov']:
                            pathfile=BytesIO(ffmpegx.extraer_fotograma(pathfile))
                        img = Image.open(pathfile)
                        biyee=BytesIO()
                        img.thumbnail((94,64),4)
                        img=img.convert('RGB')
                        img.save(biyee,'jpeg')
                        if self.guardando:
                            self.image_bytes_list[tarea.url] = biyee
                            self.urlram.add(tarea.url)
                            if not self.guardando:
                                self.temporalima[tarea.url] = biyee
                                self.urlran.add(tarea.url)
                        else:
                            self.temporalima[tarea.url] = biyee
                            self.urlran.add(tarea.url)
                            if self.guardando:
                                self.image_bytes_list[tarea.url] = biyee
                                self.urlram.add(tarea.url)
                        tarea.imaok=True



                        fondo = Image.new("RGB", (94,64), (0, 0, 0))
                        fondo.paste(img, ((94 - img.width) // 2, (64 - img.height) // 2))
                        photo = PhotoImage(fondo)#PhotoImage(img)




                        self.photos.append(photo)
                        vari=tarea.posirecta
                        if not vari is None and not tarea.cerrar:
                            #self.canvas.itemconfig(self.marcos[vari].ima, image=photo,state=tk.NORMAL)
                            self.root.after(0,itemconfimg,self.canvas,self.marcos[vari].ima,photo)
                    except Exception as e:
                        tarea.descri+=f'error en cargar la imagen de {primaimage[0]}\n{traceback.format_exc()}\n\n'
                        print('error en cargar la imagen de',primaimage[0])
                        #print('detalle:',e)
                        #print(f"Ocurrio en la linea_1: {e.__traceback__.tb_lineno}")
                        #nex=e.__traceback__.tb_next
                        #if nex:
                        #    print(f"Ocurrio en la linea_2: {nex.tb_lineno}")
                        traceback.print_exc()
                        okima=False
                ahora=sum(tamanio)
                ahora2=ahora
                vari=tarea.posirecta
                if not vari is None and not tarea.cerrar:
                    #self.canvas.itemconfig(self.marcos[vari].peso,text=memon(ahora+sum(tamaniook)))
                    self.root.after(0,itemconf,self.canvas,self.marcos[vari].peso,memon(ahora+sum(tamaniook)))
                    nocero=time.time()-a1
                    if ahora==pesoaguar:
                        ahora=0
                    else:
                        pesoaguar=ahora
                    if nocero:
                        #self.canvas.itemconfig(self.marcos[vari].veloci,text=conv[0] or memon(ahora/nocero)+"/s")
                        self.root.after(0,itemconf,self.canvas,self.marcos[vari].veloci,conv[0] or memon(ahora/nocero)+"/s")
                    if maxi[0]<2:
                        segmenhechos, segmentotal=segmenduo
                        if segmenhechos:
                            ahora2=sum(segmenhechos)
                        tee=f'{segmentotal and ahora2*100/segmentotal :.1f}%'
                    else:
                        tee=f'{sum(nelem)}/{maxi[0]}'
                    #self.canvas.itemconfig(self.marcos[vari].proges,text=tee)
                    self.root.after(0,itemconf,self.canvas,self.marcos[vari].proges,tee)
                time.sleep(0.2)
            print('if not primaimage')
            if not primaimage:
                print('PATHFILE VOID')
                raise Exception('PATHFILE VOID')
            vari=tarea.posirecta
            ahora=sum(tamanio)
            peso=memon(sum(tamanio)+sum(tamaniook))
            if not vari is None and not tarea.cerrar:
                self.root.after(0,itemconf,self.canvas,self.marcos[vari].peso,peso)
                #self.canvas.itemconfig(self.marcos[vari].peso,text=peso)
                self.root.after(0,itemconf,self.canvas,self.marcos[vari].veloci,"")
                #self.canvas.itemconfig(self.marcos[vari].veloci,text="")
            if maxi[0]<2:
                segmenhechos, segmentotal=segmenduo
                if segmenhechos:
                    ahora=sum(segmenhechos)
                tee=f'{segmentotal and ahora*100/segmentotal :.1f}%'
            else:
                tee=f'{sum(nelem)}/{maxi[0]}'
            if not vari is None and not tarea.cerrar:
                self.root.after(0,itemconf,self.canvas,self.marcos[vari].proges,tee)
                #self.canvas.itemconfig(self.marcos[vari].proges,text=tee)

            if not tarea.imaok and not tarea.cerrar:
                pathfile:str=primaimage[0]
                if pathfile.split('.')[-1] in ['mp4','ts','mov']:
                    pathfile=BytesIO(ffmpegx.extraer_fotograma(pathfile))
                try:
                    img = Image.open(pathfile)
                    biyee=BytesIO()
                    img.thumbnail((94,64),4)
                    img=img.convert('RGB')
                    img.save(biyee,'jpeg')

                    #self.temporalima={}
                    if self.guardando:
                        self.image_bytes_list[tarea.url] = biyee
                        self.urlram.add(tarea.url)
                        if not self.guardando:
                            self.temporalima[tarea.url] = biyee
                            self.urlran.add(tarea.url)
                    else:
                        self.temporalima[tarea.url] = biyee
                        self.urlran.add(tarea.url)
                        if self.guardando:
                            self.image_bytes_list[tarea.url] = biyee
                            self.urlram.add(tarea.url)
                    tarea.imaok=True
                    

                    
                    fondo = Image.new("RGB", (94,64), (0, 0, 0))
                    fondo.paste(img, ((94 - img.width) // 2, (64 - img.height) // 2))
                    photo = PhotoImage(fondo)#PhotoImage(img)



                    self.photos.append(photo)
                    vari=tarea.posirecta
                    if not vari is None and not tarea.cerrar:
                        #self.canvas.itemconfig(self.marcos[vari].ima, image=photo,state=tk.NORMAL)
                        self.root.after(0,itemconfimg,self.canvas,self.marcos[vari].ima,photo)
                except Exception as e:
                    tarea.descri+=f'{traceback.format_exc()}\n\n\n'
                    traceback.print_exc()
                    
            if tarea.color0 != 3:
                spl=tee.partition('/')
                if tee in ['100.0%','0.0%'] or spl[0]==spl[2]:
                    tarea.color0=2
                else:
                    tarea.color0=4
            vari=tarea.posirecta
            if not vari is None and not tarea.cerrar:
                #self.canvas.itemconfig(self.marcos[vari].recta, fill=COLORES[tarea.color0][tarea.color1])
                #self.canvas.itemconfig(self.marcos[vari].recta2, fill=COLORES[tarea.color0][tarea.color1])
                self.root.after(0,itemconfill,self.canvas,self.marcos[vari].recta,COLORES[tarea.color0][tarea.color1])
                self.root.after(0,itemconfill,self.canvas,self.marcos[vari].recta2,COLORES[tarea.color0][tarea.color1])
            if not tarea.cerrar:
                don.post_processing()
        except Exception as e:
            print('PROCESABARRA Exception',e)
            tarea.color0=3
            vari=tarea.posirecta
            if not vari is None and not tarea.cerrar:
                #self.canvas.itemconfig(self.marcos[vari].recta, fill=COLORES[3][tarea.color1])
                #self.canvas.itemconfig(self.marcos[vari].recta2, fill=COLORES[3][tarea.color1])
                self.root.after(0,itemconfill,self.canvas,self.marcos[vari].recta,COLORES[3][tarea.color1])
                self.root.after(0,itemconfill,self.canvas,self.marcos[vari].recta2,COLORES[3][tarea.color1])
            tarea.descri+=f'fallo {tarea.url}\n{traceback.format_exc()}\n\n'
            print('fallo '+tarea.url)
            #print('nombreactual '+(self.nombreactual or 'None'))
            #print('detalle:',e)
            #print(f"Ocurrio en la linea_1: {e.__traceback__.tb_lineno}")
            #nex=e.__traceback__.tb_next
            #if nex:
            #    print(f"Ocurrio en la linea_2: {nex.tb_lineno}")
            traceback.print_exc()
        tarea.proges=tee
        tarea.peso=peso
    
    def download_part(self,url:str, start_byte:int, end_byte:int, filename:str,ses:requests.Session, size:list,idx:int, tarea:Tarea,fallo:list):
        #r = ses.get(url, headers={"Range":f"bytes={start_byte}-{end_byte}"}, stream=True)
        intentos = 0
        with open(filename, "r+b") as f:
            while start_byte <= end_byte and not tarea.cerrar and not fallo[0]:
                headers = {'Range': f'bytes={start_byte}-{end_byte}'}
                try:
                    r = ses.get(url, headers=headers, stream=True, timeout=5)
                    r.raise_for_status()
                    f.seek(start_byte)
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            chun=len(chunk)
                            f.write(chunk)
                            start_byte+=chun
                            with self.lock1:
                                size[idx]+=chun
                        if tarea.cerrar or fallo[0]:
                            r.close()
                            break
                except Exception as e:#requests.exceptions.RequestException
                    print(f"ERROR download_part: {e}")
                    if intentos > 2:
                        print("❌ Se alcanzó el número máximo de reintentos. Cancelando.")
                        fallo[0]=True
                        return
                    print("Reintentando en 2 segundo...",intentos)
                    intentos += 1
                    traceback.print_exc()
                    time.sleep(2)
                    
        #print('fin hilo '+str(start_byte))

    def download_file(self,url:str,filename:str,tarea:Tarea, size:list,idx:int,nphilo:int,head:dict,session:requests.Session,segmenduo:list,alter):
        fallo=[False]
        philos=[]
        try:
            #response = urllib.request.urlopen(url)
            if not session:
                session=requests.Session()
            if head:
                session.headers.update(head)
            for _ in range(5):
                response = session.get(url, stream=True)
                if response.status_code in [200,206]:
                    break
                elif response.status_code == 404:
                    response.content
                    if alter:
                        url=alter()
                        filename=filename[:filename.rfind('.')]+url[url.rfind('.'):]
                    else:
                        raise Exception('No existe archivo: Error 404')
                else:
                    response.content
                if tarea.cerrar:
                    return filename
                    #raise Exception('Tarea cerrada')
                time.sleep(2)
            else:
                tarea.listex[idx]+=f'status_code: {response.status_code} {url}\n'
                print(response.status_code,url)
                raise Exception('No status_code 200 session.get')
            #print(response.status_code,url)
            if 'Content-Length' in response.headers:
                file_size = int(response.headers['Content-Length'])
            else:
                resh=session.head(url)
                if 'Content-Length' in resh.headers:
                    file_size = int(resh.headers['Content-Length'])
                else:
                    file_size=1024*1024
                    print('No Content-Length')
                    print(response.status_code,url)
                    tarea.listex[idx]+=f'No Content-Length\nstatus_code: {response.status_code} {url}\n'
                    #raise
            
            if segmenduo:
                segmenduo[1]=file_size
            intentos = 0
            #a=filename.rfind('\\')
            #b=filename.rfind('/',a+1)
            #base=filename[:a if a>b else b]
            #if not os.path.exists(base):
            #    os.makedirs(base,exist_ok=True)
            if file_size <= 5 * 1024 * 1024 or nphilo<2:
                with open(filename, "wb") as f:
                    try:
                        for chunk in response.iter_content(chunk_size=1024*8):
                            size[idx] += len(chunk)
                            if chunk:
                                f.write(chunk)
                            if tarea.cerrar:
                                response.close()
                                break
                    except Exception as e:
                        #print(f"Error: {traceback.format_exc()}")
                        print('Error en principal UNICO:')
                        traceback.print_exc()
                        tarea.listex[idx]+=f'Error en principal UNICO: {traceback.format_exc()}\n'
                        raise Exception(e)
                        #if intentos > 2:
                        #    print("❌ Se alcanzó el número máximo de reintentos. Cancelando.")
                        #    tarea.descri+='❌ Se alcanzo el numero máximo de reintentos. Cancelando.\n'
                        #   raise Exception('Sin Intentos')
                        #tarea.descri+='Reintentando en 1 segundo...en principal unico\n'
                        #print("Reintentando en 10 segundo...en principal unico")
                        #intentos += 1
                        #time.sleep(10)
                if tarea.cerrar:
                    os.remove(filename)
                return filename
            with open(filename, "wb") as f:
                #f.truncate(file_size)
                f.truncate(0)
            
            mid_point = file_size // nphilo
            philos=[Thread(target=self.download_part, args=(url, mid_point*ii,(mid_point*(ii+1) if ii<nphilo-1 else file_size) - 1, filename,session,size,idx,tarea,fallo)) for ii in range(1,nphilo)]
            for p in philos:
                p.start()
            #print('numero de philos',len(philos)+1)
            #intentos=0
            downloaded=0
            with open(filename, "r+b") as f:
                while downloaded <= mid_point-1 and not tarea.cerrar and not fallo[0]:
                    try:
                        if intentos==0:
                            f.seek(0)
                            for chunk in response.iter_content(chunk_size=self.parteciya):
                                if chunk:
                                    lenchu = len(chunk)
                                    downloaded += lenchu
                                    if downloaded >= mid_point:
                                        downloaded -= lenchu
                                        lenchu=mid_point-downloaded
                                        f.write(chunk[:lenchu])
                                        downloaded += lenchu
                                        with self.lock1:
                                            size[idx] += lenchu
                                        response.close()
                                        break
                                    else:
                                        f.write(chunk)
                                        with self.lock1:
                                            size[idx] += lenchu
                                if tarea.cerrar or fallo[0]:
                                    response.close()
                                    break
                        else:
                            headers = {'Range': f'bytes={downloaded}-{mid_point-1}'}
                            response = session.get(url, headers=headers, stream=True, timeout=5)
                            response.raise_for_status()
                            f.seek(downloaded)
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    chun=len(chunk)
                                    f.write(chunk)
                                    downloaded+=chun
                                    with self.lock1:
                                        size[idx]+=chun
                                if tarea.cerrar or fallo[0]:
                                    response.close()
                                    break
                    except Exception as e:
                        #print(f"Error: {traceback.format_exc()}")
                        print('ERROR EN PRINCIPAL:')
                        traceback.print_exc()
                        tarea.listex[idx]+=f'ERROR EN PRINCIPAL: {traceback.format_exc()}\n'
                        response.close()
                        if intentos > 2:
                            fallo[0]=True
                            print("❌ Se alcanzo el numero maximo de reintentos. Cancelando.")
                            tarea.listex[idx]+='❌ Se alcanzo el numero maximo de reintentos. Cancelando.\n'
                            raise Exception('Sin Intentos')
                        tarea.listex[idx]+='REINTENTANDO en 4 segundo...en principal\n'
                        print("REINTENTANDO en 4 segundo...en principal")
                        intentos += 1
                        time.sleep(4)
            #print('fin hilo principal')
            for p in philos:
                p.join()
            if tarea.cerrar:
                os.remove(filename)
            #print('fin de los otro hilos')
            if fallo[0]:
                raise Exception('FALLO descarga de alguna parte')
            return filename
        except Exception as e:
            for p in philos:
                p.join()
            if os.path.exists(filename):
                os.remove(filename)
            print('DOWNLOAD_FILE ERROR',e)
            traceback.print_exc()
            tarea.listex[idx]+=f'DOWNLOAD_FILE ERROR {e}\n\n'
            raise Exception('')

    #locks_comprobador={None:[]}
    def procesalo(self, na: str):
        self.taskbar_progress.setProgress(100)
        lock = self.locks_comprobador[na]
        with self.lockrun:
            if self.runstop==0:
                self.taskbar_progress.setProgress(100)
            self.runstop+=1
        while True:
            fin=True
            #if not self.suichi:
            if not self.suichi or not self.ondic[na]:
                break
            with lock:
                if self.caindpro and self.canom==na:
                    self.indicedeprocesamiento2[na]=0
                    self.caindpro=False
                if not len(self.datos2[na])>self.indicedeprocesamiento2[na]:
                    break
                while len(self.datos2[na])>self.indicedeprocesamiento2[na]:
                    if self.caindpro and self.canom==na:
                        self.indicedeprocesamiento2[na]=0
                        self.caindpro=False
                    elemento=self.datos2[na][self.indicedeprocesamiento2[na]]
                    self.indicedeprocesamiento2[na]+=1
                    if elemento.color0 == 0:
                        fin=False
                        elemento.color0=1
                        break
            if fin:
                break
            self.procesabarra(elemento)
            if not self.datos2[na]:
                break
        with self.lockrun:
            self.runstop-=1
            if self.runstop==0:
                self.taskbar_progress.setProgress(0)

    def creahilo(self,na:str):
        hilos=self.dichilostarea[na]
        hilos=[h for h in hilos if h.is_alive()]
        for _ in range(self.ntareas[na]-len(hilos)):
            if not self.suichi or not self.ondic[na]:
                break
            hh1=Thread(target=self.procesalo,args=(na,),daemon=True)
            hilos.append(hh1)
            hh1.start()
        self.dichilostarea[na]=hilos

    def on_off(self):
        self.suichi=not self.suichi
        if self.suichi:
            bx="SwitchOn.TButton"
            for na in self.dichilostarea.keys():
                if self.ondic[na]:
                    self.creahilo(na)
        else:
            bx="SwitchOff.TButton"
        self.suich.config(style=bx)
    def on_offuni(self):
        self.ondic[self.nombreactual]=not self.ondic[self.nombreactual]
        if self.ondic[self.nombreactual]:
            bx="SwitchOn.TButton"
            self.creahilo(self.nombreactual)
        else:
            bx="SwitchOff.TButton"
        self.suichuni.config(style=bx)

    def update_scroll(self, delta:int):
        self.canvas.yview_scroll(int(-1 * (delta / 120)), "units")
        #print(delta)
        prco=self.start_index2[self.nombreactual]
        if 0>delta:
            prco+=self.elementosmostrados
        else:
            prco-=self.elementosmostrados
        if prco<0 or prco>=len(self.datos2[self.nombreactual]):
            return
        for i in range(self.elementosmostrados if len(self.datos2[self.nombreactual])>self.start_index2[self.nombreactual]+self.elementosmostrados else len(self.datos2[self.nombreactual])-self.start_index2[self.nombreactual]):
            self.datos2[self.nombreactual][self.start_index2[self.nombreactual]+i].posirecta=None
        if 0>delta:
            self.start_index2[self.nombreactual]+=self.elementosmostrados
        else:
            self.start_index2[self.nombreactual]-=self.elementosmostrados
        if self.start_index2[self.nombreactual]>len(self.datos2[self.nombreactual]):
            self.start_index2[self.nombreactual]-=self.elementosmostrados
        self.draw_visible_rectangles()
        for i in range(self.elementosmostrados if len(self.datos2[self.nombreactual])>self.start_index2[self.nombreactual]+self.elementosmostrados else len(self.datos2[self.nombreactual])-self.start_index2[self.nombreactual]):
            self.datos2[self.nombreactual][self.start_index2[self.nombreactual]+i].posirecta=i

    def on_mouse_wheel(self, event):
        self.update_scroll(event.delta)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gestor de Descargas")
    #root.geometry("472x650+800+10")
    root.geometry("520x650+800+10")
    root.minsize(310,108)
    app = DraggableRectangleApp(root)
    root.mainloop()