import csv
from faker import Faker
import random
import datetime

if __name__ == '__main__':
    fake = Faker('pt_PT')

    fake.seed_instance(1)
    random.seed(1)

    clinicas = ['JCS Almirante Reis','JCS Brandoa','JCS Venda Nova','JCS Dafundo','JCS Queijas']

    pacientes = [fake.unique.numerify(text='%##########') for _ in range(5000)]

    fake.seed_instance(1)
    random.seed(1)
    medicos = [str(random.randint(1,3))+fake.unique.numerify(text='########') for _ in range(60)]

    trabalha = []
    with open('../tables/trabalha.csv','r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            trabalha.append(row)

    clinicas_medicos = {}
    for _ in trabalha:
        if _['nome'] not in clinicas_medicos:
            clinicas_medicos.update({_['nome']:[[] for __ in range(7)]})
        clinicas_medicos[_['nome']][int(_['dia_da_semana'])].append(_['nif'])

    horas = [datetime.time(8),datetime.time(8,30),datetime.time(9),datetime.time(9,30),datetime.time(10),datetime.time(10,30),datetime.time(11),datetime.time(11,30),datetime.time(12),datetime.time(12,30),datetime.time(14),datetime.time(14,30),datetime.time(15),datetime.time(15,30),datetime.time(16),datetime.time(16,30),datetime.time(17),datetime.time(17,30),datetime.time(18),datetime.time(18,30)]

    random.seed(2)
    with open('../tables/consulta.csv','w') as csvfile:
        headers = ['ssn','nif','nome','data','hora','codigo_sns']
        writer = csv.DictWriter(csvfile,fieldnames=headers)

        writer.writeheader()

        dia = datetime.date(2023,1,1)
        while dia < datetime.date(2025,1,1):
            dia_semana = (dia.weekday()+1)%7
            pacientes_dia = set()

            for clinica in clinicas_medicos:
                consultas = 0
                horas_temp = {}

                for medico in clinicas_medicos[clinica][dia_semana]:
                    horas_temp.update({medico:[_ for _ in horas]})

                for medico in clinicas_medicos[clinica][dia_semana]:
                    paciente = random.choice(pacientes)
                    while paciente in pacientes_dia:
                        paciente = random.choice(pacientes)
                    pacientes_dia.add(paciente)

                    if dia < datetime.date(2024,6,1):
                        if random.random() <= 0.8:
                            writer.writerow({headers[0]:paciente,headers[1]:medico,headers[2]:clinica,headers[3]:dia,headers[4]:horas_temp[medico].pop(random.randint(0,len(horas_temp)-1)),headers[5]:fake.unique.numerify(text='############')})
                        else:
                            writer.writerow({headers[0]:paciente,headers[1]:medico,headers[2]:clinica,headers[3]:dia,headers[4]:horas_temp[medico].pop(random.randint(0,len(horas_temp)-1)),headers[5]:''})
                    else:
                        writer.writerow({headers[0]:paciente,headers[1]:medico,headers[2]:clinica,headers[3]:dia,headers[4]:horas_temp[medico].pop(random.randint(0,len(horas_temp)-1)),headers[5]:''})

                    paciente = random.choice(pacientes)
                    while paciente in pacientes_dia:
                        paciente = random.choice(pacientes)
                    pacientes_dia.add(paciente)
                    
                    if dia < datetime.date(2024,6,1):
                        if random.random() <= 0.8:
                            writer.writerow({headers[0]:paciente,headers[1]:medico,headers[2]:clinica,headers[3]:dia,headers[4]:horas_temp[medico].pop(random.randint(0,len(horas_temp)-1)),headers[5]:fake.unique.numerify(text='############')})
                        else:
                            writer.writerow({headers[0]:paciente,headers[1]:medico,headers[2]:clinica,headers[3]:dia,headers[4]:horas_temp[medico].pop(random.randint(0,len(horas_temp)-1)),headers[5]:''})
                    else:
                        writer.writerow({headers[0]:paciente,headers[1]:medico,headers[2]:clinica,headers[3]:dia,headers[4]:horas_temp[medico].pop(random.randint(0,len(horas_temp)-1)),headers[5]:''})
                    
                    consultas += 2
                while consultas < 20:
                    medico = random.choice(clinicas_medicos[clinica][dia_semana])
                    
                    paciente = random.choice(pacientes)
                    while paciente in pacientes_dia:
                        paciente = random.choice(pacientes)                    
                    pacientes_dia.add(paciente)

                    if dia < datetime.date(2024,6,1):
                        if random.random() <= 0.8:
                            writer.writerow({headers[0]:paciente,headers[1]:medico,headers[2]:clinica,headers[3]:dia,headers[4]:horas_temp[medico].pop(random.randint(0,len(horas_temp)-1)),headers[5]:fake.unique.numerify(text='############')})
                        else:
                            writer.writerow({headers[0]:paciente,headers[1]:medico,headers[2]:clinica,headers[3]:dia,headers[4]:horas_temp[medico].pop(random.randint(0,len(horas_temp)-1)),headers[5]:''})
                    else:
                        writer.writerow({headers[0]:paciente,headers[1]:medico,headers[2]:clinica,headers[3]:dia,headers[4]:horas_temp[medico].pop(random.randint(0,len(horas_temp)-1)),headers[5]:''})
                    
                    consultas += 1
            dia += datetime.timedelta(1)