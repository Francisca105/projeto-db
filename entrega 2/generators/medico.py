import csv
from faker import Faker
import random

def nif():
    nif = str(random.randint(1,3))
    for _ in range(8):
        nif += str(random.randint(0,9))
    return nif

def telefone():
    telefone = random.choice(['91','93','96'])
    for _ in range(7):
        telefone += str(random.randint(0,9))
    return telefone

if __name__ == '__main__':
    fake = Faker('pt_PT')

    fake.seed_instance(1)
    random.seed(1)

    n = 60

    nifs = [nif() for _ in range(n)]
    nomes = [fake.unique.name() for _ in range(n)]
    telefones = [telefone() for _ in range(n)]
    moradas = [fake.unique.address().replace(",","").replace("\n",", ").replace("Av ","Avenida ").replace("R.","Rua").replace("Prof.","Professor").replace("S/N",str(random.randint(1,232))) for _ in range(n)]
    especialidades = ['ortopedia','cardiologia','pediatria','psiquiatria','cirurgia geral']

    with open('../tables/medico.csv','w') as csvfile:
        headers = ['nif','nome','telefone','morada','especialidade']
        writer = csv.DictWriter(csvfile,fieldnames=headers)
        
        writer.writeheader()
        for _ in range(20):
            writer.writerow({headers[0]:nifs[_],headers[1]:nomes[_],headers[2]:telefones[_],headers[3]:moradas[_],headers[4]:'clínica geral'})
        for _ in range(20,60):
            writer.writerow({headers[0]:nifs[_],headers[1]:nomes[_],headers[2]:telefones[_],headers[3]:moradas[_],headers[4]:str(random.choice(especialidades))})
