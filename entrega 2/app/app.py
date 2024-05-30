#!/usr/bin/python3
import os
from datetime import datetime
from logging.config import dictConfig
from psycopg.rows import namedtuple_row
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@postgres/postgres")

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s:%(lineno)s - %(funcName)20s(): %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

def verifica_data(dia, hora):
    """
    Verifica se o dia e hora passados são válidos.
    """
    try:
        dia = datetime.strptime(dia, "%Y-%m-%d").date()
        hora = datetime.strptime(hora, "%H:%M").time()

        return datetime.combine(dia, hora)
    except Exception as e:
        return False
    
def eh_passado(data):
    """
    Verifica se a data passada é passada.
    """
    now = datetime.now()
    if data == now: # Não é passado nem futuro, para impedir
        return None # marcação/cancelamento de consultas para o momento atual.
    
    return data < now

def verifica_horario(data):
    """
    Verifica se o horário passado é válido.
    """
    hora = data.hour
    minuto = data.minute

    return (hora >= 8 and hora <= 12) or (hora >= 14 and hora <= 18) and (minuto == 0 or minuto == 30)

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    kwargs={
        "autocommit": True,  # If True don’t start transactions automatically.
        "row_factory": namedtuple_row,
    },
    min_size=4,
    max_size=10,
    open=True,
    # check=ConnectionPool.check_connection,
    name="postgres_pool",
    timeout=5,
)

app = Flask(__name__)
app.config.from_prefixed_env()
log = app.logger

#
# Rotas GET
#

@app.route("/")
def clinicas():
    """
    Retorna a lista de clínicas.
    """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                clinicas = cur.execute(
                    """
                    SELECT nome, morada FROM clinica;
                    """,
                    {},
                ).fetchall()
                log.debug(f"Encontradas {cur.rowcount} clinicas.")

                return jsonify(clinicas)
            except Exception as e:
                return jsonify({"erro": str(e)}), 400

@app.route('/c/<clinica>', methods=['GET'])
def clinica_especialidades(clinica):
    """
    Retorna a lista de especialidades de uma clínica.
    """

    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                especialidades = cur.execute(
                    """
                    SELECT DISTINCT medico.especialidade
                    FROM medico
                    JOIN trabalha ON trabalha.nif = medico.nif
                    WHERE trabalha.nome = %(clinica)s;
                    """,
                    {"clinica": clinica},
                ).fetchall()
                log.debug(f"Encontradas {cur.rowcount} especialidades da clinica {clinica}.")

                especialidades_flat = [especialidade[0] for especialidade in especialidades]
                return jsonify(especialidades_flat)
        
            except Exception as e:
                return jsonify({"erro": str(e)}), 400

@app.route('/c/<clinica>/<especialidade>/', methods=['GET'])
def clinica_medicos(clinica, especialidade):
    """
    Retorna a lista de médicos de uma clínica com uma especialidade.
    """

    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                medicos = cur.execute(
                    """
                    SELECT medico.nome, medico.nif
                    FROM medico
                    JOIN trabalha ON trabalha.nif = medico.nif
                    WHERE trabalha.nome = %(clinica)s AND medico.especialidade = %(especialidade)s;
                    """,
                    {"clinica": clinica, "especialidade": especialidade},
                ).fetchall()  
                log.debug(f"Encontrados {cur.rowcount} medicos da clinica {clinica} com especialidade {especialidade}.") 

                return jsonify(medicos)
            except Exception as e:
                return jsonify({"erro": str(e)}), 400

#
# Rotas POST
#

@app.route('/a/<clinica>/registar/', methods=['POST'])
def marcar_consulta(clinica):
    # ssn = request.args.get('paciente')
    # nif = request.args.get('medico')
    # date = request.args.get('data')
    # hora = request.args.get('hora')

    data = request.json
    ssn = str(data['paciente'])
    nif = str(data['medico'])
    date = str(data['data'])
    hora = str(data['hora'])
    
    log.debug(f"Recebido: paciente={ssn}, medico={nif}, data={date}, hora={hora}")
    
    if not all([ssn, nif, date, hora]):
        return jsonify({"erro": "Faltam parâmetros obrigatórios"}), 400
    
    date_hora = verifica_data(date, hora)

    if not date_hora:
        return jsonify({"erro": "Data ou hora inválida"}), 400
    
    if eh_passado(date_hora):
        return jsonify({"erro": "Não é possível marcar uma consulta para uma data passada"}), 400
    
    if not verifica_horario(date_hora):
        return jsonify({"erro": "Horário fora do expediente"}), 400

    weekday = (date_hora.weekday()+1)%7

    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:        
                trabalha_dia = cur.execute(
                    """
                    SELECT * FROM trabalha
                    WHERE nif = %(nif)s AND nome = %(clinica)s AND dia_da_semana = %(weekday)s;
                    """,
                    {"nif": nif, "clinica": clinica, "weekday": weekday},
                ).fetchone()

                if not trabalha_dia:
                    return jsonify({"erro": f"O médico não trabalha na clinica {clinica} neste dia"}), 400
                
                paciente_verifica = cur.execute(
                    """
                    SELECT * FROM consulta
                    WHERE ssn = %(ssn)s AND data = %(date)s AND hora = %(hora)s;
                    """,
                    {"ssn": ssn, "date": date, "hora": hora},
                ).fetchone()

                if paciente_verifica:
                    return jsonify({"erro": "O paciente já tem uma consulta marcada para este dia e hora"}), 400
                
                medico_verifica = cur.execute(
                    """
                    SELECT * FROM consulta
                    WHERE nif = %(nif)s AND data = %(date)s AND hora = %(hora)s;
                    """,
                    {"nif": nif, "date": date, "hora": hora},
                ).fetchone()

                if medico_verifica:
                    return jsonify({"erro": "O médico já tem uma consulta marcada para este dia e hora"}), 400


                status = cur.execute(
                    """
                    INSERT INTO consulta (nif, ssn, data, hora, nome)
                    VALUES (%(nif)s, %(ssn)s, %(date)s, %(hora)s, %(clinica)s);
                    """,
                    {"nif": nif, "ssn": ssn, "date": date, "hora": hora, "clinica": clinica},
                ).fetchall()

                log.debug(f"Consulta marcada: {status}")

                return jsonify({"success": True, "msg": "Consulta marcada com sucesso"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})


@app.route('/a/<clinica>/cancelar/', methods=['POST', 'DELETE'])
def cancelar_appointment(clinica):
    # ssn = request.args.get('paciente')
    # nif = request.args.get('medico')
    # date = request.args.get('data')
    # hora = request.args.get('hora')
    
    data = request.json
    ssn = str(data['paciente'])
    nif = str(data['medico'])
    date = str(data['data'])
    hora = str(data['hora'])

    if not all([ssn, nif, date, hora]):
        return jsonify({"erro": "Faltam parâmetros obrigatórios"}), 400

    date_hora = verifica_data(date, hora)
    if not date_hora:
        return jsonify({"erro": "Data ou hora inválida"}), 400
    
    if eh_passado(date_hora):
        return jsonify({"erro": "Não é possível cancelar uma consulta já passada"}), 400
    
    if not verifica_horario(date_hora):
        return jsonify({"erro": "Horário fora do expediente"}), 400
    
    log.debug(f"Recebido: paciente={ssn}, medico={nif}, data={date}, hora={hora}")
    
    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                sql_query = """
                    SELECT * FROM consulta
                    WHERE nif = %(nif)s AND ssn = %(ssn)s AND data = %(date)s AND hora = %(hora)s AND nome = %(nome)s;
                """
                cur.execute(sql_query, {"nif": nif, "ssn": ssn, "date": date, "hora": hora, "nome": clinica})
                consulta = cur.fetchone()

                if not consulta:
                    return jsonify({"erro": "Consulta não encontrada"}), 404
                
                log.debug(f"Consulta pedida para cancelar: {consulta}")
                status = cur.execute(
                    """
                    DELETE FROM consulta
                    WHERE nif = %(nif)s AND ssn = %(ssn)s AND data = %(date)s AND hora = %(hora)s AND nome = %(clinica)s;
                    """,
                    {"nif": nif, "ssn": ssn, "date": date, "hora": hora, "clinica": clinica},
                )
                log.debug(f"Consulta cancelada: {status}")
                return jsonify({"success": True, "msg": "Consulta cancelada com sucesso"})
            except Exception as e:
                return jsonify({"success": False, "erro": str(e)})

if __name__ == "__main__":
    app.run()