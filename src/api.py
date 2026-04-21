import os
from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Enable CORS so our React frontend on localhost:5173 can securely talk to this API
CORS(app, resources={r"/api/*": {"origins": "*"}})

DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise ValueError("❌ No DB_URL discovered in .env. Ensure your python-dotenv is loading properly.")

engine = create_engine(DB_URL)

@app.route('/api/mediciones', methods=['GET'])
def get_mediciones():
    try:
        with engine.connect() as conn:
            # We boldly query the materialized view for ultimate performance
            result = conn.execute(text("SELECT * FROM mv_mediciones_estado ORDER BY fecha_medicion ASC"))
            
            datos = []
            for row in result:
                rm = row._mapping
                datos.append({
                    "id": rm['medicion_id'],
                    "fecha": str(rm['fecha_medicion']) if rm['fecha_medicion'] else None,
                    "valor": float(rm['valor']),
                    "operador": rm['operador'],
                    "ubicacion": rm['ubicacion'],
                    "latitud": float(rm['latitud']) if rm['latitud'] else None,
                    "longitud": float(rm['longitud']) if rm['longitud'] else None,
                    "parametro": rm['parametro'],
                    "unidad": rm['unidad_medicion'],
                    "limite_maximo": float(rm['limite_maximo']) if rm['limite_maximo'] else None,
                    "limite_minimo": float(rm['limite_minimo']) if rm['limite_minimo'] else None,
                    "estado": rm['estado_cumplimiento']
                })
            return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Data Sentinel API Gateway is running on http://127.0.0.1:5000")
    print("Press CTRL+C to quit")
    app.run(debug=True, port=5000)
