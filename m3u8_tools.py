import os
import requests
import threading
import m3u8
from typing import Callable
import queue
import shutil
import ffmpegx
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

class M3u8_stream:
    def __init__(self, url:str, headers:dict[str,str]=None, deco:Callable[[bytes],bytes]=None, 
                 n_thread:int=1, headers_seg:dict[str,str]=None, session:requests.Session=None, alter=None,usetext=True):
        #self.output_file=''
        self.completo=False
        self.duration=[]
        self.url = url
        self.headers = headers
        self.deco = deco
        self.n_thread = n_thread
        self.headers_seg = headers if headers_seg is None else headers_seg
        self.session = session or requests.Session()
        self.sessionkey = requests.Session()
        self.alter = alter
        self.usetex = usetext
        self.lock=threading.Lock()

    def __str__(self):
        # Representación en cadena del objeto
        return f"M3u8_stream({self.url})"

    def read(self,alter,filename:str):
        print("[*] Leyendo archivo m3u8...")
        url=self.url
        response = self.session.get(url,headers=None if self.headers is None else self.headers)
        #response.raise_for_status()
        if response.status_code in [200,206]:
            pass
        elif response.status_code == 404:
            response.content
            if alter:
                url=alter()
                filename=filename[:filename.rfind('.')]+url[url.rfind('.'):]
            else:
                raise Exception('No existe archivo: Error 404')
        else:
            response.raise_for_status()
        return m3u8.loads(response.text).segments,filename
    
    #def download(self, output_file:str):
    #def download(self,output_file:str,tarea, size:list,idf:int,segmenhechos:list=None,nelem:list=None):
    def download(self,output_file:str,tarea, size:list,sizeok:list,idf:int,segmenduo:list,conv,alter):
        print(output_file)
        segment_urls, output_file= self.read(alter,output_file)
        self.conv=conv
        segments_dir=output_file+"_seg"
        urlbase=''
        if self.headers_seg:
            self.session.headers.update(self.headers_seg)
        if segment_urls[0].uri[:7] not in ['http://','https:/']:
            urlbase=self.url[:self.url.rfind('/')+1]
        self.segment_count=total_segments = len(segment_urls)
        if not segmenduo is None:
            segmenhechos:list=segmenduo[0]
            for _ in range(self.n_thread):
                segmenhechos.append(0)
            segmenduo[1]=total_segments
        # Crear la carpeta para los segmentos
        #if os.path.exists(segments_dir):
        #    shutil.rmtree(segments_dir)  # Eliminar carpeta si existe
        os.makedirs(segments_dir,exist_ok=True)
        if os.path.exists(segments_dir+"\\lis.txt"):
            with os.scandir(segments_dir) as entries:
                for entry in entries:
                    sizeok[idf]+= entry.stat().st_size
            self.completo=True
            self._pp(output_file)
            return output_file
        
        # Cola para distribuir tareas
        task_queue:queue.Queue[tuple[str,int]] = queue.Queue()
        
        # Llenar la cola con tareas
        for i, seg in enumerate(segment_urls):
            self.duration.append(seg.duration)
            task_queue.put((urlbase+seg.uri, i, seg.key))
        
        def worker(idh:int):
            """Función ejecutada por cada hilo."""
            csa=0
            while True:
                try:
                    url, index, key = task_queue.get_nowait()
                except queue.Empty:
                    break  # No hay más tareas
                try:
                    self.download_segment(url, index, key, segments_dir, self.session,size,sizeok,idf,tarea)
                    if tarea.cerrar:
                        break
                    if segmenduo:
                        segmenhechos[idh]+=1
                except Exception as e:
                    task_queue.put((url,index,key))
                    csa+=1
                task_queue.task_done()
                if csa>3:
                    break
        print('n_thread',self.n_thread)
        threads =[threading.Thread(target=worker,args=(i,)) for i in range(self.n_thread)]
        for t in threads:
            t.start()
        # Esperar a que todos los hilos terminen
        for t in threads:
            t.join()
        if tarea.cerrar:
            #raise Exception('tarea cerrada')
            return output_file
        # Verificar que todos los segmentos se descargaron
        missing_segments = []
        for i in range(total_segments):
            #segment_path = os.path.join(segments_dir, f"{i}.ts")
            segment_path = os.path.join(segments_dir, str(i))
            if not os.path.exists(segment_path):
                missing_segments.append(i)
        
        if missing_segments:
            print(f"Advertencia: Faltan los segmentos: {missing_segments}")
        else:
            self.completo=True
            self._pp(output_file)
        return output_file
    
    def create_ffmpeg_concat_file(self,output_dir:str):
        """Crea un archivo de lista para ffmpeg con los segmentos."""
        with open(os.path.join(output_dir, "lis.txt"), 'w',encoding="utf-8") as f:
            if not self.usetex:
                return
            #output_dir=output_dir.replace("'","'\\''")
            for i in range(self.segment_count):
                #segment_path = os.path.join(output_dir, f"{i}.ts")
                #segment_path = os.path.join(output_dir, str(i))
                # Escapamos las comillas y usamos paths relativos
                #f.write(f"file '{os.path.join(output_dir, str(i))}'\nduration {self.duration[i]}\n")
                f.write(f"file '{i}'\nduration {self.duration[i]}\n")

    def _pp(self,output_file:str):
        self.conv[0]='Convirtiendo'
        """Une los segmentos en un archivo MP4 usando ffmpeg."""
        output_dir=output_file+'_seg'
        try:
            self.create_ffmpeg_concat_file(output_dir)
            if self.usetex:
                command = [
                    "ffmpeg.exe",
                    "-f", "concat",
                    "-safe", "0",
                    #"-i", os.path.join(output_dir, "lis.txt"),
                    "-i", "lis.txt",
                    "-c", "copy",
                    output_file,"-y"
                ]
                ffmpegx.run(command,path=output_dir)#, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #except subprocess.CalledProcessError as e:
            #    print(f"Error al unir con ffmpeg: {e.stderr.decode()}")
            else:
                ffmpegx.popen(output_file,[str(i) for i in range(self.segment_count)],output_dir)
            shutil.rmtree(output_dir)
        except FileNotFoundError:
            print("Error: ffmpeg no está instalado o no se encuentra en el PATH.")
        except Exception as ex:
            print(f"Error al unir con ffmpeg:{ex}")
        self.conv[0]=' '

    def download_segment(self,url:str, index:int,key_info, output_dir:str, session:requests.Session,size:list,sizeok:list,idx:int,tarea):
        #output_file = os.path.join(output_dir, f"{index}.ts")
        output_file = os.path.join(output_dir, str(index))
        if os.path.exists(output_file):
            with self.lock:
                sizeok[idx]+=os.path.getsize(output_file)
            return
        response = session.get(url, stream=True)
        data = bytearray()
        for chunk in response.iter_content(chunk_size=8*1024):
            if chunk:
                chun=len(chunk)
                data.extend(chunk)
                with self.lock:
                    size[idx]+=chun
            if tarea.cerrar:
                response.close()
                return
        encrypted_data=bytes(data)
        data=None
        if key_info:
            
            #if key_info.uri != current_key_uri:
                # Descargar nueva clave
                #print(f"    [-] Nueva clave: {key_info.uri}")
            key_resp = self.sessionkey.get(key_info.uri)
            #print(key_resp.status_code, key_info.uri)
            key_bytes = key_resp.content
            #    current_key_uri = key_info.uri
            # IV puede ser hexadecimal o None (entonces se usa secuencia)
            iv = bytes.fromhex(key_info.iv[2:]) if key_info.iv else index.to_bytes(16, 'big')

            # Crear el descifrador AES-128 CBC
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv)

            # Descifrar el segmento
            decrypted_data = cipher.decrypt(encrypted_data)
            
            # (Opcional) quitar padding si hay
            try:
                decrypted_data = unpad(decrypted_data, AES.block_size)
            except ValueError:
                pass  # algunos segmentos pueden no tener padding exacto
        else:
            decrypted_data = encrypted_data
        if self.deco:
            decrypted_data=self.deco(decrypted_data)
        with open(output_file, 'wb') as f:
            f.write(decrypted_data)