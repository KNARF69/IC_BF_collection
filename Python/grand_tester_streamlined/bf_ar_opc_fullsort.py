#Author: Frank Kok
#University of Twente 2024

import math
import mmh3
import random
from bitarray import bitarray
from collections import Counter
import numpy as np

class bf_ar_fs_opcode(object):
    def __init__(fsop, config, inputs, it_ar, c_index):
        config = config
        fsop.inputs = inputs
        fsop.it = it_ar
        fsop.addr_instr_list, fsop.addr_list, fsop.instr_list, fsop.addr_instr_list_inj, fsop.addr_list_inj, fsop.instr_list_inj, fsop.randnr, fsop.opcH, fsop.restH, fsop.opcH_inj, fsop.restH_inj = fsop.inputs
        fsop.config_index = c_index     #configurable count
        fsop.l = 16
        
        fsop.opc51R = 51                                                            #300 instances
        fsop.opc3I, fsop.opc19I, fsop.opc103I, fsop.opc115I = 3, 19, 103, 115       #554,1667,79,80
        fsop.opc35S, fsop.opc99S = 35, 99                                           #458,375
        fsop.opc23U, fsop.opc55U, fsop.opc111U = 23, 55, 111                        #13,178,415
        fsop.opclist = [3,19,23,35,51,55,99,103,111,115]
        
        #config
        fsop.MHpar, fsop.SHpar = [1,1,1,1,1,1,1,1,1,1], [1,1,1,1,1,1,1,1,1,1]   #hashes per array (main and sub)
        #input select for main and sub arrays, format: [x,x,x],[y,y,y]
        fsop.Msel51R, fsop.Ssel51R =    [9,9,9],    [4,4,4]
        fsop.Msel3I, fsop.Ssel3I =      [9,9,9],    [4,4,4]
        fsop.Msel19I, fsop.Ssel19I =    [9,9,9],    [4,4,4]
        fsop.Msel115I, fsop.Ssel115I =  [9,9,9],    [4,4,4]
        fsop.Msel103I, fsop.Ssel103I =  [9,9,9],    [4,4,4]
        fsop.Msel35S, fsop.Ssel35S =    [9,9,9],    [4,4,4]   
        fsop.Msel99S, fsop.Ssel99S =    [9,9,9],    [4,4,4]    
        fsop.Msel23U, fsop.Ssel23U =    [9,9,9],    [4,4,4]    
        fsop.Msel55U, fsop.Ssel55U =    [9,9,9],    [4,4,4]  
        fsop.Msel111U, fsop.Ssel111U =  [9,9,9],    [4,4,4]

        #array lengths, format: main, sub
        fsop.Mlen51R, fsop.Slen51R =    850     ,500
        fsop.Mlen3I, fsop.Slen3I =      2510    ,1250
        fsop.Mlen19I, fsop.Slen19I =    30      ,20
        fsop.Mlen103I, fsop.Slen103I =  690     ,420
        fsop.Mlen115I, fsop.Slen115I =  450     ,350
        fsop.Mlen35S, fsop.Slen35S =    280     ,80 
        fsop.Mlen99S, fsop.Slen99S =    560     ,520
        fsop.Mlen23U, fsop.Slen23U =    120     ,20
        fsop.Mlen55U, fsop.Slen55U =    620     ,500
        fsop.Mlen111U, fsop.Slen111U =  120     ,110
        
        
        fsop.Msel = [fsop.Msel51R, fsop.Msel3I, fsop.Msel19I, fsop.Msel103I, fsop.Msel115I, fsop.Msel35S, fsop.Msel99S, fsop.Msel23U, fsop.Msel55U, fsop.Msel111U]
        fsop.Ssel = [fsop.Ssel51R, fsop.Ssel3I, fsop.Ssel19I, fsop.Ssel103I, fsop.Ssel115I, fsop.Ssel35S, fsop.Ssel99S, fsop.Ssel23U, fsop.Ssel55U, fsop.Ssel111U]
        fsop.Mlen_all = [fsop.Mlen51R, fsop.Mlen3I, fsop.Mlen19I, fsop.Mlen103I, fsop.Mlen115I, fsop.Mlen35S, fsop.Mlen99S, fsop.Mlen23U, fsop.Mlen55U, fsop.Mlen111U]
        fsop.Slen_all = [fsop.Slen51R, fsop.Slen3I, fsop.Slen19I, fsop.Slen103I, fsop.Slen115I, fsop.Slen35S, fsop.Slen99S, fsop.Slen23U, fsop.Slen55U, fsop.Slen111U]
        
        
        fsop.Marcnt, fsop.Sarcnt = [0]*len(fsop.Msel), [0]*len(fsop.Ssel)
        fsop.Mtsize, fsop.Stsize = [0]*len(fsop.Msel), [0]*len(fsop.Ssel)
        
        fsop.tot_hashcnt, fsop.tot_size, fsop.tot_arcnt = 0, 0, 0
        fsop.totsize, fsop.totarcnt = [0]*len(fsop.Msel), [0]*len(fsop.Msel)
        
        for sms in range(len(fsop.Msel)):
            fsop.Marcnt[sms], fsop.Sarcnt[sms] = len(fsop.Msel[sms]), len(fsop.Ssel[sms])
            fsop.Mtsize[sms], fsop.Stsize[sms] = fsop.Mlen_all[sms]*fsop.Marcnt[sms], fsop.Slen_all[sms]*fsop.Sarcnt[sms]
            fsop.tot_hashcnt += (fsop.Marcnt[sms]*fsop.MHpar[sms]) + (fsop.Sarcnt[sms]*fsop.SHpar[sms])
            fsop.tot_size += fsop.Mtsize[sms]+fsop.Stsize[sms]
        
        
        fsop.itx = fsop.it*12 #quick fix


        fsop.true_pos = 0
        fsop.false_pos = 0
        fsop.true_neg = 0
        fsop.false_neg = 0
        fsop.Mtn, fsop.Stn, fsop.Ttn = 0,0,0
        
        fsop.ins_len = 10
        fsop.ins = [[] for i in range(fsop.ins_len)]
        fsop.injs = [[] for i in range(fsop.ins_len)]
        fsop.ins[0] = fsop.addr_instr_list
        fsop.ins[1] = fsop.instr_list
        fsop.ins[2] = fsop.addr_list
        fsop.injs[0], fsop.injs[1], fsop.injs[2] = fsop.addr_instr_list_inj, fsop.instr_list_inj, fsop.addr_list_inj 
        
        
        fsop.Mcounter, fsop.Scounter = 0, 0
        fsop.wbv_opc = 0        #wrong but valid opcode
        
        
        for i in range(len(fsop.addr_instr_list)):
            fsop.ins[3].append(fsop.instr_list[i][25:32])        #opcode
            fsop.ins[4].append(fsop.instr_list[i][0:25])          #rest (not opcode)
            fsop.ins[5].append(fsop.instr_list[i][17:20] + fsop.instr_list[i][25:32]) #funct7+opcode
            fsop.ins[6].append(fsop.instr_list[i][0:17] + fsop.instr_list[i][20:25]) #rest (not f3+opc)
            fsop.ins[7].append(fsop.instr_list[i][0:7] + fsop.instr_list[i][17:20] + fsop.instr_list[i][25:32]) #funct7+funct3+opcode
            fsop.ins[8].append(fsop.instr_list[i][7:17] + fsop.instr_list[i][20:25]) #rest (not f7,f3,opc)
            fsop.ins[9].append(fsop.addr_list[i] + fsop.instr_list[i][0:25]) #address+rest (not opcode)
            
            fsop.injs[3].append(fsop.instr_list_inj[i][25:32])        #opcode
            fsop.injs[4].append(fsop.instr_list_inj[i][0:25])          #rest (not opcode)
            fsop.injs[5].append(fsop.instr_list_inj[i][17:20] + fsop.instr_list_inj[i][25:32]) #funct7+opcode
            fsop.injs[6].append(fsop.instr_list_inj[i][0:17] + fsop.instr_list_inj[i][20:25]) #rest (not f3+opc)
            fsop.injs[7].append(fsop.instr_list_inj[i][0:7] + fsop.instr_list_inj[i][17:20] + fsop.instr_list_inj[i][25:32]) #funct7+funct3+opcode
            fsop.injs[8].append(fsop.instr_list_inj[i][7:17] + fsop.instr_list_inj[i][20:25]) #rest (not f7,f3,opc)
            fsop.injs[9].append(fsop.addr_list_inj[i] + fsop.instr_list_inj[i][0:25]) #address+rest (not opcode)
           
        #initialise all arrays 
        fsop.M_ar51R =  np.zeros((fsop.Marcnt[0], fsop.Mlen_all[0]), dtype=bool)
        fsop.M_ar3I =   np.zeros((fsop.Marcnt[1], fsop.Mlen_all[1]), dtype=bool)
        fsop.M_ar19I =  np.zeros((fsop.Marcnt[2], fsop.Mlen_all[2]), dtype=bool)
        fsop.M_ar103I = np.zeros((fsop.Marcnt[3], fsop.Mlen_all[3]), dtype=bool)
        fsop.M_ar115I = np.zeros((fsop.Marcnt[4], fsop.Mlen_all[4]), dtype=bool)
        fsop.M_ar35S =  np.zeros((fsop.Marcnt[5], fsop.Mlen_all[5]), dtype=bool)
        fsop.M_ar99S =  np.zeros((fsop.Marcnt[6], fsop.Mlen_all[6]), dtype=bool)
        fsop.M_ar23U =  np.zeros((fsop.Marcnt[7], fsop.Mlen_all[7]), dtype=bool)
        fsop.M_ar55U =  np.zeros((fsop.Marcnt[8], fsop.Mlen_all[8]), dtype=bool)
        fsop.M_ar111U = np.zeros((fsop.Marcnt[9], fsop.Mlen_all[9]), dtype=bool)
        
        fsop.S_ar51R =  np.zeros((fsop.Sarcnt[0], fsop.Slen_all[0]), dtype=bool)
        fsop.S_ar3I =   np.zeros((fsop.Sarcnt[1], fsop.Slen_all[1]), dtype=bool)
        fsop.S_ar19I =  np.zeros((fsop.Sarcnt[2], fsop.Slen_all[2]), dtype=bool)
        fsop.S_ar103I = np.zeros((fsop.Sarcnt[3], fsop.Slen_all[3]), dtype=bool)
        fsop.S_ar115I = np.zeros((fsop.Sarcnt[4], fsop.Slen_all[4]), dtype=bool)
        fsop.S_ar35S =  np.zeros((fsop.Sarcnt[5], fsop.Slen_all[5]), dtype=bool)
        fsop.S_ar99S =  np.zeros((fsop.Sarcnt[6], fsop.Slen_all[6]), dtype=bool)
        fsop.S_ar23U =  np.zeros((fsop.Sarcnt[7], fsop.Slen_all[7]), dtype=bool)
        fsop.S_ar55U =  np.zeros((fsop.Sarcnt[8], fsop.Slen_all[8]), dtype=bool)
        fsop.S_ar111U = np.zeros((fsop.Sarcnt[9], fsop.Slen_all[9]), dtype=bool)
            


    def insert(fsop):
        for i in range(len(fsop.addr_instr_list)):
            opc = int(fsop.ins[3][i],2)
            Marc, Sarc = 0, 0
            for sms in range(len(fsop.Msel)):       #selects opc_specific array_set required: len(Msel) == len(Ssel)
                for Marc in range(len(fsop.Msel[sms])):
                    for h in range(fsop.MHpar[sms]):
                        RI = fsop.itx + h + Marc*fsop.MHpar[sms] + Sarc*fsop.SHpar[sms]
                        #RI = fsop.itx + h + sms*Marc*fsop.MHpar[sms] + sms*Sarc*fsop.SHpar[sms]
                        index = fsop.multiplyshift(fsop.randnr[RI], fsop.ins[fsop.Msel[sms][Marc]][i], fsop.l, fsop.Mlen_all[sms])
                        if opc is fsop.opclist[sms]:
                            if sms == 0:
                                fsop.M_ar51R[Marc][index] = True
                            elif sms == 1:
                                fsop.M_ar3I[Marc][index] = True
                            elif sms == 2:
                                fsop.M_ar19I[Marc][index] = True
                            elif sms == 3:
                                fsop.M_ar103I[Marc][index] = True
                            elif sms == 4:
                                fsop.M_ar115I[Marc][index] = True
                            elif sms == 5:
                                fsop.M_ar35S[Marc][index] = True
                            elif sms == 6:
                                fsop.M_ar99S[Marc][index] = True
                            elif sms == 7:
                                fsop.M_ar23U[Marc][index] = True
                            elif sms == 8:
                                fsop.M_ar55U[Marc][index] = True
                            elif sms == 9:
                                fsop.M_ar111U[Marc][index] = True
                            else:
                                print(f"M - insert error, sms: {sms}")
                            
                for Sarc in range(len(fsop.Ssel[sms])):
                    for h in range(fsop.SHpar[sms]):
                        RI = fsop.itx + h + Marc*fsop.MHpar[sms] + Sarc*fsop.SHpar[sms]
                        index = fsop.multiplyshift(fsop.randnr[RI], fsop.ins[fsop.Ssel[sms][Sarc]][i], fsop.l, fsop.Slen_all[sms])
                        if opc is fsop.opclist[sms]:
                            if sms == 0:
                                fsop.S_ar51R[Sarc][index] = True
                            elif sms == 1:
                                fsop.S_ar3I[Sarc][index] = True
                            elif sms == 2:
                                fsop.S_ar19I[Sarc][index] = True
                            elif sms == 3:
                                fsop.S_ar103I[Sarc][index] = True
                            elif sms == 4:
                                fsop.S_ar115I[Sarc][index] = True
                            elif sms == 5:
                                fsop.S_ar35S[Sarc][index] = True
                            elif sms == 6:
                                fsop.S_ar99S[Sarc][index] = True
                            elif sms == 7:
                                fsop.S_ar23U[Sarc][index] = True
                            elif sms == 8:
                                fsop.S_ar55U[Sarc][index] = True
                            elif sms == 9:
                                fsop.S_ar111U[Sarc][index] = True
                            else:
                                print(f"S - insert error, sms: {sms}")      #end insertloop
        
        Mfc51R, Mfc3I, Mfc19I, Mfc103I, Mfc115I, Mfc35S, Mfc99S, Mfc23U, Mfc55U, Mfc111U = [], [], [], [], [], [], [], [], [], []
        Sfc51R, Sfc3I, Sfc19I, Sfc103I, Sfc115I, Sfc35S, Sfc99S, Sfc23U, Sfc55U, Sfc111U = [], [], [], [], [], [], [], [], [], []
        
        for sms in range(len(fsop.Msel)):                   #fillcount indiv arrays
            for Marc in range(len(fsop.Msel[sms])):
                if sms == 0:
                    Mfc51R.append(np.count_nonzero(fsop.M_ar51R[Marc]))
                elif sms == 1:
                    Mfc3I.append(np.count_nonzero(fsop.M_ar3I[Marc]))
                elif sms == 2:
                    Mfc19I.append(np.count_nonzero(fsop.M_ar19I[Marc]))
                elif sms == 3:
                    Mfc103I.append(np.count_nonzero(fsop.M_ar103I[Marc]))
                elif sms == 4:
                    Mfc115I.append(np.count_nonzero(fsop.M_ar115I[Marc]))
                elif sms == 5:
                    Mfc35S.append(np.count_nonzero(fsop.M_ar35S[Marc]))
                elif sms == 6:
                    Mfc99S.append(np.count_nonzero(fsop.M_ar99S[Marc]))
                elif sms == 7:
                    Mfc23U.append(np.count_nonzero(fsop.M_ar23U[Marc]))
                elif sms == 8:
                    Mfc55U.append(np.count_nonzero(fsop.M_ar55U[Marc]))
                elif sms == 9:
                    Mfc111U.append(np.count_nonzero(fsop.M_ar111U[Marc]))
                else:
                    print(f"M - insert error, sms: {sms}")
                    
            for Sarc in range(len(fsop.Ssel[sms])):
                if sms == 0:
                    Sfc51R.append(np.count_nonzero(fsop.S_ar51R[Sarc]))
                elif sms == 1:
                    Sfc3I.append(np.count_nonzero(fsop.S_ar3I[Sarc]))
                elif sms == 2:
                    Sfc19I.append(np.count_nonzero(fsop.S_ar19I[Sarc]))
                elif sms == 3:
                    Sfc103I.append(np.count_nonzero(fsop.S_ar103I[Sarc]))
                elif sms == 4:
                    Sfc115I.append(np.count_nonzero(fsop.S_ar115I[Sarc]))
                elif sms == 5:
                    Sfc35S.append(np.count_nonzero(fsop.S_ar35S[Sarc]))
                elif sms == 6:
                    Sfc99S.append(np.count_nonzero(fsop.S_ar99S[Sarc]))
                elif sms == 7:
                    Sfc23U.append(np.count_nonzero(fsop.S_ar23U[Sarc]))
                elif sms == 8:
                    Sfc55U.append(np.count_nonzero(fsop.S_ar55U[Sarc]))
                elif sms == 9:
                    Sfc111U.append(np.count_nonzero(fsop.S_ar111U[Sarc]))
                else:
                    print(f"S - insert error, sms: {sms}")

        Mfc_avg, Sfc_avg = [0]*len(fsop.Msel), [0]*len(fsop.Ssel)
        Mfr_avg, Sfr_avg = [0]*len(fsop.Msel), [0]*len(fsop.Ssel)
        
        Mfc_avg[0], Sfc_avg[0] = round(np.mean(Mfc51R), 6),     round(np.mean(Sfc51R), 6)
        Mfc_avg[1], Sfc_avg[1] = round(np.mean(Mfc3I), 6),      round(np.mean(Sfc3I), 6)
        Mfc_avg[2], Sfc_avg[2] = round(np.mean(Mfc19I), 6),     round(np.mean(Sfc19I), 6)
        Mfc_avg[3], Sfc_avg[3] = round(np.mean(Mfc103I), 6),    round(np.mean(Sfc103I), 6)
        Mfc_avg[4], Sfc_avg[4] = round(np.mean(Mfc115I), 6),    round(np.mean(Sfc115I), 6)
        Mfc_avg[5], Sfc_avg[5] = round(np.mean(Mfc35S), 6),     round(np.mean(Sfc35S), 6)
        Mfc_avg[6], Sfc_avg[6] = round(np.mean(Mfc99S), 6),     round(np.mean(Sfc99S), 6)
        Mfc_avg[7], Sfc_avg[7] = round(np.mean(Mfc23U), 6),     round(np.mean(Sfc23U), 6)
        Mfc_avg[8], Sfc_avg[8] = round(np.mean(Mfc55U), 6),     round(np.mean(Sfc55U), 6)
        Mfc_avg[9], Sfc_avg[9] = round(np.mean(Mfc111U), 6),    round(np.mean(Sfc111U), 6)
        
        Mfr_avg[0], Sfr_avg[0] = round(Mfc_avg[0]/fsop.Mlen_all[0], 6),       round(Sfc_avg[0]/fsop.Slen_all[0], 6)
        Mfr_avg[1], Sfr_avg[1] = round(Mfc_avg[1]/fsop.Mlen_all[1], 6),       round(Sfc_avg[1]/fsop.Slen_all[1], 6)
        Mfr_avg[2], Sfr_avg[2] = round(Mfc_avg[2]/fsop.Mlen_all[2], 6),       round(Sfc_avg[2]/fsop.Slen_all[2], 6)
        Mfr_avg[3], Sfr_avg[3] = round(Mfc_avg[3]/fsop.Mlen_all[3], 6),       round(Sfc_avg[3]/fsop.Slen_all[3], 6)
        Mfr_avg[4], Sfr_avg[4] = round(Mfc_avg[4]/fsop.Mlen_all[4], 6),       round(Sfc_avg[4]/fsop.Slen_all[4], 6)
        Mfr_avg[5], Sfr_avg[5] = round(Mfc_avg[5]/fsop.Mlen_all[5], 6),       round(Sfc_avg[5]/fsop.Slen_all[5], 6)
        Mfr_avg[6], Sfr_avg[6] = round(Mfc_avg[6]/fsop.Mlen_all[6], 6),       round(Sfc_avg[6]/fsop.Slen_all[6], 6)
        Mfr_avg[7], Sfr_avg[7] = round(Mfc_avg[7]/fsop.Mlen_all[7], 6),       round(Sfc_avg[7]/fsop.Slen_all[7], 6)
        Mfr_avg[8], Sfr_avg[8] = round(Mfc_avg[8]/fsop.Mlen_all[8], 6),       round(Sfc_avg[8]/fsop.Slen_all[8], 6)
        Mfr_avg[9], Sfr_avg[9] = round(Mfc_avg[9]/fsop.Mlen_all[9], 6),       round(Sfc_avg[9]/fsop.Slen_all[9], 6)
                
        return Mfc_avg, Sfc_avg, Mfr_avg, Sfr_avg, fsop.Mtsize, fsop.Stsize, fsop.tot_size, fsop.Msel, fsop.Ssel, fsop.MHpar, fsop.SHpar, fsop.Mlen_all, fsop.Slen_all


    def test(fsop):
        opc_mismatch = 0
        for i in range(len(fsop.addr_instr_list_inj)):
            elementpresent = True
            Mpres, Spres, opcpres = True, True, True
            Marc, Sarc = 0, 0
            opcj = int(fsop.injs[3][i],2)
            if opcj in fsop.opclist:
                if opcj != int(fsop.ins[3][i],2):
                    fsop.wbv_opc += 1
                    
                for sms in range(len(fsop.Msel)):
                    for Marc in range(len(fsop.Msel[sms])):
                        for h in range(fsop.MHpar[sms]):
                            RI = fsop.itx + h + Marc*fsop.MHpar[sms] + Sarc*fsop.SHpar[sms]
                            index = fsop.multiplyshift(fsop.randnr[RI], fsop.injs[fsop.Msel[sms][Marc]][i], fsop.l, fsop.Mlen_all[sms])
                            if opcj is fsop.opclist[sms]:
                                if sms == 0:
                                    if fsop.M_ar51R[Marc][index] == False:
                                        elementpresent = False
                                        Mpres = False
                                elif sms == 1:
                                    if fsop.M_ar3I[Marc][index] == False:
                                        elementpresent = False
                                        Mpres = False
                                elif sms == 2:
                                    if fsop.M_ar19I[Marc][index] == False:
                                        elementpresent = False
                                        Mpres = False
                                elif sms == 3:
                                    if fsop.M_ar103I[Marc][index] == False:
                                        elementpresent = False
                                        Mpres = False
                                elif sms == 4:
                                    if fsop.M_ar115I[Marc][index] == False:
                                        elementpresent = False
                                        Mpres = False
                                elif sms == 5:
                                    if fsop.M_ar35S[Marc][index] == False:
                                        elementpresent = False
                                        Mpres = False
                                elif sms == 6:
                                    if fsop.M_ar99S[Marc][index] == False:
                                        elementpresent = False
                                        Mpres = False
                                elif sms == 7:
                                    if fsop.M_ar23U[Marc][index] == False:
                                        elementpresent = False
                                        Mpres = False
                                elif sms == 8:
                                    if fsop.M_ar55U[Marc][index] == False:
                                        elementpresent = False
                                        Mpres = False
                                elif sms == 9:
                                    if fsop.M_ar111U[Marc][index] == False:
                                        elementpresent = False
                                        Mpres = False
                                else:
                                    print(f"M - insert error, sms: {sms}")
                                    
                    for Sarc in range(len(fsop.Ssel[sms])):
                        for h in range(fsop.SHpar[sms]):
                            RI = fsop.itx + h + Marc*fsop.MHpar[sms] + Sarc*fsop.SHpar[sms]
                            index = fsop.multiplyshift(fsop.randnr[RI], fsop.injs[fsop.Ssel[sms][Sarc]][i], fsop.l, fsop.Slen_all[sms])
                            if opcj is fsop.opclist[sms]:
                                if sms == 0:
                                    if fsop.S_ar51R[Sarc][index] == False:
                                        elementpresent = False
                                        Spres = False
                                elif sms == 1:
                                    if fsop.S_ar3I[Sarc][index] == False:
                                        elementpresent = False
                                        Spres = False
                                elif sms == 2:
                                    if fsop.S_ar19I[Sarc][index] == False:
                                        elementpresent = False
                                        Spres = False
                                elif sms == 3:
                                    if fsop.S_ar103I[Sarc][index] == False:
                                        elementpresent = False
                                        Spres = False
                                elif sms == 4:
                                    if fsop.S_ar115I[Sarc][index] == False:
                                        elementpresent = False
                                        Spres = False
                                elif sms == 5:
                                    if fsop.S_ar35S[Sarc][index] == False:
                                        elementpresent = False
                                        Spres = False
                                elif sms == 6:
                                    if fsop.S_ar99S[Sarc][index] == False:
                                        elementpresent = False
                                        Spres = False
                                elif sms == 7:
                                    if fsop.S_ar23U[Sarc][index] == False:
                                        elementpresent = False
                                        Spres = False
                                elif sms == 8:
                                    if fsop.S_ar55U[Sarc][index] == False:
                                        elementpresent = False
                                        Spres = False
                                elif sms == 9:
                                    if fsop.S_ar111U[Sarc][index] == False:
                                        elementpresent = False
                                        Spres = False
                                else:
                                    print(f"S - insert error, sms: {sms}")                          
            else:
                elementpresent = False
                opcpres = False

                                    
            if fsop.addr_instr_list_inj[i] in fsop.addr_instr_list:
                inj_valid = True
            else:
                inj_valid = False
            
            if (elementpresent == True) and (inj_valid == True):
                fsop.true_pos += 1
            elif (elementpresent == True) and (inj_valid == False):
                fsop.false_pos += 1
            elif (elementpresent == False) and (inj_valid == True):
                fsop.false_neg += 1
            elif (elementpresent == False) and (inj_valid == False):
                fsop.true_neg += 1
                if (Mpres == False) and (Spres == False):
                    fsop.Ttn += 1
                elif (Mpres == True) and (Spres == False):
                    fsop.Stn += 1
                elif (Mpres == False) and (Spres == True):
                    fsop.Mtn += 1
                elif opcpres == False:
                    opc_mismatch += 1
                else:
                    print("error fp calculation")
            else:
                print("error") 
        # print(f"wrong but valid opcode count: {fsop.wbv_opc}")  
        return fsop.true_pos, fsop.false_pos, fsop.true_neg, fsop.false_neg, fsop.Mtn, fsop.Stn, fsop.Ttn, opc_mismatch
    
    
    @classmethod
    def multiplyshift(s, init, key, l, mod):
        tmp = int(key)
        mult = mmh3.hash(str(init) + str(tmp))
        return int((mult % 2**64)) %mod