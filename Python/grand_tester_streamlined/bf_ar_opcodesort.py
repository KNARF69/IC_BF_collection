#Author: Frank Kok
#University of Twente 2024

import math
import mmh3
import random
from bitarray import bitarray
from collections import Counter
import numpy as np

class bf_ar_opcode(object):
    def __init__(opar, config, inputs, it_ar, c_index):
        config = config
        opar.inputs = inputs
        opar.it = it_ar
        opar.addr_instr_list, opar.addr_list, opar.instr_list, opar.addr_instr_list_inj, opar.addr_list_inj, opar.instr_list_inj, opar.randnr, opar.opcH, opar.restH, opar.opcH_inj, opar.restH_inj = opar.inputs
        opar.config_index = c_index
        opar.l = 16
        
        #types
        
        opar.opc51R = 51                                                            #300 instances
        opar.opc3I, opar.opc19I, opar.opc103I, opar.opc115I = 3, 19, 103, 115       #554,1667,79,80
        opar.opc35S, opar.opc99S = 35, 99                                           #458,375
        opar.opc23U, opar.opc55U, opar.opc111U = 23, 55, 111                        #13,178,415

        opar.opclist = [3,19,23,35,51,55,99,103,111,115]
        
        #config
        #hashes per array + input selector :[x,x,x]
        #inputs: 0:addr_instr, 1:instr, 2:addr, 3:opcode, 4:rest, 5:funct7+opcode, 6:rest (not f3+opc), 7:funct7+funct3+opcode, 8:rest (not f7,f3,opc)
        opar.Hpar = [1,1,1,1,1,1,1,1,1,1,1]
        opar.sel_main = [0,0,0]
        opar.sel51R =   [4,4,4]
        opar.sel3I =    [4,4,4]
        opar.sel19I =   [4,4,4]
        opar.sel103I =  [4,4,4]
        opar.sel115I =  [4,4,4]
        opar.sel35S =   [4,4,4]
        opar.sel99S =   [4,4,4]
        opar.sel23U =   [4,4,4]
        opar.sel55U =   [4,4,4]
        opar.sel111U =  [4,4,4]
        
        #array lengths main + each opcode
        opar.len_main = 6300
        opar.len51R =   480
        opar.len3I =    1220
        opar.len19I =   20
        opar.len103I =  420
        opar.len115I =  340
        opar.len35S =   80
        opar.len99S =   510
        opar.len23U =   20
        opar.len55U =   500
        opar.len111U =  110
        
        opar.sel = [opar.sel_main, opar.sel51R, opar.sel3I, opar.sel19I, opar.sel103I, opar.sel115I, opar.sel35S, opar.sel99S, opar.sel23U, opar.sel55U, opar.sel111U]
        opar.len_all = [opar.len_main, opar.len51R, opar.len3I, opar.len19I, opar.len103I, opar.len115I, opar.len35S, opar.len99S, opar.len23U, opar.len55U, opar.len111U]

        opar.arcnt, opar.tsize, opar.ar_all = [0]*len(opar.sel), [0]*len(opar.sel), [0]*len(opar.sel)
        opar.tot_hashcnt, opar.tot_size, opar.tot_arcnt = 0, 0, 0
        for sms in range(len(opar.sel)):
            opar.arcnt[sms] = len(opar.sel[sms])
            opar.tsize[sms] = opar.len_all[sms]*opar.arcnt[sms]
            opar.tot_hashcnt += len(opar.sel[sms])*opar.Hpar[sms]
        opar.tot_size = sum(opar.tsize)
        opar.tot_arcnt = sum(opar.arcnt)
        opar.itx = opar.it*opar.tot_hashcnt

        opar.true_pos = 0
        opar.false_pos = 0
        opar.true_neg = 0
        opar.false_neg = 0
        
        opar.Ttn, opar.Stn, opar.Mtn = 0, 0, 0
        
        opar.ins_len = 9
        opar.ins = [[] for i in range(opar.ins_len)]
        opar.injs = [[] for i in range(opar.ins_len)]
        opar.ins[0] = opar.addr_instr_list
        opar.ins[1] = opar.instr_list
        opar.ins[2] = opar.addr_list
        opar.injs[0], opar.injs[1], opar.injs[2] = opar.addr_instr_list_inj, opar.instr_list_inj, opar.addr_list_inj 
        
        for i in range(len(opar.addr_instr_list)):
            opar.ins[3].append(opar.instr_list[i][25:32])        #opcode
            opar.ins[4].append(opar.instr_list[i][0:25])          #rest (not opcode)
            opar.ins[5].append(opar.instr_list[i][17:20] + opar.instr_list[i][25:32]) #funct7+opcode
            opar.ins[6].append(opar.instr_list[i][0:17] + opar.instr_list[i][20:25]) #rest (not f3+opc)
            opar.ins[7].append(opar.instr_list[i][0:7] + opar.instr_list[i][17:20] + opar.instr_list[i][25:32]) #funct7+funct3+opcode
            opar.ins[8].append(opar.instr_list[i][7:17] + opar.instr_list[i][20:25]) #rest (not f7,f3,opc)
            
            opar.injs[3].append(opar.instr_list_inj[i][25:32])        #opcode
            opar.injs[4].append(opar.instr_list_inj[i][0:25])          #rest (not opcode)
            opar.injs[5].append(opar.instr_list_inj[i][17:20] + opar.instr_list_inj[i][25:32]) #funct7+opcode
            opar.injs[6].append(opar.instr_list_inj[i][0:17] + opar.instr_list_inj[i][20:25]) #rest (not f3+opc)
            opar.injs[7].append(opar.instr_list_inj[i][0:7] + opar.instr_list_inj[i][17:20] + opar.instr_list_inj[i][25:32]) #funct7+funct3+opcode
            opar.injs[8].append(opar.instr_list_inj[i][7:17] + opar.instr_list_inj[i][20:25]) #rest (not f7,f3,opc)
            

        opar.ar_main = np.zeros((opar.arcnt[0], opar.len_all[0]), dtype=bool)
        opar.ar51R = np.zeros((opar.arcnt[1], opar.len_all[1]), dtype=bool)
        opar.ar3I = np.zeros((opar.arcnt[2], opar.len_all[2]), dtype=bool)
        opar.ar19I = np.zeros((opar.arcnt[3], opar.len_all[3]), dtype=bool)
        opar.ar103I = np.zeros((opar.arcnt[4], opar.len_all[4]), dtype=bool)
        opar.ar115I = np.zeros((opar.arcnt[5], opar.len_all[5]), dtype=bool)
        opar.ar35S = np.zeros((opar.arcnt[6], opar.len_all[6]), dtype=bool)
        opar.ar99S = np.zeros((opar.arcnt[7], opar.len_all[7]), dtype=bool)
        opar.ar23U = np.zeros((opar.arcnt[8], opar.len_all[8]), dtype=bool)
        opar.ar55U = np.zeros((opar.arcnt[9], opar.len_all[9]), dtype=bool)
        opar.ar111U = np.zeros((opar.arcnt[10], opar.len_all[10]), dtype=bool)
            


    def insert(opar):
        for i in range(len(opar.addr_instr_list)):
            opc = int(opar.ins[3][i],2)
            for sms in range(len(opar.sel)):      #select main, R, I, S, U (0-4)
                for arc in range(len(opar.sel[sms])):      #arraycount (within same type)
                    for h in range(opar.Hpar[sms]):
                        RI = opar.itx + arc*opar.Hpar[sms] + h
                        if sms == 0:
                            index = opar.multiplyshift(opar.randnr[RI], opar.ins[opar.sel[sms][arc]][i], opar.l, opar.len_all[sms])
                            opar.ar_main[arc][index] = True
                        else:
                            if opc is opar.opclist[sms-1]:
                                index = opar.multiplyshift(opar.randnr[RI], opar.ins[opar.sel[sms][arc]][i], opar.l, opar.len_all[sms])
                                if sms == 1:
                                    opar.ar51R[arc][index] = True
                                elif sms == 2:
                                    opar.ar3I[arc][index] = True
                                elif sms == 3:
                                    opar.ar19I[arc][index] = True
                                elif sms == 4:
                                    opar.ar103I[arc][index] = True
                                elif sms == 5:
                                    opar.ar115I[arc][index] = True
                                elif sms == 6:
                                    opar.ar35S[arc][index] = True
                                elif sms == 7:
                                    opar.ar99S[arc][index] = True
                                elif sms == 8:
                                    opar.ar23U[arc][index] = True
                                elif sms == 9:
                                    opar.ar55U[arc][index] = True
                                elif sms == 10:
                                    opar.ar111U[arc][index] = True
                                else:
                                    print(f"insert error, sms: {sms}")
        
        fcmain, fc51R, fc3I, fc19I, fc103I, fc115I, fc35S, fc99S, fc23U, fc55U, fc111U = [], [], [], [], [], [], [], [], [], [], []
        frmain, fr51R, fr3I, fr19I, fr103I, fr115I, fr35S, fr99S, fr23U, fr55U, fr111U = [], [], [], [], [], [], [], [], [], [], []
        fr_avg = [0]*len(opar.sel)
        
        
        for sms in range(len(opar.sel)):
            for arc in range(len(opar.sel[sms])):
                if sms == 0:
                    fcmain.append(np.count_nonzero(opar.ar_main[arc]))
                    frmain.append(round((fcmain[arc] / opar.len_all[sms]), 6))
                elif sms == 1:
                    fc51R.append(np.count_nonzero(opar.ar51R[arc]))
                    fr51R.append(round((fc51R[arc] / opar.len_all[sms]), 6))
                elif sms == 2:
                    fc3I.append(np.count_nonzero(opar.ar3I[arc]))
                    fr3I.append(round((fc3I[arc] / opar.len_all[sms]), 6))
                elif sms == 3:
                    fc19I.append(np.count_nonzero(opar.ar19I[arc]))
                    fr19I.append(round((fc19I[arc] / opar.len_all[sms]), 6))
                elif sms == 4:
                    fc103I.append(np.count_nonzero(opar.ar103I[arc]))
                    fr103I.append(round((fc103I[arc] / opar.len_all[sms]), 6))
                elif sms == 5:
                    fc115I.append(np.count_nonzero(opar.ar115I[arc]))
                    fr115I.append(round((fc115I[arc] / opar.len_all[sms]), 6))
                elif sms == 6:
                    fc35S.append(np.count_nonzero(opar.ar35S[arc]))
                    fr35S.append(round((fc35S[arc] / opar.len_all[sms]), 6))
                elif sms == 7:
                    fc99S.append(np.count_nonzero(opar.ar99S[arc]))
                    fr99S.append(round((fc99S[arc] / opar.len_all[sms]), 6))
                elif sms == 8:
                    fc23U.append(np.count_nonzero(opar.ar23U[arc]))
                    fr23U.append(round((fc23U[arc] / opar.len_all[sms]), 6))
                elif sms == 9:
                    fc55U.append(np.count_nonzero(opar.ar55U[arc]))
                    fr55U.append(round((fc55U[arc] / opar.len_all[sms]), 6))
                elif sms == 10:
                    fc111U.append(np.count_nonzero(opar.ar111U[arc]))
                    fr111U.append(round((fc111U[arc] / opar.len_all[sms]), 6))
                else:
                    print(f"fillcount/rate error, sms: {sms}")
                    
        fr_avg[0] = round(np.mean(frmain), 6)
        fr_avg[1] = round(np.mean(fr51R), 6)
        fr_avg[2] = round(np.mean(fr3I), 6)
        fr_avg[3] = round(np.mean(fr19I), 6)
        fr_avg[4] = round(np.mean(fr103I), 6)
        fr_avg[5] = round(np.mean(fr115I), 6)
        fr_avg[6] = round(np.mean(fr35S), 6)
        fr_avg[7] = round(np.mean(fr99S), 6)
        fr_avg[8] = round(np.mean(fr23U), 6)
        fr_avg[9] = round(np.mean(fr55U), 6)
        fr_avg[10] = round(np.mean(fr111U), 6)
        
        return fr_avg, opar.tsize, opar.tot_size, opar.sel, opar.Hpar, opar.len_all


    def test(opar):
        opc_mismatch = 0
        for i in range(len(opar.addr_instr_list_inj)):
            elementpresent = True
            Mpres, Spres, opcpres = True, True, True
            opcj = int(opar.injs[3][i],2)
            if opcj in opar.opclist:
                for sms in range(len(opar.sel)):      #select main, R, I, S, U (0-4)
                    for arc in range(len(opar.sel[sms])):      #arraycount (within same type)
                        for h in range(opar.Hpar[sms]):
                            RI = opar.itx + arc*opar.Hpar[sms] + h
                            if sms == 0:
                                index = opar.multiplyshift(opar.randnr[RI], opar.injs[opar.sel[sms][arc]][i], opar.l, opar.len_all[sms])
                                if opar.ar_main[arc][index] == False:
                                    elementpresent = False
                                    Mpres = False
                            else:
                                if opcj is opar.opclist[sms-1]:
                                    index = opar.multiplyshift(opar.randnr[RI], opar.injs[opar.sel[sms][arc]][i], opar.l, opar.len_all[sms])
                                    if sms == 1:
                                        if opar.ar51R[arc][index] == False:
                                            elementpresent = False
                                            Spres = False
                                    elif sms == 2:
                                        if opar.ar3I[arc][index] == False:
                                            elementpresent = False
                                            Spres = False
                                    elif sms == 3:
                                        if opar.ar19I[arc][index] == False:
                                            elementpresent = False
                                            Spres = False
                                    elif sms == 4:
                                        if opar.ar103I[arc][index] == False:
                                            elementpresent = False
                                            Spres = False
                                    elif sms == 5:
                                        if opar.ar115I[arc][index] == False:
                                            elementpresent = False
                                            Spres = False
                                    elif sms == 6:
                                        if opar.ar35S[arc][index] == False:
                                            elementpresent = False
                                            Spres = False
                                    elif sms == 7:
                                        if opar.ar99S[arc][index] == False:
                                            elementpresent = False
                                            Spres = False
                                    elif sms == 8:
                                        if opar.ar23U[arc][index] == False:
                                            elementpresent = False
                                            Spres = False
                                    elif sms == 9:
                                        if opar.ar55U[arc][index] == False:
                                            elementpresent = False
                                            Spres = False
                                    elif sms == 10:
                                        if opar.ar111U[arc][index] == False:
                                            elementpresent = False
                                            Spres = False
            else:
                elementpresent = False
                opcpres = False
                                    
            if opar.addr_instr_list_inj[i] in opar.addr_instr_list:
                inj_valid = True
            else:
                inj_valid = False
            
            if (elementpresent == True) and (inj_valid == True):
                opar.true_pos += 1
            elif (elementpresent == True) and (inj_valid == False):
                opar.false_pos += 1
            elif (elementpresent == False) and (inj_valid == True):
                opar.false_neg += 1
            elif (elementpresent == False) and (inj_valid == False):
                opar.true_neg += 1
                if (Mpres == False) and (Spres == False):
                    opar.Ttn += 1
                elif (Mpres == True) and (Spres == False):
                    opar.Stn += 1
                elif (Mpres == False) and (Spres == True):
                    opar.Mtn += 1
                elif opcpres == False:
                    opc_mismatch += 1
                else:
                    print("error fp calculation")
            else:
                print("error")   
        return opar.true_pos, opar.false_pos, opar.true_neg, opar.false_neg, opar.Mtn, opar.Stn, opar.Ttn, opc_mismatch
    
    
    @classmethod
    def multiplyshift(s, init, key, l, mod):
        tmp = int(key)
        mult = mmh3.hash(str(init) + str(tmp))
        return int((mult % 2**64)) %mod