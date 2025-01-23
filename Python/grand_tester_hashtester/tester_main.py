#Author: Frank Kok
#University of Twente 2024


import sys
import random
import math
from datetime import date
from bitarray import bitarray
from functools import reduce
import numpy as np
from datetime import datetime
random.seed(datetime.now().timestamp())

import ctypes

#files/functions to test
from bf_ar_sets_hashtest import bf_ar_hashes

def split_and_inject(raw_exe_path, runcount):
    input_list_unique = []
    current_input_inj = []
    neo_list = []
    cm_list =  []

    input_list = []
    addr_instr_list = []
    addr_list = []
    instr_list = []
    addr_instr_list_inj = []
    addr_list_inj = []
    instr_list_inj = []
    opcH, restH, opcH_inj, restH_inj = [], [], [], []
    
    dataselect = 2
    generate = 0
    inj_loc = 1         #0:all 64b, 1:instr only (last 32b)
    randnr = []
    list_length = 4000

    if dataselect == 0:
        if generate == 1:
            with open(raw_exe_path + "64b_rand_bin.txt", "w") as f:
            #with open("64b_rand_bin.txt", "w") as f:
                while len(input_list_unique) < list_length:
                    unique_int = random.getrandbits(64)
                    unique_bit = format(unique_int, '064b')
                    if unique_int not in input_list_unique:
                        input_list_unique.append(unique_int)
                        f.write(format(unique_int, '064b') + "\n")
        with open(raw_exe_path + "64b_rand_bin.txt", "r") as file:
            for line in file:
                input_list.append(line.strip())
                
    elif dataselect == 1:
        if generate == 1:
            memstart_b10 = 2**17 + 2**11 + 2**5 + 2**2
            with open(raw_exe_path + "neorv32_raw_hex_exe.mem", "r") as file:
                for line in file:
                    mem_bin = format(memstart_b10, '032b')
                    neo_list.append(mem_bin + line.strip())
                    memstart_b10 += 4
            with open(raw_exe_path + "64b_neorv32_bin.txt", "w") as f:
                for line in neo_list:
                    f.write(line + "\n")    
        #else:
        with open(raw_exe_path + "64b_neorv32_bin.txt", "r") as file:
            for line in file:
                input_list.append(line.strip())
                
    elif dataselect == 2:   #coremark ~4100 lines
        if generate == 1:
            with open(raw_exe_path + "coremark_a_i_full.txt", "r") as file:
                for line in file:
                    # addr,instr = line.strip().split()
                    combined_num = line.replace(" ", "").strip()
                    cm_list.append(combined_num)
            with open(raw_exe_path + "coremark_bin.txt", "w") as f:
                for line in cm_list:
                    f.write(line + "\n")
        with open (raw_exe_path + "coremark_bin.txt", "r") as file:
            for line in file:
                input_list.append(line.strip())            
        
                    
                    
    #split input, assign  
    for i in range(len(input_list)):
        addr_instr_list.append(input_list[i][0:64])
        addr_list.append(input_list[i][0:32])
        instr_list.append(input_list[i][32:64])

    #INJECT and assign
    for j in range(len(addr_instr_list)):
        if inj_loc == 1:
            inj_index = random.randint(32, len(addr_instr_list[0]) - 1)
        else:
            inj_index = random.randint(0, len(addr_instr_list[0]) - 1)
        current_input = list(addr_instr_list[j])

        current_input[inj_index] = '1' if current_input[inj_index] == '0' else '0'
        addr_instr_inj = ''.join(current_input)
        addr_instr_list_inj.append(addr_instr_inj)
        addr_list_inj.append(addr_instr_inj[0:32])
        instr_list_inj.append(addr_instr_inj[32:64])
    
    for k in range(len(addr_instr_list)):
        randnr.append(random.randint(0, 2**32 - 1))

    for l in range (len(instr_list)):
        opcH.append(instr_list[l][25:32])
        restH.append(instr_list[l][0:25])
        opcH_inj.append(instr_list_inj[l][25:32])
        restH_inj.append(instr_list_inj[l][0:25])

    inputs = []
    inputs = np.array([addr_instr_list, addr_list, instr_list, addr_instr_list_inj, addr_list_inj, instr_list_inj, randnr, opcH, restH, opcH_inj, restH_inj])
 
    return inputs

def main(arguments):
    raw_exe_path = arguments[1]
    runcount = int(arguments[2])
    config = []
    selector = [1]
    
    
    inputs = split_and_inject(raw_exe_path, runcount)
    print(f"runcount: {runcount}")
    
    if selector[0] == 1:        #bfar_sets with configurable hashes (configured in bf_ar_sets_hashtest.py)
        print("-------------------------------------bfar_hashes-------------------------------------")       
        fr_A, fr_B, fr_C, fr_D, fr_E = [], [], [], [], []
        frA_avg, frB_avg, frC_avg, frD_avg, frE_avg = 0,0,0,0,0
        tnA_avg, tnB_avg, tnC_avg, tnD_avg, tnE_avg = 0,0,0,0,0
        bfst_tp, bfst_fp, bfst_tn, bfst_fn = [], [], [], []
        tp_bfst, fp_bfst, tn_bfst, fn_bfst = [], [], [], []
        tn_mult_bfst = []
        tn_mult_avg = []
        tn_sets_bfst = []
        fr_sets = []
        frs_avg = []
        
        fr_sets_avg, tn_sets_avg, tn_mult_avg = [], [], []
        tn1s, tn2s, tn3s, tn4s, tn5s = 0,0,0,0,0
        tnA, tnB, tnC, tnD, tnE = [], [], [], [], []
        tn1s, tn2s, tn3s, tn4s, tn5s = [], [], [], [], []
        
        
        for i in range(runcount):
            bfhashes = bf_ar_hashes(config, inputs, i, 0)
            
            fc_avg, fr_avg, size_all, tot_size, sel_all, Hpar, len_all, SiU = bfhashes.insert()
            tp, fp, tn, fn, tn_sets, tnset = bfhashes.test()
            
            tp_bfst.append(tp)
            fp_bfst.append(fp)
            tn_bfst.append(tn)
            fn_bfst.append(fn)
            
            
            for s in range(SiU):
                if s == 0:
                    fr_A.append(fr_avg[s])
                    tnA.append(tn_sets[s])
                    tn1s.append(tnset[s])
                elif s == 1:
                    fr_B.append(fr_avg[s])
                    tnB.append(tn_sets[s])
                    tn2s.append(tnset[s])
                elif s == 2:
                    fr_C.append(fr_avg[s])
                    tnC.append(tn_sets[s])
                    tn3s.append(tnset[s])
                elif s == 3:
                    fr_D.append(fr_avg[s])
                    tnD.append(tn_sets[s])
                    tn4s.append(tnset[s])
                elif s == 4:
                    fr_E.append(fr_avg[s])
                    tnE.append(tn_sets[s])
                    tn5s.append(tnset[s])
                else:
                    print("Error: SiU out of range")
                    
                    
        tp_avg = round(np.mean(tp_bfst) , 5)
        fp_avg = round(np.mean(fp_bfst) , 5)
        tn_avg = round(np.mean(tn_bfst) , 5)
        fn_avg = round(np.mean(fn_bfst) , 5)
        

        for s in range(SiU):
            if s == 0:
                fr_sets_avg.append(round(np.mean(fr_A) , 5))
                tn_sets_avg.append(round(np.mean(tnA) , 5))
                tn_mult_avg.append(round(np.mean(tn1s) , 5))
            elif s == 1:
                fr_sets_avg.append(round(np.mean(fr_B) , 5))
                tn_sets_avg.append(round(np.mean(tnB) , 5))
                tn_mult_avg.append(round(np.mean(tn2s) , 5))
            elif s == 2:
                fr_sets_avg.append(round(np.mean(fr_C) , 5))
                tn_sets_avg.append(round(np.mean(tnC) , 5))
                tn_mult_avg.append(round(np.mean(tn3s) , 5))
            elif s == 3:
                fr_sets_avg.append(round(np.mean(fr_D) , 5))
                tn_sets_avg.append(round(np.mean(tnD) , 5))
                tn_mult_avg.append(round(np.mean(tn4s) , 5))
            elif s == 4:
                fr_sets_avg.append(round(np.mean(fr_E) , 5))
                tn_sets_avg.append(round(np.mean(tnE) , 5))
                tn_mult_avg.append(round(np.mean(tn5s) , 5))
                
        
        print(f"avg_tp: {tp_avg}, min,max: {min(tp_bfst), max(tp_bfst)}")
        print(f"avg_fp: {fp_avg}, min,max: {min(fp_bfst), max(fp_bfst)}")
        print(f"avg_tn: {tn_avg}, min,max: {min(tn_bfst), max(tn_bfst)}")
        print(f"avg_fn: {fn_avg}, min,max: {min(fn_bfst), max(fn_bfst)}")
        
        print(f"tn_mult_avg (cum) (1 - {SiU}): {tn_mult_avg}")
           
        for s in range(SiU):
            if s == 0:
                print(f"A-set avg - fr, tn, len, size, sel, Hpar: {fr_sets_avg[s]}, {tn_sets_avg[s]}, {len_all[s]}, {size_all[s]}, {sel_all[s]}, {Hpar[s]}")
            elif s == 1:
                print(f"B-set avg - fr, tn, len, size, sel, Hpar: {fr_sets_avg[s]}, {tn_sets_avg[s]}, {len_all[s]}, {size_all[s]}, {sel_all[s]}, {Hpar[s]}")
            elif s == 2:
                print(f"C-set avg - fr, tn, len, size, sel, Hpar: {fr_sets_avg[s]}, {tn_sets_avg[s]}, {len_all[s]}, {size_all[s]}, {sel_all[s]}, {Hpar[s]}")
            elif s == 3:
                print(f"D-set avg - fr, tn, len, size, sel, Hpar: {fr_sets_avg[s]}, {tn_sets_avg[s]}, {len_all[s]}, {size_all[s]}, {sel_all[s]}, {Hpar[s]}")
            elif s == 4:
                print(f"E-set avg - fr, tn, len, size, sel, Hpar: {fr_sets_avg[s]}, {tn_sets_avg[s]}, {len_all[s]}, {size_all[s]}, {sel_all[s]}, {Hpar[s]}")
        print(f"total size: {tot_size}")
        
    
    
    



if __name__ == "__main__":
    main(sys.argv)

    