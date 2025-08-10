import random
import os
import joblib
import numpy as np
import pandas as pd
from deap import creator, base, tools, algorithms
from deap.algorithms import eaSimple, varAnd

from mloptimizer.domain.hyperspace import HyperparameterSpace
from matplotlib import pyplot as plt
from mloptimizer.application.reporting.plots import plotly_search_space, plotly_logbook
from mloptimizer.infrastructure.tracking import Tracker
from mloptimizer.domain.evaluation import Evaluator
from mloptimizer.domain.population import IndividualUtils


class GeneticAlgorithm:
    def __init__(self, hyperparam_space: HyperparameterSpace = None, tracker: Tracker = None,
                 seed=None, evaluator: Evaluator=None, use_parallel=False, maximize=True):
        """
        Class to run the genetic algorithm (combined functionality from DeapOptimizer and GeneticAlgorithmRunner)

        Parameters
        ----------
        hyperparam_space : HyperparameterSpace
            Hyperparameter space for optimization
        tracker : Tracker
            Tracker for logging and checkpointing
        seed : int
            Seed for random operations
        evaluator : Evaluator
            Function to evaluate an individual
        use_parallel : bool
            Flag for parallel processing
        maximize : bool
            Whether to maximize or minimize the objective function
        """
        self.hyperparam_space = hyperparam_space
        self.tracker = tracker
        self.evaluator = evaluator
        self.use_parallel = use_parallel
        self.maximize = maximize
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        self.populations = []

        # Toolbox setup (from DeapOptimizer)
        self.toolbox = base.Toolbox()
        self.eval_dict = {}
        self.logbook = None
        self.stats = None
        self.setup()

        self.generations_run_ = 0
        self.stopped_early_ = False

    def setup(self):
        """
        Set up DEAP's toolbox and statistics (from DeapOptimizer)
        """
        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("avg", np.mean)
        self.stats.register("min", np.min)
        self.stats.register("max", np.max)

        if hasattr(creator, "FitnessMax"):
            del creator.FitnessMax
        if hasattr(creator, "FitnessMin"):
            del creator.FitnessMin
        if hasattr(creator, "Individual"):
            del creator.Individual

        if self.maximize:
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
            creator.create("Individual", list, fitness=creator.FitnessMax)
        else:
            creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
            creator.create("Individual", list, fitness=creator.FitnessMin)

        if self.use_parallel:
            try:
                import multiprocessing
                pool = multiprocessing.Pool()
                self.toolbox.register("map", pool.map)
            except ImportError:
                print("Multiprocessing not available.")

        self.toolbox.register("individual",
                              IndividualUtils(hyperparam_space=self.hyperparam_space,
                                              mlopt_seed=self.seed).init_individual,creator.Individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.evaluator.evaluate_individual)

    def simple_run(self, population_size: int, n_generations: int, cxpb: float = 0.5, mutation_prob: float = 0.5,
                   n_elites: int = 10, tournsize: int = 3, indpb: float = 0.05):
        """
        Run the genetic algorithm using DEAP's eaSimple method (from GeneticAlgorithmRunner)
        """
        hof, pop = self._pre_run(indpb=indpb, n_elites=n_elites, population_size=population_size, tournsize=tournsize)
        population, logbook = eaSimple(population=pop, toolbox=self.toolbox, cxpb=cxpb, mutpb=mutation_prob,
                                       ngen=n_generations, stats=self.stats, halloffame=hof, verbose=True)
        return population, logbook, hof

    def _pre_run(self, indpb: float = 0.5, n_elites: int = 10, population_size: int = 10, tournsize: int = 4):
        """
        Initialize the population and hall of fame (from GeneticAlgorithmRunner)
        """
        pop = self.toolbox.population(n=population_size)
        hof = tools.HallOfFame(n_elites)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutUniformInt,
                              low=[x.min_value for x in self.hyperparam_space.evolvable_hyperparams.values()],
                              up=[x.max_value for x in self.hyperparam_space.evolvable_hyperparams.values()],
                              indpb=indpb)
        self.toolbox.register("select", tools.selTournament, tournsize=tournsize)
        hist = tools.History()
        self.toolbox.decorate("mate", hist.decorator)
        self.toolbox.decorate("mutate", hist.decorator)
        hist.update(pop)
        return hof, pop

    def _log_and_visualize_results(self, logbook):
        """
        Log and visualize the results of the genetic algorithm.
        """
        hyperparam_names = list(self.hyperparam_space.evolvable_hyperparams.keys())
        hyperparam_names.append("fitness")
        population_df = self.population_2_df()
        df = population_df[hyperparam_names]
        g = plotly_search_space(df)
        g.write_html(os.path.join(self.tracker.graphics_path, "search_space.html"),
                     full_html=False, include_plotlyjs='cdn')
        plt.close()

        g2 = plotly_logbook(logbook, population_df)
        g2.write_html(os.path.join(self.tracker.graphics_path, "logbook.html"),
                     full_html=False, include_plotlyjs='cdn')
        plt.close()

    def custom_run(self, population_size: int, n_generations: int, cxpb: float = 0.5, mutation_prob: float = 0.5,
                   n_elites: int = 10, tournsize: int = 3, indpb: float = 0.05, checkpoint: str = None,
                   early_stopping: bool = False, patience: int = 10, min_delta: float = 0.01):
        """
        Run the genetic algorithm with tracking of each generation (from GeneticAlgorithmRunner)
        """
        hof, pop = self._pre_run(indpb=indpb, n_elites=n_elites, population_size=population_size, tournsize=tournsize)
        population, logbook, hof = self.custom_ea_simple(population=pop, toolbox=self.toolbox, cxpb=cxpb,
                                                         mutpb=mutation_prob, ngen=n_generations, halloffame=hof,
                                                         checkpoint_path=self.tracker.opt_run_checkpoint_path,
                                                         stats=self.stats, early_stopping=early_stopping,
                                                         patience=patience, min_delta=min_delta)
        self.logbook = logbook
        self._log_and_visualize_results(logbook)

        return population, logbook, hof

    def custom_ea_simple(self, population: list, toolbox: base.Toolbox, cxpb: float = 0.5, mutpb: float = 0.5,
                         start_gen: int = 0, ngen: int = 4, checkpoint_path: str = None, stats: tools.Statistics = None,
                         halloffame: tools.HallOfFame = None, verbose: bool = True,
                         early_stopping: bool = False, patience: int = 10, min_delta: float = 0.01):
        """
        Custom evolution algorithm with tracking and checkpointing (from GeneticAlgorithmRunner)
        """
        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

        # Early stopping variables
        best_fitness = None
        no_improve = 0

        for gen in range(start_gen, ngen + 1):
            self.tracker.start_progress_file(gen)
            population = varAnd(population, toolbox, cxpb, mutpb)

            invalid_ind = [ind for ind in population if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
            c = 1
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
                ind_formatted = IndividualUtils(hyperparam_space=self.hyperparam_space,
                                                mlopt_seed=self.seed).individual2dict(ind)
                self.tracker.append_progress_file(gen, ngen, c, len(invalid_ind), ind_formatted, fit)
                c += 1

            halloffame.update(population)
            record = stats.compile(population) if stats else {}
            logbook.record(gen=gen, nevals=len(invalid_ind), **record)

            population = toolbox.select(population, len(population))
            self.populations.append([[ind, ind.fitness] for ind in population])

            if checkpoint_path:
                cp = dict(population=population, generation=gen, halloffame=halloffame, logbook=logbook,
                          rndstate=self.seed)
                cp_file = os.path.join(checkpoint_path, "cp_gen_{}.pkl".format(gen))
                joblib.dump(cp, cp_file)
            self.tracker.write_population_file(self.population_2_df())
            self.tracker.write_logbook_file(logbook)
            self.tracker.log_clfs([], gen, [])

            # Early stopping logic
            gen_best_fitness = max([ind.fitness.values[0] for ind in population])

            if best_fitness is None or gen_best_fitness > best_fitness + min_delta:
                best_fitness = gen_best_fitness
                no_improve = 0
            else:
                no_improve += 1

            if early_stopping and no_improve >= patience:
                self.generations_run_ = gen
                self.tracker.info(f"Early stopping at generation {gen} with best fitness: {best_fitness}")
                self.stopped_early_ = True
                break

        if not self.stopped_early_:
            self.generations_run_ = ngen

        return population, logbook, halloffame

    def population_2_df(self):
        """
        Convert the population to a pandas dataframe (from GeneticAlgorithmRunner)
        """
        data = []
        n = 0
        for p in self.populations:
            for i in p:
                i_hyperparams = IndividualUtils(hyperparam_space=self.hyperparam_space,
                                                mlopt_seed=self.seed).individual2dict(i[0])
                i_hyperparams['fitness'] = i[1].values[0]
                i_hyperparams['population'] = n
                data.append(i_hyperparams)
            n += 1

        return pd.DataFrame(data)
