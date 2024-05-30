import csv
from datetime import date
import random

if __name__ == '__main__':
    random.seed(1)

    consultas = []
    with open('../tables/consulta.csv','r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            consultas.append(row)

    sintomas = ['dor de cabeça','febre','tosse','dor no peito','falta de ar','náusea','vômito','diarreia','constipação','dor abdominal','fadiga','fraqueza','tontura','palpitações','perda de apetite','perda de peso','ganho de peso','dor nas articulações','dor muscular','calafrios','sudorese','erupção cutânea','prurido','inchaço','hemorragia nasal','visão turva','zumbido nos ouvidos','dificuldade para urinar','dor ao urinar','urina escura','icterícia','desmaio','confusão mental','depressão','ansiedade','insônia','rouquidão','dificuldade para engolir','perda de cabelo','manchas na pele','tremores','dormência','formigamento','refluxo ácido','gases excessivos','dores de crescimento','cãibras','fotossensibilidade','tosse com sangue','palidez']

    observacoes_metricas = ['temperatura corporal','pressão arterial','frequência cardíaca','frequência respiratória','quantidade de oxigénio no sangue','glicemia','colestrol','índice de massa corporal','peso','altura','volume de urina produzido em 24 horas','quantidade de hemoglobina no sangue','nível de creatinina no sangue','taxa de filtração glomerular','contagem de leucócitos','pressão intracraniana','volume sistólico','espessura da camada de gordura corporal','volume diastólico final','espessura da pele']
    
    with open('../tables/observacao.csv','w') as csvfile:
        headers = ['id','parametro','valor']
        writer = csv.DictWriter(csvfile,fieldnames=headers)

        writer.writeheader()

        i = 1
        for consulta in consultas:
            if date.fromisoformat(consulta['data']) < date(2024,6,1):
                sintomas_temp = [_ for _ in sintomas]
                for _ in range(1,random.randint(1,5)+1):
                    writer.writerow({headers[0]:i,headers[1]:sintomas_temp.pop(random.randint(0,len(sintomas_temp)-1)),headers[2]:''})
                
                observacoes_metricas_temp = [_ for _ in observacoes_metricas]
                for _ in range(0,random.randint(1,3)):
                    writer.writerow({headers[0]:i,headers[1]:observacoes_metricas_temp.pop(random.randint(0,len(observacoes_metricas_temp)-1)),headers[2]:random.uniform(0.1,200)})
                i += 1
