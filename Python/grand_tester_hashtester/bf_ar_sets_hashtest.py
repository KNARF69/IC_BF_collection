#Author: Frank Kok
#University of Twente 2024


import math
import mmh3
import random
from bitarray import bitarray
from collections import Counter
import numpy as np

import ctypes

c_mmh3 = ctypes.CDLL(r"C:\Users\Frank\Documents\UT\.Master_Thesis\Simulators\C_hashes\grand_tester_subsel\mmh3_64.dll")
func_mmh3 = c_mmh3.murmurhash
func_mmh3.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32]
func_mmh3.restype = ctypes.c_uint32





class bf_ar_hashes(object):
    def __init__(arhs, config, inputs, it_ar, c_index):
        config = config
        arhs.inputs = inputs
        arhs.it = it_ar
        arhs.addr_instr_list, arhs.addr_list, arhs.instr_list, arhs.addr_instr_list_inj, arhs.addr_list_inj, arhs.instr_list_inj, arhs.randnr, arhs.opcH, arhs.restH, arhs.opcH_inj, arhs.restH_inj = arhs.inputs
        arhs.config_index = c_index     #configurable count
        arhs.l = 16
        
        #config
        arhs.hashtoggle = 2         #0: multiplyshift, 1: crc32, 2: crc_gpt, 3: mmh3, 4: crc_gpt_singleseed         - crc_gpt is with different poly's, crc_gpt_singleseed with only 1. (crc32 doesn't work well)
        arhs.SiU = 4                # number of ACTIVE sets
        arhs.Hpar = [1,1,1,1,1]       # number = hashes per array for set(indicated by index)
        arhs.selA = [0]
        arhs.selB = [0]
        arhs.selC = [0]
        arhs.selD = [0]
        arhs.selE = [0]
        
        arhs.lens = 6000 #8192
        arhs.lenA = arhs.lens
        arhs.lenB = arhs.lens
        arhs.lenC = arhs.lens
        arhs.lenD = arhs.lens
        arhs.lenE = arhs.lens
        
        # leave it at a single array per set, single hash per array, and observe the cross-correlation between the sets for different hash functions
        
        arhs.sel_all = [arhs.selA, arhs.selB, arhs.selC, arhs.selD, arhs.selE]
        arhs.len_all = [arhs.lenA, arhs.lenB, arhs.lenC, arhs.lenD, arhs.lenE]
        arhs.size_all = [] 
        arhs.arcnt = []
        
        arhs.tot_hashcnt, arhs.tot_size, arhs.tot_arcnt = 0, 0, 0
        
        for s in range(arhs.SiU):
            arhs.arcnt.append(len(arhs.sel_all[s]))
            arhs.size_all.append(arhs.len_all[s]*len(arhs.sel_all[s]))
            arhs.tot_arcnt += len(arhs.sel_all[s])
            arhs.tot_hashcnt += arhs.Hpar[s]*len(arhs.sel_all[s])
            arhs.tot_size += arhs.len_all[s]*len(arhs.sel_all[s])
        
        #arhs.itx = arhs.it*arhs.tot_hashcnt
        arhs.itx = arhs.it * arhs.tot_hashcnt
        #yeah i know, it's a quick fix, but it works
        

        arhs.true_pos = 0
        arhs.false_pos = 0
        arhs.true_neg = 0
        arhs.false_neg = 0

        arhs.tn_A, arhs.tn_B, arhs.tn_C, arhs.tn_D, arhs.tn_E = 0, 0, 0, 0, 0
        arhs.tn_sets = [arhs.tn_A, arhs.tn_B, arhs.tn_C, arhs.tn_D, arhs.tn_E]
        arhs.tn_multi = []
        arhs.tnsets = [0]*arhs.SiU

        # arhs.Mtn, arhs.Stn, arhs.Ttn = 0,0,0
        
        arhs.ins_len = 10
        #arhs.ins, arhs.injs = [[]*arhs.ins_len], [[]*arhs.ins_len]
        arhs.ins = [[] for i in range(arhs.ins_len)]
        arhs.injs = [[] for i in range(arhs.ins_len)]
        arhs.ins[0] = arhs.addr_instr_list
        arhs.ins[1] = arhs.instr_list
        arhs.ins[2] = arhs.addr_list
        arhs.injs[0], arhs.injs[1], arhs.injs[2] = arhs.addr_instr_list_inj, arhs.instr_list_inj, arhs.addr_list_inj 
        
        
        arhs.Mcounter, arhs.Scounter = 0, 0
        arhs.wbv_opc = 0        #wrong but valid opcode
        
        
        for i in range(len(arhs.addr_instr_list)):
            arhs.ins[3].append(arhs.instr_list[i][25:32])        #opcode
            arhs.ins[4].append(arhs.instr_list[i][0:25])          #rest (not opcode)
            arhs.ins[5].append(arhs.instr_list[i][17:20] + arhs.instr_list[i][25:32]) #funct7+opcode
            arhs.ins[6].append(arhs.instr_list[i][0:17] + arhs.instr_list[i][20:25]) #rest (not f3+opc)
            arhs.ins[7].append(arhs.instr_list[i][0:7] + arhs.instr_list[i][17:20] + arhs.instr_list[i][25:32]) #funct7+funct3+opcode
            arhs.ins[8].append(arhs.instr_list[i][7:17] + arhs.instr_list[i][20:25]) #rest (not f7,f3,opc)
            arhs.ins[9].append(arhs.addr_list[i] + arhs.instr_list[i][0:25]) #address+rest (not opcode)
            
            arhs.injs[3].append(arhs.instr_list_inj[i][25:32])        #opcode
            arhs.injs[4].append(arhs.instr_list_inj[i][0:25])          #rest (not opcode)
            arhs.injs[5].append(arhs.instr_list_inj[i][17:20] + arhs.instr_list_inj[i][25:32]) #funct7+opcode
            arhs.injs[6].append(arhs.instr_list_inj[i][0:17] + arhs.instr_list_inj[i][20:25]) #rest (not f3+opc)
            arhs.injs[7].append(arhs.instr_list_inj[i][0:7] + arhs.instr_list_inj[i][17:20] + arhs.instr_list_inj[i][25:32]) #funct7+funct3+opcode
            arhs.injs[8].append(arhs.instr_list_inj[i][7:17] + arhs.instr_list_inj[i][20:25]) #rest (not f7,f3,opc)
            arhs.injs[9].append(arhs.addr_list_inj[i] + arhs.instr_list_inj[i][0:25]) #address+rest (not opcode)
            
        
        arhs.bf_A = np.zeros((len(arhs.sel_all[0]), arhs.len_all[0]), dtype=bool)
        arhs.bf_B = np.zeros((len(arhs.sel_all[1]), arhs.len_all[1]), dtype=bool)
        arhs.bf_C = np.zeros((len(arhs.sel_all[2]), arhs.len_all[2]), dtype=bool)
        arhs.bf_D = np.zeros((len(arhs.sel_all[3]), arhs.len_all[3]), dtype=bool)
        arhs.bf_E = np.zeros((len(arhs.sel_all[4]), arhs.len_all[4]), dtype=bool)
        

    def insert(arhs):
        for i in range(len(arhs.addr_instr_list)):
            RI = arhs.itx
            opc = int(arhs.ins[3][i],2)
            indexhex = 0
            for st in range(arhs.SiU):       #SiU for selected nr of sets
                for arc in range(arhs.arcnt[st]):
                    for h in range(arhs.Hpar[st]):
                        RI += 1
                        #RI = arhs.itx + arc*st*arhs.Hpar[st] + h
                        #RI = arhs.itx + st*arhs.arcnt[st] + arc*arhs.Hpar[st] + h
                        if arhs.hashtoggle == 0:
                            index = arhs.multiplyshift(arhs.randnr[RI], arhs.ins[arhs.sel_all[st][arc]][i], arhs.l, arhs.len_all[st])
                        elif arhs.hashtoggle == 1:
                            # print(f"randnr, ins, len_all: {arhs.randnr[RI]}, {arhs.ins[arhs.sel_all[st][arc]][i]}, {arhs.len_all[st]}")
                            index = arhs.crchash(arhs.randnr[RI], arhs.ins[arhs.sel_all[st][arc]][i], arhs.len_all[st])
                        elif arhs.hashtoggle == 2:
                            index = arhs.crc_gpt(arhs.randnr[RI], arhs.ins[arhs.sel_all[st][arc]][i], arhs.len_all[st])
                            
                        elif arhs.hashtoggle == 3:
                            #index = func_mmh3(arhs.ins[arhs.sel_all[st][arc]][i], arhs.len_all[st], arhs.randnr[RI])
                            #tempout = func_mmh3(key[j].encode('utf-8'), len(key[j]), seed)
                            temp = func_mmh3(arhs.ins[arhs.sel_all[st][arc]][i].encode('utf-8'), 64, int(arhs.randnr[RI]))   #len(arhs.ins[arhs.sel_all[st][arc]][i])
                            index = temp % arhs.len_all[st]
                        # elif arhs.hashtoggle == 4:
                        #     #errc = func_sha1(index, indexhex, arhs.ins[arhs.sel_all[st][arc]][i], arhs.len_all[st])
                        #     errc = 
                        
                        elif arhs.hashtoggle == 4:
                            index = arhs.crc_gpt_singleseed(arhs.randnr[RI], arhs.ins[arhs.sel_all[st][arc]][i], arhs.len_all[st])
                            
                        if st == 0:
                            arhs.bf_A[arc][index] = True
                        elif st == 1:
                            arhs.bf_B[arc][index] = True
                        elif st == 2:
                            arhs.bf_C[arc][index] = True
                        elif st == 3:
                            arhs.bf_D[arc][index] = True
                        elif st == 4:
                            arhs.bf_E[arc][index] = True
                        else:
                            print(f"insert error, st: {st}")
                            
        fc_avg, fr_avg = [0]*len(arhs.sel_all), [0]*len(arhs.sel_all)
        fr_A, fr_B, fr_C, fr_D, fr_E = [], [], [], [], []
        fct_A, fct_B, fct_C, fct_D, fct_E = [], [], [], [], []
        
        
        for s in range(arhs.SiU):
            if s == 0:
                fct_A = np.count_nonzero(arhs.bf_A)
                fr_avg[s] = round(fct_A/arhs.size_all[s], 6)
            elif s == 1:
                fct_B = np.count_nonzero(arhs.bf_B)
                fr_avg[s] = round(fct_B/arhs.size_all[s], 6)
            elif s == 2:
                fct_C = np.count_nonzero(arhs.bf_C)
                fr_avg[s] = round(fct_C/arhs.size_all[s], 6)
            elif s == 3:
                fct_D = np.count_nonzero(arhs.bf_D)
                fr_avg[s] = round(fct_D/arhs.size_all[s], 6)
            elif s == 4:
                fct_E = np.count_nonzero(arhs.bf_E)
                fr_avg[s] = round(fct_E/arhs.size_all[s], 6)
            else:
                print(f"insert error, st: {s}")
            
        return fc_avg, fr_avg, arhs.size_all, arhs.tot_size, arhs.sel_all, arhs.Hpar, arhs.len_all, arhs.SiU

    def test(arhs):
        #opc_mismatch = 0
        for i in range(len(arhs.addr_instr_list_inj)):
            elementpresent = True
            setpresent = [True]*arhs.SiU
            RI = arhs.itx
            indexhex = 0
            #opcj = int(arhs.injs[3][i],2)
            for st in range(arhs.SiU):
                for arc in range(arhs.arcnt[st]):
                    for h in range(arhs.Hpar[st]):
                        RI += 1
                        #RI = arhs.itx + arc*st*arhs.Hpar[st] + h
                        #RI = arhs.itx + st*arhs.arcnt[st] + arc*arhs.Hpar[st] + h
                        if arhs.hashtoggle == 0:
                            index = arhs.multiplyshift(arhs.randnr[RI], arhs.injs[arhs.sel_all[st][arc]][i], arhs.l, arhs.len_all[st])
                        elif arhs.hashtoggle == 1:
                            index = arhs.crchash(arhs.randnr[RI], arhs.injs[arhs.sel_all[st][arc]][i], arhs.len_all[st])
                        elif arhs.hashtoggle == 2:
                            index = arhs.crc_gpt(arhs.randnr[RI], arhs.injs[arhs.sel_all[st][arc]][i], arhs.len_all[st])
                        
                        elif arhs.hashtoggle == 3:
                            #index = func_mmh3(arhs.injs[arhs.sel_all[st][arc]][i], arhs.len_all[st], arhs.randnr[RI])
                            tjemp = func_mmh3(arhs.injs[arhs.sel_all[st][arc]][i].encode('utf-8'), 64, int(arhs.randnr[RI]))   #len(arhs.ins[arhs.sel_all[st][arc]][i])
                            index = tjemp % arhs.len_all[st]
                            
                        elif arhs.hashtoggle == 4:
                            index = arhs.crc_gpt_singleseed(arhs.randnr[RI], arhs.injs[arhs.sel_all[st][arc]][i], arhs.len_all[st])
                            
                        # elif arhs.hashtoggle == 5:
                        #     errc = func_sha1(index, indexhex, arhs.injs[arhs.sel_all[st][arc]][i], arhs.len_all[st])
                        
                        
                        if st == 0:
                            #print(f"arhs.bf_A[{arc}][{index}]: {arhs.bf_A[arc][index]}")
                            if arhs.bf_A[arc][index] == False:
                                elementpresent = False
                                setpresent[st] = False
                        elif st == 1:
                            if arhs.bf_B[arc][index] == False:
                                elementpresent = False
                                setpresent[st] = False
                        elif st == 2:
                            if arhs.bf_C[arc][index] == False:
                                elementpresent = False
                                setpresent[st] = False
                        elif st == 3:
                            if arhs.bf_D[arc][index] == False:
                                elementpresent = False
                                setpresent[st] = False
                        elif st == 4:
                            if arhs.bf_E[arc][index] == False:
                                elementpresent = False
                                setpresent[st] = False
                        else:
                            print(f"test error, st: {st}")
                                    
            if arhs.addr_instr_list_inj[i] in arhs.addr_instr_list:
                inj_valid = True
            else:
                inj_valid = False
            
            if (elementpresent == True) and (inj_valid == True):
                arhs.true_pos += 1
            elif (elementpresent == True) and (inj_valid == False):
                arhs.false_pos += 1
            elif (elementpresent == False) and (inj_valid == True):
                arhs.false_neg += 1
            elif (elementpresent == False) and (inj_valid == False):
                arhs.true_neg += 1
                setpres_cnt = sum(setpresent)
                arhs.tnsets[setpres_cnt-1] += 1
                # arhs.tn_multi.append(setpres_cnt)
                for s in range(arhs.SiU):
                    # if setpres_cnt == s+1:
                    #     arhs.tn_multi[s] += 1
                    if setpresent[s] == False:
                        if s == 0:
                            arhs.tn_A += 1
                        elif s == 1:
                            arhs.tn_B += 1
                        elif s == 2:
                            arhs.tn_C += 1
                        elif s == 3:
                            arhs.tn_D += 1
                        elif s == 4:
                            arhs.tn_E += 1
                        else:
                            print("error, setpresent")

                        
                        
                # if setpres_cnt == 1:        #nr of sets returning False, index tn_multi = False's -1
                #     arhs.tn_multi[0] += 1   #tn_multi[0] is for 1 set returning False
                # elif setpres_cnt == 2:
                #     arhs.tn_multi[1] += 1
                # elif setpres_cnt == 3:
                #     arhs.tn_multi[2] += 1
                # elif setpres_cnt == 4:
                #     arhs.tn_multi[3] += 1
                # elif setpres_cnt == 5:
                #     arhs.tn_multi[4] += 1
                # else:
                #     print("error, setpres_cnt > 5")
                    
                # if setpresent[0] == False:
                #     arhs.tn_A += 1
                # if setpresent[1] == False:
                #     arhs.tn_B += 1
                # if setpresent[2] == False:
                #     arhs.tn_C += 1
                # if setpresent[3] == False:
                #     arhs.tn_D += 1
                # if setpresent[4] == False:
                #     arhs.tn_E += 1
            else:
                print("Test error, elementpresent") 
                
        arhs.tn_sets = [arhs.tn_A, arhs.tn_B, arhs.tn_C, arhs.tn_D, arhs.tn_E]
                
        return arhs.true_pos, arhs.false_pos, arhs.true_neg, arhs.false_neg, arhs.tn_sets, arhs.tnsets    #arhs.tn_A, arhs.tn_B, arhs.tn_C, arhs.tn_D, arhs.tn_E
        # print(f"wrong but valid opcode count: {arhs.wbv_opc}")  
        #return arhs.true_pos, arhs.false_pos, arhs.true_neg, arhs.false_neg, arhs.Mtn, arhs.Stn, arhs.Ttn, opc_mismatch
    

    # @classmethod                                #OG multiplyshift
    # def multiplyshift(s, init, key, l, mod):
    #     tmp = int(key)
    #     #tmp = 0
    #     #tmp = int.from_bytes(key, byteorder="little")
    #     mult = init * tmp
    #     # if mult > 2**164:                        #increase if data more than 32bit
    #     #     print("impossible")
    #     # return int((mult % 2**32) >> 32 - l) % mod
    #     return int((mult % 2**64) >> 32 - l) % mod
    
    # @classmethod
    # def multiplyshift(s, init, key, l, mod):
    #     tmp = int(key)
    #     mult = mmh3.hash(str(init) + str(tmp))
    #     return int((mult % 2**64)) %mod # >> 32 - l) % mod
    
    
    @classmethod
    def multiplyshift(arhs, init, key, l, outlength):   #key: int, seed: int, outlength: int) -> int:
        # Ensure the seed is an odd integer
        key = int(key)
        seed = int(init)# % 4206911
        if seed % 2 == 0:
            seed += 1

        # Calculate the number of bits we need to shift right
        shift_amount = 64 - l
        
        # Perform the multiply-shift hashing
        hashed_value = ((key * seed) >> shift_amount)%outlength
        
        # Limit the output to the specified number of bits
        # max_value = (1 << outlength) - 1
        # hashed_value &= max_value
        
        return hashed_value
    
    
    @classmethod
    def crchash(self, crc_in, data_in, outlen):       #randnr, input, outlength
        crctemp = format(int(crc_in), '016b')
        datatemp = format(int(data_in), '064b')
        
        data = []
        crcIn = []
        
        for i in range(len(datatemp)):
            data.append(int(datatemp[i]))
            
        for i in range(len(crctemp)):
            crcIn.append(int(crctemp[i]))
        
        ret = [0]*16
        diflen = False
        
        ret[0] = crcIn[0] ^ crcIn[1] ^ crcIn[2] ^ crcIn[3] ^ crcIn[4] ^ crcIn[9] ^ crcIn[10] ^ crcIn[11] ^ crcIn[12] ^ crcIn[13] ^ crcIn[14] ^ crcIn[15] ^ data[0] ^ data[1] ^ data[2] ^ data[3] ^ data[4] ^ data[9] ^ data[10] ^ data[11] ^ data[12] ^ data[13] ^ data[14] ^ data[15] ^ data[16] ^ data[17] ^ data[18] ^ data[19] ^ data[21] ^ data[23] ^ data[24] ^ data[25] ^ data[26] ^ data[27] ^ data[28] ^ data[29] ^ data[30] ^ data[31] ^ data[32] ^ data[33] ^ data[34] ^ data[37] ^ data[38] ^ data[39] ^ data[40] ^ data[41] ^ data[42] ^ data[43] ^ data[44] ^ data[45] ^ data[46] ^ data[47] ^ data[48] ^ data[49] ^ data[51] ^ data[52] ^ data[53] ^ data[54] ^ data[55] ^ data[56] ^ data[57] ^ data[58] ^ data[59] ^ data[60] ^ data[61] ^ data[62] ^ data[63]
        ret[1] = crcIn[5] ^ crcIn[9] ^ data[5] ^ data[9] ^ data[20] ^ data[21] ^ data[22] ^ data[23] ^ data[35] ^ data[37] ^ data[50] ^ data[51]
        ret[2] = crcIn[6] ^ crcIn[10] ^ data[6] ^ data[10] ^ data[21] ^ data[22] ^ data[23] ^ data[24] ^ data[36] ^ data[38] ^ data[51] ^ data[52]
        ret[3] = crcIn[7] ^ crcIn[11] ^ data[7] ^ data[11] ^ data[22] ^ data[23] ^ data[24] ^ data[25] ^ data[37] ^ data[39] ^ data[52] ^ data[53]
        ret[4] = crcIn[8] ^ crcIn[12] ^ data[8] ^ data[12] ^ data[23] ^ data[24] ^ data[25] ^ data[26] ^ data[38] ^ data[40] ^ data[53] ^ data[54]
        ret[5] = crcIn[9] ^ crcIn[13] ^ data[9] ^ data[13] ^ data[24] ^ data[25] ^ data[26] ^ data[27] ^ data[39] ^ data[41] ^ data[54] ^ data[55]
        ret[6] = crcIn[0] ^ crcIn[10] ^ crcIn[14] ^ data[0] ^ data[10] ^ data[14] ^ data[25] ^ data[26] ^ data[27] ^ data[28] ^ data[40] ^ data[42] ^ data[55] ^ data[56]
        ret[7] = crcIn[0] ^ crcIn[1] ^ crcIn[11] ^ crcIn[15] ^ data[0] ^ data[1] ^ data[11] ^ data[15] ^ data[26] ^ data[27] ^ data[28] ^ data[29] ^ data[41] ^ data[43] ^ data[56] ^ data[57]
        ret[8] = crcIn[1] ^ crcIn[2] ^ crcIn[12] ^ data[1] ^ data[2] ^ data[12] ^ data[16] ^ data[27] ^ data[28] ^ data[29] ^ data[30] ^ data[42] ^ data[44] ^ data[57] ^ data[58]
        ret[9] = crcIn[2] ^ crcIn[3] ^ crcIn[13] ^ data[2] ^ data[3] ^ data[13] ^ data[17] ^ data[28] ^ data[29] ^ data[30] ^ data[31] ^ data[43] ^ data[45] ^ data[58] ^ data[59]
        ret[10] = crcIn[0] ^ crcIn[3] ^ crcIn[4] ^ crcIn[14] ^ data[0] ^ data[3] ^ data[4] ^ data[14] ^ data[18] ^ data[29] ^ data[30] ^ data[31] ^ data[32] ^ data[44] ^ data[46] ^ data[59] ^ data[60]
        ret[11] = crcIn[0] ^ crcIn[1] ^ crcIn[4] ^ crcIn[5] ^ crcIn[15] ^ data[0] ^ data[1] ^ data[4] ^ data[5] ^ data[15] ^ data[19] ^ data[30] ^ data[31] ^ data[32] ^ data[33] ^ data[45] ^ data[47] ^ data[60] ^ data[61]
        ret[12] = crcIn[1] ^ crcIn[2] ^ crcIn[5] ^ crcIn[6] ^ data[1] ^ data[2] ^ data[5] ^ data[6] ^ data[16] ^ data[20] ^ data[31] ^ data[32] ^ data[33] ^ data[34] ^ data[46] ^ data[48] ^ data[61] ^ data[62]
        ret[13] = crcIn[2] ^ crcIn[3] ^ crcIn[6] ^ crcIn[7] ^ data[2] ^ data[3] ^ data[6] ^ data[7] ^ data[17] ^ data[21] ^ data[32] ^ data[33] ^ data[34] ^ data[35] ^ data[47] ^ data[49] ^ data[62] ^ data[63]
        ret[14] = crcIn[0] ^ crcIn[1] ^ crcIn[2] ^ crcIn[7] ^ crcIn[8] ^ crcIn[9] ^ crcIn[10] ^ crcIn[11] ^ crcIn[12] ^ crcIn[13] ^ crcIn[14] ^ crcIn[15] ^ data[0] ^ data[1] ^ data[2] ^ data[7] ^ data[8] ^ data[9] ^ data[10] ^ data[11] ^ data[12] ^ data[13] ^ data[14] ^ data[15] ^ data[16] ^ data[17] ^ data[19] ^ data[21] ^ data[22] ^ data[23] ^ data[24] ^ data[25] ^ data[26] ^ data[27] ^ data[28] ^ data[29] ^ data[30] ^ data[31] ^ data[32] ^ data[35] ^ data[36] ^ data[37] ^ data[38] ^ data[39] ^ data[40] ^ data[41] ^ data[42] ^ data[43] ^ data[44] ^ data[45] ^ data[46] ^ data[47] ^ data[49] ^ data[50] ^ data[51] ^ data[52] ^ data[53] ^ data[54] ^ data[55] ^ data[56] ^ data[57] ^ data[58] ^ data[59] ^ data[60] ^ data[61] ^ data[62]
        ret[15] = crcIn[0] ^ crcIn[1] ^ crcIn[2] ^ crcIn[3] ^ crcIn[8] ^ crcIn[9] ^ crcIn[10] ^ crcIn[11] ^ crcIn[12] ^ crcIn[13] ^ crcIn[14] ^ crcIn[15] ^ data[0] ^ data[1] ^ data[2] ^ data[3] ^ data[8] ^ data[9] ^ data[10] ^ data[11] ^ data[12] ^ data[13] ^ data[14] ^ data[15] ^ data[16] ^ data[17] ^ data[18] ^ data[20] ^ data[22] ^ data[23] ^ data[24] ^ data[25] ^ data[26] ^ data[27] ^ data[28] ^ data[29] ^ data[30] ^ data[31] ^ data[32] ^ data[33] ^ data[36] ^ data[37] ^ data[38] ^ data[39] ^ data[40] ^ data[41] ^ data[42] ^ data[43] ^ data[44] ^ data[45] ^ data[46] ^ data[47] ^ data[48] ^ data[50] ^ data[51] ^ data[52] ^ data[53] ^ data[54] ^ data[55] ^ data[56] ^ data[57] ^ data[58] ^ data[59] ^ data[60] ^ data[61] ^ data[62] ^ data[63]
        
        if outlen == 2^13:
            tempout = [ret[0], ret[1], ret[2]^ret[5], ret[3], ret[4], ret[6]^ret[8], ret[7]^ret[10], ret[9], ret[11], ret[12], ret[13], ret[14], ret[15]]
            diflen = True
        elif outlen == 2^12:
            tempout = [ret[0], ret[2]^ret[5], ret[3], ret[4], ret[6]^ret[8], ret[7]^ret[10], ret[9], ret[11], ret[12], ret[1]^ret[13], ret[14], ret[15]]
            diflen = True
        else:
            tempout = [ret[0], ret[1], ret[2], ret[3], ret[4], ret[5], ret[6], ret[7], ret[8], ret[9], ret[10], ret[11], ret[12], ret[13], ret[14], ret[15]]
            diflen = False
            
        Tout = ''.join(map(str, tempout))
        intout = int(Tout,2)
            
        if not diflen:
            intout = intout % outlen
            
        return intout
    
    @classmethod
    def crc_gpt(self, seed, binary_input, outlen):
        
    #def crc_gpt(binary_input: str, binary_seed: str) -> str:
    # """
    # Calculate a 13-bit CRC hash from a 64-bit binary input using a 32-bit binary seed.
    
    # :param binary_input: 64-bit binary string input
    # :param binary_seed: 32-bit binary string seed
    # :return: 13-bit binary string hash
    # """
    # Convert binary strings to integers
        #print(f"type seed, binary_input: {type(seed)}, {type(binary_input)}")
    
        input_64b = int(bin(int(str(binary_input), 2))[2:])
        seed_32b = int(bin(int(str(seed)))[2:])
    
        # input_64b = int(binary_input, 2)
        # #seed_32b = int(binary_seed, 2)
        # seed_32b = int(bin(seed)[2:])
        
        # Define CRC polynomial (example polynomial)
        polynomial = 0x1A2B3C4D ^ seed_32b  # XOR the seed with the polynomial for variability
        crc = 0
        
        # Perform CRC calculation
        for bit in range(64):
            crc ^= (input_64b >> (63 - bit)) & 1
            if crc & 1:
                crc = (crc >> 1) ^ polynomial
            else:
                crc >>= 1
        
        # Extract the lower 13 bits of the CRC as the hash value
        hash_13b = crc & 0x1FFF  # 0x1FFF is 13-bit mask (binary: 0001 1111 1111 1111)
        
        # Convert the hash to a 13-bit binary string
        #hash_13b_binary = f'{hash_13b:013b}'
        
        if outlen != 2^13:
            hash_13b = hash_13b % outlen

        
        return hash_13b     #_binary
        
        
    @classmethod
    def crc_gpt_singleseed(self, seed, binary_input, outlen):
        
    #def crc_gpt(binary_input: str, binary_seed: str) -> str:
    # """
    # Calculate a 13-bit CRC hash from a 64-bit binary input using a 32-bit binary seed.
    
    # :param binary_input: 64-bit binary string input
    # :param binary_seed: 32-bit binary string seed
    # :return: 13-bit binary string hash
    # """
    # Convert binary strings to integers
        #print(f"type seed, binary_input: {type(seed)}, {type(binary_input)}")
        seed2 = 4206911
    
        input_64b = int(bin(int(str(binary_input), 2))[2:])
        seed_32b = int(bin(int(str(seed2)))[2:])
    
        # input_64b = int(binary_input, 2)
        # #seed_32b = int(binary_seed, 2)
        # seed_32b = int(bin(seed)[2:])
        
        # Define CRC polynomial (example polynomial)
        polynomial = 0x1A2B3C4D ^ seed_32b  # XOR the seed with the polynomial for variability
        crc = 0
        
        # Perform CRC calculation
        for bit in range(64):
            crc ^= (input_64b >> (63 - bit)) & 1
            if crc & 1:
                crc = (crc >> 1) ^ polynomial
            else:
                crc >>= 1
        
        # Extract the lower 13 bits of the CRC as the hash value
        hash_13b = crc & 0x1FFF  # 0x1FFF is 13-bit mask (binary: 0001 1111 1111 1111)
        
        # Convert the hash to a 13-bit binary string
        #hash_13b_binary = f'{hash_13b:013b}'
        
        if outlen != 2^13:
            hash_13b = hash_13b % outlen
        
        return hash_13b     #_binary
        