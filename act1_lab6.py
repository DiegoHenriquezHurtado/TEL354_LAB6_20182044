# imports
import yaml
import requests

# Clases
class Alumno:
    def __init__(self, nombre, codigo, mac):
        self.nombre = nombre
        self.codigo = codigo
        self.mac = mac

class Curso:
    def __init__(self, codigo, estado, nombre, alumnos, servidores):
        self.codigo = codigo
        self.estado = estado
        self.nombre = nombre
        self.alumnos = alumnos  # lista de códigos de alumno
        self.servidores = servidores  # lista de nombres de servidores

class Servidor:
    def __init__(self, nombre, ip, servicios):
        self.nombre = nombre
        self.ip = ip
        self.servicios = servicios  # lista de dicts con nombre, protocolo, puerto

# Variables globales
alumnos = []
cursos = []
servidores = []
conexiones = {}

# Funciones necesarias

def importar_archivo(nombre_archivo):
    try:
        global alumnos, cursos, servidores
        with open(nombre_archivo, 'r', encoding='utf-8') as file:
            datos = yaml.safe_load(file)
            alumnos = [Alumno(**a) for a in datos.get('alumnos', [])]
            cursos = [Curso(**c) for c in datos.get('cursos', [])]
            servidores = [Servidor(**s) for s in datos.get('servidores', [])]
            print("Importación completada.")
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'datos.yaml' en el directorio actual")
        return None
    except yaml.YAMLError as e:
        print(f"Error al leer el archivo YAML: {e}")
        return None

#ALUMNOS
def mostrar_submenu_alumno():
    while(True):
        print("------------------")
        print("--Submenu-alumno--")
        print("1. Crear")
        print("2. Listar")
        print("3. Mostrar Detalle")
        print("0. Volver")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            crear_alumno()
        elif opcion == '2':
            listar_alumnos()
        elif opcion == '3':
            break
        elif opcion == '0':
            break
        else:
            print("Opción no válida")

def listar_alumnos():
    for a in alumnos:
        print(f"{a.codigo} - {a.nombre} - {a.mac}")

def crear_alumno():
    print("\n--- Crear Alumno ---")
    nombre = input("Nombre completo: ")
    codigo = input("Codigo PUCP: ")
    mac = input("Direccion MAC (ej. 00:44:11:22:33:44): ")

    # Validar que no se repita
    if any(a.codigo == codigo for a in alumnos):
        print("Ya existe un alumno con ese codigo.")
        return

    nuevo = Alumno(nombre, codigo, mac)
    alumnos.append(nuevo)
    print(f"Alumno {nombre} agregado con exito.")

# CURSOS
def mostrar_submenu_cursos():
    while(True):
        print("--Submenu-cursos--")
        print("1. Listar")
        print("2. Mostrar Detalle")
        print("3. Actualizar")
        print("4. Listar Cursos que tiene acceso a SSH")
        print("0. Volver")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            listar_cursos()
        elif opcion == '2':
            cod = input("Código de curso para ver detalles: ")
            mostrar_detalle_curso(cod)
        elif opcion == '3':
            agregar_alumno_a_curso()
            break
        elif opcion == '4':
            listar_cursos_con_ssh_en_servidor1()
        elif opcion == '0':
            break
        else:
            print("Opción no válida")

def listar_cursos():
    for c in cursos:
        print(f"{c.codigo} - {c.nombre} - Estado: {c.estado}")

def mostrar_detalle_curso(codigo_curso):
    curso = next((c for c in cursos if c.codigo == codigo_curso), None)
    if curso:
        print(f"{curso.nombre} ({curso.codigo}) - Estado: {curso.estado}")
        print("Alumnos:")
        for cod in curso.alumnos:
            alumno = next((a for a in alumnos if a.codigo == cod), None)
            if alumno:
                print(f"  - {alumno.nombre} ({alumno.codigo})")

def listar_cursos_con_ssh_en_servidor1():
    print("\nCursos con acceso SSH al Servidor 1:\n")
    encontrados = False
    for curso in cursos:
        #if curso.estado != "DICTANDO":
        #    continue
        for srv in curso.servidores:
            if srv['nombre'] == "Servidor 1" and "ssh" in srv.get('servicios_permitidos', []):
                print(f"- {curso.codigo}: {curso.nombre}")
                encontrados = True
                break
    if not encontrados:
        print("Ningún curso tiene acceso SSH al Servidor 1.")

def agregar_alumno_a_curso():
    print("\n--- Agregar alumno a un curso ---")
    codigo_alumno = input("Código del alumno: ")
    codigo_curso = input("Código del curso: ")

    alumno = next((a for a in alumnos if a.codigo == codigo_alumno), None)
    curso = next((c for c in cursos if c.codigo == codigo_curso), None)

    if not alumno:
        print("Alumno no encontrado.")
        return
    if not curso:
        print("Curso no encontrado.")
        return

    if codigo_alumno in curso.alumnos:
        print("El alumno ya está inscrito en este curso.")
    else:
        curso.alumnos.append(codigo_alumno)
        print(f"Alumno {alumno.nombre} agregado al curso {curso.codigo} - {curso.nombre}.")

# SERVIDORES
def mostrar_submenu_servidores():
    while(True):
        print("------------------")
        print("--Submenu-Servidores--")
        print("1. Listar")
        print("2. Mostrar Detalle")
        print("0. Volver")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            listar_servidores()
        elif opcion == '2':
            nombre = input("Nombre de servidor para ver detalles: ")
            mostrar_detalle_servidor(nombre)
        elif opcion == '0':
            break
        else:
            print("Opción no válida")

def listar_servidores():
    for s in servidores:
        print(f"{s.nombre} - IP: {s.ip}")

def mostrar_detalle_servidor(nombre_servidor):
    serv = next((s for s in servidores if s.nombre == nombre_servidor), None)
    if serv:
        print(f"{serv.nombre} - IP: {serv.ip}")
        print("Servicios:")
        for svc in serv.servicios:
            print(f"  - {svc['nombre']} ({svc['protocolo']}:{svc['puerto']})")
    else:
        print("Dicho servidor no se encuentra en el archivo.yaml importado")

# CONEXIONES
def mostrar_submenu_conexiones():
    while(True):
        print("------------------")
        print("--Submenu-conexiones--")
        print("1. Crear")
        print("2. Listar")
        print("3. Borrar")
        print("0. Volver")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            handler = input("Ingrese un nombre identificador (handler) para la conexión: ")
            alumno_mac = input("Ingrese la MAC del alumno (ej. 00:44:11:22:44:A7:2A): ")
            servidor_mac = input("Ingrese la MAC del servidor (ej. 00:44:11:22:44:A7:2A): ")
            protocolo = input("Ingrese el protocolo (TCP o UDP): ").upper()
            puerto = int(input("Ingrese el puerto del servicio (ej. 22 para SSH): "))

            crear_conexion(handler, alumno_mac, servidor_mac, protocolo, puerto)
        elif opcion == '2':
            listar_conexiones()
            break
        elif opcion == '3':
            handler = input("Ingrese el handler de la conexión a borrar: ")
            borrar_conexion(handler)
            break
        elif opcion == '0':
            break
        else:
            print("Opción no válida")

def get_attachment_points(mac_address, controller_ip='127.0.0.1', controller_port=8080):

    url = f'http://{controller_ip}:{controller_port}/wm/device/'

    try:
        # Normalizar la MAC del input
        input_mac = mac_address.lower().replace('-', ':')

        # Hacer la solicitud GET
        response = requests.get(url)
        response.raise_for_status()

        # La API devuelve una lista de dispositivos
        devices = response.json()

        for device in devices:
            # Manejar diferentes formatos de MAC en la respuesta
            device_mac = device.get('mac')

            # Si device_mac es una lista, tomar el primer elemento
            if isinstance(device_mac, list):
                if not device_mac:  # Si la lista está vacía
                    continue
                device_mac = device_mac[0]

            # Comparar MACs normalizadas
            if device_mac and str(device_mac).lower().replace('-', ':') == input_mac:
                attachment_points = device.get('attachmentPoint', [])
                if attachment_points:
                    attachment_point = attachment_points[0]
                    dpid = attachment_point.get('switchDPID')
                    port = attachment_point.get('port')
                    if dpid and port:
                        return dpid, port

        return None, None

    except requests.exceptions.RequestException as e:
        print(f"Error al consultar la API: {e}")
        return None, None

def get_route(src_dpid, src_port, dst_dpid, dst_port, controller_ip="127.0.0.1", port=8080):

    url = f"http://{controller_ip}:{port}/wm/topology/route/{src_dpid}/{src_port}/{dst_dpid}/{dst_port}/json"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza error si status != 200

        route = response.json()  # La respuesta es una lista de hops (pasos)
        path = []

        for hop in route:
            switch = hop.get('switch')
            port = hop.get('port')
            path.append({'switch': switch, 'port': port})

        return path

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la ruta: {e}")
        return []

def crear_conexion(handler, alumno_mac, servidor_mac, protocolo, puerto, controller_ip="127.0.0.1", controller_port=8080):
    if handler in conexiones:
        print(f"[ERROR] Ya existe una conexión con el handler '{handler}'.")
        return

    print(f"[INFO] Obteniendo punto de conexión del alumno {alumno_mac}...")
    dpid_alumno, port_alumno = get_attachment_points(alumno_mac, controller_ip, controller_port)
    if not dpid_alumno:
        print("[ERROR] No se pudo obtener el punto de conexión del alumno.")
        return

    print(f"[INFO] Obteniendo punto de conexión del servidor {servidor_mac}...")
    dpid_servidor, port_servidor = get_attachment_points(servidor_mac, controller_ip, controller_port)
    if not dpid_servidor:
        print("[ERROR] No se pudo obtener el punto de conexión del servidor.")
        return

    print("[INFO] Calculando la ruta...")
    ruta = get_route(dpid_alumno, port_alumno, dpid_servidor, port_servidor, controller_ip, controller_port)
    if not ruta:
        print("[ERROR] No se pudo calcular la ruta entre el alumno y el servidor.")
        return

    print("[INFO] Instalando la ruta en los switches...")
    build_route(ruta, alumno_mac, servidor_mac, protocolo, puerto)

    conexiones[handler] = {
        "alumno_mac": alumno_mac,
        "servidor_mac": servidor_mac,
        "protocolo": protocolo,
        "puerto": puerto,
        "ruta": ruta
    }

    print(f"[OK] Conexión '{handler}' creada exitosamente.")

def listar_conexiones():
    if not conexiones:
        print("[INFO] No hay conexiones creadas.")
        return
    for handler, info in conexiones.items():
        print(f"- Handler: {handler}")
        print(f"  MAC alumno: {info['alumno_mac']}")
        print(f"  IP servidor: {info['servidor_ip']}")
        print(f"  Protocolo: {info['protocolo']}")
        print(f"  Puerto: {info['puerto']}")
        print(f"  Ruta: {info['ruta']}")
        print()

def delete_flow(flow_name, controller_ip="127.0.0.1", controller_port=8080):
    url = f"http://{controller_ip}:{controller_port}/wm/staticflowpusher/json"
    try:
        response = requests.delete(url, json={"name": flow_name})
        response.raise_for_status()
        print(f"[OK] Flow '{flow_name}' eliminado correctamente.")
    except requests.RequestException as e:
        print(f"[ERROR] No se pudo eliminar el flow '{flow_name}': {e}")

def borrar_conexion(handler, controller_ip="127.0.0.1", controller_port=8080):
    if handler not in conexiones:
        print(f"[ERROR] No existe la conexión con handler '{handler}'.")
        return

    conexion = conexiones[handler]
    alumno_mac = conexion["alumno_mac"]
    servidor_mac = conexion["servidor_mac"]
    protocolo = conexion["protocolo"].upper()
    puerto = conexion["puerto"]
    ruta = conexion["ruta"]

    proto_number = {"TCP": 6, "UDP": 17}[protocolo]

    # Eliminar flows instalados en cada switch
    for i in range(len(ruta)-1):
        hop = ruta[i]
        dpid = hop["switch"]

        # Flow alumno -> servidor
        name1 = f"flow_{dpid}_{alumno_mac}_{servidor_mac}"
        delete_flow(name1, controller_ip, controller_port)

    for i in range(len(ruta)-1, 0, -1):
        hop = ruta[i]
        dpid = hop["switch"]

        # Flow servidor -> alumno
        name2 = f"flow_{dpid}_{servidor_mac}_{alumno_mac}"
        delete_flow(name2, controller_ip, controller_port)

    for hop in ruta:
        dpid = hop["switch"]

        # Flow ARP alumno -> servidor
        arp_name1 = f"flow_{dpid}_{alumno_mac}_{servidor_mac}_ARP"
        delete_flow(arp_name1, controller_ip, controller_port)

        # Flow ARP servidor -> alumno
        arp_name2 = f"flow_{dpid}_{servidor_mac}_{alumno_mac}_ARP"
        delete_flow(arp_name2, controller_ip, controller_port)

    # Finalmente eliminar del diccionario
    del conexiones[handler]
    print(f"[OK] Conexión '{handler}' eliminada completamente.")


def insert_flow(dpid, match_fields, actions, priority=100, controller_ip='127.0.0.1', controller_port=8080):
    url = f"http://{controller_ip}:{controller_port}/wm/staticflowpusher/json"
    flow = {
        "switch": dpid,
        "name": f"flow_{dpid}_{match_fields.get('eth_src', 'any')}_{match_fields.get('eth_dst', 'any')}",
        "priority": str(priority),
        "active": "true",
        "match": match_fields,
        "actions": actions
    }

    try:
        response = requests.post(url, json=flow)
        response.raise_for_status()
        print(f"[OK] Flow insertado en switch {dpid}")
    except requests.RequestException as e:
        print(f"[ERROR] No se pudo insertar flow en {dpid}: {e}")


def build_route(ruta, alumno_mac, servidor_mac, protocolo, puerto, controller_ip="127.0.0.1", controller_port=8080):
    protocolo = protocolo.upper()
    if protocolo not in ["TCP", "UDP"]:
        print("[ERROR] Protocolo no soportado.")
        return

    proto_number = {"TCP": 6, "UDP": 17}[protocolo]

    # Reglas de alumno -> servidor
    for i in range(len(ruta)-1):
        actual = ruta[i]
        siguiente = ruta[i+1]

        dpid = actual['switch']
        out_port = siguiente['port']

        match_fields = {
            "eth_type": "0x0800",  # IPv4
            "eth_src": alumno_mac,
            "eth_dst": servidor_mac,
            "ip_proto": proto_number,
            f"{protocolo.lower()}_dst": puerto
        }

        actions = f"output={out_port}"
        insert_flow(dpid, match_fields, actions, controller_ip=controller_ip, controller_port=controller_port)

    # Reglas de servidor -> alumno
    for i in range(len(ruta)-1, 0, -1):
        actual = ruta[i]
        anterior = ruta[i-1]

        dpid = actual['switch']
        out_port = anterior['port']

        match_fields = {
            "eth_type": "0x0800",  # IPv4
            "eth_src": servidor_mac,
            "eth_dst": alumno_mac,
            "ip_proto": proto_number,
            f"{protocolo.lower()}_src": puerto
        }

        actions = f"output={out_port}"
        insert_flow(dpid, match_fields, actions, controller_ip=controller_ip, controller_port=controller_port)

    # Flujos para ARP (bidireccionales)
    for hop in ruta:
        dpid = hop['switch']
        out_port = hop['port']
        match_fields = {
            "eth_type": "0x0806",  # ARP
            "eth_src": alumno_mac,
            "eth_dst": servidor_mac
        }
        insert_flow(dpid, match_fields, f"output={out_port}", priority=1, controller_ip=controller_ip, controller_port=controller_port)

        match_fields = {
            "eth_type": "0x0806",  # ARP
            "eth_src": servidor_mac,
            "eth_dst": alumno_mac
        }
        insert_flow(dpid, match_fields, f"output={out_port}", priority=1, controller_ip=controller_ip, controller_port=controller_port)

    print("[OK] Rutas instaladas correctamente.")


# Menú principal
def menu():
    while True:
        print("\n--- Menú Principal ---")
        print("1) Importar")
        print("2) Exportar")
        print("3) Cursos")
        print("4) Alumnos")
        print("5) Servidores")
        print("6) Políticas")
        print("7) Conexiones")
        print("0) Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            nombre_archivo = input("Nombre del archivo YAML: ")
            importar_archivo(nombre_archivo)
        elif opcion == '4':
            mostrar_submenu_alumno()
        elif opcion == '3':
            mostrar_submenu_cursos()
        elif opcion == '5':
            mostrar_submenu_servidores()
        elif opcion == '7':
            mostrar_submenu_conexiones()
        elif opcion == '0':
            break
        else:
            print("Opción no válida")

def main():
    menu()

if __name__ == "__main__":
    main()

