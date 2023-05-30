from RC_CRJ import  *
from RC_RND import *
from RC_CND import *
from RC_DCND import *
from RC_DCNDK import *
from RC_RCRJ import *
from RC_all import *
import sys
if __name__=="__main__":
    # argv:
    # 1.RC topology：RC_CRJ ,RC_RND,RC_CND,RC_DCND
    # 2.If adaptive?: "1"--adaptive，"0"--not adaptive
    # 3.Problems: "Narma","Three_Out"
    # 4.Memristor Model：CHEN ,HP
    RC_Method,Is_Adapt,Problem,Model=sys.argv[1:]
    rc=eval(RC_Method)(Is_Adapt)
    rc.evolve(500)
