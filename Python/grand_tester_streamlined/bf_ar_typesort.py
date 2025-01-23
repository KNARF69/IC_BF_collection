#Author: Frank Kok
#University of Twente 2024

import math
import mmh3
import random
from bitarray import bitarray
from collections import Counter
import numpy as np

class bf_ar_type(object):
    def __init__(ta, config, inputs, it_ar, c_index):
        config = config
        ta.inputs = inputs
        ta.it = it_ar
        ta.addr_instr_list, ta.addr_list, ta.instr_list, ta.addr_instr_list_inj, ta.addr_list_inj, ta.instr_list_inj, ta.randnr, ta.opcH, ta.restH, ta.opcH_inj, ta.restH_inj = ta.inputs
        ta.config_index = c_index
        ta.l = 16
        
        #types
        ta.opc_R = [51,0]
        ta.opc_I = [3,19,103,115]
        ta.opc_S = [35,99]
        ta.opc_U = [23,55,111]
        ta.types = [ta.opc_R, ta.opc_I, ta.opc_S, ta.opc_U]
        ta.typelist = [3,19,23,35,51,55,99,103,111,115]

        #config - [x,x,x] x is selected inputs, 3 arrays
        #inputs: 0:addr_instr, 1:instr, 2:addr, 3:opcode, 4:rest, 5:funct7+opcode, 6:rest (not f3+opc), 7:funct7+funct3+opcode, 8:rest (not f7,f3,opc)
        ta.sel_main = [0,0,0]
        ta.sel_R    = [1,1,1]
        ta.sel_I    = [1,1,1]
        ta.sel_S    = [1,1,1]
        ta.sel_U    = [1,1,1]

        ta.Hpar = [1,1,1,1,1]   #hashes per array
        #array lengths: main, R, I, S, U
        ta.len_main = 6300
        ta.len_R    = 350
        ta.len_I    = 1830
        ta.len_S    = 920
        ta.len_U    = 600
        
        ta.sel = [ta.sel_main, ta.sel_R, ta.sel_I, ta.sel_S, ta.sel_U]
        ta.len_all = [ta.len_main, ta.len_R, ta.len_I, ta.len_S, ta.len_U]
        ta.arcnt, ta.tsize, ta.ar_all = [0]*len(ta.sel), [0]*len(ta.sel), [0]*len(ta.sel)
        ta.tot_hashcnt, ta.tot_size, ta.tot_arcnt = 0, 0, 0
        for sms in range(len(ta.sel)):
            ta.arcnt[sms] = len(ta.sel[sms])
            ta.tsize[sms] = ta.len_all[sms]*ta.arcnt[sms]
            # ta.ar_all[ar] = np.zeros((ta.arcnt[ar], ta.len_all[ar]), dtype=bool)
            ta.tot_hashcnt += len(ta.sel[sms])*ta.Hpar[sms]
        ta.tot_size = sum(ta.tsize)
        ta.tot_arcnt = sum(ta.arcnt)
        ta.itx = ta.it*ta.tot_hashcnt

        ta.true_pos = 0
        ta.false_pos = 0
        ta.true_neg = 0
        ta.false_neg = 0
        
        
        #inputs: 0:addr_instr, 1:instr, 2:addr, 3:opcode, 4:rest, 5:funct7+opcode, 6:rest (not f3+opc), 7:funct7+funct3+opcode, 8:rest (not f7,f3,opc)
        ta.ins_len = 9
        ta.ins = [[] for i in range(ta.ins_len)]
        ta.injs = [[] for i in range(ta.ins_len)]
        ta.ins[0] = ta.addr_instr_list
        ta.ins[1] = ta.instr_list
        ta.ins[2] = ta.addr_list
        ta.injs[0], ta.injs[1], ta.injs[2] = ta.addr_instr_list_inj, ta.instr_list_inj, ta.addr_list_inj
        for i in range(len(ta.addr_instr_list)):
            ta.ins[3].append(ta.instr_list[i][25:32])        #opcode
            ta.ins[4].append(ta.instr_list[i][0:25])          #rest (not opcode)
            ta.ins[5].append(ta.instr_list[i][17:20] + ta.instr_list[i][25:32]) #funct7+opcode
            ta.ins[6].append(ta.instr_list[i][0:17] + ta.instr_list[i][20:25]) #rest (not f3+opc)
            ta.ins[7].append(ta.instr_list[i][0:7] + ta.instr_list[i][17:20] + ta.instr_list[i][25:32]) #funct7+funct3+opcode
            ta.ins[8].append(ta.instr_list[i][7:17] + ta.instr_list[i][20:25]) #rest (not f7,f3,opc)
            
            ta.injs[3].append(ta.instr_list_inj[i][25:32])        #opcode
            ta.injs[4].append(ta.instr_list_inj[i][0:25])          #rest (not opcode)
            ta.injs[5].append(ta.instr_list_inj[i][17:20] + ta.instr_list_inj[i][25:32]) #funct7+opcode
            ta.injs[6].append(ta.instr_list_inj[i][0:17] + ta.instr_list_inj[i][20:25]) #rest (not f3+opc)
            ta.injs[7].append(ta.instr_list_inj[i][0:7] + ta.instr_list_inj[i][17:20] + ta.instr_list_inj[i][25:32]) #funct7+funct3+opcode
            ta.injs[8].append(ta.instr_list_inj[i][7:17] + ta.instr_list_inj[i][20:25]) #rest (not f7,f3,opc)
            
        ta.ar_main = np.zeros((ta.arcnt[0], ta.len_all[0]), dtype=bool)
        ta.ar_R = np.zeros((ta.arcnt[1], ta.len_all[1]), dtype=bool)
        ta.ar_I = np.zeros((ta.arcnt[2], ta.len_all[2]), dtype=bool)
        ta.ar_S = np.zeros((ta.arcnt[3], ta.len_all[3]), dtype=bool)
        ta.ar_U = np.zeros((ta.arcnt[4], ta.len_all[4]), dtype=bool)
            


    def insert(ta):
        for i in range(len(ta.addr_instr_list)):
            opc = int(ta.ins[3][i],2)   #grab opcode from input
            for sms in range(len(ta.sel)):      #select main, R, I, S, U (0-4)
                for arc in range(len(ta.sel[sms])):      #arraycount (within same type)
                    for h in range(ta.Hpar[sms]):
                        RI = ta.itx + arc*ta.Hpar[sms] + h
                        if sms == 0:        #main array
                            index = ta.multiplyshift(ta.randnr[RI], ta.ins[ta.sel[sms][arc]][i], ta.l, ta.len_all[sms])
                            ta.ar_main[arc][index] = True
                        else:               #other arrays (R, I, S, U)
                            if opc in ta.types[sms-1]:    #check if opcode is in the type list (analog to opcode decoder)
                                index = ta.multiplyshift(ta.randnr[RI], ta.ins[ta.sel[sms][arc]][i], ta.l, ta.len_all[sms])
                                if sms == 1:
                                    ta.ar_R[arc][index] = True
                                elif sms == 2:
                                    ta.ar_I[arc][index] = True
                                elif sms == 3:
                                    ta.ar_S[arc][index] = True
                                elif sms == 4:
                                    ta.ar_U[arc][index] = True
        
        fillcount_main, fillcount_R, fillcount_I, fillcount_S, fillcount_U = [], [], [], [], []
        fillrate_main, fillrate_R, fillrate_I, fillrate_S, fillrate_U = [], [], [], [], []
        fr_avg = [0]*len(ta.sel)
        
        for sms in range(len(ta.sel)):
            for arc in range(len(ta.sel[sms])):
                if sms == 0:
                    fillcount_main.append(np.count_nonzero(ta.ar_main[arc]))
                    fillrate_main.append(round((fillcount_main[arc] / ta.len_all[sms]), 6))
                elif sms == 1:
                    fillcount_R.append(np.count_nonzero(ta.ar_R[arc]))
                    fillrate_R.append(round((fillcount_R[arc] / ta.len_all[sms]), 6))
                elif sms == 2:
                    fillcount_I.append(np.count_nonzero(ta.ar_I[arc]))
                    fillrate_I.append(round((fillcount_I[arc] / ta.len_all[sms]), 6))
                elif sms == 3:
                    fillcount_S.append(np.count_nonzero(ta.ar_S[arc]))
                    fillrate_S.append(round((fillcount_S[arc] / ta.len_all[sms]), 6))
                elif sms == 4:
                    fillcount_U.append(np.count_nonzero(ta.ar_U[arc]))
                    fillrate_U.append(round((fillcount_U[arc] / ta.len_all[sms]), 6))
                    
        fr_avg[0] = np.mean(fillrate_main)
        fr_avg[1] = np.mean(fillrate_R)
        fr_avg[2] = np.mean(fillrate_I)
        fr_avg[3] = np.mean(fillrate_S)
        fr_avg[4] = np.mean(fillrate_U)
        
        return fr_avg, ta.tsize, ta.tot_size, ta.sel, ta.Hpar, ta.len_all


    def test(ta):
        for i in range(len(ta.addr_instr_list_inj)):
            elementpresent = True
            opcj = int(ta.injs[3][i],2)
            if opcj in ta.typelist:
                for sms in range(len(ta.sel)):      #select main, R, I, S, U (0-4)
                    for arc in range(len(ta.sel[sms])):      #arraycount (within same type)
                        for h in range(ta.Hpar[sms]):
                            RI = ta.itx + arc*ta.Hpar[sms] + h
                            if sms == 0:
                                index = ta.multiplyshift(ta.randnr[RI], ta.injs[ta.sel[sms][arc]][i], ta.l, ta.len_all[sms])
                                if ta.ar_main[arc][index] == False:
                                    elementpresent = False
                            else:
                                if opcj in ta.types[sms-1]:
                                    index = ta.multiplyshift(ta.randnr[RI], ta.injs[ta.sel[sms][arc]][i], ta.l, ta.len_all[sms])
                                    if sms == 1:
                                        if ta.ar_R[arc][index] == False:
                                            elementpresent = False
                                    elif sms == 2:
                                        if ta.ar_I[arc][index] == False:
                                            elementpresent = False
                                    elif sms == 3:
                                        if ta.ar_S[arc][index] == False:
                                            elementpresent = False
                                    elif sms == 4:
                                        if ta.ar_U[arc][index] == False:
                                            elementpresent = False
            else:
                elementpresent = False
                                    


            if ta.addr_instr_list_inj[i] in ta.addr_instr_list:
                inj_valid = True
            else:
                inj_valid = False
            
            if (elementpresent == True) and (inj_valid == True):
                ta.true_pos += 1
            elif (elementpresent == True) and (inj_valid == False):
                ta.false_pos += 1
            elif (elementpresent == False) and (inj_valid == True):
                ta.false_neg += 1
            elif (elementpresent == False) and (inj_valid == False):
                ta.true_neg += 1
            else:
                print("error")

        return ta.true_pos, ta.false_pos, ta.true_neg, ta.false_neg
    
    @classmethod
    def multiplyshift(s, init, key, l, mod):
        tmp = int(key)
        mult = mmh3.hash(str(init) + str(tmp))
        return int((mult % 2**64)) %mod