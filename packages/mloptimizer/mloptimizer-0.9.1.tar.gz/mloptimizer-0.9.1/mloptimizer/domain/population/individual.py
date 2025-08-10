from mloptimizer.domain.hyperspace import HyperparameterSpace
from sklearn.svm import SVR
import random


class IndividualUtils:
    def __init__(self, hyperparam_space: HyperparameterSpace = None, estimator_class=None, mlopt_seed=None):
        self.hyperparam_space = hyperparam_space
        self.estimator_class = estimator_class
        self.mlopt_seed = mlopt_seed
        if self.mlopt_seed is not None:
            random.seed(self.mlopt_seed)

    def get_clf(self, individual):
        individual_dict = self.individual2dict(individual)
        if self.estimator_class is SVR:
            # SVR is a deterministic model, so it does not require a random seed
            clf = self.estimator_class(**individual_dict)
        else:
            clf = self.estimator_class(random_state=self.mlopt_seed, **individual_dict)
        return clf

    def individual2dict(self, individual):
        """
        Method to convert an individual to a dictionary of hyperparams

        Parameters
        ----------
        individual : individual
            individual to convert

        Returns
        -------
        individual_dict : dict
            dictionary of hyperparams
        """
        individual_dict = {}
        keys = list(self.hyperparam_space.evolvable_hyperparams.keys())
        for i in range(len(keys)):
            individual_dict[keys[i]] = self.hyperparam_space.evolvable_hyperparams[keys[i]].correct(individual[i])
        return {**individual_dict, **self.hyperparam_space.fixed_hyperparams}

    def init_individual(self, pcls):
        """
        Method to create an individual (from DeapOptimizer)
        """
        ps = [random.randint(self.hyperparam_space.evolvable_hyperparams[k].min_value,
                             self.hyperparam_space.evolvable_hyperparams[k].max_value)
              for k in self.hyperparam_space.evolvable_hyperparams.keys()]
        return pcls(ps)

class Individual:
    def __init__(self, genome, fitness=None):
        self.genome = genome
        self.fitness = fitness

    def set_fitness(self, fitness):
        self.fitness = fitness

    def __repr__(self):
        return f"Individual(genome={self.genome}, fitness={self.fitness})"