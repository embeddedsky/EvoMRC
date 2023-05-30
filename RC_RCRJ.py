import numpy as np
from files import *
import random
import copy
import sys
from RCRJ_Genome import *
class RC_RCRJ:
    def __init__(self,Is_Adapt):

        self.population_size=40
        self.population=[]

        self.species=[]

        self.init_reservoir_num=10
        self.max_reservoir_num = 30

        self.tournament_size=3
        self.p_complexity=0.5

        self.Is_Adapt=Is_Adapt




    def initial_population(self):
        self.population.clear()
        for i in range(0,self.population_size):
            gene=RCRJ_Genome(self.init_reservoir_num)
            gene.cal_fitness()
            print("The",i,"-th individual's fitness",gene.fitness)
            self.population.append(gene)


    def evolve(self,K):
        self.initial_population()
        with open('output/fitness_record','w+') as f:
            for k in range(0,K):
                self.evolve_no_specia()
                print("The",k,"-th optimal：",self.population[0].fitness)
                f.writelines(str(self.population[0].fitness))
                f.writelines('\n')
                np.save("output/w1",self.population[0].w1)
                np.save("output/w2", self.population[0].w2)
                np.save("output/w_out", self.population[0].w_out)
                np.save("output/w_bool", self.population[0].w_bool)
                f.flush()
                self.population[0].change_to_cir()
        f.close()
        self.population[0].change_to_cir()



    def evolve_no_specia(self):
        self.population.sort(key=lambda x: x.fitness, reverse=True)

        mutate_rate_range=[0.2,0.8]

        for p in range(1,self.population_size):
            mutate_rate=mutate_rate_range[0]+(mutate_rate_range[1]-mutate_rate_range[0])*p/self.population_size

            if random.random()>mutate_rate:
                parent1,parent2=self.__tournament_selection()
                temp_pop = copy.deepcopy(parent1)
                if parent1.reservoir_num!=parent2.reservoir_num:
                    if random.random()<self.p_complexity:
                        if parent1.reservoir_num>parent2.reservoir_num:
                            temp_pop=copy.deepcopy(parent1)
                        else:
                            temp_pop=copy.deepcopy(parent2)
                    else:
                        if parent1.fitness>parent2.fitness:
                            temp_pop=copy.deepcopy(parent1)
                        else:
                            temp_pop=copy.deepcopy(parent2)
                for i in range(0,temp_pop.reservoir_num):
                    if i < min(parent1.reservoir_num, parent2.reservoir_num):
                        for j in range(0,temp_pop.reservoir_num):
                            if j<min(parent1.reservoir_num, parent2.reservoir_num):
                                if parent1.w_bool[i][j]!=0 and parent2.w_bool[i][j]!=0 and random.random()<0.5:
                                    temp_pop.w1[i][j]=(parent1.w1[i][j]+parent2.w1[i][j])/2
                                    temp_pop.w2[i][j] = (parent1.w2[i][j] + parent2.w2[i][j]) / 2
                                elif parent1.w_bool[i][j]!=0 and parent2.w_bool[i][j]!=0 and random.random()>=0.5 and random.random()<0.75:
                                    temp_pop.w1[i][j] = parent1.w1[i][j]
                                    temp_pop.w2[i][j] = parent1.w2[i][j]
                                elif parent1.w_bool[i][j]!=0 and parent2.w_bool[i][j]!=0 and random.random()>=0.75 and random.random()<1.0:
                                    temp_pop.w1[i][j] = parent2.w1[i][j]
                                    temp_pop.w2[i][j] = parent2.w2[i][j]
                                elif parent1.w_bool[i][j]==0 and parent2.w_bool[i][j]!=0:
                                    temp_pop.w1[i][j] = parent2.w1[i][j]
                                    temp_pop.w2[i][j] = parent2.w2[i][j]
                                else:
                                    temp_pop.w1[i][j] = parent1.w1[i][j]
                                    temp_pop.w2[i][j] = parent1.w2[i][j]


                if random.random()<mutate_rate:
                    if self.Is_Adapt=="1":
                        temp_pop.rewire_ra()
   
                    temp_pop.mutate_weight()

                    if random.random() < 0.8 and temp_pop.reservoir_num < self.max_reservoir_num:
                        temp_pop.add_node()

                    if random.random() < 0.8:
                        temp_pop.mutate_step()

                    if random.random() < 0.8:
                        temp_pop.mutate_in_gnd()
                self.population[p] = copy.deepcopy(temp_pop)
            else:
                if self.Is_Adapt == "1":
                    self.population[p].rewire_ra()

                self.population[p].mutate_weight()

                if random.random() < 0.8 and self.population[p].reservoir_num < self.max_reservoir_num:
                    self.population[p].add_node()

                if random.random() < 0.8:
                    self.population[p].mutate_step()

                if random.random() < 0.8:
                    self.population[p].mutate_in_gnd()




        for p in range(0,self.population_size):
            self.population[p].cal_fitness()
            print("The",p,"-th's individual fitness",self.population[p].fitness)


    def __tournament_selection(self):
        temp_tournament: list = []

        while len(temp_tournament) is not self.tournament_size:
            rand_index = random.randrange(0, self.population_size)

            temp: RCRJ_Genome = self.population[rand_index]
            if temp not in temp_tournament:
                temp_tournament.append(temp)


        temp_tournament = sorted(temp_tournament, key=lambda x: x.fitness, reverse=True)

        return temp_tournament[0], temp_tournament[1]



