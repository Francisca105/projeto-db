import csv
from faker import Faker
import random

if __name__ == '__main__':
    fake = Faker('pt_PT')

    fake.seed_instance(1)
    random.seed(1)

    n = 5000

    ssns = [fake.unique.numerify(text='%##########') for _ in range(n)]
    nifs = [str(random.randint(1,3))+fake.unique.numerify(text='########') for _ in range(n)]
    nomes = [fake.name() for _ in range(n)]
    telefones = [random.choice(['91','93','96'])+fake.unique.numerify(text='#######') for _ in range(n)]
    moradas = [fake.address().replace(",","").replace("\n",", ").replace("Av ","Avenida ").replace("R.","Rua").replace("Prof.","Professor").replace("S/N",str(random.randint(1, 232))) for _ in range(n)]
    datas = [fake.passport_dob() for _ in range(n)]

    with open('../tables/paciente.csv','w') as csvfile:
        headers = ['ssn','nif','nome','telefone','morada','data_nasc']
        writer = csv.DictWriter(csvfile,fieldnames=headers)
        
        writer.writeheader()
        for _ in range(n):
            writer.writerow({headers[0]:ssns[_],headers[1]:nifs[_],headers[2]:nomes[_],headers[3]:telefones[_],headers[4]:moradas[_],headers[5]:datas[_]})
