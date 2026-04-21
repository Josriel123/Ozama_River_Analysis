import os
import PyPDF2
import json
from google import genai
from google.genai import types
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)

# --- CONFIGURACIÓN ---
API_KEY = os.getenv("API_KEY")
DB_URL = os.getenv("DB_URL")
PDF_PATH = os.path.join(BASE_DIR, "data", "URBE_Informe_2013.pdf")
MODEL_ID = "gemini-3-flash-preview"

client = genai.Client(api_key=API_KEY)
engine = create_engine(DB_URL)


def extraer_texto_pdf(ruta):
    with open(ruta, 'rb') as f:
        lector = PyPDF2.PdfReader(f)
        return "".join([p.extract_text() for p in lector.pages if p.extract_text()])


def obtener_o_crear_id(tabla, nombre, columna_nombre, unidad=None):
    with engine.begin() as conn:
        res = conn.execute(text(f"SELECT id FROM {tabla} WHERE LOWER({columna_nombre}) = LOWER(:n)"),
                           {"n": nombre}).fetchone()
        if res: return res[0]

        if tabla == "parametros":
            return conn.execute(text(f"INSERT INTO {tabla} (nombre, unidad) VALUES (:n, :u) RETURNING id"),
                                {"n": nombre, "u": unidad}).fetchone()[0]
        else:
            return \
            conn.execute(text(f"INSERT INTO {tabla} (nombre) VALUES (:n) RETURNING id"), {"n": nombre}).fetchone()[0]


# --- NUEVA FUNCIÓN DE REFERENCIA ---
def obtener_listas_referencia():
    """Trae los nombres existentes de la DB para dárselos a la IA."""
    with engine.connect() as conn:
        # Traer ubicaciones
        res_u = conn.execute(text("SELECT nombre FROM ubicaciones")).fetchall()
        ubicaciones = [fila[0] for fila in res_u]

        # Traer parámetros/contaminantes
        res_p = conn.execute(text("SELECT nombre FROM parametros")).fetchall()
        contaminantes = [fila[0] for fila in res_p]

    return ubicaciones, contaminantes


# --- EJECUCIÓN DEL PIPELINE ---

# 1. Obtenemos lo que ya tenemos en la DB
lista_ubicaciones, lista_contaminantes = obtener_listas_referencia()

# --- PASO 1: EXTRACCIÓN INTELIGENTE ---
print("🚀 Iniciando Pipeline Automático...")
texto = extraer_texto_pdf(PDF_PATH)

prompt = f"""
    Eres un ingeniero de datos. Extrae las mediciones del texto.
    Si el texto dice "menor que", "debajo de" o "<", usa el operador "<".
    Si dice "más de" o ">", usa el operador ">". Si es un número exacto, usa "=".
    Si dice "mayor o igual" o "menor o igual", añade un "=" al final del primer operador (por ejemplo: menor o igual <=).
    
    El objetivo es cerrar la brecha de informacion que hay en el internet sobre el rio ozama y para ello hay que crear
    una base de datos con lo que hay publico en internet, para asi tener todo organizado, actualizado en un mismo sitio.
    
    La base de datos actual tiene los siguientes parametros, los cuales se pueden modificar y añadir mas conforme
    se vea necesario:
    Contaminantes(o parametros): {lista_contaminantes}
    Ubicaciones: {lista_ubicaciones}
    
    Chequea si la ubicacion que obtengas del texto es similar o la misma que alguno de lo que estan en la lista
    para que asi tenga coherencia, si si hay, entonces usa la que esta en la lista oficial.
    Si no pues no pasa nada, ponlo como si fuese uno nuevo. Lo mismo aplica para los contaminantes
    Ex: Tu obtienes "Ozama (Sabana Larga)" y en ubicaciones esta "Sabana Larga" entonces deberas de poner "Sabana Larga"
    
    "IMPORTANTE: Usa siempre la llave 'unidad' para la unidad de medida, nunca 'unit'."
    "IMPORTANTE: La 'fecha' debe estar obligatoriamente en formato ISO 'YYYY-MM-DD' (si solo dice agosto 2013, pon '2013-08-01')."
    
    Devuelve un JSON con esta estructura:
    [
      {{
        "ubicacion": "nombre", 
        "contaminante": "nombre", 
        "operador": "<", 
        "fecha": "YYYY-MM-DD",
        "valor": 5.0, 
        "unidad": "mg/L",
        "fuente": "URBE_Informe_2013.pdf - Pag 1"
      }}
    ]
    Texto: {texto}
"""

response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
    config=types.GenerateContentConfig(response_mime_type="application/json")
)

datos = json.loads(response.text)
print(f"🧠 IA extrajo {len(datos)} mediciones.")
print(response.text)

# --- PASO 2: CARGA AUTOMÁTICA CON VALIDACIÓN ---
try:
    for item in datos:
        # Validación de seguridad: Si no tiene valor o ubicación, ignora esa fila
        if not item.get('ubicacion') or item.get('valor') is None:
            continue

        unidad_detectada = item.get('unit') or item.get('unidad') or "S/U"

        u_id = obtener_o_crear_id("ubicaciones", item['ubicacion'], "nombre")
        p_id = obtener_o_crear_id("parametros", item['contaminante'], "nombre", unidad_detectada)

        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO mediciones (ubicacion_id, parametro_id, valor, operador, fuente, fecha_medicion)
                VALUES (:u, :p, :v, :op, :f, :fecha)
            """), {
                "u": u_id, "p": p_id, "v": item['valor'], "op": item.get('operador', '='), "f": item.get('fuente'), "fecha": item.get('fecha')
            })

    with engine.begin() as conn:
        conn.execute(text("REFRESH MATERIALIZED VIEW mv_mediciones_estado;"))

    print("✅ ¡Pipeline completado! Datos en Neon y Vista Materializada actualizada.")

except Exception as e:
    print(f"❌ Error en la automatización: {e}")