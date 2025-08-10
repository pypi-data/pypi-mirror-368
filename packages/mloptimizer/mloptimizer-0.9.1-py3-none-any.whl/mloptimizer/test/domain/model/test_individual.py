from mloptimizer.domain.population import Individual

def test_create_individual_with_genome():
    genome = [0, 1, 1, 0]
    individual = Individual(genome)
    assert individual.genome == genome
    assert individual.fitness is None

def test_create_individual_empty_genome():
    genome = []
    individual = Individual(genome)
    assert individual.genome == genome
    assert individual.fitness is None

def test_set_fitness_positive():
    individual = Individual([1, 1, 0, 0])
    individual.set_fitness(10.0)
    assert individual.fitness == 10.0

def test_set_fitness_zero():
    individual = Individual([1, 1, 0, 0])
    individual.set_fitness(0.0)
    assert individual.fitness == 0.0

def test_set_fitness_negative():
    individual = Individual([1, 1, 0, 0])
    individual.set_fitness(-5.0)
    assert individual.fitness == -5.0

def test_update_fitness():
    individual = Individual([1, 1, 0, 0])
    individual.set_fitness(10.0)
    assert individual.fitness == 10.0
    individual.set_fitness(20.0)
    assert individual.fitness == 20.0