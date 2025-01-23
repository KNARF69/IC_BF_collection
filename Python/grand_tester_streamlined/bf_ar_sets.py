#Author: Frank Kok
#University of Twente 2024

import math
import mmh3
import random
from bitarray import bitarray
from collections import Counter
import numpy as np

class bf_ar_sets(object):
    def __init__(arst, config, inputs, it_ar, c_index):
        #inputs = 0:addr_instr_list, 1:addr_list, 2:instr_list, 3:addr_instr_list_inj, 4:addr_list_inj, 5:instr_list_inj, 6:randnr
        config = config
        arst.inputs = inputs
        arst.it = it_ar
        arst.addr_instr_list, arst.addr_list, arst.instr_list, arst.addr_instr_list_inj, arst.addr_list_inj, arst.instr_list_inj, arst.randnr, arst.opcH, arst.restH, arst.opcH_inj, arst.restH_inj = arst.inputs
        arst.config_index = c_index     #configurable count
        arst.l = 16
        
        #configurable variables:
        arst.SiU = 2                # number of ACTIVE sets (A,B,C,D,E)
        arst.Hpar = [1,1,1,1,1]       # number = hashes per array for set(indicated by index) (just leave at 1)
        #input select + array count: [x,x,x] - x:input - 3 arrays (nr of x's is number of arrays in the set), only active sets are used
        arst.selA = [0,0,0]
        arst.selB = [1,1,1]
        arst.selC = [0]
        arst.selD = [0]
        arst.selE = [0]
        
        arst.lenA = 6000    #8192
        arst.lenB = 4000    #4096
        arst.lenC = 8192
        arst.lenD = 8192
        arst.lenE = 8192
        
        
        arst.sel_all = [arst.selA, arst.selB, arst.selC, arst.selD, arst.selE]
        arst.len_all = [arst.lenA, arst.lenB, arst.lenC, arst.lenD, arst.lenE]
        arst.size_all = [] 
        arst.arcnt = []
        
        arst.tot_hashcnt, arst.tot_size, arst.tot_arcnt = 0, 0, 0
        
        for s in range(arst.SiU):
            arst.arcnt.append(len(arst.sel_all[s]))
            arst.size_all.append(arst.len_all[s]*len(arst.sel_all[s]))
            arst.tot_arcnt += len(arst.sel_all[s])
            arst.tot_hashcnt += arst.Hpar[s]*len(arst.sel_all[s])
            arst.tot_size += arst.len_all[s]*len(arst.sel_all[s])
        
        arst.itx = arst.it * arst.tot_hashcnt
        

        arst.true_pos = 0
        arst.false_pos = 0
        arst.true_neg = 0
        arst.false_neg = 0

        arst.tn_A, arst.tn_B, arst.tn_C, arst.tn_D, arst.tn_E = 0, 0, 0, 0, 0
        arst.tn_sets = [arst.tn_A, arst.tn_B, arst.tn_C, arst.tn_D, arst.tn_E]
        arst.tn_multi = []
        arst.tnsets = [0]*arst.SiU

        # arst.Mtn, arst.Stn, arst.Ttn = 0,0,0
        
        arst.ins_len = 10
        arst.ins = [[] for i in range(arst.ins_len)]
        arst.injs = [[] for i in range(arst.ins_len)]
        arst.ins[0] = arst.addr_instr_list
        arst.ins[1] = arst.instr_list
        arst.ins[2] = arst.addr_list
        arst.injs[0], arst.injs[1], arst.injs[2] = arst.addr_instr_list_inj, arst.instr_list_inj, arst.addr_list_inj 
        
        
        arst.Mcounter, arst.Scounter = 0, 0
        arst.wbv_opc = 0        #wrong but valid opcode
        
        
        for i in range(len(arst.addr_instr_list)):
            arst.ins[3].append(arst.instr_list[i][25:32])        #opcode
            arst.ins[4].append(arst.instr_list[i][0:25])          #rest (not opcode)
            arst.ins[5].append(arst.instr_list[i][17:20] + arst.instr_list[i][25:32]) #funct7+opcode
            arst.ins[6].append(arst.instr_list[i][0:17] + arst.instr_list[i][20:25]) #rest (not f3+opc)
            arst.ins[7].append(arst.instr_list[i][0:7] + arst.instr_list[i][17:20] + arst.instr_list[i][25:32]) #funct7+funct3+opcode
            arst.ins[8].append(arst.instr_list[i][7:17] + arst.instr_list[i][20:25]) #rest (not f7,f3,opc)
            arst.ins[9].append(arst.addr_list[i] + arst.instr_list[i][0:25]) #address+rest (not opcode)
            
            arst.injs[3].append(arst.instr_list_inj[i][25:32])        #opcode
            arst.injs[4].append(arst.instr_list_inj[i][0:25])          #rest (not opcode)
            arst.injs[5].append(arst.instr_list_inj[i][17:20] + arst.instr_list_inj[i][25:32]) #funct7+opcode
            arst.injs[6].append(arst.instr_list_inj[i][0:17] + arst.instr_list_inj[i][20:25]) #rest (not f3+opc)
            arst.injs[7].append(arst.instr_list_inj[i][0:7] + arst.instr_list_inj[i][17:20] + arst.instr_list_inj[i][25:32]) #funct7+funct3+opcode
            arst.injs[8].append(arst.instr_list_inj[i][7:17] + arst.instr_list_inj[i][20:25]) #rest (not f7,f3,opc)
            arst.injs[9].append(arst.addr_list_inj[i] + arst.instr_list_inj[i][0:25]) #address+rest (not opcode)
            
        
        arst.bf_A = np.zeros((len(arst.sel_all[0]), arst.len_all[0]), dtype=bool)
        arst.bf_B = np.zeros((len(arst.sel_all[1]), arst.len_all[1]), dtype=bool)
        arst.bf_C = np.zeros((len(arst.sel_all[2]), arst.len_all[2]), dtype=bool)
        arst.bf_D = np.zeros((len(arst.sel_all[3]), arst.len_all[3]), dtype=bool)
        arst.bf_E = np.zeros((len(arst.sel_all[4]), arst.len_all[4]), dtype=bool)

    def insert(arst):
        for i in range(len(arst.addr_instr_list)):
            RI = arst.itx
            opc = int(arst.ins[3][i],2)
            for st in range(arst.SiU):       #SiU for selected nr of sets
                for arc in range(arst.arcnt[st]):
                    for h in range(arst.Hpar[st]):
                        RI += 1
                        index = arst.multiplyshift(arst.randnr[RI], arst.ins[arst.sel_all[st][arc]][i], arst.l, arst.len_all[st])
                        if st == 0:
                            arst.bf_A[arc][index] = True
                        elif st == 1:
                            arst.bf_B[arc][index] = True
                        elif st == 2:
                            arst.bf_C[arc][index] = True
                        elif st == 3:
                            arst.bf_D[arc][index] = True
                        elif st == 4:
                            arst.bf_E[arc][index] = True
                        else:
                            print(f"insert error, st: {st}")
                            
        fc_avg, fr_avg = [0]*len(arst.sel_all), [0]*len(arst.sel_all)
        fr_A, fr_B, fr_C, fr_D, fr_E = [], [], [], [], []
        fct_A, fct_B, fct_C, fct_D, fct_E = [], [], [], [], []
        
        
        for s in range(arst.SiU):
            if s == 0:
                fct_A = np.count_nonzero(arst.bf_A)
                fr_avg[s] = round(fct_A/arst.size_all[s], 6)
            elif s == 1:
                fct_B = np.count_nonzero(arst.bf_B)
                fr_avg[s] = round(fct_B/arst.size_all[s], 6)
            elif s == 2:
                fct_C = np.count_nonzero(arst.bf_C)
                fr_avg[s] = round(fct_C/arst.size_all[s], 6)
            elif s == 3:
                fct_D = np.count_nonzero(arst.bf_D)
                fr_avg[s] = round(fct_D/arst.size_all[s], 6)
            elif s == 4:
                fct_E = np.count_nonzero(arst.bf_E)
                fr_avg[s] = round(fct_E/arst.size_all[s], 6)
            else:
                print(f"insert error, st: {s}")
            
        return fc_avg, fr_avg, arst.size_all, arst.tot_size, arst.sel_all, arst.Hpar, arst.len_all, arst.SiU

    def test(arst):
        #opc_mismatch = 0
        for i in range(len(arst.addr_instr_list_inj)):
            elementpresent = True
            setpresent = [True]*arst.SiU
            RI = arst.itx
            #opcj = int(arst.injs[3][i],2)
            for st in range(arst.SiU):
                for arc in range(arst.arcnt[st]):
                    for h in range(arst.Hpar[st]):
                        RI += 1
                        index = arst.multiplyshift(arst.randnr[RI], arst.injs[arst.sel_all[st][arc]][i], arst.l, arst.len_all[st])
                        if st == 0:
                            if arst.bf_A[arc][index] == False:
                                elementpresent = False
                                setpresent[st] = False
                        elif st == 1:
                            if arst.bf_B[arc][index] == False:
                                elementpresent = False
                                setpresent[st] = False
                        elif st == 2:
                            if arst.bf_C[arc][index] == False:
                                elementpresent = False
                                setpresent[st] = False
                        elif st == 3:
                            if arst.bf_D[arc][index] == False:
                                elementpresent = False
                                setpresent[st] = False
                        elif st == 4:
                            if arst.bf_E[arc][index] == False:
                                elementpresent = False
                                setpresent[st] = False
                        else:
                            print(f"test error, st: {st}")
                                    
            if arst.addr_instr_list_inj[i] in arst.addr_instr_list:
                inj_valid = True
            else:
                inj_valid = False
            
            if (elementpresent == True) and (inj_valid == True):
                arst.true_pos += 1
            elif (elementpresent == True) and (inj_valid == False):
                arst.false_pos += 1
            elif (elementpresent == False) and (inj_valid == True):
                arst.false_neg += 1
            elif (elementpresent == False) and (inj_valid == False):
                arst.true_neg += 1
                setpres_cnt = sum(setpresent)
                arst.tnsets[setpres_cnt-1] += 1
                for s in range(arst.SiU):
                    if setpresent[s] == False:
                        if s == 0:
                            arst.tn_A += 1
                        elif s == 1:
                            arst.tn_B += 1
                        elif s == 2:
                            arst.tn_C += 1
                        elif s == 3:
                            arst.tn_D += 1
                        elif s == 4:
                            arst.tn_E += 1
                        else:
                            print("error, setpresent")
            else:
                print("Test error, elementpresent") 
                
        arst.tn_sets = [arst.tn_A, arst.tn_B, arst.tn_C, arst.tn_D, arst.tn_E]
                
        return arst.true_pos, arst.false_pos, arst.true_neg, arst.false_neg, arst.tn_sets, arst.tnsets

    
    @classmethod
    def multiplyshift(s, init, key, l, mod):
        tmp = int(key)
        mult = mmh3.hash(str(init) + str(tmp))
        return int((mult % 2**64)) %mod