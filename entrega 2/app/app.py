#!/usr/bin/python3
import os
from datetime import datetime, timedelta
from logging.config import dictConfig
from psycopg.rows import namedtuple_row
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from zoneinfo import ZoneInfo

TZ = 'Etc/GMT-1'

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@postgres/postgres")

times = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", 
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30"
]

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
        dia_ = datetime.strptime(dia, "%Y-%m-%d").date()
        hora_ = datetime.strptime(hora, "%H:%M").time()

        dt_naive = datetime.combine(dia_, hora_)
        dt_with_tz = dt_naive.replace(tzinfo=ZoneInfo(TZ))
        
        return dt_with_tz
    except Exception as e:
        log.debug(e)
        return False
    
def time_now():
    """
    Gera o tempo atual com a timezone definida.
    """
    return datetime.now(ZoneInfo(TZ))
    
def eh_passado(data):
    """
    Verifica se a data passada é passada.
    """
    now = time_now()

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

def dia_semana(data):
    """
    Retorna o dia da semana em formato numérico.
    """
    return (data.weekday()+1)%7

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    kwargs={
        "autocommit": False, # Use transactions
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
                log.debug(f"Encontradas {cur.rowcount} clinicas")

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
                cur.execute(
                    """
                    SELECT * FROM clinica
                    WHERE nome = %(clinica)s;
                    """,
                    {"clinica": clinica},
                )

                clinica_ = cur.fetchone()

                if not clinica_:
                    return jsonify({"erro": f"Clínica {clinica} não encontrada"}), 404

                cur.execute(
                    """
                    SELECT DISTINCT medico.especialidade
                    FROM medico
                    JOIN trabalha ON trabalha.nif = medico.nif
                    WHERE trabalha.nome = %(clinica)s;
                    """,
                    {"clinica": clinica},
                )

                especialidades = cur.fetchall()
                especialidades_flat = [especialidade[0] for especialidade in especialidades]
                
                log.debug(f"Encontradas {cur.rowcount} especialidades na clinica {clinica}")
                return jsonify(especialidades_flat)
        
            except Exception as e:
                return jsonify({"erro": str(e)}), 400

@app.route('/c/<clinica>/<especialidade>', methods=['GET'])
def clinica_medicos(clinica, especialidade):
    """
    Retorna a lista de médicos de uma clínica com uma especialidade.
    """

    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:

                cur.execute(
                    """
                    SELECT * FROM clinica
                    WHERE nome = %(clinica)s;
                    """,
                    {"clinica": clinica},
                )

                clinica_ = cur.fetchone()

                if not clinica_:
                    return jsonify({"erro": "Clínica não encontrada"}), 404
                
                cur.execute(
                    """
                    SELECT DISTINCT medico.nome, medico.nif
                    FROM medico
                    JOIN trabalha ON trabalha.nif = medico.nif
                    WHERE trabalha.nome = %(clinica)s AND medico.especialidade = %(especialidade)s;
                    """,
                    {"clinica": clinica, "especialidade": especialidade},
                )
                
                medicos = cur.fetchall()

                log.debug(f"Encontrados {cur.rowcount} medicos da clinica {clinica} com especialidade {especialidade}") 

                todos_medicos = []

                for medico in medicos:
                    log.debug(f"Medico: {medico}")
                    este_medico = {
                        "nif": medico[1],
                        "nome": medico[0],
                        "horarios": []
                    }
                    dia = time_now().date()
                    
                    dias = cur.execute(
                        """
                        SELECT dia_da_semana
                        FROM trabalha
                        WHERE nif = %(nif)s AND nome = %(clinica)s;
                        """,
                        {"nif": medico.nif, "clinica": clinica},
                    ).fetchall()

                    log.debug(f"Dias de trabalho: {dias}")

                    while len(este_medico["horarios"]) < 3:
                        if dia_semana(dia) in [dia[0] for dia in dias]:
                            horarios = cur.execute(
                                """
                                SELECT hora
                                FROM consulta
                                WHERE nif = %(nif)s AND data = %(dia)s;
                                """,
                                {"nif": medico.nif, "dia": dia},
                            ).fetchall()

                            for hora in times:
                                dia_str = dia.strftime("%Y-%m-%d")
                                data_hora = verifica_data(dia_str, hora)

                                if hora not in horarios and data_hora and not eh_passado(data_hora):
                                    este_medico["horarios"].append({"dia": dia_str, "hora": hora})

                                    if len(este_medico["horarios"]) == 3:
                                        break

                        dia += timedelta(days=1)
                    todos_medicos.append(este_medico)

                return jsonify(todos_medicos)
            except Exception as e:
                return jsonify({"erro": str(e)}), 400

#
# Rotas POST
#

@app.route('/a/<clinica>/registar', methods=['POST'])
def marcar_consulta(clinica):
    ssn = request.args.get('paciente')
    nif = request.args.get('medico')
    date = request.args.get('data')
    hora = request.args.get('hora')

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

    weekday = dia_semana(date_hora)

    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:     
                conn.transaction()

                cur.execute(
                    """
                    SELECT nif FROM paciente
                    WHERE ssn = %(ssn)s;
                    """,
                    {"ssn": ssn},
                )

                paciente = cur.fetchone()

                if not paciente:
                    return jsonify({"erro": "Paciente não encontrado"}), 404
                
                cur.execute(
                    """
                    SELECT * FROM medico
                    WHERE nif = %(nif)s;
                    """,
                    {"nif": nif},
                )

                medico = cur.fetchone()

                if not medico:
                    return jsonify({"erro": "Médico não encontrado"}), 404
                
                if paciente[0] == nif:
                    return jsonify({"erro": "Paciente e médico não podem ser a mesma pessoa"}), 400

                cur.execute(
                    """
                    SELECT * FROM clinica
                    WHERE nome = %(clinica)s;
                    """,
                    {"clinica": clinica},
                )

                clinica_ = cur.fetchone()

                if not clinica_:
                    return jsonify({"erro": "Clínica não encontrada"}), 404

                cur.execute(
                    """
                    SELECT * FROM trabalha
                    WHERE nif = %(nif)s AND nome = %(clinica)s AND dia_da_semana = %(weekday)s;
                    """,
                    {"nif": nif, "clinica": clinica, "weekday": weekday},
                )
                
                trabalha_dia = cur.fetchone()

                if not trabalha_dia:
                    return jsonify({"erro": f"O médico não trabalha na clinica {clinica} neste dia"}), 400
                
                cur.execute(
                    """
                    SELECT * FROM consulta
                    WHERE ssn = %(ssn)s AND data = %(date)s AND hora = %(hora)s;
                    """,
                    {"ssn": ssn, "date": date, "hora": hora},
                )
                
                paciente_verifica = cur.fetchone()

                if paciente_verifica:
                    return jsonify({"erro": "O paciente já tem uma consulta marcada para este dia e hora"}), 400
                
                cur.execute(
                    """
                    SELECT * FROM consulta
                    WHERE nif = %(nif)s AND data = %(date)s AND hora = %(hora)s;
                    """,
                    {"nif": nif, "date": date, "hora": hora},
                ).fetchone()

                medico_verifica = cur.fetchone()

                if medico_verifica:
                    return jsonify({"erro": "O médico já tem uma consulta marcada para este dia e hora"}), 400

                cur.execute(
                    """
                    INSERT INTO consulta (nif, ssn, data, hora, nome)
                    VALUES (%(nif)s, %(ssn)s, %(date)s, %(hora)s, %(clinica)s);
                    """,
                    {"nif": nif, "ssn": ssn, "date": date, "hora": hora, "clinica": clinica},
                )

                log.debug(f"Consulta marcada")

                conn.commit()
                return jsonify({"success": True, "msg": "Consulta marcada com sucesso"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})


@app.route('/a/<clinica>/cancelar', methods=['POST', 'DELETE'])
def cancelar_appointment(clinica):
    ssn = request.args.get('paciente')
    nif = request.args.get('medico')
    date = request.args.get('data')
    hora = request.args.get('hora')

    log.debug(f"{ssn} {nif} {date} {hora}")

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
                conn.transaction()

                cur.execute(
                    """
                    SELECT nif FROM paciente
                    WHERE ssn = %(ssn)s;
                    """,
                    {"ssn": ssn},
                )

                paciente = cur.fetchone()

                if not paciente:
                    return jsonify({"erro": "Paciente não encontrado"}), 404
                
                cur.execute(
                    """
                    SELECT * FROM medico
                    WHERE nif = %(nif)s;
                    """,
                    {"nif": nif},
                )

                medico = cur.fetchone()

                if not medico:
                    return jsonify({"erro": "Médico não encontrado"}), 404
                
                if paciente[0] == nif:
                    return jsonify({"erro": "Paciente e médico não podem ser a mesma pessoa"}), 400
                
                cur.execute(
                    """
                    SELECT * FROM clinica
                    WHERE nome = %(clinica)s;
                    """,
                    {"clinica": clinica},
                )

                clinica_ = cur.fetchone()

                if not clinica_:
                    return jsonify({"erro": "Clínica não encontrada"}), 404

                sql_query = """
                    SELECT * FROM consulta
                    WHERE nif = %(nif)s AND ssn = %(ssn)s AND data = %(date)s AND hora = %(hora)s AND nome = %(nome)s;
                """
                cur.execute(sql_query, {"nif": nif, "ssn": ssn, "date": date, "hora": hora, "nome": clinica})
                consulta = cur.fetchone()

                log.debug(f"{nif} {ssn} {date} {hora} {clinica}")
                

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

                conn.commit()
                return jsonify({"success": True, "msg": "Consulta cancelada com sucesso"})
            except Exception as e:
                return jsonify({"success": False, "erro": str(e)})

if __name__ == "__main__":
    app.run()