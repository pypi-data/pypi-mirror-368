class Population:
    def __init__(self):
        self.individuals = []

    def add_individual(self, individual):
        self.individuals.append(individual)

    def get_individuals(self):
        return self.individuals

    def __repr__(self):
        return f"Population(size={len(self.individuals)})"