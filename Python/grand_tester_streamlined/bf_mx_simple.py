#Author: Frank Kok
#University of Twente 2024

import math
import mmh3
import random
from bitarray import bitarray
from collections import Counter
import numpy as np

class bf_mxs(object):
    def __init__(mxs, config, inputs, i):
        #stuff from tester_main
        mxs.config = config
        mxs.inputs = inputs
        mxs.it = i
        mxs.addr_instr_list, mxs.addr_list, mxs.instr_list, mxs.addr_instr_list_inj, mxs.addr_list_inj, mxs.instr_list_inj, mxs.randnr, mxs.opcH, mxs.restH, mxs.opcH_inj, mxs.restH_inj = mxs.inputs

        #configurable variables:
        mxs.mode = 2        #set mode 0: addr*instr, 1: addr_instr*addr_instr, 2: addr_instr*instr
        mxs.depth = 173     #depth of the matrix, size is depth**2
        mxs.hash_p_item = 1 #number of hashes per item per axis
        
        mxs.mxcount = 1     #number of matrices, multiple matrices better in bf_mx_2d_multiple.py
        mxs.dim = 2         #DONT CHANGE (only 2d implemented)
        mxs.mod = mxs.depth
        mxs.totalsize = mxs.mxcount * mxs.depth**mxs.dim
        mxs.hashcount = mxs.mxcount * mxs.dim * mxs.hash_p_item
        mxs.itx = mxs.it*mxs.mxcount*mxs.dim*mxs.hash_p_item
        mxs.l = 16

        mxs.true_pos = 0
        mxs.false_pos = 0
        mxs.true_neg = 0
        mxs.false_neg = 0

        mxs.fillcount = 0
        mxs.fillrate = 0

        mxs.results = []
        

        
        if mxs.dim == 2:
            mxs.matrix = np.zeros((mxs.mxcount, mxs.depth, mxs.depth), dtype=bool)
        else:
            print("dimension error")
        


    def insert(mxs):
        for i in range(len(mxs.addr_instr_list)):
                for j in range(mxs.mxcount):
                        for l in range(mxs.hash_p_item):
                            if mxs.mode == 0:
                                x_coord = mxs.multiplyshift(mxs.randnr[j+l+mxs.itx], mxs.addr_list[i], mxs.l, mxs.mod)
                                y_coord = mxs.multiplyshift(mxs.randnr[1+j+l+mxs.itx], mxs.instr_list[i], mxs.l, mxs.mod)
                            elif mxs.mode == 1:
                                x_coord = mxs.multiplyshift(mxs.randnr[j+l+mxs.itx], mxs.addr_instr_list[i], mxs.l, mxs.mod)
                                y_coord = mxs.multiplyshift(mxs.randnr[1+j+l+mxs.itx], mxs.addr_instr_list[i], mxs.l, mxs.mod)
                            elif mxs.mode == 2:
                                x_coord = mxs.multiplyshift(mxs.randnr[j+l+mxs.itx], mxs.addr_instr_list[i], mxs.l, mxs.mod)
                                y_coord = mxs.multiplyshift(mxs.randnr[1+j+l+mxs.itx], mxs.instr_list[i], mxs.l, mxs.mod)
                            else:
                                print("insert error")
                                
                            mxs.matrix[j][x_coord][y_coord] = True
                            
        mxs.fillcount = np.count_nonzero(mxs.matrix)
        mxs.fillrate = mxs.fillcount / mxs.totalsize
        return mxs.totalsize, mxs.fillcount


    def test(mxs):
        for i in range(len(mxs.addr_instr_list_inj)):
            elementpresent = True
            for j in range(mxs.mxcount):
                for l in range(mxs.hash_p_item):
                    if mxs.mode == 0:
                        x_coord = mxs.multiplyshift(mxs.randnr[j+l+mxs.itx], mxs.addr_list_inj[i], mxs.l, mxs.mod)
                        y_coord = mxs.multiplyshift(mxs.randnr[1+j+l+mxs.itx], mxs.instr_list_inj[i], mxs.l, mxs.mod)
                    elif mxs.mode == 1:
                        x_coord = mxs.multiplyshift(mxs.randnr[j+l+mxs.itx], mxs.addr_instr_list_inj[i], mxs.l, mxs.mod)
                        y_coord = mxs.multiplyshift(mxs.randnr[1+j+l+mxs.itx], mxs.addr_instr_list_inj[i], mxs.l, mxs.mod)
                    elif mxs.mode == 2:
                        x_coord = mxs.multiplyshift(mxs.randnr[j+l+mxs.itx], mxs.addr_instr_list_inj[i], mxs.l, mxs.mod)
                        y_coord = mxs.multiplyshift(mxs.randnr[1+j+l+mxs.itx], mxs.instr_list_inj[i], mxs.l, mxs.mod)
                    else:
                        print("test error")
                    if mxs.matrix[j][x_coord][y_coord] == False:
                        elementpresent = False
            
            if mxs.addr_instr_list_inj[i] in mxs.addr_instr_list:
                inj_valid = True
            else:
                inj_valid = False
            
            if (elementpresent == True) and (inj_valid == True):
                mxs.true_pos += 1
            elif (elementpresent == True) and (inj_valid == False):
                mxs.false_pos += 1
            elif (elementpresent == False) and (inj_valid == True):
                mxs.false_neg += 1
            elif (elementpresent == False) and (inj_valid == False):
                mxs.true_neg += 1
            else:
                print("error")

        return mxs.true_pos, mxs.false_pos, mxs.true_neg, mxs.false_neg
    
    
    @classmethod
    def multiplyshift(s, init, key, l, mod):
        tmp = int(key)
        mult = mmh3.hash(str(init) + str(tmp))
        return int((mult % 2**64)) %mod