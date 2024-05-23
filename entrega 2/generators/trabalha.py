import csv
from faker import Faker
import random

def nif():
    nif = str(random.randint(1,3))
    for _ in range(8):
        nif += str(random.randint(0,9))
    return nif

def medico_clinica_dia(i, nifs, medico_nomes, headers):
    clinicas_restantes = len(medico_nomes[i])
    dias = [_+1 for _ in range(7)]
    dias_restantes = 7
    nif_nome_dia = []

    for _ in range(clinicas_restantes):
        n = random.randint(1,dias_restantes-clinicas_restantes+1)
        b = random.sample(dias,n)

        dias = list(filter(lambda x: x in dias and x not in b, dias))

        dias_restantes -= n
        clinicas_restantes -= 1

        nif_nome_dia += [{headers[0]:nifs[i],headers[1]:medico_nomes[i][_],headers[2]:e} for e in b]

    return nif_nome_dia

if __name__ == '__main__':
    fake = Faker('pt_PT')

    fake.seed_instance(1)
    random.seed(1)

    n = 60

    nifs = [nif() for _ in range(n)]
    nomes = ['JCS Almirante Reis','JCS Brandoa','JCS Venda Nova','JCS Dafundo','JCS Queijas']
    medico_nomes = [random.sample(nomes,random.randint(2,5)) for _ in range(n)]
    
    random.seed(11) # Hardcoded para haver pelo menos 8 médicos em cada clínica todos os dias
    with open('../tables/trabalha.csv','w') as csvfile:
        headers = ['nif','nome','dia_da_semana']
        writer = csv.DictWriter(csvfile,fieldnames=headers)

        writer.writeheader()
        for _ in range(n):
            valores_medico = medico_clinica_dia(_,nifs,medico_nomes,headers)  
            for valor in valores_medico:
                writer.writerow(valor)
