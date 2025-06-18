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

def alumno_autorizado(codigo_alumno, servidor_nombre, servicio_nombre):
    for curso in cursos:
        if curso.estado != "DICTANDO":
            continue
        if codigo_alumno not in curso.alumnos:
            continue
        for srv in curso.servidores:
            if srv['nombre'] == servidor_nombre and servicio_nombre in srv['servicios_permitidos']:
                return True
    return False

def crear_conexion():
    cod = input("Código del alumno: ")
    nom_srv = input("Nombre del servidor: ")
    nom_srvc = input("Nombre del servicio: ")

    alumno = next((a for a in alumnos if a.codigo == cod), None)
    servidor = next((s for s in servidores if s.nombre == nom_srv), None)

    if not alumno or not servidor:
        print("Alumno o servidor no encontrados.")
        return

    servicio = next((svc for svc in servidor.servicios if svc['nombre'] == nom_srvc), None)
    if not servicio:
        print("Servicio no encontrado.")
        return

    if not alumno_autorizado(alumno.codigo, servidor.nombre, servicio['nombre']):
        print("Acceso denegado: alumno no está autorizado para este servicio.")
        return

    alumno_dpid, alumno_port = get_attachment_point(alumno.mac)
    servidor_dpid, servidor_port = get_attachment_point_by_ip(servidor.ip)

    if None in [alumno_dpid, alumno_port, servidor_dpid, servidor_port]:
        print("No se pudo obtener los attachment points.")
        return

    route = get_route(alumno_dpid, alumno_port, servidor_dpid, servidor_port)
    build_route(route, alumno.mac, servidor.ip, servicio['protocolo'], servicio['puerto'])

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
            build_route()
        elif opcion == '2':
            #Listar
            break
        elif opcion == '3':
            #Borrar
            break
        elif opcion == '0':
            break
        else:
            print("Opción no válida")


# Funciones pendientes: get_attachment_point, get_route, build_route
def get_attachment_points(mac_address, controller_ip='192.168.200.200', controller_port=8080):

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

def get_route(src_dpid, src_port, dst_dpid, dst_port, controller_ip="192.168.200.200", port=8080):

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

def build_route(route, alumno_mac, servidor_ip, protocolo, puerto):
    protocolo_num = {'TCP': 6, 'UDP': 17}.get(protocolo.upper())
    if protocolo_num is None:
        print("Protocolo no soportado")
        return

    for hop in route:
        dpid = hop['switch']
        in_port = hop['in_port']
        out_port = hop['out_port']

        # Flow de ida (alumno -> servidor)
        flow = {
            "switch": dpid,
            "name": f"flow_{dpid}_{in_port}_to_srv",
            "cookie": "0",
            "priority": "32768",
            "ingress-port": in_port,
            "active": "true",
            "eth_type": "0x0800",
            "eth_src": alumno_mac,
            "ipv4_dst": servidor_ip,
            "ip_proto": protocolo_num,
            "tp_dst": puerto,
            "idle_timeout": 10,
            "actions": f"output={out_port}"
        }
        requests.post(f"http://192.168.200.200:8080/wm/staticflowpusher/json", json=flow)

        # Flow de retorno (servidor -> alumno)
        reverse_flow = {
            "switch": dpid,
            "name": f"flow_{dpid}_{out_port}_to_alumno",
            "cookie": "0",
            "priority": "32768",
            "ingress-port": out_port,
            "active": "true",
            "eth_type": "0x0800",
            "ipv4_src": servidor_ip,
            "eth_dst": alumno_mac,
            "ip_proto": protocolo_num,
            "tp_src": puerto,
            "idle_timeout": 10,
            "actions": f"output={in_port}"
        }
        requests.post(f"http://192.168.200.200:8080/wm/staticflowpusher/json", json=reverse_flow)

    print("Flujos instalados correctamente")


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
        elif opcion= '7':
            mostrar_submenu_conexiones()
        elif opcion == '0':
            break
        else:
            print("Opción no válida")

def main():
    menu()

if __name__ == "__main__":
    main()

