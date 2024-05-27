import csv
from faker import Faker
import random

if __name__ == '__main__':
    fake = Faker('pt_PT')

    fake.seed_instance(1)
    random.seed(1)

    n = 28

    nifs = [str(random.randint(1,3))+fake.unique.numerify(text='########') for _ in range(n)]
    nomes = [fake.unique.name() for _ in range(n)]
    telefones = [random.choice(['91','93','96'])+fake.unique.numerify(text='#######') for _ in range(n)]
    moradas = [fake.unique.address().replace(",","").replace("\n",", ").replace("Av ","Avenida ").replace("R.","Rua").replace("Prof.","Professor").replace("S/N",str(random.randint(1, 232))) for _ in range(n)]
    
    with open('../tables/enfermeiro.csv','w') as csvfile:
        headers = ['nif','nome','telefone','morada', 'nome_clinica']
        writer = csv.DictWriter(csvfile,fieldnames=headers)
        
        writer.writeheader()
        for _ in range(n):
            writer.writerow({headers[0]:nifs[_],headers[1]:nomes[_],headers[2]:telefones[_],headers[3]:moradas[_]})
