#Author: Frank Kok
#University of Twente 2024

import math
import mmh3
import random
from bitarray import bitarray
from collections import Counter
import numpy as np

class bf_ar(object):
    def __init__(ar, config, inputs, it_ar, c_index):
        #BFAR IS CONFIGURED IN tester_main.py
        ar.C_mode, ar.C_AC, ar.C_HPAr, ar.C_LA = config
        ar.inputs = inputs
        ar.it = it_ar
        ar.addr_instr_list, ar.addr_list, ar.instr_list, ar.addr_instr_list_inj, ar.addr_list_inj, ar.instr_list_inj, ar.randnr, ar.opcH, ar.restH, ar.opcH_inj, ar.restH_inj = ar.inputs
        #inputs: 0:addr_instr_list, 1:addr_list, 2:instr_list, 3:addr_instr_list_inj, 4:addr_list_inj, 5:instr_list_inj, 6:randnr, 7:opcH, 8:restH, 9:opcH_inj, 10:restH_inj
        ar.config_index = c_index     #configurable count
        
        ar.arraycount = ar.C_AC[ar.config_index]
        ar.hashes_p_ar = ar.C_HPAr[ar.config_index]
        ar.arraysize = ar.C_LA[ar.config_index]
        ar.mode = ar.C_mode[ar.config_index]
        ar.mod = ar.arraysize

        ar.totalsize = ar.arraycount * ar.arraysize
        ar.hashcount = ar.arraycount * ar.hashes_p_ar
        ar.l = 16

        ar.itx = ar.it*ar.arraycount*ar.hashes_p_ar

        ar.true_pos = 0
        ar.false_pos = 0
        ar.true_neg = 0
        ar.false_neg = 0

        ar.fillcount = 0
        ar.fillrate = 0
        ar.fillrate_indiv = np.zeros(ar.arraycount)

        ar.results = []

        ar.bf_array = np.zeros((ar.arraycount, ar.arraysize), dtype=bool)   #initialise empty arrays


    def insert(ar):         #Insert elements into the bloom filter  -   this stage hashes the inputs and inserts them into the arrays of the BF
        for i in range(len(ar.addr_instr_list)):    #Iterate through all elements in the input list
            for j in range(ar.arraycount):          #Iterate through all arrays in the BF
                for k in range(ar.hashes_p_ar):     #Iterate through all hashes per array (set to 1, relic from testing)
                    x = j*ar.hashes_p_ar+k+ar.itx   #Index for the random number list to give each hash a unique random number
                    if ar.mode[j] == 0:        #mode determines the input of the hash (0:addr_instr, 1:instr, 2:addr etc.)
                        index = ar.multiplyshift(ar.randnr[x], ar.addr_instr_list[i], ar.l, ar.mod)     #Hash the input and get the index
                    elif ar.mode[j] == 1:
                        index = ar.multiplyshift(ar.randnr[x], ar.instr_list[i], ar.l, ar.mod)
                    elif ar.mode[j] == 2:
                        index = ar.multiplyshift(ar.randnr[x], ar.addr_list[i], ar.l, ar.mod)
                    elif ar.mode[j] == 3:   #funct7
                        index = ar.multiplyshift(ar.randnr[x], ar.instr_list[i][0:7], ar.l, ar.mod)
                    elif ar.mode[j] == 4:   #Rs2
                        index = ar.multiplyshift(ar.randnr[x], ar.instr_list[i][7:12], ar.l, ar.mod)
                    elif ar.mode[j] == 5:   #Rs1
                        index = ar.multiplyshift(ar.randnr[x], ar.instr_list[i][12:17], ar.l, ar.mod)
                    elif ar.mode[j] == 6:   #Funct3
                        index = ar.multiplyshift(ar.randnr[x], ar.instr_list[i][17:20], ar.l, ar.mod)
                    elif ar.mode[j] == 7:   #Rd
                        index = ar.multiplyshift(ar.randnr[x], ar.instr_list[i][20:25], ar.l, ar.mod)
                    elif ar.mode[j] == 8:   #Opcode
                        index = ar.multiplyshift(ar.randnr[x], ar.instr_list[i][25:32], ar.l, ar.mod)
                    else:
                        print(f"insert error, mode {ar.mode[j]},j:{j},k:{k},x:{x}")
                        
                    ar.bf_array[j][index] = True    #Set the index to True in the BF array
                    
        #calculate fillcount+rate
        ar.fillcount = np.count_nonzero(ar.bf_array)
        for l in range(ar.arraycount):
            ar.fillrate_indiv[l] = np.count_nonzero(ar.bf_array[l]) #/ ar.arraysize
        ar.fillrate = ar.fillcount / ar.totalsize
        
        return ar.fillrate_indiv, ar.arraycount, ar.arraysize, ar.totalsize, ar.fillcount       #return data


    def test(ar):           #test the BF, feed injected input sets, measure response, return results
        for i in range(len(ar.addr_instr_list_inj)):    #Iterate through all elements in the injected input list
            elementpresent = True                   #Set elementpresent to True
            for j in range(ar.arraycount):          #Iterate through all arrays in the BF
                for k in range(ar.hashes_p_ar):     #Iterate through all hashes per array
                    x = j*ar.hashes_p_ar+k+ar.itx   #Index for the random number list to give each hash a unique random number (matched with insert, so hashes are the same between stages)
                    if ar.mode[j] == 0:     #addr+instr
                        index = ar.multiplyshift(ar.randnr[x], ar.addr_instr_list_inj[i], ar.l, ar.mod)
                    elif ar.mode[j] == 1:   #instr
                        index = ar.multiplyshift(ar.randnr[x], ar.instr_list_inj[i], ar.l, ar.mod)
                    elif ar.mode[j] == 2:   #addr
                        index = ar.multiplyshift(ar.randnr[x], ar.addr_list_inj[i], ar.l, ar.mod)
                    elif ar.mode[j] == 3:   #funct7
                        index = ar.multiplyshift(ar.randnr[x], ar.instr_list_inj[i][0:7], ar.l, ar.mod)
                    elif ar.mode[j] == 4:   #Rs2
                        index = ar.multiplyshift(ar.randnr[x], ar.instr_list_inj[i][7:12], ar.l, ar.mod)
                    elif ar.mode[j] == 5:   #Rs1
                        index = ar.multiplyshift(ar.randnr[x], ar.instr_list_inj[i][12:17], ar.l, ar.mod)
                    elif ar.mode[j] == 6:   #Funct3
                        index = ar.multiplyshift(ar.randnr[x], ar.instr_list_inj[i][17:20], ar.l, ar.mod)
                    elif ar.mode[j] == 7:   #Rd
                        index = ar.multiplyshift(ar.randnr[x], ar.instr_list_inj[i][20:25], ar.l, ar.mod)
                    elif ar.mode[j] == 8:   #Opcode
                        index = ar.multiplyshift(ar.randnr[x], ar.instr_list_inj[i][25:32], ar.l, ar.mod)
                    else:
                        print(f"test error, mode {ar.mode[j]},j:{j},k:{k},x:{x}")
                        
                    #if any of the hashes return False, set elementpresent to False, meaning a negative filter response 
                    #since all input elements are injected, this means a true negative, and a positive filter response is a false positive
                    if ar.bf_array[j][index] == False:
                        elementpresent = False

            #reduntant, but for clarity
            #checks whether injected input is in the original input list (it never is (as far as I(Frank) know))
            if ar.addr_instr_list_inj[i] in ar.addr_instr_list:
                inj_valid = True
            else:
                inj_valid = False
            
            
            #determine result based on elementpresent and inj_valid
            if (elementpresent == True) and (inj_valid == True):
                ar.true_pos += 1
            elif (elementpresent == True) and (inj_valid == False):
                ar.false_pos += 1
            elif (elementpresent == False) and (inj_valid == True):
                ar.false_neg += 1
            elif (elementpresent == False) and (inj_valid == False):
                ar.true_neg += 1
            else:
                print("error")

        #returns results
        return ar.true_pos, ar.false_pos, ar.true_neg, ar.false_neg
    
    @classmethod
    def multiplyshift(s, init, key, l, mod):
        tmp = int(key)
        mult = mmh3.hash(str(init) + str(tmp))
        return int((mult % 2**64)) %mod