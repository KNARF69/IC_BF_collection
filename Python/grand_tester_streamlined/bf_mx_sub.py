#Author: Frank Kok
#University of Twente 2024

import math
import mmh3
import random
from bitarray import bitarray
from collections import Counter
import numpy as np

class bf_mx_sub(object):
    def __init__(mxhy, config, inputs, i, c_index):
        mxhy.l = 16
        mxhy.inputs = inputs
        mxhy.it = i
        mxhy.c_index = c_index
        mxhy.addr_instr_list, mxhy.addr_list, mxhy.instr_list, mxhy.addr_instr_list_inj, mxhy.addr_list_inj, mxhy.instr_list_inj, mxhy.randnr, mxhy.opcH, mxhy.restH, mxhy.opcH_inj, mxhy.restH_inj = mxhy.inputs
        
        
        mxhy.matrix_main = []
        mxhy.matrix_R = []
        mxhy.matrix_I = []
        mxhy.matrix_S = []
        mxhy.matrix_U = []
        
        #config
        mxhy.mx_count = [3,3,3,3,3]     #nr of matrices for main, R, I, S, U
        mxhy.mxHpDim = [1,1,1,1,1]      #hashes per dimension
        mxhy.mx_depth_main = [100,60]   #dimensions of the matrices
        mxhy.mx_depth_R = [19,19]
        mxhy.mx_depth_I = [44,44]
        mxhy.mx_depth_S = [32,32]
        mxhy.mx_depth_U = [26,26]
        mxhy.mx_dim = [len(mxhy.mx_depth_main),len(mxhy.mx_depth_R),len(mxhy.mx_depth_I),len(mxhy.mx_depth_S),len(mxhy.mx_depth_U)]
        
        #select inputs for the two axes of the matrices
        mxhy.sel_main = [0,1]
        mxhy.sel_R = [1,1]
        mxhy.sel_I = [1,1]
        mxhy.sel_S = [1,1]
        mxhy.sel_U = [1,1]
        
        mxhy.totalsize = 0
        mxhy.hashcount = 0
        for i in range(len(mxhy.mx_count)):
            mxhy.hashcount += mxhy.mx_count[i] * mxhy.mx_dim[i] * mxhy.mxHpDim[i]
            
        mxhy.itx = mxhy.it * mxhy.hashcount
        
        mxhy.ins = [[],[],[],[],[], [],[],[],[],[],[],[]]
        mxhy.ins[0] = mxhy.addr_instr_list
        mxhy.ins[1] = mxhy.instr_list
        mxhy.ins[2] = mxhy.addr_list

        mxhy.injs = [[],[],[],[],[],[],[],[],[],[],[],[]]
        mxhy.injs[0] = mxhy.addr_instr_list_inj
        mxhy.injs[1] = mxhy.instr_list_inj
        mxhy.injs[2] = mxhy.addr_list_inj
        
        for i in range(len(mxhy.addr_instr_list)):
            mxhy.ins[3].append(mxhy.instr_list[i][0:7])
            mxhy.ins[4].append(mxhy.instr_list[i][7:12])
            mxhy.ins[5].append(mxhy.instr_list[i][12:17])
            mxhy.ins[6].append(mxhy.instr_list[i][17:20])
            mxhy.ins[7].append(mxhy.instr_list[i][20:25])
            mxhy.ins[8].append(mxhy.instr_list[i][25:32])           #opcode
            
            mxhy.injs[3].append(mxhy.instr_list_inj[i][0:7])
            mxhy.injs[4].append(mxhy.instr_list_inj[i][7:12])
            mxhy.injs[5].append(mxhy.instr_list_inj[i][12:17])
            mxhy.injs[6].append(mxhy.instr_list_inj[i][17:20])
            mxhy.injs[7].append(mxhy.instr_list_inj[i][20:25])
            mxhy.injs[8].append(mxhy.instr_list_inj[i][25:32])      #opcode_inj
            
            mxhy.ins[9].append(mxhy.instr_list[i][17:20] + mxhy.instr_list[i][25:32])
            mxhy.injs[9].append(mxhy.instr_list_inj[i][17:20] + mxhy.instr_list_inj[i][25:32])
            mxhy.ins[10].append(mxhy.instr_list[i][0:17] + mxhy.instr_list[i][20:25])
            mxhy.injs[10].append(mxhy.instr_list_inj[i][0:17] + mxhy.instr_list_inj[i][20:25])
            mxhy.ins[11].append(mxhy.instr_list[i][0:25])
            mxhy.injs[11].append(mxhy.instr_list_inj[i][0:25])
            
        mxhy.opc_R = [51,0]
        mxhy.opc_I = [3,19,103,115]
        mxhy.opc_S = [35,99]
        mxhy.opc_U = [23,55,111]
        
        mxhy.true_pos = 0
        mxhy.false_pos = 0
        mxhy.true_neg = 0
        mxhy.false_neg = 0
        mxhy.fillcount = 0
        mxhy.fillrate = 0
        mxhy.results = []
        
        
        if mxhy.mx_dim[0] == 1:
            mxhy.matrix_main = np.zeros((mxhy.mx_count[0], mxhy.mx_depth_main[0]), dtype=bool)
        elif mxhy.mx_dim[0] == 2:
            mxhy.matrix_main = np.zeros((mxhy.mx_count[0], mxhy.mx_depth_main[0], mxhy.mx_depth_main[1]), dtype=bool)
        elif mxhy.mx_dim[0] == 3:
            mxhy.matrix_main = np.zeros((mxhy.mx_count[0], mxhy.mx_depth_main[0], mxhy.mx_depth_main[1], mxhy.mx_depth_main[2]), dtype=bool)
        else:
            print(f"mxhy.mx_dim[0]:{mxhy.mx_dim[0]} is not supported (init)")
        
        if mxhy.mx_dim[1] == 1:
            mxhy.matrix_R = np.zeros((mxhy.mx_count[1], mxhy.mx_depth_R[0]), dtype=bool)    
        elif mxhy.mx_dim[1] == 2:
            mxhy.matrix_R = np.zeros((mxhy.mx_count[1], mxhy.mx_depth_R[0], mxhy.mx_depth_R[1]), dtype=bool)
        elif mxhy.mx_dim[1] == 3:
            mxhy.matrix_R = np.zeros((mxhy.mx_count[1], mxhy.mx_depth_R[0], mxhy.mx_depth_R[1], mxhy.mx_depth_R[2]), dtype=bool)
        else:
            print(f"mxhy.mx_dim[1]:{mxhy.mx_dim[1]} is not supported (init)")
        
        if mxhy.mx_dim[2] == 1:
            mxhy.matrix_I = np.zeros((mxhy.mx_count[2], mxhy.mx_depth_I[0]), dtype=bool)    
        elif mxhy.mx_dim[2] == 2:
            mxhy.matrix_I = np.zeros((mxhy.mx_count[2], mxhy.mx_depth_I[0], mxhy.mx_depth_I[1]), dtype=bool)
        elif mxhy.mx_dim[2] == 3:
            mxhy.matrix_I = np.zeros((mxhy.mx_count[2], mxhy.mx_depth_I[0], mxhy.mx_depth_I[1], mxhy.mx_depth_I[2]), dtype=bool)
        else:
            print(f"mxhy.mx_dim[2]:{mxhy.mx_dim[2]} is not supported (init)")
        
        if mxhy.mx_dim[3] == 1:
            mxhy.matrix_S = np.zeros((mxhy.mx_count[3], mxhy.mx_depth_S[0]), dtype=bool)    
        elif mxhy.mx_dim[3] == 2:
            mxhy.matrix_S = np.zeros((mxhy.mx_count[3], mxhy.mx_depth_S[0], mxhy.mx_depth_S[1]), dtype=bool)
        elif mxhy.mx_dim[3] == 3:
            mxhy.matrix_S = np.zeros((mxhy.mx_count[3], mxhy.mx_depth_S[0], mxhy.mx_depth_S[1], mxhy.mx_depth_S[2]), dtype=bool)
        else:
            print(f"mxhy.mx_dim[3]:{mxhy.mx_dim[3]} is not supported (init)")
        
        if mxhy.mx_dim[4] == 1:
            mxhy.matrix_U = np.zeros((mxhy.mx_count[4], mxhy.mx_depth_U[0]), dtype=bool)    
        elif mxhy.mx_dim[4] == 2:
            mxhy.matrix_U = np.zeros((mxhy.mx_count[4], mxhy.mx_depth_U[0], mxhy.mx_depth_U[1]), dtype=bool)
        elif mxhy.mx_dim[4] == 3:
            mxhy.matrix_U = np.zeros((mxhy.mx_count[4], mxhy.mx_depth_U[0], mxhy.mx_depth_U[1], mxhy.mx_depth_U[2]), dtype=bool)
        else:
            print(f"mxhy.mx_dim[4]:{mxhy.mx_dim[4]} is not supported (init)")
            
        
    def insert(mxhy):
        for i in range(len(mxhy.addr_instr_list)):
            opc = int(mxhy.ins[8][i],2)
            for mxs in range(2):
                if mxs == 0:
                    coord_m = np.zeros((mxhy.mx_count[0], mxhy.mx_dim[0]), dtype=int)
                    for cx in range(mxhy.mx_count[0]):                          #nr of mx's
                        for dm in range(mxhy.mx_dim[0]):                        #nr of dimensions
                            RI = mxhy.itx + cx*mxhy.mx_dim[0]*2 + dm
                            coord_m[cx][dm] = mxhy.multiplyshift(mxhy.randnr[RI], mxhy.ins[mxhy.sel_main[dm]][i], mxhy.l, mxhy.mx_depth_main[dm])
                        
                        if mxhy.mx_dim[0] == 1:
                            mxhy.matrix_main[cx][coord_m[cx][0]] = True    
                        elif mxhy.mx_dim[0] == 2:
                            mxhy.matrix_main[cx][coord_m[cx][0]][coord_m[cx][1]] = True
                        elif mxhy.mx_dim[0] == 3:
                            mxhy.matrix_main[cx][coord_m[cx][0]][coord_m[cx][1]][coord_m[cx][2]] = True
                        else:
                            print(f"insert error - main")
                            
                elif mxs == 1:
                    if opc in mxhy.opc_R:
                        coord_sub = np.zeros((mxhy.mx_count[1], mxhy.mx_dim[1]), dtype=int)
                        for cx in range(mxhy.mx_count[1]):
                            for dm in range(mxhy.mx_dim[1]):
                                RI = mxhy.itx + cx*mxhy.mx_dim[1]*2 + dm
                                coord_sub[cx][dm] = (mxhy.multiplyshift(mxhy.randnr[RI], mxhy.ins[mxhy.sel_R[dm]][i], mxhy.l, mxhy.mx_depth_R[dm]))
                                
                            if mxhy.mx_dim[1] == 1:
                                mxhy.matrix_R[cx][coord_sub[cx][0]] = True
                            elif mxhy.mx_dim[1] == 2:
                                mxhy.matrix_R[cx][coord_sub[cx][0]][coord_sub[cx][1]] = True
                            elif mxhy.mx_dim[1] == 3:
                                mxhy.matrix_R[cx][coord_sub[cx][0]][coord_sub[cx][1]][coord_sub[cx][2]] = True
                            else:
                                print(f"insert error - R")
                                
                    elif opc in mxhy.opc_I:
                        coord_sub = np.zeros((mxhy.mx_count[2], mxhy.mx_dim[2]), dtype=int)
                        for cx in range(mxhy.mx_count[2]):
                            for dm in range(mxhy.mx_dim[2]):
                                RI = mxhy.itx + cx*mxhy.mx_dim[2]*2 + dm
                                coord_sub[cx][dm] = (mxhy.multiplyshift(mxhy.randnr[RI], mxhy.ins[mxhy.sel_I[dm]][i], mxhy.l, mxhy.mx_depth_I[dm]))
                            
                            if mxhy.mx_dim[2] == 1:
                                mxhy.matrix_I[cx][coord_sub[cx][0]] = True    
                            elif mxhy.mx_dim[2] == 2:
                                mxhy.matrix_I[cx][coord_sub[cx][0]][coord_sub[cx][1]] = True
                            elif mxhy.mx_dim[2] == 3:
                                mxhy.matrix_I[cx][coord_sub[cx][0]][coord_sub[cx][1]][coord_sub[cx][2]] = True
                            else:
                                print(f"insert error - I")
                                
                    elif opc in mxhy.opc_S:
                        coord_sub = np.zeros((mxhy.mx_count[3], mxhy.mx_dim[3]), dtype=int)
                        for cx in range(mxhy.mx_count[3]):
                            for dm in range(mxhy.mx_dim[3]):
                                RI = mxhy.itx + cx*mxhy.mx_dim[3]*2 + dm
                                coord_sub[cx][dm] = (mxhy.multiplyshift(mxhy.randnr[RI], mxhy.ins[mxhy.sel_S[dm]][i], mxhy.l, mxhy.mx_depth_S[dm]))
                            
                            if mxhy.mx_dim[3] == 1:
                                mxhy.matrix_S[cx][coord_sub[cx][0]] = True
                            elif mxhy.mx_dim[3] == 2:
                                mxhy.matrix_S[cx][coord_sub[cx][0]][coord_sub[cx][1]] = True
                            elif mxhy.mx_dim[3] == 3:
                                mxhy.matrix_S[cx][coord_sub[cx][0]][coord_sub[cx][1]][coord_sub[cx][2]] = True
                            else:
                                print(f"insert error - S")
                        
                    elif opc in mxhy.opc_U:
                        coord_sub = np.zeros((mxhy.mx_count[4], mxhy.mx_dim[4]), dtype=int)
                        for cx in range(mxhy.mx_count[4]):
                            for dm in range(mxhy.mx_dim[4]):
                                RI = mxhy.itx + cx*mxhy.mx_dim[4]*2 + dm
                                coord_sub[cx][dm] = (mxhy.multiplyshift(mxhy.randnr[RI], mxhy.ins[mxhy.sel_U[dm]][i], mxhy.l, mxhy.mx_depth_U[dm]))
                            
                            if mxhy.mx_dim[4] == 1:
                                mxhy.matrix_U[cx][coord_sub[cx][0]] = True    
                            elif mxhy.mx_dim[4] == 2:
                                mxhy.matrix_U[cx][coord_sub[cx][0]][coord_sub[cx][1]] = True
                            elif mxhy.mx_dim[4] == 3:
                                mxhy.matrix_U[cx][coord_sub[cx][0]][coord_sub[cx][1]][coord_sub[cx][2]] = True
                            else:
                                print(f"insert error - U")

                    else:
                        print("insert error - opc selection")
                        

        fillcount_main = np.zeros(mxhy.mx_count[0], dtype=int)
        fillcount_R = np.zeros(mxhy.mx_count[1], dtype=int)
        fillcount_I = np.zeros(mxhy.mx_count[2], dtype=int)
        fillcount_S = np.zeros(mxhy.mx_count[3], dtype=int)
        fillcount_U = np.zeros(mxhy.mx_count[4], dtype=int)	

        mxhy.fillrate_main = np.zeros(mxhy.mx_count[0], dtype=float)
        mxhy.fillrate_R = np.zeros(mxhy.mx_count[1], dtype=float)
        mxhy.fillrate_I = np.zeros(mxhy.mx_count[2], dtype=float)
        mxhy.fillrate_S = np.zeros(mxhy.mx_count[3], dtype=float)
        mxhy.fillrate_U = np.zeros(mxhy.mx_count[4], dtype=float)
        
        mainsize = mxhy.mx_depth_main[0] * mxhy.mx_depth_main[1]
        Rsize = mxhy.mx_depth_R[0] * mxhy.mx_depth_R[1]
        Isize = mxhy.mx_depth_I[0] * mxhy.mx_depth_I[1]
        Ssize = mxhy.mx_depth_S[0] * mxhy.mx_depth_S[1]
        Usize = mxhy.mx_depth_U[0] * mxhy.mx_depth_U[1]
        
        mxhy.size_main = [mainsize*mxhy.mx_count[0], mainsize]
        mxhy.size_R = [Rsize*mxhy.mx_count[1], Rsize]
        mxhy.size_I = [Isize*mxhy.mx_count[2], Isize]
        mxhy.size_S = [Ssize*mxhy.mx_count[3], Ssize]
        mxhy.size_U = [Usize*mxhy.mx_count[4], Usize]
        mxhy.sizes = [mxhy.size_main, mxhy.size_R, mxhy.size_I, mxhy.size_S, mxhy.size_U]

        for j in range(mxhy.mx_count[0]):
            fillcount_main[j] = np.count_nonzero(mxhy.matrix_main[j])
            mxhy.fillrate_main[j] = round(fillcount_main[j] / (mainsize), 6)
        for j in range(mxhy.mx_count[1]):
            fillcount_R[j] = np.count_nonzero(mxhy.matrix_R[j])
            mxhy.fillrate_R[j] = round(fillcount_R[j] / (Rsize), 6)
        for j in range(mxhy.mx_count[2]):
            fillcount_I[j] = np.count_nonzero(mxhy.matrix_I[j])
            mxhy.fillrate_I[j] = round(fillcount_I[j] / (Isize), 6)
        for j in range(mxhy.mx_count[3]):
            fillcount_S[j] = np.count_nonzero(mxhy.matrix_S[j])
            mxhy.fillrate_S[j] = round(fillcount_S[j] / (Ssize), 6)
        for j in range(mxhy.mx_count[4]):
            fillcount_U[j] = np.count_nonzero(mxhy.matrix_U[j])
            mxhy.fillrate_U[j] = round(fillcount_U[j] / (Usize), 6)
            
        mxhy.fillrates = [mxhy.fillrate_main, mxhy.fillrate_R, mxhy.fillrate_I, mxhy.fillrate_S, mxhy.fillrate_U]
            
        return mxhy.sizes, mxhy.fillrates


    def test(mxhy):
        for i in range(len(mxhy.addr_instr_list_inj)):
            elementpresent = True
            opcj = int(mxhy.injs[8][i],2)
            for mxs in range(2):
                if mxs == 0:
                    coord_m = np.zeros((mxhy.mx_count[0], mxhy.mx_dim[0]), dtype=int)
                    for cx in range(mxhy.mx_count[0]):                          #nr of mx's
                        for dm in range(mxhy.mx_dim[0]):                        #nr of dimensions
                            RI = mxhy.itx + cx*mxhy.mx_dim[0]*2 + dm
                            coord_m[cx][dm] = (mxhy.multiplyshift(mxhy.randnr[RI], mxhy.injs[mxhy.sel_main[dm]][i], mxhy.l, mxhy.mx_depth_main[dm]))
                        
                        if mxhy.mx_dim[0] == 1:
                            if mxhy.matrix_main[cx][coord_m[cx][0]] == False:
                                elementpresent = False    
                        elif mxhy.mx_dim[0] == 2:
                            if mxhy.matrix_main[cx][coord_m[cx][0]][coord_m[cx][1]] == False:
                                elementpresent = False
                        elif mxhy.mx_dim[0] == 3:
                            if mxhy.matrix_main[cx][coord_m[cx][0]][coord_m[cx][1]][coord_m[cx][2]] == False:
                                elementpresent = False
                        else:
                            print(f"test error - main")
                            
                elif mxs == 1:
                    if opcj in mxhy.opc_R:
                        coord_sub = np.zeros((mxhy.mx_count[1], mxhy.mx_dim[1]), dtype=int)
                        for cx in range(mxhy.mx_count[1]):
                            for dm in range(mxhy.mx_dim[1]):
                                RI = mxhy.itx + cx*mxhy.mx_dim[1]*2 + dm
                                coord_sub[cx][dm] = (mxhy.multiplyshift(mxhy.randnr[RI], mxhy.injs[mxhy.sel_R[dm]][i], mxhy.l, mxhy.mx_depth_R[dm]))
                                
                            if mxhy.mx_dim[1] == 1:
                                if mxhy.matrix_R[cx][coord_sub[cx][0]] == False:
                                    elementpresent = False
                            elif mxhy.mx_dim[1] == 2:
                                if mxhy.matrix_R[cx][coord_sub[cx][0]][coord_sub[cx][1]] == False:
                                    elementpresent = False
                            elif mxhy.mx_dim[1] == 3:
                                if mxhy.matrix_R[cx][coord_sub[cx][0]][coord_sub[cx][1]][coord_sub[cx][2]] == False:
                                    elementpresent = False
                            else:
                                print(f"test error - R")
                                
                    elif opcj in mxhy.opc_I:
                        coord_sub = np.zeros((mxhy.mx_count[2], mxhy.mx_dim[2]), dtype=int)
                        for cx in range(mxhy.mx_count[2]):
                            for dm in range(mxhy.mx_dim[2]):
                                RI = mxhy.itx + cx*mxhy.mx_dim[2]*2 + dm
                                coord_sub[cx][dm] = (mxhy.multiplyshift(mxhy.randnr[RI], mxhy.injs[mxhy.sel_I[dm]][i], mxhy.l, mxhy.mx_depth_I[dm]))
                                
                            if mxhy.mx_dim[2] == 1:
                                if mxhy.matrix_I[cx][coord_sub[cx][0]] == False:
                                    elementpresent = False
                            elif mxhy.mx_dim[2] == 2:
                                if mxhy.matrix_I[cx][coord_sub[cx][0]][coord_sub[cx][1]] == False:
                                    elementpresent = False
                            elif mxhy.mx_dim[2] == 3:
                                if mxhy.matrix_I[cx][coord_sub[cx][0]][coord_sub[cx][1]][coord_sub[cx][2]] == False:
                                    elementpresent = False
                            else:
                                print(f"test error - I")
                                
                    elif opcj in mxhy.opc_S:
                        coord_sub = np.zeros((mxhy.mx_count[3], mxhy.mx_dim[3]), dtype=int)
                        for cx in range(mxhy.mx_count[3]):
                            for dm in range(mxhy.mx_dim[3]):
                                RI = mxhy.itx + cx*mxhy.mx_dim[3]*2 + dm
                                coord_sub[cx][dm] = (mxhy.multiplyshift(mxhy.randnr[RI], mxhy.injs[mxhy.sel_S[dm]][i], mxhy.l, mxhy.mx_depth_S[dm]))
                            
                            if mxhy.mx_dim[3] == 1:
                                if mxhy.matrix_S[cx][coord_sub[cx][0]] == False:
                                    elementpresent = False
                            elif mxhy.mx_dim[3] == 2:
                                if mxhy.matrix_S[cx][coord_sub[cx][0]][coord_sub[cx][1]] == False:
                                    elementpresent = False
                            elif mxhy.mx_dim[3] == 3:
                                if mxhy.matrix_S[cx][coord_sub[cx][0]][coord_sub[cx][1]][coord_sub[cx][2]] == False:
                                    elementpresent = False
                            else:
                                print(f"test error - S")
                                
                    elif opcj in mxhy.opc_U:
                        coord_sub = np.zeros((mxhy.mx_count[4], mxhy.mx_dim[4]), dtype=int)
                        for cx in range(mxhy.mx_count[4]):
                            for dm in range(mxhy.mx_dim[4]):
                                RI = mxhy.itx + cx*mxhy.mx_dim[4]*2 + dm
                                coord_sub[cx][dm] = (mxhy.multiplyshift(mxhy.randnr[RI], mxhy.injs[mxhy.sel_U[dm]][i], mxhy.l, mxhy.mx_depth_U[dm]))
                            
                            if mxhy.mx_dim[4] == 1:
                                if mxhy.matrix_U[cx][coord_sub[cx][0]] == False:
                                    elementpresent = False    
                            elif mxhy.mx_dim[4] == 2:
                                if mxhy.matrix_U[cx][coord_sub[cx][0]][coord_sub[cx][1]] == False:
                                    elementpresent = False
                            elif mxhy.mx_dim[4] == 3:
                                if mxhy.matrix_U[cx][coord_sub[cx][0]][coord_sub[cx][1]][coord_sub[cx][2]] == False:
                                    elementpresent = False
                            else:
                                print(f"test error - U")

            if mxhy.addr_instr_list_inj[i] in mxhy.addr_instr_list:
                inj_valid = True
            else:
                inj_valid = False
            
            if (elementpresent == True) and (inj_valid == True):
                mxhy.true_pos += 1
            elif (elementpresent == True) and (inj_valid == False):
                mxhy.false_pos += 1
            elif (elementpresent == False) and (inj_valid == True):
                mxhy.false_neg += 1
            elif (elementpresent == False) and (inj_valid == False):
                mxhy.true_neg += 1
            else:
                print("error")

        return mxhy.true_pos, mxhy.false_pos, mxhy.true_neg, mxhy.false_neg
    

    @classmethod
    def multiplyshift(s, init, key, l, mod):
        tmp = int(key)
        mult = mmh3.hash(str(init) + str(tmp))
        return int((mult % 2**64)) %mod