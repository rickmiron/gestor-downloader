import subprocess
import json
rutaff=['','']
def ffprobe_info(file_path:str):
    result= subprocess.run(
            ['ffprobe.exe', '-v', 'error','-hide_banner' ,'-select_streams', 'v:1' ,'-show_streams' ,"-print_format", "json", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
    if result.returncode == 0:
        stream=json.loads(result.stdout)['streams']
        if stream:
            return stream[0]['disposition']['attached_pic']
def run(comand:list,path:str=None):
    return subprocess.run(
            comand,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            cwd=path
        )
def popen(output_file:str,archivos_ts:list,path_ts:str=None):
    with subprocess.Popen(["ffmpeg.exe", "-i", "pipe:0", "-c", "copy", output_file,"-y"],cwd=path_ts,stdin=subprocess.PIPE) as proc:
        for archivo in archivos_ts:
            with open(archivo, "rb") as f:
                proc.stdin.write(f.read())
        proc.stdin.close()
        proc.wait()
def insertpic(pathtext:str,pathimage:str,out_path:str,path:str=None):
    comand=['ffmpeg','-f','concat','-safe','0','-i',pathtext,'-i',pathimage,'-map','1','-map','0','-c','copy','-disposition:0','attached_pic',out_path]
    subprocess.run(
            comand,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            cwd=path
        )
def insertpicnotex(pathtext:str,pathimage:str,out_path:str,path_ts:str,n_files:int):
    comand=['ffmpeg','-f','concat','-safe','0','-i',pathtext,'-i',pathimage,'-map','1','-map','0','-c','copy','-disposition:0','attached_pic',out_path]
    #if n_files>2001:

    comand=['ffmpeg','-i',f'concat:{"|".join([str(c) for c in range(n_files)])}','-map','1','-map','0','-c','copy','-disposition:0','attached_pic',out_path]
    subprocess.run(
            comand,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            cwd=path_ts
        )
    
def extraer_fotograma(video_path:str):
    comando = [
        'ffmpeg',
        '-ss', '1',        # Saltar al segundo deseado
        '-i', video_path,              # Input
        '-vframes', '1',               # Solo un frame
        '-f', 'image2',                # Formato de salida imagen
        '-vcodec', 'mjpeg',            # JPEG como salida
        'pipe:1'                       # Salida por stdout
    ]
    proceso = subprocess.run(comando, capture_output=True)
    #print(proceso.stderr)
    return proceso.stdout#, proceso.stderr
    
def veri():
    comand=[rutaff[0] or 'ffmpeg', '-version']
    resul=subprocess.run(
            comand,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
    print(resul)