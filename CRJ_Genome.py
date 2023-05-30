import numpy as np
from files import *
import subprocess as sp
from raw_read import  rawread
import random
import re
import sys

vref=np.load(sys.argv[3]+"/ref.npy")
vref=vref.T
def find_first_pos(array, value):
    idx = (np.abs(array - value)).argmin()
    return idx


def find_last_pos(array, value):
    idx = (np.abs(array - value))[::-1].argmin()
    return array.shape[0] - idx

class CRJ_Genome:
    def __init__(self,N):
        self.reservoir_num=N
        list_temp = []
        for i in range(1,self.reservoir_num+1):
            list_temp.append(i)
        if  sys.argv[3]=="Narma":
            self.outlayer=1
            self.in_gnd = random.sample(list_temp, 4)
        elif sys.argv[3]=="Three_Out":
            self.outlayer = 3
            self.in_gnd = random.sample(list_temp, 2)
        else:
            raise ValueError

        if sys.argv[4]=="CHEN":
            self.w1=np.random.uniform(low=0.0,high=1.0,size=(N,N))
        elif sys.argv[4]=="HP":
            self.w1 = np.random.uniform(low=100.0, high=10000.0, size=(N, N))
        else:
            raise ValueError
        self.w2=np.random.uniform(low=0.0,high=0.5,size=(N,N))

        self.step=np.random.randint(low=2,high=int(self.reservoir_num/2))
        self.w_bool=np.zeros((N,N))
        for i in range(0,self.reservoir_num-1):
            self.w_bool[i][i+1]=1
        self.w_bool[self.reservoir_num-1][0] = 1
        start=0
        while (start+self.step)<=(self.reservoir_num-1):
            self.w_bool[start][start+self.step]=1
            self.w_bool[start + self.step][start] = 1
            start+=self.step

        self.fitness=-9999

        self.w_out=np.random.uniform(low=-1.0,high=1.0,size=(self.reservoir_num,self.outlayer))

        self.zeta = 0.3  # the fraction of the weights removed

    def change_to_cir(self):
        with open(cir_filename, "w+", encoding='UTF-8') as f:
            with open(sys.argv[3]+"/"+sys.argv[4]+"/"+fixed1_filename, 'r', encoding='UTF-8') as fx:
                fixed_text = fx.read()
                fx.close()
            f.write(fixed_text)
            f.writelines("\n\n\n")
            if sys.argv[3] == "Narma":
                f.writelines('vtemprc1 100 ' + str(self.in_gnd[0]) + ' dc 0\n')
                f.writelines('vtemprc2 101 ' + str(self.in_gnd[1]) + ' dc 0\n')
                f.writelines('vtemprc3 102 ' + str(self.in_gnd[2]) + ' dc 0\n')
                f.writelines('vtemprc4  ' + str(self.in_gnd[3]) + ' 0 dc 0\n')
            elif sys.argv[3] == "Three_Out":
                f.writelines('vtemprc1 100 ' + str(self.in_gnd[0]) + ' dc 0\n')
                f.writelines('vtemprc2  ' + str(self.in_gnd[1]) + ' 0 dc 0\n')
            else:
                raise ValueError
            for source in range(0, self.reservoir_num):
                for target in range(0, self.reservoir_num):
                    if self.w_bool[source][target] == 1:
                        instruction = "xunit" + str(source + 1) + "-" + str(target + 1) + "  " + str(
                            source + 1) + "  " + str(target + 1) + "  " + "unitrc1" + "  " + \
                                      "ra=" + str("%.2f" % self.w1[source][target]) + "  " + "tb=" + str(
                            "%.2f" % self.w2[source][target])
                    # else:
                    #     instruction = "xunit" + str(source+1) + "-" + str(target+1) + "  " + str(source+1) + "  " + str(
                    #         target+1) + "  " + "unitrc2"
                        f.writelines(instruction)
                        f.writelines("\n")
                f.writelines("\n")
            f.writelines(".save   time\n")

            for source in range(0, self.reservoir_num):
                for target in range(0, self.reservoir_num):
                    instruction = ".save   v.xunit{}-{}.vtemp2#branch".format(str(source + 1), str(target + 1))
                    f.writelines(instruction + "\n")
                f.writelines("\n")
            with open(sys.argv[3]+"/"+sys.argv[4]+"/"+fixed2_filename, 'r', encoding='UTF-8') as fx:
                fixed_text = fx.read()
                fx.close()
            f.write(fixed_text)
            f.close()

    def expand_row_col(self):
        if sys.argv[4] == "CHEN":
            row=np.random.uniform(low=0.0,high=1.0,size=(1,self.reservoir_num))
            self.w1=np.row_stack((self.w1,row))
            col=np.random.uniform(low=0.0,high=1.0,size=(self.reservoir_num+1,1))
            self.w1=np.column_stack((self.w1,col))
        elif sys.argv[4] == "HP":
            row = np.random.uniform(low=100.0, high=10000.0, size=(1, self.reservoir_num))
            self.w1 = np.row_stack((self.w1, row))
            col = np.random.uniform(low=100.0, high=10000.0, size=(self.reservoir_num + 1, 1))
            self.w1 = np.column_stack((self.w1, col))
        else:
            raise ValueError

        row = np.random.uniform(low=0.0, high=0.5, size=(1, self.reservoir_num))
        self.w2 = np.row_stack((self.w2, row))
        col = np.random.uniform(low=0.0, high=0.5, size=(self.reservoir_num + 1, 1))
        self.w2=np.column_stack((self.w2, col))

        row = np.zeros((1, self.reservoir_num))
        self.w_bool=np.row_stack((self.w_bool,row))
        col = np.zeros((self.reservoir_num+1,1))
        self.w_bool = np.column_stack((self.w_bool, col))




    def add_node(self):
        self.expand_row_col()
        self.reservoir_num+=1
        # 重新更新wbool
        for i in range(0, self.reservoir_num - 1):
            self.w_bool[i][i + 1] = 1
        self.w_bool[self.reservoir_num - 1][0] = 1
        start = 0
        while (start + self.step) <= (self.reservoir_num - 1):
            self.w_bool[start][start + self.step] = 1
            self.w_bool[start + self.step][start] = 1
            start += self.step

    def zero_count(self):
        zero_number=0
        for i in range(0,self.reservoir_num):
            for j in range(0, self.reservoir_num):
                if self.w_bool[i][j]==0 and i!=j:
                    zero_number+=1
        return zero_number

    def add_connection(self):
        zero_number=self.zero_count()
        if zero_number==0:
            return
        index=random.randint(0,zero_number)

        index_count=0
        for i in range(0,self.reservoir_num):
            for j in range(0,self.reservoir_num):
                if self.w_bool[i][j]==0 and i!=j:
                    if index_count==index:
                        self.w_bool[i][j] = 1
                        return
                    index_count+=1

    def mutate_weight(self):
        for i in range(0, self.reservoir_num):
            for j in range(0, self.reservoir_num):
                if self.w_bool[i][j] != 0:
                    if random.random() < 0.5:
                        if sys.argv[4] == "CHEN":
                            self.w1[i][j] = random.uniform(0.0, 1.0)
                        elif  sys.argv[4] == "HP":
                            self.w1[i][j] = random.uniform(100.0, 10000.0)
                        else:
                            raise ValueError
                    if random.random() < 0.5:
                        self.w2[i][j] = random.uniform(0, 0.5)
    def mutate_in_gnd(self):
        index=random.randint(0,len(self.in_gnd)-1)
        a=random.randint(1,self.reservoir_num)
        while a  in self.in_gnd:
            a = random.randint(1, self.reservoir_num)
        self.in_gnd[index]=a
    def mutate_step(self):
        self.step = np.random.randint(low=2, high=int(self.reservoir_num / 2))


        for i in range(0, self.reservoir_num - 1):
            self.w_bool[i][i + 1] = 1
        self.w_bool[self.reservoir_num - 1][0] = 1
        start = 0
        while (start + self.step) <= (self.reservoir_num - 1):
            self.w_bool[start][start + self.step] = 1
            self.w_bool[start + self.step][start] = 1
            start += self.step

    def cal_fitness(self):
        self.change_to_cir()
        p = sp.Popen(["%s" % (spicepath), '-b','-o',log_file,cir_filename])
        try:
            p.communicate(timeout=1000)
        except:
            p.kill()
            print("program run error")
        p.kill()
        [arrs, plots] = rawread(target_filename)  # arrs is the voltages'n'currents

        if sys.argv[3] == "Narma":
            res_out = arrs[1:-1]
        elif  sys.argv[3]=="Three_Out":
            res_out = arrs[1:-3]
        else:
            raise ValueError
        # record=np.zeros((self.reservoir_num,self.reservoir_num,res_out.shape[1]))
        #
        # for t in range(0,res_out.shape[1]):
        #     index = 0
        #     for name in plots['varnames']:
        #         number=re.findall(r'\d+',name)
        #         if len(number)>=3:
        #             from_node=int(number[0])-1
        #             to_node = int(number[1])-1
        #             record[from_node,to_node,t]=res_out[index][t]
        #             index+=1
        #
        # res=np.zeros((1,self.reservoir_num,res_out.shape[1]))
        # for t in range(0,res_out.shape[1]):
        #     for i in range(0,self.reservoir_num):
        #         if record[i][i][t]!=0:
        #             raise Exception("对角线为0")
        #         in_current = np.sum(record[:, i, t])
        #         out_current = np.sum(record[i, :, t])
        #         current = in_current + out_current
        #         res[0,i,t]=current
        # x = res[0].T
        x=res_out.T
        temp = np.linalg.pinv(x)
        w_out = np.dot(temp, vref)

        self.w_out=w_out
        readout=np.zeros((res_out.shape[1],self.outlayer))
        for t in range(0, res_out.shape[1]):
            # readout[t]=np.dot(res[:,:,t],w_out)
            readout[t] = np.dot(res_out[:, t], w_out)
        self.fitness=-9999

        if sys.argv[3] == "Narma":
            error = abs(readout[:, 0] - vref)
            error1=np.sqrt(np.sum(np.power(error,2))/res_out.shape[1])
            self.fitness=100-(10000*error1)
        elif sys.argv[3]=="Three_Out":
            error = abs(readout - vref)
            error1 = np.sqrt(np.sum(np.power(error[:, 0], 2)) / res_out.shape[1])
            error2 = np.sqrt(np.sum(np.power(error[:, 1], 2)) / res_out.shape[1])
            error3 = np.sqrt(np.sum(np.power(error[:, 2], 2)) / res_out.shape[1])
            self.fitness = 100 - (10000 * error1 + 10000 * error2 + 10000 * error3)
        else:
            raise ValueError

    def rewire_ra(self):
        noWeights=np.sum(self.w_bool)
        # remove zeta largest negative and smallest positive weights
        if sys.argv[4]=="CHEN":
            values = np.sort(self.w1.ravel())
            firstZeroPos = find_first_pos(values, 0)
            lastZeroPos = find_last_pos(values, 0)

            smallestPositive = values[int(min(values.shape[0] - 1, lastZeroPos + self.zeta * (values.shape[0] - lastZeroPos)))]
            rewiredWeights = self.w_bool.copy()
            rewiredWeights[self.w1 < smallestPositive] =0
        elif sys.argv[4]=="HP":
            temp = 1 / self.w1
            values = np.sort(temp.ravel())

            firstZeroPos = find_first_pos(values, 0)
            lastZeroPos = find_last_pos(values, 0)

            smallestPositive = values[
                int(min(values.shape[0] - 1, lastZeroPos + self.zeta * (values.shape[0] - lastZeroPos)))]
            rewiredWeights = self.w_bool.copy()
            rewiredWeights[temp < smallestPositive] = 0
        else:
            raise ValueError
        rewiredWeights[rewiredWeights != 1] = 0


        # add zeta random weights
        nrAdd = 0
        noRewires = noWeights - np.sum(rewiredWeights)
        while (nrAdd < noRewires):
            i = np.random.randint(0, rewiredWeights.shape[0])
            j = np.random.randint(0, rewiredWeights.shape[1])
            if (rewiredWeights[i, j] == 0):
                rewiredWeights[i, j] = 1
                if sys.argv[4] == "CHEN":
                    self.w1[i,j]= random.uniform(0.0, 1.0)
                elif sys.argv[4] == "HP":
                    self.w1[i, j] = random.uniform(100.0, 10000.0)
                else:
                    raise ValueError
                nrAdd += 1

        # self.w_bool=rewiredWeights.copy()




















