#Author: Frank Kok
#University of Twente 2024

import math
import mmh3
import random
from bitarray import bitarray
from collections import Counter
import numpy as np

class bf_mx_2dm(object):
    def __init__(mx2, config, inputs, i):
        mx2.config = config
        mx2.inputs = inputs
        mx2.it = i
        mx2.addr_instr_list, mx2.addr_list, mx2.instr_list, mx2.addr_instr_list_inj, mx2.addr_list_inj, mx2.instr_list_inj, mx2.randnr, mx2.opcH, mx2.restH, mx2.opcH_inj, mx2.restH_inj = mx2.inputs
        mx2.mode = [2,2,2,2,5,5]     #[x,x,y] x/y is selected inputs, 3 matrices in this case, see the modes in the insert and test functions
        mx2.mxcount = len(mx2.mode)
        mx2.dim = 2     #DONT CHANGE
        
        #matrix depths for different number of matrices
        if mx2.mxcount == 7:
            mx2.depth = 65
        elif mx2.mxcount == 6:
            mx2.depth = 71
        elif mx2.mxcount == 5:
            mx2.depth = 77
        elif mx2.mxcount == 4:
            mx2.depth = 86
        elif mx2.mxcount == 3:
            mx2.depth = 100
        else:
            mx2.depth = 100
            
        mx2.hash_p_item = 1 #number of hashes per item per axis
        mx2.mod = mx2.depth
        mx2.totalsize = mx2.mxcount * mx2.depth**mx2.dim
        mx2.hashcount = mx2.mxcount * mx2.dim * mx2.hash_p_item
        mx2.itx = mx2.it*mx2.mxcount*mx2.dim*mx2.hash_p_item
        mx2.l = 16

        mx2.true_pos = 0
        mx2.false_pos = 0
        mx2.true_neg = 0
        mx2.false_neg = 0

        mx2.fillcount = 0
        mx2.fillrate = 0

        mx2.results = []

        
        if mx2.dim == 2:
            mx2.matrix = np.zeros((mx2.mxcount, mx2.depth, mx2.depth), dtype=bool)
        else:
            print("dimension error")


    def insert(mx2):
        for i in range(len(mx2.addr_instr_list)):
                for j in range(mx2.mxcount):
                        for l in range(mx2.hash_p_item):
                                RI = mx2.itx + l*mx2.dim + j*mx2.hash_p_item
                                if mx2.mode[j] == 0:        #mode determines the input of the hashes
                                    x_coord = mx2.multiplyshift(mx2.randnr[RI], mx2.addr_list[i], mx2.l, mx2.mod)
                                    y_coord = mx2.multiplyshift(mx2.randnr[RI+1], mx2.instr_list[i], mx2.l, mx2.mod)
                                elif mx2.mode[j] == 1:
                                    x_coord = mx2.multiplyshift(mx2.randnr[RI], mx2.addr_instr_list[i], mx2.l, mx2.mod)
                                    y_coord = mx2.multiplyshift(mx2.randnr[RI+1], mx2.addr_instr_list[i], mx2.l, mx2.mod)
                                elif mx2.mode[j] == 2:
                                    x_coord = mx2.multiplyshift(mx2.randnr[RI], mx2.addr_instr_list[i], mx2.l, mx2.mod)
                                    y_coord = mx2.multiplyshift(mx2.randnr[RI+1], mx2.instr_list[i], mx2.l, mx2.mod)
                                elif mx2.mode[j] == 3:  #bad
                                    x_coord = mx2.multiplyshift(mx2.randnr[RI], mx2.addr_instr_list[i], mx2.l, mx2.mod)
                                    y_coord = mx2.multiplyshift(mx2.randnr[RI+1], mx2.addr_list[i], mx2.l, mx2.mod)
                                elif mx2.mode[j] == 4:  #badder
                                    x_coord = mx2.multiplyshift(mx2.randnr[RI], mx2.addr_list[i], mx2.l, mx2.mod)
                                    y_coord = mx2.multiplyshift(mx2.randnr[RI+1], mx2.addr_list[i], mx2.l, mx2.mod)
                                elif mx2.mode[j] == 5:
                                    x_coord = mx2.multiplyshift(mx2.randnr[RI], mx2.instr_list[i], mx2.l, mx2.mod)
                                    y_coord = mx2.multiplyshift(mx2.randnr[RI+1], mx2.instr_list[i], mx2.l, mx2.mod)
                                else:
                                    print("insert error")   
                                mx2.matrix[j][x_coord][y_coord] = True
                            
        mx2.fillcount = np.count_nonzero(mx2.matrix)
        mx2.fillrate = mx2.fillcount / mx2.totalsize
        return mx2.totalsize, mx2.fillcount


    def test(mx2):
        for i in range(len(mx2.addr_instr_list_inj)):
            elementpresent = True
            for j in range(mx2.mxcount):
                    for l in range(mx2.hash_p_item):
                        RI = mx2.itx + l*mx2.dim + j*mx2.hash_p_item
                        if mx2.mode[j] == 0:
                            x_coord = mx2.multiplyshift(mx2.randnr[RI], mx2.addr_list_inj[i], mx2.l, mx2.mod)
                            y_coord = mx2.multiplyshift(mx2.randnr[RI+1], mx2.instr_list_inj[i], mx2.l, mx2.mod)
                        elif mx2.mode[j] == 1:
                            x_coord = mx2.multiplyshift(mx2.randnr[RI], mx2.addr_instr_list_inj[i], mx2.l, mx2.mod)
                            y_coord = mx2.multiplyshift(mx2.randnr[RI+1], mx2.addr_instr_list_inj[i], mx2.l, mx2.mod)
                        elif mx2.mode[j] == 2:
                            x_coord = mx2.multiplyshift(mx2.randnr[RI], mx2.addr_instr_list_inj[i], mx2.l, mx2.mod)
                            y_coord = mx2.multiplyshift(mx2.randnr[RI+1], mx2.instr_list_inj[i], mx2.l, mx2.mod)
                        elif mx2.mode[j] == 3:
                            x_coord = mx2.multiplyshift(mx2.randnr[RI], mx2.addr_instr_list_inj[i], mx2.l, mx2.mod)
                            y_coord = mx2.multiplyshift(mx2.randnr[RI+1], mx2.addr_list_inj[i], mx2.l, mx2.mod)
                        elif mx2.mode[j] == 4:
                            x_coord = mx2.multiplyshift(mx2.randnr[RI], mx2.addr_list_inj[i], mx2.l, mx2.mod)
                            y_coord = mx2.multiplyshift(mx2.randnr[RI+1], mx2.addr_list_inj[i], mx2.l, mx2.mod)
                        elif mx2.mode[j] == 5:
                            x_coord = mx2.multiplyshift(mx2.randnr[RI], mx2.instr_list_inj[i], mx2.l, mx2.mod)
                            y_coord = mx2.multiplyshift(mx2.randnr[RI+1], mx2.instr_list_inj[i], mx2.l, mx2.mod)
                        else:
                            print("test error")
                        
                        
                        if mx2.matrix[j][x_coord][y_coord] == False:
                            elementpresent = False
            
            if mx2.addr_instr_list_inj[i] in mx2.addr_instr_list:
                inj_valid = True
            else:
                inj_valid = False
            
            if (elementpresent == True) and (inj_valid == True):
                mx2.true_pos += 1
            elif (elementpresent == True) and (inj_valid == False):
                mx2.false_pos += 1
            elif (elementpresent == False) and (inj_valid == True):
                mx2.false_neg += 1
            elif (elementpresent == False) and (inj_valid == False):
                mx2.true_neg += 1
            else:
                print("error")

        return mx2.true_pos, mx2.false_pos, mx2.true_neg, mx2.false_neg
    
    @classmethod
    def multiplyshift(s, init, key, l, mod):
        tmp = int(key)
        mult = mmh3.hash(str(init) + str(tmp))
        return int((mult % 2**64)) %mod