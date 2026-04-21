from sqlalchemy import create_engine, text

class DatabaseController:
    def __init__(self, db_url):
        self.db_url = db_url
        self.engine = create_engine(db_url)

    def obtener_o_crear_id(self, tabla, nombre, columna_nombre, unidad=None):
        with self.engine.begin() as conn:
            res = conn.execute(text(f"SELECT id FROM {tabla} WHERE LOWER({columna_nombre}) = LOWER(:n)"),
                               {"n": nombre}).fetchone()
            if res: return res[0]

            if tabla == "parametros":
                return conn.execute(text(f"INSERT INTO {tabla} (nombre, unidad) VALUES (:n, :u) RETURNING id"),
                                    {"n": nombre, "u": unidad}).fetchone()[0]
            else:
                return \
                    conn.execute(text(f"INSERT INTO {tabla} (nombre) VALUES (:n) RETURNING id"),
                                 {"n": nombre}).fetchone()[0]

    def obtener_listas_referencia(self):
        """Trae los nombres existentes de la DB para dárselos a la IA."""
        with self.engine.connect() as conn:
            # Traer ubicaciones
            res_u = conn.execute(text("SELECT nombre FROM ubicaciones")).fetchall()
            ubicaciones = [fila[0] for fila in res_u]

            # Traer parámetros/contaminantes
            res_p = conn.execute(text("SELECT nombre FROM parametros")).fetchall()
            contaminantes = [fila[0] for fila in res_p]

        return ubicaciones, contaminantes