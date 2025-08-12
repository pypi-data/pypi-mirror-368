from .protobuf.NuvaDatabase_pb2 import NuvaDatabase
from .queries import ValencesByVaccine, VaccinesByValence, VaccinesByDisease, ValencesByDisease, DiseasesByVaccine, DiseasesByValence
import requests
import json

class Repository:
    def __init__(self, data):
        self.data = data
        self.indexTable = {}

        for x in data:
            self.indexTable[x.id] = x
    
    def find(self, id):
        if id in self.indexTable:
            return self.indexTable[id]
        return None

    def all(self):
        return self.data

class NuvaRepositories:
    def __init__(self, db):
        self.vaccines = Repository(db.vaccines)
        self.valences = Repository(db.valences)
        self.diseases = Repository(db.diseases)

class NuvaQueries:
    def __init__(self, repositories):
        self.valences_by_vaccine = ValencesByVaccine(repositories)
        self.vaccine_by_valences = VaccinesByValence(repositories)
        self.vaccines_by_disease = VaccinesByDisease(repositories)
        self.valences_by_disease = ValencesByDisease(repositories)
        self.diseases_by_vaccine = DiseasesByVaccine(repositories)
        self.diseases_by_valence = DiseasesByValence(repositories)

class Nuva:
    def __init__(self, db):
        self.db = db
        self.repositories = NuvaRepositories(db)
        self.queries = NuvaQueries(self.repositories)

    @staticmethod
    def load(lang = 'en'):
        manifest = requests.get('https://cdn.nuva.fr/versions/last.json').json()
        nuva = requests.get('https://cdn.nuva.fr/proto/%s_%s.db' % (manifest['dump_hash'], lang))
        db = NuvaDatabase()
        db.ParseFromString(nuva.content)
        return Nuva(db)

    @staticmethod
    def load_from_file(path):
        db = NuvaDatabase()
        with open(path, 'rb') as f:
            db.ParseFromString(f.read())
        return Nuva(db)
