#Author: Frank Kok
#University of Twente 2024

import math
import mmh3
import random
from bitarray import bitarray
from collections import Counter
import numpy as np

class bf_mx_3d(object):
    def __init__(m3x, config, inputs, i):
        m3x.config = config
        m3x.inputs = inputs
        m3x.it = i
        m3x.addr_instr_list, m3x.addr_list, m3x.instr_list, m3x.addr_instr_list_inj, m3x.addr_list_inj, m3x.instr_list_inj, m3x.randnr, m3x.opcH, m3x.restH, m3x.opcH_inj, m3x.restH_inj = m3x.inputs
        m3x.mode = [2,2,3,3,3,3]     #same as 2D, but more modes available
        m3x.mxcount = len(m3x.mode) #1
        m3x.dim = 3     #DONT CHANGE
        if m3x.mxcount == 1:
            m3x.depth = 31
        elif m3x.mxcount == 2:
            m3x.depth = 24
        elif m3x.mxcount == 3:
            m3x.depth = 21
        elif m3x.mxcount == 4:
            m3x.depth = 19
        elif m3x.mxcount == 5:
            m3x.depth = 18
        elif m3x.mxcount == 6:
            m3x.depth = 17
        else:
            m3x.depth = 20
        #m3x.depth = 32#31#25#20#24#55
        m3x.hash_p_item = 1#2#1#2
        m3x.mod = m3x.depth
        m3x.totalsize = m3x.mxcount * m3x.depth**m3x.dim
        m3x.hashcount = m3x.mxcount * m3x.dim * m3x.hash_p_item
        m3x.itx = m3x.it*m3x.mxcount*m3x.dim*m3x.hash_p_item
        m3x.l = 16

        m3x.true_pos = 0
        m3x.false_pos = 0
        m3x.true_neg = 0
        m3x.false_neg = 0

        m3x.fillcount = 0
        m3x.fillrate = 0

        m3x.results = []
        
        if m3x.dim == 3:
            m3x.matrix = np.zeros((m3x.mxcount, m3x.depth, m3x.depth, m3x.depth), dtype=bool)
        else:
            print("dimension error")
        


    def insert(m3x):
        for i in range(len(m3x.addr_instr_list)):
                for j in range(m3x.mxcount):
                        for l in range(m3x.hash_p_item):
                            RI = m3x.itx + j*(m3x.dim + m3x.hash_p_item) + l
                            if m3x.mode[j] == 0:
                                x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.addr_list[i], m3x.l, m3x.mod)
                                y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.instr_list[i], m3x.l, m3x.mod)
                                z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.addr_instr_list[i], m3x.l, m3x.mod)
                            elif m3x.mode[j] == 1:
                                x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.addr_instr_list[i], m3x.l, m3x.mod)
                                y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.addr_instr_list[i], m3x.l, m3x.mod)
                                z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.addr_instr_list[i], m3x.l, m3x.mod)
                            elif m3x.mode[j] == 2:
                                x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.instr_list[i], m3x.l, m3x.mod)
                                y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.instr_list[i], m3x.l, m3x.mod)
                                z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.instr_list[i], m3x.l, m3x.mod)
                            elif m3x.mode[j] == 3:
                                x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.instr_list[i], m3x.l, m3x.mod)
                                y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.instr_list[i], m3x.l, m3x.mod)
                                z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.addr_instr_list[i], m3x.l, m3x.mod)
                            elif m3x.mode[j] == 4:
                                x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.instr_list[i], m3x.l, m3x.mod)
                                y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.addr_instr_list[i], m3x.l, m3x.mod)
                                z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.addr_instr_list[i], m3x.l, m3x.mod)
                            elif m3x.mode[j] == 5:
                                x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.instr_list[i], m3x.l, m3x.mod)
                                y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.instr_list[i], m3x.l, m3x.mod)
                                z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.addr_list[i], m3x.l, m3x.mod)
                            elif m3x.mode[j] == 6:
                                x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.opcH[i], m3x.l, m3x.mod)
                                y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.restH[i], m3x.l, m3x.mod)
                                z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.addr_instr_list[i], m3x.l, m3x.mod)
                            elif m3x.mode[j] == 7:
                                x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.opcH[i], m3x.l, m3x.mod)
                                y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.restH[i], m3x.l, m3x.mod)
                                z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.instr_list[i], m3x.l, m3x.mod)
                            elif m3x.mode[j] == 8:
                                x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.opcH[i], m3x.l, m3x.mod)
                                y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.restH[i], m3x.l, m3x.mod)
                                z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.restH[i], m3x.l, m3x.mod)
                            elif m3x.mode[j] == 9:
                                x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.opcH[i], m3x.l, m3x.mod)
                                y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.restH[i][0:12], m3x.l, m3x.mod)
                                z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.restH[i][12:25], m3x.l, m3x.mod)
                            elif m3x.mode[j] == 10:
                                x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.opcH[i], m3x.l, m3x.mod)
                                y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.instr_list[i], m3x.l, m3x.mod)
                                z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.instr_list[i], m3x.l, m3x.mod)
                            elif m3x.mode[j] == 11:
                                x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.opcH[i], m3x.l, m3x.mod)
                                y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.addr_instr_list[i], m3x.l, m3x.mod)
                                z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.addr_instr_list[i], m3x.l, m3x.mod)
                            elif m3x.mode[j] == 12:
                                x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.opcH[i], m3x.l, m3x.mod)
                                y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.addr_instr_list[i], m3x.l, m3x.mod)
                                z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.instr_list[i], m3x.l, m3x.mod)
                            else:
                                print("insert error")
                                  
                            m3x.matrix[j][x_coord][y_coord][z_coord] = True
                            
        m3x.fillcount = np.count_nonzero(m3x.matrix)
        m3x.fillrate = m3x.fillcount / m3x.totalsize
        return m3x.totalsize, m3x.fillcount


    def test(m3x):
        for i in range(len(m3x.addr_instr_list_inj)):
            elementpresent = True
            for j in range(m3x.mxcount):
                    for l in range(m3x.hash_p_item):
                        RI = m3x.itx + j*(m3x.dim + m3x.hash_p_item) + l
                        if m3x.mode[j] == 0:
                            x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.addr_list_inj[i], m3x.l, m3x.mod)
                            y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.instr_list_inj[i], m3x.l, m3x.mod)
                            z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.addr_instr_list_inj[i], m3x.l, m3x.mod)
                        elif m3x.mode[j] == 1:
                            x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.addr_instr_list_inj[i], m3x.l, m3x.mod)
                            y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.addr_instr_list_inj[i], m3x.l, m3x.mod)
                            z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.addr_instr_list_inj[i], m3x.l, m3x.mod)
                        elif m3x.mode[j] == 2:
                            x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.instr_list_inj[i], m3x.l, m3x.mod)
                            y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.instr_list_inj[i], m3x.l, m3x.mod)
                            z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.instr_list_inj[i], m3x.l, m3x.mod)
                        elif m3x.mode[j] == 3:
                            x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.instr_list_inj[i], m3x.l, m3x.mod)
                            y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.instr_list_inj[i], m3x.l, m3x.mod)
                            z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.addr_instr_list_inj[i], m3x.l, m3x.mod)
                        elif m3x.mode[j] == 4:
                            x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.instr_list_inj[i], m3x.l, m3x.mod)
                            y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.addr_instr_list_inj[i], m3x.l, m3x.mod)
                            z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.addr_instr_list_inj[i], m3x.l, m3x.mod)
                        elif m3x.mode[j] == 5:
                            x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.instr_list_inj[i], m3x.l, m3x.mod)
                            y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.instr_list_inj[i], m3x.l, m3x.mod)
                            z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.addr_list_inj[i], m3x.l, m3x.mod)
                        elif m3x.mode[j] == 6:
                            x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.opcH_inj[i], m3x.l, m3x.mod)
                            y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.restH_inj[i], m3x.l, m3x.mod)
                            z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.addr_instr_list_inj[i], m3x.l, m3x.mod)
                        elif m3x.mode[j] == 7:
                            x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.opcH_inj[i], m3x.l, m3x.mod)
                            y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.restH_inj[i], m3x.l, m3x.mod)
                            z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.instr_list_inj[i], m3x.l, m3x.mod)
                        elif m3x.mode[j] == 8:
                            x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.opcH_inj[i], m3x.l, m3x.mod)
                            y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.restH_inj[i], m3x.l, m3x.mod)
                            z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.restH_inj[i], m3x.l, m3x.mod)
                        elif m3x.mode[j] == 9:
                            x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.opcH_inj[i], m3x.l, m3x.mod)
                            y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.restH_inj[i][0:12], m3x.l, m3x.mod)
                            z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.restH_inj[i][12:25], m3x.l, m3x.mod)
                        elif m3x.mode[j] == 10:
                            x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.opcH_inj[i], m3x.l, m3x.mod)
                            y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.instr_list_inj[i], m3x.l, m3x.mod)
                            z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.instr_list_inj[i], m3x.l, m3x.mod)
                        elif m3x.mode[j] == 11:
                            x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.opcH_inj[i], m3x.l, m3x.mod)
                            y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.addr_instr_list_inj[i], m3x.l, m3x.mod)
                            z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.addr_instr_list_inj[i], m3x.l, m3x.mod)
                        elif m3x.mode[j] == 12:
                            x_coord = m3x.multiplyshift(m3x.randnr[RI], m3x.opcH_inj[i], m3x.l, m3x.mod)
                            y_coord = m3x.multiplyshift(m3x.randnr[RI+1], m3x.addr_instr_list_inj[i], m3x.l, m3x.mod)
                            z_coord = m3x.multiplyshift(m3x.randnr[RI+2], m3x.instr_list_inj[i], m3x.l, m3x.mod)
                        else:
                            print("insert error")
                            
                        if m3x.matrix[j][x_coord][y_coord][z_coord] == False:
                            elementpresent = False

            
            if m3x.addr_instr_list_inj[i] in m3x.addr_instr_list:
                inj_valid = True
            else:
                inj_valid = False
            
            if (elementpresent == True) and (inj_valid == True):
                m3x.true_pos += 1
            elif (elementpresent == True) and (inj_valid == False):
                m3x.false_pos += 1
            elif (elementpresent == False) and (inj_valid == True):
                m3x.false_neg += 1
            elif (elementpresent == False) and (inj_valid == False):
                m3x.true_neg += 1
            else:
                print("error")

        return m3x.true_pos, m3x.false_pos, m3x.true_neg, m3x.false_neg
    
    
    @classmethod
    def multiplyshift(s, init, key, l, mod):
        tmp = int(key)
        mult = mmh3.hash(str(init) + str(tmp))
        return int((mult % 2**64)) %mod