#Author: Frank Kok
#University of Twente 2024
#main file


import sys
import random
import math
from datetime import date
from bitarray import bitarray
from functools import reduce
import numpy as np
from datetime import datetime
random.seed(datetime.now().timestamp())

#files/functions to test
from bf_array import bf_ar
from bf_mx_simple import bf_mxs
from bf_mx_2d_multiple import bf_mx_2dm
from bf_mx_3ds import bf_mx_3d
from bf_mx_sub import bf_mx_sub
from bf_ar_typesort import bf_ar_type
from bf_ar_opcodesort import bf_ar_opcode
from bf_ar_opc_fullsort import bf_ar_fs_opcode
from bf_ar_sets import bf_ar_sets

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
    
    dataselect = 3      #input dataset selector, 3 is recommended
    generate = 0        #whether to generate(1) or read from already generated files(0)
    inj_loc = 1         #fault injection location:   0:all 64b  -   1:instr only (last 32b)
    randnr = []
    list_length = 4000

    if dataselect == 0:     #random
        if generate == 1:
            with open(raw_exe_path + "64b_rand_bin.txt", "w") as f:
                while len(input_list_unique) < list_length:
                    unique_int = random.getrandbits(64)
                    unique_bit = format(unique_int, '064b')
                    if unique_int not in input_list_unique:
                        input_list_unique.append(unique_int)
                        f.write(format(unique_int, '064b') + "\n")
        with open(raw_exe_path + "64b_rand_bin.txt", "r") as file:
            for line in file:
                input_list.append(line.strip())
                
    elif dataselect == 1:       #bad dataset
        if generate == 1:
            memstart_b10 = 2*25 + 2**17 + 2**11 + 2**5 + 2**2
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
        if generate == 1:   #suggestion: add something for memory offset, maybe remove shitty instr's
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
                
    elif dataselect == 3:   #def_coremark   better memory offset
        if generate == 1:
            memstart = 2**19 + 2**17 + 2**16
            with open(raw_exe_path + "coremark_a_i_full.txt", "r") as file:
                for line in file:
                    addr,instr = line.strip().split()
                    #combined_num = line.replace(" ", "").strip()
                    #cm_list.append(combined_num)
                    int_addr = int(addr, 2) + memstart
                    cm_list.append(format(int_addr, '032b') + instr)
                    
            with open(raw_exe_path + "coremark_bin_ShM.txt", "w") as f:
                for line in cm_list:
                    f.write(line + "\n")
        with open (raw_exe_path + "coremark_bin_ShM.txt", "r") as file:
            for line in file:
                input_list.append(line.strip()) 
        
                    
                    
    #split input, assign  
    for i in range(len(input_list)):
        addr_instr_list.append(input_list[i][0:64])
        addr_list.append(input_list[i][0:32])
        instr_list.append(input_list[i][32:64])

    #INJECT and assign  -   flips 1 bit in each input (fault injection)
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
    
    #generate random numbers for seeds for the hashes
    for k in range(len(addr_instr_list)):
        randnr.append(random.randint(0, 2**32 - 1))

    #split instr into opcode and rest
    for l in range (len(instr_list)):
        opcH.append(instr_list[l][25:32])
        restH.append(instr_list[l][0:25])
        opcH_inj.append(instr_list_inj[l][25:32])
        restH_inj.append(instr_list_inj[l][0:25])


    #put all data arrays into "inputs" array
    inputs = []
    inputs = np.array([addr_instr_list, addr_list, instr_list, addr_instr_list_inj, addr_list_inj, instr_list_inj, randnr, opcH, restH, opcH_inj, restH_inj])
    #inputs: 0:addr_instr_list, 1:addr_list, 2:instr_list, 3:addr_instr_list_inj, 4:addr_list_inj, 5:instr_list_inj, 6:randnr, 7:opcH, 8:restH, 9:opcH_inj, 10:restH_inj
    return inputs


#MAIN   -   main function, contains selector for the different tests
#example terminal input(when already in folder): python tester_main.py ./ 100
def main(arguments):    
    raw_exe_path = arguments[1]     #path to tester_main.py
    runcount = int(arguments[2])    #number of runs for each test
    config = []
    selector = [1,0,0,0,0,0,0,0,0]      #selector for which BFs to enable for testing, 1=enable, 0=disable
    #BFAR, BFMXS, BF2DM, BF3DS, BFSUB, BFARTYPE, BFOPCODE, BFOPC_FS, BFSETS
    
    
    #configuration for BFAR(bf_array.py)    (C_mode_ar, C_AC)       - (rest of the BFs are controlled from their own files)
    #C_mode_ar: multiple modes for the BFAR; x= 0:addr+instr, 1:instr, 2:addr (rest see bf_array.py)
    #[x,x,x] number of x's number of arrays     ;       multiple configs possible : [0,0,0,0,0], [0,0,0,1,1], [0,0,0,1,1,1], [1,1,1,1,1,1,1,1]
    C_mode_ar = [0,0,0,0,0], [0,0,0,1,1], [0,0,0,1,1,1], [1,1,1,1,1,1,1,1]
    C_totsize = 30000 #total memory size BFAR
    
    inputs = split_and_inject(raw_exe_path, runcount)
    print(f"runcount: {runcount}")
    
    #___________________________________ START SELECTION ___________________________________
    if selector[0] == 1: #controls BFAR (to run multiple times with different configurations)
        config_ar = []    
        C_AC, C_HPAr, C_arsize = [], [], []
        for i in range(len(C_mode_ar)):
            C_AC.append(len(C_mode_ar[i]))
            C_HPAr.append(1)    #hashes per array
            C_arsize.append(round(C_totsize/len(C_mode_ar[i])))  
        config_index_ar = len(C_mode_ar)
        config_ar = [C_mode_ar, C_AC, C_HPAr, C_arsize]
        
        for c in range(config_index_ar):    #BFAR, loops each config runcount number of times
            print(f"-----------------------------BFAR ; {C_mode_ar[c]}-----------------------------")
            #initialize arrays and variables
            tpar, fpar, tner, fner, tsar, fcar = [], [], [], [], [], []
            artp, arfp, artn, arfn, arts, arfc = [], [], [], [], [], []
            fillrate_indiv = []
            arcount = 0
            arsize = 0
            fr_indiv = []
            fr_indiv_sum = [0]*len(C_mode_ar[c])
            fr_indiv_avg = []
            
            for i in range(runcount):   #runs BFAR "runcount" times, saves results
                bfar = bf_ar(config_ar, inputs, i, c)
                fr_indiv, arcount, arsize, tsar, fcar = bfar.insert()
                tpar, fpar, tner, fner = bfar.test()
                
                artp.append(tpar)   #true positive count
                arfp.append(fpar)   #false positive count
                artn.append(tner)   #true negative count
                arfn.append(fner)   #false negative count
                arts.append(tsar)   #total size
                arfc.append(fcar)   #fillcount
                fillrate_indiv.append(fr_indiv) #fillrate for each array

            #calculate averages
            artp_avg = sum(artp) / runcount
            arfp_avg = sum(arfp) / runcount
            artn_avg = sum(artn) / runcount
            arfn_avg = sum(arfn) / runcount
            ar_fillrate_avg = sum(arfc) / sum(arts)
            
            for j in range(arcount):
                for k in range(runcount):
                    fr_indiv_sum[j] += fillrate_indiv[k][j]
                fr_indiv_avg.append(fr_indiv_sum[j] / runcount)


            #print results
            print(f"avg_tp: {artp_avg}, min,max: {min(artp), max(artp)}")
            print(f"avg_fp: {arfp_avg}, min,max: {min(arfp), max(arfp)}")
            print(f"avg_tn: {artn_avg}, min,max: {min(artn), max(artn)}")
            print(f"avg_fn: {arfn_avg}, min,max: {min(arfn), max(arfn)}")
            print(f"avg_fillrate: {ar_fillrate_avg}, min,max: {min(arfc), max(arfc)}")
            print(f"avg_fillrate_indiv: {fr_indiv_avg}")
            print(f"fpr_avg: {arfp_avg / len(inputs[0])} min,max: {min(arfp) / len(inputs[0]), max(arfp) / len(inputs[0])}")
            print(f"(BFAR) filter size: {arts[0]} -//- {arsize}x{arcount}")       
    
    #===================================================================================================
    #                           REST OF THE BF'S ARE CONTROLLED FROM THEIR OWN FILES
    #                               TOUCHING CODE BELOW MAY BREAK THE TESTER
    #===================================================================================================
    
    
    if selector[1] == 1:
        print("-------------------------------------BFMXS-------------------------------------")
        tpmxs, fpmxs, tnmxs, fnmxs, tsmxs, fcmxs = [], [], [], [], [], []
        mxstp, mxsfp, mxstn, mxsfn, mxsts, mxsfc = [], [], [], [], [], []
        
        for i in range(runcount):
            mxs = bf_mxs(config, inputs, i)
            tsmxs, fcmxs = mxs.insert()
            tpmxs, fpmxs, tnmxs, fnmxs = mxs.test()
            
            mxstp.append(tpmxs)
            mxsfp.append(fpmxs)
            mxstn.append(tnmxs)
            mxsfn.append(fnmxs)
            mxsts.append(tsmxs)
            mxsfc.append(fcmxs)

        mxstp_avg = sum(mxstp) / runcount
        mxsfp_avg = sum(mxsfp) / runcount
        mxstn_avg = sum(mxstn) / runcount
        mxsfn_avg = sum(mxsfn) / runcount
        mxs_fillrate_avg = sum(mxsfc) / sum(mxsts)
        
        print(f"avg_tp: {mxstp_avg}, min,max: {min(mxstp), max(mxstp)}")
        print(f"avg_fp: {mxsfp_avg}, min,max: {min(mxsfp), max(mxsfp)}")
        print(f"avg_tn: {mxstn_avg}, min,max: {min(mxstn), max(mxstn)}")
        print(f"avg_fn: {mxsfn_avg}, min,max: {min(mxsfn), max(mxsfn)}")
        print(f"avg_fillrate: {mxs_fillrate_avg}, min,max: {min(mxsfc), max(mxsfc)}")
        print(f"fpr_avg: {mxsfp_avg / len(inputs[0])} min,max: {min(mxsfp) / len(inputs[0]), max(mxsfp) / len(inputs[0])}")
        print(f"(MXS) filter size: {mxsts[0]}")
    if selector[2] == 1:
        print("-------------------------------------BFMX2DM-------------------------------------")
        tpmx2dm, fpmx2dm, tnmx2dm, fnmx2dm, tsmx2dm, fcmx2dm = [], [], [], [], [], []
        mx2dmtp, mx2dmfp, mx2dmtn, mx2dmfn, mx2dmsts, mx2dmfc = [], [], [], [], [], []
        
        for i in range(runcount):
            mx2dm = bf_mx_2dm(config, inputs, i)
            tsmx2dm, fcmx2dm = mx2dm.insert()
            tpmx2dm, fpmx2dm, tnmx2dm, fnmx2dm = mx2dm.test()
            
            mx2dmtp.append(tpmx2dm)
            mx2dmfp.append(fpmx2dm)
            mx2dmtn.append(tnmx2dm)
            mx2dmfn.append(fnmx2dm)
            mx2dmsts.append(tsmx2dm)
            mx2dmfc.append(fcmx2dm)
            
        mx2dmtp_avg = sum(mx2dmtp) / runcount
        mx2dmfp_avg = sum(mx2dmfp) / runcount
        mx2dmtn_avg = sum(mx2dmtn) / runcount
        mx2dmfn_avg = sum(mx2dmfn) / runcount
        mx2d_fillrate_avg = sum(mx2dmfc) / sum(mx2dmsts)
        
        print(f"avg_tp: {mx2dmtp_avg}, min,max: {min(mx2dmtp), max(mx2dmtp)}")
        print(f"avg_fp: {mx2dmfp_avg}, min,max: {min(mx2dmfp), max(mx2dmfp)}")
        print(f"avg_tn: {mx2dmtn_avg}, min,max: {min(mx2dmtn), max(mx2dmtn)}")
        print(f"avg_fn: {mx2dmfn_avg}, min,max: {min(mx2dmfn), max(mx2dmfn)}")
        print(f"avg_fillrate: {mx2d_fillrate_avg}, min,max: {min(mx2dmfc), max(mx2dmfc)}")
        print(f"fpr_avg: {mx2dmfp_avg / len(inputs[0])} min,max: {min(mx2dmfp) / len(inputs[0]), max(mx2dmfp) / len(inputs[0])}")
        print(f"(MX2DM) filter size: {mx2dmsts[0]}")
    if selector[3] == 1:
        print("-------------------------------------BFMX3D-------------------------------------")
        tpmx3ds, fpmx3ds, tnmx3ds, fnmx3ds, tsmx3ds, fcmx3ds = [], [], [], [], [], []
        mx3dstp, mx3dsfp, mx3dstn, mx3dsfn, mx3dssts, mx3dsfc = [], [], [], [], [], []
        
        for i in range(runcount):
            mx3ds = bf_mx_3d(config, inputs, i)
            tsmx3ds, fcmx3ds = mx3ds.insert()
            tpmx3ds, fpmx3ds, tnmx3ds, fnmx3ds = mx3ds.test()
            
            mx3dstp.append(tpmx3ds)
            mx3dsfp.append(fpmx3ds)
            mx3dstn.append(tnmx3ds)
            mx3dsfn.append(fnmx3ds)
            mx3dssts.append(tsmx3ds)
            mx3dsfc.append(fcmx3ds)
        
        mx3dstp_avg = sum(mx3dstp) / runcount
        mx3dsfp_avg = sum(mx3dsfp) / runcount
        mx3dstn_avg = sum(mx3dstn) / runcount
        mx3dsfn_avg = sum(mx3dsfn) / runcount
        mx3ds_fillrate_avg = sum(mx3dsfc) / sum(mx3dssts)
        
        print(f"avg_tp: {mx3dstp_avg}, min,max: {min(mx3dstp), max(mx3dstp)}")
        print(f"avg_fp: {mx3dsfp_avg}, min,max: {min(mx3dsfp), max(mx3dsfp)}")
        print(f"avg_tn: {mx3dstn_avg}, min,max: {min(mx3dstn), max(mx3dstn)}")
        print(f"avg_fn: {mx3dsfn_avg}, min,max: {min(mx3dsfn), max(mx3dsfn)}")
        print(f"avg_fillrate: {mx3ds_fillrate_avg}, min,max: {min(mx3dsfc), max(mx3dsfc)}")
        print(f"fpr_avg: {mx3dsfp_avg / len(inputs[0])} min,max: {min(mx3dsfp) / len(inputs[0]), max(mx3dsfp) / len(inputs[0])}")
        print(f"(MX3DS) filter size: {mx3dssts[0]}")
    
    if selector[4] == 1:
        print("-------------------------------------bf_mx_sub-------------------------------------")
        tpmxsub, fpmxsub, tnmxsub, fnmxsub, tsmxsub, fcmxsub = [], [], [], [], [], []
        mxsubtp, mxsubfp, mxsubtn, mxsubfn, mxsubsts, mxsubfc = [], [], [], [], [], []
        fillrate_main, fillrate_R, fillrate_I, fillrate_S, fillrate_U = [], [], [], [], []
        size_main, size_R, size_I, size_S, size_U = [], [], [], [], []
        fr_main_single, fr_R_single, fr_I_single, fr_S_single, fr_U_single = [], [], [], [], []

        totalsize = [0]*runcount
        sizes, fillrates = [], []
        
        for i in range(runcount):
            mxsub = bf_mx_sub(config, inputs, i, 0)     #0=> c config_index
            sizes, fillrates = mxsub.insert()           #sizes,fillrates
            tpmxsub, fpmxsub, tnmxsub, fnmxsub = mxsub.test()
            
            mxsubtp.append(tpmxsub)
            mxsubfp.append(fpmxsub)
            mxsubtn.append(tnmxsub)
            mxsubfn.append(fnmxsub)
            
            size_main.append(sizes[0])
            size_R.append(sizes[1])
            size_I.append(sizes[2])
            size_S.append(sizes[3])
            size_U.append(sizes[4])
            fillrate_main.append(fillrates[0])
            fillrate_R.append(fillrates[1])
            fillrate_I.append(fillrates[2])
            fillrate_S.append(fillrates[3])
            fillrate_U.append(fillrates[4])
            for k in range(len(sizes)):
                totalsize[i] += sizes[k][0]
                
            fr_main_single.append(round(np.mean(fillrates[0]) , 5))        #average fillrate for each run
            fr_R_single.append(round(np.mean(fillrates[1]) , 5))
            fr_I_single.append(round(np.mean(fillrates[2]) , 5))
            fr_S_single.append(round(np.mean(fillrates[3]) , 5))
            fr_U_single.append(round(np.mean(fillrates[4]) , 5))
                
        mxsubtp_avg = sum(mxsubtp) / runcount
        mxsubfp_avg = sum(mxsubfp) / runcount
        mxsubtn_avg = sum(mxsubtn) / runcount
        mxsubfn_avg = sum(mxsubfn) / runcount 

        fr_main_avg, fr_R_avg, fr_I_avg, fr_S_avg, fr_U_avg = round(np.mean(fr_main_single) , 5), round(np.mean(fr_R_single) , 5), round(np.mean(fr_I_single) , 5), round(np.mean(fr_S_single) , 5), round(np.mean(fr_U_single) , 5)
            
        totalsize_avg = sum(totalsize) / runcount
                
        print(f"avg_tp: {mxsubtp_avg}, min,max: {min(mxsubtp), max(mxsubtp)}")
        print(f"avg_fp: {mxsubfp_avg}, min,max: {min(mxsubfp), max(mxsubfp)}")
        print(f"avg_tn: {mxsubtn_avg}, min,max: {min(mxsubtn), max(mxsubtn)}")
        print(f"avg_fn: {mxsubfn_avg}, min,max: {min(mxsubfn), max(mxsubfn)}")
        
        print(f"avg_fillrate_main: {fr_main_avg}, min,max: {min(fr_main_single), max(fr_main_single)}")
        print(f"avg_fillrate_R: {fr_R_avg},  min,max: {min(fr_R_single), max(fr_R_single)}")
        print(f"avg_fillrate_I: {fr_I_avg},  min,max: {min(fr_I_single), max(fr_I_single)}")
        print(f"avg_fillrate_S: {fr_S_avg},  min,max: {min(fr_S_single), max(fr_S_single)}")
        print(f"avg_fillrate_U: {fr_U_avg},  min,max: {min(fr_U_single), max(fr_U_single)}")        
        
        print(f"size totals: {totalsize_avg}")
        print(f"size_main (total, indiv): {size_main[0][0]}, {size_main[0][1]}")
        print(f"size_R    (total, indiv): {size_R[0][0]}, {size_R[0][1]}")
        print(f"size_I    (total, indiv): {size_I[0][0]}, {size_I[0][1]}")
        print(f"size_S    (total, indiv): {size_S[0][0]}, {size_S[0][1]}")
        print(f"size_U    (total, indiv): {size_U[0][0]}, {size_U[0][1]}")

    if selector[5] == 1:
        print("-------------------------------------bf_ar_type-------------------------------------")
        art_tp, art_fp, art_tn, art_fn = [], [], [], []
        tp_art, fp_art, tn_art, fn_art = [], [], [], []
        fillrate_main, fillrate_R, fillrate_I, fillrate_S, fillrate_U = [], [], [], [], []
        size_main, size_R, size_I, size_S, size_U = [], [], [], [], []

        
        for i in range(runcount):
            bfart = bf_ar_type(config, inputs, i, 0)
            art_fillrates, art_typesizes, art_totsize, art_sel, art_Hpar, art_len_all = bfart.insert()
            art_tp, art_fp, art_tn, art_fn = bfart.test()
            
            tp_art.append(art_tp)
            fp_art.append(art_fp)
            tn_art.append(art_tn)
            fn_art.append(art_fn)
            fillrate_main.append(art_fillrates[0])
            fillrate_R.append(art_fillrates[1])
            fillrate_I.append(art_fillrates[2])
            fillrate_S.append(art_fillrates[3])
            fillrate_U.append(art_fillrates[4])
            
        art_tp_avg = round(np.mean(tp_art) , 5)
        art_fp_avg = round(np.mean(fp_art) , 5)
        art_tn_avg = round(np.mean(tn_art) , 5)
        art_fn_avg = round(np.mean(fn_art) , 5)
        
        fr_avg_main = round(np.mean(fillrate_main) , 5)
        fr_avg_R = round(np.mean(fillrate_R) , 5)
        fr_avg_I = round(np.mean(fillrate_I) , 5)
        fr_avg_S = round(np.mean(fillrate_S) , 5)
        fr_avg_U = round(np.mean(fillrate_U) , 5)
        
        print(f"avg_tp: {art_tp_avg}, min,max: {min(tp_art), max(tp_art)}")
        print(f"avg_fp: {art_fp_avg}, min,max: {min(fp_art), max(fp_art)}")
        print(f"avg_tn: {art_tn_avg}, min,max: {min(tn_art), max(tn_art)}")
        print(f"avg_fn: {art_fn_avg}, min,max: {min(fn_art), max(fn_art)}")
        
        print(f"avg_fillrate_main: {fr_avg_main}, min,max: {min(fillrate_main), max(fillrate_main)}")
        print(f"avg_fillrate_R: {fr_avg_R},  min,max: {min(fillrate_R), max(fillrate_R)}")
        print(f"avg_fillrate_I: {fr_avg_I},  min,max: {min(fillrate_I), max(fillrate_I)}")
        print(f"avg_fillrate_S: {fr_avg_S},  min,max: {min(fillrate_S), max(fillrate_S)}")
        print(f"avg_fillrate_U: {fr_avg_U},  min,max: {min(fillrate_U), max(fillrate_U)}")
        
        print(f"main size, length, arrcnt, HpAr: {art_typesizes[0]}, {art_len_all[0]}, {art_sel[0]}, {art_Hpar[0]}")
        print(f"R    size, length, arrcnt, HpAr: {art_typesizes[1]}, {art_len_all[1]}, {art_sel[1]}, {art_Hpar[1]}")
        print(f"I    size, length, arrcnt, HpAr: {art_typesizes[2]}, {art_len_all[2]}, {art_sel[2]}, {art_Hpar[2]}")
        print(f"S    size, length, arrcnt, HpAr: {art_typesizes[3]}, {art_len_all[3]}, {art_sel[3]}, {art_Hpar[3]}")
        print(f"U    size, length, arrcnt, HpAr: {art_typesizes[4]}, {art_len_all[4]}, {art_sel[4]}, {art_Hpar[4]}")
        print(f"total size: {art_totsize}")
        
    if selector[6] == 1:
        print("-------------------------------------bf_ar_opcode-------------------------------------")
        arop_tp, arop_fp, arop_tn, arop_fn = [], [], [], []
        tp_arop, fp_arop, tn_arop, fn_arop = [], [], [], []        
        frmain, fr51R, fr3I, fr19I, fr103I, fr115I, fr35S, fr99S, fr23U, fr55U, fr111U = [], [], [], [], [], [], [], [], [], [], []
        szmain, sz51R, sz3I, sz19I, sz103I, sz115I, sz35S, sz99S, sz23U, sz55U, sz111U = [], [], [], [], [], [], [], [], [], [], []
        
        opMtn, opStn, opTtn, opc_mm = [], [], [], []
        Mtn_avg, Stn_avg, Ttn_avg, opcmm_avg = 0,0,0,0
        
        #arop
        for i in range(runcount):
            bfarop = bf_ar_opcode(config, inputs, i, 0)
            arop_fillrates, arop_typesizes, arop_totsize, arop_sel, arop_Hpar, arop_len_all = bfarop.insert()
            arop_tp, arop_fp, arop_tn, arop_fn, arop_Mtn, arop_Stn, arop_Ttn, opcode_mm  = bfarop.test()
            
            tp_arop.append(arop_tp)
            fp_arop.append(arop_fp)
            tn_arop.append(arop_tn)
            fn_arop.append(arop_fn)
            
                            
            opMtn.append(arop_Mtn)
            opStn.append(arop_Stn)
            opTtn.append(arop_Ttn)
            opc_mm.append(opcode_mm)
            
            frmain.append(arop_fillrates[0])
            fr51R.append(arop_fillrates[1])
            fr3I.append(arop_fillrates[2])
            fr19I.append(arop_fillrates[3])
            fr103I.append(arop_fillrates[4])
            fr115I.append(arop_fillrates[5])
            fr35S.append(arop_fillrates[6])
            fr99S.append(arop_fillrates[7])
            fr23U.append(arop_fillrates[8])
            fr55U.append(arop_fillrates[9])
            fr111U.append(arop_fillrates[10])
            
        arop_tp_avg = round(np.mean(tp_arop) , 5)
        arop_fp_avg = round(np.mean(fp_arop) , 5)
        arop_tn_avg = round(np.mean(tn_arop) , 5)
        arop_fn_avg = round(np.mean(fn_arop) , 5)
        
        fravgmain = round(np.mean(frmain) , 5)
        fravg51R = round(np.mean(fr51R) , 5)
        fravg3I = round(np.mean(fr3I) , 5)
        fravg19I = round(np.mean(fr19I) , 5)
        fravg103I = round(np.mean(fr103I) , 5)
        fravg115I = round(np.mean(fr115I) , 5)
        fravg35S = round(np.mean(fr35S) , 5)
        fravg99S = round(np.mean(fr99S) , 5)
        fravg23U = round(np.mean(fr23U) , 5)
        fravg55U = round(np.mean(fr55U) , 5)
        fravg111U = round(np.mean(fr111U) , 5)
        
        Mtn_avg = round(np.mean(opMtn) , 5)
        Stn_avg = round(np.mean(opStn) , 5)
        Ttn_avg = round(np.mean(opTtn) , 5)
        opcmm_avg = round(np.mean(opc_mm) , 5)
        
        
        print(f"avg_tp: {arop_tp_avg}, min,max: {min(tp_arop), max(tp_arop)}")
        print(f"avg_fp: {arop_fp_avg}, min,max: {min(fp_arop), max(fp_arop)}")
        print(f"avg_tn: {arop_tn_avg}, min,max: {min(tn_arop), max(tn_arop)}")
        print(f"avg_fn: {arop_fn_avg}, min,max: {min(fn_arop), max(fn_arop)}")
        
        print(f"avg_Ttn: {Ttn_avg}, min,max: {min(opTtn), max(opTtn)}")
        print(f"avg_Mtn: {Mtn_avg}, min,max: {min(opMtn), max(opMtn)}")
        print(f"avg_Stn: {Stn_avg}, min,max: {min(opStn), max(opStn)}")
        print(f"avg_opcode_mm: {opcmm_avg}")
                
        print(f"avg_fillrate_main:  {fravgmain}, min,max: {min(frmain), max(frmain)}")
        print(f"avg_fillrate_51R:   {fravg51R}, min,max: {min(fr51R), max(fr51R)}")
        print(f"avg_fillrate_3I:    {fravg3I}, min,max: {min(fr3I), max(fr3I)}")
        print(f"avg_fillrate_19I:   {fravg19I}, min,max: {min(fr19I), max(fr19I)}")
        print(f"avg_fillrate_103I:  {fravg103I}, min,max: {min(fr103I), max(fr103I)}")
        print(f"avg_fillrate_115I:  {fravg115I}, min,max: {min(fr115I), max(fr115I)}")
        print(f"avg_fillrate_35S:   {fravg35S}, min,max: {min(fr35S), max(fr35S)}")
        print(f"avg_fillrate_99S:   {fravg99S}, min,max: {min(fr99S), max(fr99S)}")
        print(f"avg_fillrate_23U:   {fravg23U}, min,max: {min(fr23U), max(fr23U)}")
        print(f"avg_fillrate_55U:   {fravg55U}, min,max: {min(fr55U), max(fr55U)}")
        print(f"avg_fillrate_111U:  {fravg111U}, min,max: {min(fr111U), max(fr111U)}")
        
        print(f"main size, length, arrcnt, HpAr: {arop_typesizes[0]}, {arop_len_all[0]}, {arop_sel[0]}, {arop_Hpar[0]}")
        print(f"51R  size, length, arrcnt, HpAr: {arop_typesizes[1]}, {arop_len_all[1]}, {arop_sel[1]}, {arop_Hpar[1]}")
        print(f"3I   size, length, arrcnt, HpAr: {arop_typesizes[2]}, {arop_len_all[2]}, {arop_sel[2]}, {arop_Hpar[2]}")
        print(f"19I  size, length, arrcnt, HpAr: {arop_typesizes[3]}, {arop_len_all[3]}, {arop_sel[3]}, {arop_Hpar[3]}")
        print(f"103I size, length, arrcnt, HpAr: {arop_typesizes[4]}, {arop_len_all[4]}, {arop_sel[4]}, {arop_Hpar[4]}")
        print(f"115I size, length, arrcnt, HpAr: {arop_typesizes[5]}, {arop_len_all[5]}, {arop_sel[5]}, {arop_Hpar[5]}")
        print(f"35S  size, length, arrcnt, HpAr: {arop_typesizes[6]}, {arop_len_all[6]}, {arop_sel[6]}, {arop_Hpar[6]}")
        print(f"99S  size, length, arrcnt, HpAr: {arop_typesizes[7]}, {arop_len_all[7]}, {arop_sel[7]}, {arop_Hpar[7]}")
        print(f"23U  size, length, arrcnt, HpAr: {arop_typesizes[8]}, {arop_len_all[8]}, {arop_sel[8]}, {arop_Hpar[8]}")
        print(f"55U  size, length, arrcnt, HpAr: {arop_typesizes[9]}, {arop_len_all[9]}, {arop_sel[9]}, {arop_Hpar[9]}")
        print(f"111U size, length, arrcnt, HpAr: {arop_typesizes[10]}, {arop_len_all[10]}, {arop_sel[10]}, {arop_Hpar[10]}")
        print(f"total sub size, length: {sum(arop_typesizes)-arop_typesizes[0]}, {sum(arop_len_all)-arop_len_all[0]} ")
        print(f"total size: {arop_totsize}")
        
    if selector[7] == 1:
        print("-------------------------------------bfar_fullsort_opcode-------------------------------------")
        Mfr51R, Mfr3I, Mfr19I, Mfr103I, Mfr115I, Mfr35S, Mfr99S, Mfr23U, Mfr55U, Mfr111U = [], [], [], [], [], [], [], [], [], []
        Sfr51R, Sfr3I, Sfr19I, Sfr103I, Sfr115I, Sfr35S, Sfr99S, Sfr23U, Sfr55U, Sfr111U = [], [], [], [], [], [], [], [], [], []
        
        fsop_Mtn, fsop_Stn, fsop_Ttn, opc_mismatch = [], [], [], []
        Mfc_avg, Sfc_avg, Mfr_avg, Sfr_avg = [], [], [], []
        fsop_Mtsize, fsop_Stsize, fsop_tot_size = [], [], []
        fsop_Msel, fsop_Ssel = [], []
        fsop_MHpar, fsop_SHpar = [], []
        fsop_Mlen_all, fsop_Slen_all = [], []
        fsop_true_pos, fsop_false_pos, fsop_true_neg, fsop_false_neg = [], [], [], []
        fsop_Mtn, fsop_Stn, fsop_Ttn, opc_mismatch  = [], [], [], []
        
        Mfc, Sfc, Mfr, Sfr = [], [], [], []
        tpf, fpf, tnf, fnf = [], [], [], []
        Mtn, Stn, Ttn, opc_mis = [], [], [], []
        
        
        #fsop
        for i in range(runcount):
            bffsop = bf_ar_fs_opcode(config, inputs, i, 0)
            Mfc_avg, Sfc_avg, Mfr_avg, Sfr_avg, fsop_Mtsize, fsop_Stsize, fsop_tot_size, fsop_Msel, fsop_Ssel, fsop_MHpar, fsop_SHpar, fsop_Mlen_all, fsop_Slen_all = bffsop.insert()
            fsop_true_pos, fsop_false_pos, fsop_true_neg, fsop_false_neg, fsop_Mtn, fsop_Stn, fsop_Ttn, opc_mismatch = bffsop.test()
            
            tpf.append(fsop_true_pos)
            fpf.append(fsop_false_pos)
            tnf.append(fsop_true_neg)
            fnf.append(fsop_false_neg)
            
            Mtn.append(fsop_Mtn)
            Stn.append(fsop_Stn)
            Ttn.append(fsop_Ttn)
            opc_mis.append(opc_mismatch)
            
            Mfr51R. append(Mfr_avg[0])
            Mfr3I.  append(Mfr_avg[1])
            Mfr19I. append(Mfr_avg[2])
            Mfr103I.append(Mfr_avg[3])
            Mfr115I.append(Mfr_avg[4])
            Mfr35S. append(Mfr_avg[5])
            Mfr99S. append(Mfr_avg[6])
            Mfr23U. append(Mfr_avg[7])
            Mfr55U. append(Mfr_avg[8])
            Mfr111U.append(Mfr_avg[9])
            
            Sfr51R. append(Sfr_avg[0])
            Sfr3I.  append(Sfr_avg[1])
            Sfr19I. append(Sfr_avg[2])
            Sfr103I.append(Sfr_avg[3])
            Sfr115I.append(Sfr_avg[4])
            Sfr35S. append(Sfr_avg[5])
            Sfr99S. append(Sfr_avg[6])
            Sfr23U. append(Sfr_avg[7])
            Sfr55U. append(Sfr_avg[8])
            Sfr111U.append(Sfr_avg[9])
            
            
        tp_avg = round(np.mean(tpf) , 5)
        fp_avg = round(np.mean(fpf) , 5)
        tn_avg = round(np.mean(tnf) , 5)
        fn_avg = round(np.mean(fnf) , 5)
        
        Mfravg51R =  round(np.mean(Mfr51R) , 5)
        Mfravg3I =   round(np.mean(Mfr3I) , 5)
        Mfravg19I =  round(np.mean(Mfr19I) , 5)
        Mfravg103I = round(np.mean(Mfr103I) , 5)
        Mfravg115I = round(np.mean(Mfr115I) , 5)
        Mfravg35S =  round(np.mean(Mfr35S) , 5)
        Mfravg99S =  round(np.mean(Mfr99S) , 5)
        Mfravg23U =  round(np.mean(Mfr23U) , 5)
        Mfravg55U =  round(np.mean(Mfr55U) , 5)
        Mfravg111U = round(np.mean(Mfr111U) , 5)
        
        Sfravg51R =  round(np.mean(Sfr51R) , 5)
        Sfravg3I =   round(np.mean(Sfr3I) , 5)
        Sfravg19I =  round(np.mean(Sfr19I) , 5)
        Sfravg103I = round(np.mean(Sfr103I) , 5)
        Sfravg115I = round(np.mean(Sfr115I) , 5)
        Sfravg35S =  round(np.mean(Sfr35S) , 5)
        Sfravg99S =  round(np.mean(Sfr99S) , 5)
        Sfravg23U =  round(np.mean(Sfr23U) , 5)
        Sfravg55U =  round(np.mean(Sfr55U) , 5)
        Sfravg111U = round(np.mean(Sfr111U) , 5)
        
        Mtn_avg = round(np.mean(Mtn) , 5)
        Stn_avg = round(np.mean(Stn) , 5)
        Ttn_avg = round(np.mean(Ttn) , 5)
        opc_mis_avg = round(np.mean(opc_mis) , 5)
        
        print(f"avg_tp: {tp_avg}, min,max: {min(tpf), max(tpf)}")
        print(f"avg_fp: {fp_avg}, min,max: {min(fpf), max(fpf)}")
        print(f"avg_tn: {tn_avg}, min,max: {min(tnf), max(tnf)}")
        print(f"avg_fn: {fn_avg}, min,max: {min(fnf), max(fnf)}")
        
        print(f"avg_Ttn: {Ttn_avg}, min,max: {min(Ttn), max(Ttn)}")        
        print(f"avg_Mtn: {Mtn_avg}, min,max: {min(Mtn), max(Mtn)}")
        print(f"avg_Stn: {Stn_avg}, min,max: {min(Stn), max(Stn)}")
        print(f"avg_opc_mis: {opc_mis_avg}, min,max: {min(opc_mis), max(opc_mis)}")
        
        print(f"fravg51R (M,S):  {Mfravg51R} - {Sfravg51R}")
        print(f"fravg3I  (M,S):  {Mfravg3I} - {Sfravg3I}")
        print(f"fravg19I (M,S):  {Mfravg19I} - {Sfravg19I}")
        print(f"fravg103I(M,S):  {Mfravg103I} - {Sfravg103I}")
        print(f"fravg115I(M,S):  {Mfravg115I} - {Sfravg115I}")
        print(f"fravg35S (M,S):  {Mfravg35S} - {Sfravg35S}")
        print(f"fravg99S (M,S):  {Mfravg99S} - {Sfravg99S}")
        print(f"fravg23U (M,S):  {Mfravg23U} - {Sfravg23U}")
        print(f"fravg55U (M,S):  {Mfravg55U} - {Sfravg55U}")
        print(f"fravg111U(M,S):  {Mfravg111U} - {Sfravg111U}")
        
        print(f"R51 (M,S) len - size: {fsop_Mlen_all[0]}, {fsop_Slen_all[0]} - {fsop_Mtsize[0]}, {fsop_Stsize[0]}")
        print(f"3I  (M,S) len - size: {fsop_Mlen_all[1]}, {fsop_Slen_all[1]} - {fsop_Mtsize[1]}, {fsop_Stsize[1]}")
        print(f"19I (M,S) len - size: {fsop_Mlen_all[2]}, {fsop_Slen_all[2]} - {fsop_Mtsize[2]}, {fsop_Stsize[2]}")
        print(f"103I(M,S) len - size: {fsop_Mlen_all[3]}, {fsop_Slen_all[3]} - {fsop_Mtsize[3]}, {fsop_Stsize[3]}")
        print(f"115I(M,S) len - size: {fsop_Mlen_all[4]}, {fsop_Slen_all[4]} - {fsop_Mtsize[4]}, {fsop_Stsize[4]}")
        print(f"35S (M,S) len - size: {fsop_Mlen_all[5]}, {fsop_Slen_all[5]} - {fsop_Mtsize[5]}, {fsop_Stsize[5]}")
        print(f"99S (M,S) len - size: {fsop_Mlen_all[6]}, {fsop_Slen_all[6]} - {fsop_Mtsize[6]}, {fsop_Stsize[6]}")
        print(f"23U (M,S) len - size: {fsop_Mlen_all[7]}, {fsop_Slen_all[7]} - {fsop_Mtsize[7]}, {fsop_Stsize[7]}")
        print(f"55U (M,S) len - size: {fsop_Mlen_all[8]}, {fsop_Slen_all[8]} - {fsop_Mtsize[8]}, {fsop_Stsize[8]}")
        print(f"111U(M,S) len - size: {fsop_Mlen_all[9]}, {fsop_Slen_all[9]} - {fsop_Mtsize[9]}, {fsop_Stsize[9]}")
        print(f"total size: {fsop_tot_size}")
        
        print(f"R51 (M,S) sel - Hpar: {fsop_Msel[0]}, {fsop_Ssel[0]} - {fsop_MHpar[0]}, {fsop_SHpar[0]}")
        print(f"3I  (M,S) sel - Hpar: {fsop_Msel[1]}, {fsop_Ssel[1]} - {fsop_MHpar[1]}, {fsop_SHpar[1]}")
        print(f"19I (M,S) sel - Hpar: {fsop_Msel[2]}, {fsop_Ssel[2]} - {fsop_MHpar[2]}, {fsop_SHpar[2]}")
        print(f"103I(M,S) sel - Hpar: {fsop_Msel[3]}, {fsop_Ssel[3]} - {fsop_MHpar[3]}, {fsop_SHpar[3]}")
        print(f"115I(M,S) sel - Hpar: {fsop_Msel[4]}, {fsop_Ssel[4]} - {fsop_MHpar[4]}, {fsop_SHpar[4]}")
        print(f"35S (M,S) sel - Hpar: {fsop_Msel[5]}, {fsop_Ssel[5]} - {fsop_MHpar[5]}, {fsop_SHpar[5]}")
        print(f"99S (M,S) sel - Hpar: {fsop_Msel[6]}, {fsop_Ssel[6]} - {fsop_MHpar[6]}, {fsop_SHpar[6]}")
        print(f"23U (M,S) sel - Hpar: {fsop_Msel[7]}, {fsop_Ssel[7]} - {fsop_MHpar[7]}, {fsop_SHpar[7]}")
        print(f"55U (M,S) sel - Hpar: {fsop_Msel[8]}, {fsop_Ssel[8]} - {fsop_MHpar[8]}, {fsop_SHpar[8]}")
        print(f"111U(M,S) sel - Hpar: {fsop_Msel[9]}, {fsop_Ssel[9]} - {fsop_MHpar[9]}, {fsop_SHpar[9]}")
        
    if selector[8] == 1:
        print("-------------------------------------bfar_sets-------------------------------------")               
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
            bfset = bf_ar_sets(config, inputs, i, 0)
            
            fc_avg, fr_avg, size_all, tot_size, sel_all, Hpar, len_all, SiU = bfset.insert()
            tp, fp, tn, fn, tn_sets, tnset = bfset.test()
            
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

    