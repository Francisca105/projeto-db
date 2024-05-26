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
    for _ in range(10):
        print(nomes[_])

    # with open('../tables/consulta.csv','w') as csvfile:
        # headers = ['ssn','nif','nome','data','hora','codifo_sns']
        # writer = csv.DictWriter(csvfile,fieldnames=headers)
        # 
        # writer.writeheader()
        # for _ in range(n):
            # writer.writerow({headers[0]:ssns[_],headers[1]:nifs[_],headers[2]:nomes[_],headers[3]:datas[_],headers[4]:horas[_],headers[5]:codigos_sns[_]})
