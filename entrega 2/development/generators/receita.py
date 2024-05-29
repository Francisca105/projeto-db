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

    medicamentos = []
    with open('../auxiliar/medicamentos.txt','r') as file:
        line = file.readline().strip()
        while line != '':
            medicamentos.append(line)
            line = file.readline().strip()

    with open('../tables/receita.csv','w') as csvfile:
        headers = ['codigo_sns','medicamento','quantidade']
        writer = csv.DictWriter(csvfile,fieldnames=headers)

        writer.writeheader()
        
        for consulta in consultas:
            if date.fromisoformat(consulta['data']) < date(2024,6,3) and random.random() <= 0.8:
                medicamentos_temp = [_ for _ in medicamentos]
                for _ in range(1,random.randint(1,6)+1):
                    writer.writerow({headers[0]:consulta['codigo_sns'],headers[1]:medicamentos_temp.pop(random.randint(0,len(medicamentos_temp)-1)),headers[2]:random.randint(1,3)})
