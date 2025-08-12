class ValencesByVaccine:
    def __init__(self, repositories):
        self.valences_by_vaccine_id = {}
        for valence in repositories.valences.all():
            for vaccine_id in valence.vaccine_ids:
                self.valences_by_vaccine_id.setdefault(vaccine_id, []).append(valence)
    
    def call(self, vaccine):
        return self.valences_by_vaccine_id.get(vaccine.id, [])


class VaccinesByValence:
    def __init__(self, repositories):
        self.vaccines_by_valence = {}
        for vaccine in repositories.vaccines.all():
            for vaccine_id in vaccine.valence_ids:
                self.vaccines_by_valence.setdefault(vaccine_id, []).append(vaccine)
    
    def call(self, vaccine):
        return self.vaccines_by_valence.get(vaccine.id, [])

class VaccinesByDisease:
    def __init__(self, repositories):
        self.vaccines_by_disease_id = {}
        for valence in repositories.valences.all():
            for disease_id in valence.disease_ids:
                self.vaccines_by_disease_id.setdefault(disease_id, [])
                for vaccine_id in valence.vaccine_ids:
                    self.vaccines_by_disease_id[disease_id].append(repositories.vaccines.find(vaccine_id))

    def call(self, disease):
        return self.vaccines_by_disease_id.get(disease.id, [])

class ValencesByDisease:
    def __init__(self, repositories):
        self.valences_by_disease_id = {}
        for valence in repositories.valences.all():
            for disease_id in valence.disease_ids:
                self.valences_by_disease_id.setdefault(disease_id, []).append(valence)

    def call(self, disease):
        return self.valences_by_disease_id.get(disease.id, [])

class DiseasesByVaccine:
    def __init__(self, repositories):
        self.diseases_by_vaccine_id = {}
        for valence in repositories.valences.all():
            for vaccine_id in valence.vaccine_ids:
                for disease_id in valence.disease_ids:
                    self.diseases_by_vaccine_id.setdefault(vaccine_id, []).append(repositories.diseases.find(disease_id))

    def call(self, vaccine):
        return self.diseases_by_vaccine_id.get(vaccine.id, [])

class DiseasesByValence:
    def __init__(self, repositories):
        self.diseases_by_valence_id = {}
        for disease in repositories.diseases.all():
            for valence_id in disease.valence_ids:
                self.diseases_by_valence_id.setdefault(valence_id, []).append(disease)

    def call(self, valence):
        return self.diseases_by_valence_id.get(valence.id, [])
