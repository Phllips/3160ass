#!/usr/bin/env python
# coding: utf-8

# ### COMP 3160 Assignment 2


import random
import copy


def payoff_to_ind1(individual1, individual2, individual3, game):
    
    payoff = 0
    x1 = individual1
    x2 = individual2
    x3 = individual3
    
    if x1 == "1": ##means they selected P
        if x2 != x3: 
            return 3
        elif x2 == "1":
            return 1
        else: 
            return 5
    else:
        if x2 != x3: 
            return 2
        elif x2 == "1":
            return 0
        else: 
            return 4
            



##strategies are respresented by there 70 responses to the 70 possible histories. 
##we can store this as a hex numberto save space
def move_by_ind1(individual1, individual2, individual3, round):
    
    move = 0 #return var

    
    #strat bits
    x1 = individual1[2:]
    x2 = individual2[2:]
    x3 = individual3[2:]

    ##get history bits
    h1 = individual1[:2]
    h2 = individual2[:2]
    h3 = individual3[:2]

    ##base cases
    if round < 2: 
        if round == 0: 
            return x1[0] ##first move
        else: 
            if x1[6] == 1: 
                if x2 != x3:
                    return x1[5]
                elif x2 == 1:
                    return x1[6]
                else:
                    return x1[4]
            else: 
                if x2 != x3:
                    return x1[2]
                elif x2 == 1:
                    return x1[3]
                else:
                    return x1[1]
    else: 
        
        history = h1 + h2 + h3
        his = ''.join(str(i) for i in history)

        index = (int(his, 2)) + 6 ##the pregame moves are the first 6 bits
        ## print(index)
        ##we need to get the bit at index whatever is above

        string = str(x1)
        move = x1[index]
    
    return move ##individual1’s move


#updates the actors memory bits
def process_move(individual, move, memory_depth):
    ind1 = str(individual)
    i = 0
    for i in range(memory_depth -1):
        #print(i)
        #print(individual)
        individual[i+1] = individual[i]
        individual[i] = move
        #print(individual)
        ind1 = str(individual) + str(ind1[memory_depth:])
    return 1 


#this function allows me to specify memory depth and 
# n_rounds aswell as get the 2 individuals my actor goes against
#then i pass into the eval_function that gets the actual score
def eval_init(individual): 
    score = 0
    mem_depth = 2
    #n_rounds = 10
    one = random.randint(0, 98)
    two = random.randint(0, 98)
    #print("one:", population[one])
    score = eval_function(individual, population[one], population[two], mem_depth, n_rounds)
    return score,



def eval_function(individual1, individual2, individual3, m_depth, n_rounds):
    score = 0
    i = 0
    ind1 = copy.copy(individual1)
    ind2 = copy.copy(individual2)
    ind3 = copy.copy(individual3)
    
    for i in range(n_rounds): 
        p1 = str(move_by_ind1(ind1,ind2,ind3, i))
        p2 = str(move_by_ind1(ind2,ind3,ind1, i))
        p3 = str(move_by_ind1(ind3,ind1,ind2, i))
        score =  score + payoff_to_ind1(p1,p2,p3, 0)
        process_move(ind1, p1, m_depth)
        process_move(ind2, p2, m_depth)
        process_move(ind3, p3, m_depth)
        
    return score ##score to individual1

from deap import base
from deap import creator
from deap import tools


def create_toolbox(num_bits):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    # Initialize the toolbox
    toolbox = base.Toolbox()

    # Generate attributes 
    toolbox.register("attr_bool", random.randint, 0, 1)

    # Initialize structures
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, num_bits)

    # Define the population to be a list of individuals
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Register the evaluation operator 
    toolbox.register("evaluate", eval_init)

    # Register the crossover operator
    toolbox.register("mate", tools.cxTwoPoint)

    # Register a mutation operator
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)

    # Operator for selecting individuals for breeding
    toolbox.register("select", tools.selTournament, tournsize=3)
    
    return toolbox


if __name__ == "__main__":
    # Define the number of bits
    n_rounds = 10
    num_bits = 73

    # Create a toolbox using the above parameter
    toolbox = create_toolbox(num_bits)

    # Seed the random number generator
    random.seed(42)

    # Create an initial population of 99 individuals
    population = toolbox.population(n=99)

    # Define probabilities of crossing and mutating
    probab_crossing, probab_mutating  = 0.5, 0.05

    # Define the number of generations
    num_generations = 1000
    
    print('\nStarting the evolution process')
    fitnesses = list(map(toolbox.evaluate, population))
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit
        
    print('\nEvaluated', len(population), 'individuals')
    for g in range(num_generations):
            print("\n===== Generation", g)

            # Select the next generation individuals
            offspring = toolbox.select(population, len(population))

            # Clone the selected individuals
            offspring = list(map(toolbox.clone, offspring))

            # Apply crossover and mutation on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                # Cross two individuals
                if random.random() < probab_crossing:
                    toolbox.mate(child1, child2)
                    # "Forget" the fitness values of the children
                    del child1.fitness.values
                    del child2.fitness.values

            # Apply mutation
            for mutant in offspring:
                # Mutate an individual
                if random.random() < probab_mutating:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            

            print('Evaluated', len(invalid_ind), 'individuals')

            # The population is entirely replaced by the offspring
            population[:] = offspring

            # Gather all the fitnesses in one list and print the stats
            fits = [ind.fitness.values[0] for ind in population]

            length = len(population)
            mean = sum(fits) / length
            sum2 = sum(x*x for x in fits)
            std = abs(sum2 / length - mean**2)**0.5

            print("  Min %s" % min(fits))
            print("  Max %s" % max(fits))
            print("  Avg %s" % mean)
            print("  Std %s" % std)

            print("\n==== End of evolution")

    best_ind = tools.selBest(population, 1)[0]
    print('\nBest individual:\n', best_ind)







