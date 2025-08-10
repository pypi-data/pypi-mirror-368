from mloptimizer.domain.population import Individual, Population

def test_create_population_empty():
    population = Population()
    assert len(population.get_individuals()) == 0

def test_add_single_individual_to_population():
    population = Population()
    individual = Individual([1, 0, 1, 0])
    population.add_individual(individual)
    assert len(population.get_individuals()) == 1
    assert population.get_individuals()[0].genome == [1, 0, 1, 0]

def test_add_multiple_individuals_to_population():
    population = Population()
    individuals = [
        Individual([1, 0, 1, 0]),
        Individual([0, 1, 0, 1]),
        Individual([1, 1, 1, 1]),
    ]
    for ind in individuals:
        population.add_individual(ind)
    assert len(population.get_individuals()) == 3

def test_population_with_varying_fitness():
    population = Population()
    individuals = [
        Individual([1, 0, 1, 0], fitness=10.0),
        Individual([0, 1, 0, 1], fitness=15.0),
        Individual([1, 1, 1, 1], fitness=20.0),
    ]
    for ind in individuals:
        population.add_individual(ind)
    assert len(population.get_individuals()) == 3
    assert population.get_individuals()[0].fitness == 10.0
    assert population.get_individuals()[1].fitness == 15.0
    assert population.get_individuals()[2].fitness == 20.0