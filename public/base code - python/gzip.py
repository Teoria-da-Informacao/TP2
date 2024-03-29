# Author: Marco Simoes
# Adapted from Java's implementation of Rui Pedro Paiva
# Teoria da Informacao, LEI, 2022

import sys
from typing import Counter

from huffmantree import HuffmanTree


class GZIPHeader:
    ''' class for reading and storing GZIP header fields '''

    ID1 = ID2 = CM = FLG = XFL = OS = 0
    MTIME = []
    lenMTIME = 4
    mTime = 0

    # bits 0, 1, 2, 3 and 4, respectively (remaining 3 bits: reserved)
    FLG_FTEXT = FLG_FHCRC = FLG_FEXTRA = FLG_FNAME = FLG_FCOMMENT = 0   
    
    # FLG_FTEXT --> ignored (usually 0)
    # if FLG_FEXTRA == 1
    XLEN, extraField = [], []
    lenXLEN = 2
    
    # if FLG_FNAME == 1
    fName = ''  # ends when a byte with value 0 is read
    
    # if FLG_FCOMMENT == 1
    fComment = ''   # ends when a byte with value 0 is read
        
    # if FLG_HCRC == 1
    HCRC = []
        
        
    
    def read(self, f):
        ''' reads and processes the Huffman header from file. Returns 0 if no error, -1 otherwise '''

        # ID 1 and 2: fixed values
        self.ID1 = f.read(1)[0]  
        if self.ID1 != 0x1f: return -1 # error in the header
            
        self.ID2 = f.read(1)[0]
        if self.ID2 != 0x8b: return -1 # error in the header
        
        # CM - Compression Method: must be the value 8 for deflate
        self.CM = f.read(1)[0]
        if self.CM != 0x08: return -1 # error in the header
                    
        # Flags
        self.FLG = f.read(1)[0]
        
        # MTIME
        self.MTIME = [0]*self.lenMTIME
        self.mTime = 0
        for i in range(self.lenMTIME):
            self.MTIME[i] = f.read(1)[0]
            self.mTime += self.MTIME[i] << (8 * i)                 
                        
        # XFL (not processed...)
        self.XFL = f.read(1)[0]
        
        # OS (not processed...)
        self.OS = f.read(1)[0]
        
        # --- Check Flags
        self.FLG_FTEXT = self.FLG & 0x01
        self.FLG_FHCRC = (self.FLG & 0x02) >> 1
        self.FLG_FEXTRA = (self.FLG & 0x04) >> 2
        self.FLG_FNAME = (self.FLG & 0x08) >> 3
        self.FLG_FCOMMENT = (self.FLG & 0x10) >> 4
                    
        # FLG_EXTRA
        if self.FLG_FEXTRA == 1:
            # read 2 bytes XLEN + XLEN bytes de extra field
            # 1st byte: LSB, 2nd: MSB
            self.XLEN = [0]*self.lenXLEN
            self.XLEN[0] = f.read(1)[0]
            self.XLEN[1] = f.read(1)[0]
            self.xlen = self.XLEN[1] << 8 + self.XLEN[0]
            
            # read extraField and ignore its values
            self.extraField = f.read(self.xlen)
        
        def read_str_until_0(f):
            s = ''
            while True:
                c = f.read(1)[0]
                if c == 0: 
                    return s
                s += chr(c)
        
        # FLG_FNAME
        if self.FLG_FNAME == 1:
            self.fName = read_str_until_0(f)
        
        # FLG_FCOMMENT
        if self.FLG_FCOMMENT == 1:
            self.fComment = read_str_until_0(f)
        
        # FLG_FHCRC (not processed...)
        if self.FLG_FHCRC == 1:
            self.HCRC = f.read(2)
            
        return 0
            



class GZIP:
    ''' class for GZIP decompressing file (if compressed with deflate) '''

    gzh = None
    gzFile = ''
    fileSize = origFileSize = -1
    numBlocks = 0
    f = None
    

    bits_buffer = 0
    available_bits = 0        

    
    def __init__(self, filename):
        self.gzFile = filename
        self.f = open(filename, 'rb')
        self.f.seek(0,2)
        self.fileSize = self.f.tell()
        self.f.seek(0)

        
    

    def decompress(self):
        ''' main function for decompressing the gzip file with deflate algorithm '''
        
        numBlocks = 0

        # get original file size: size of file before compression
        origFileSize = self.getOrigFileSize()
        print(origFileSize)
        
        # read GZIP header
        error = self.getHeader()
        if error != 0:
            print('Formato invalido!')
            return
        
        # show filename read from GZIP header
        print(self.gzh.fName)
        
        
        # MAIN LOOP - decode block by block
        BFINAL = 0    
        while not BFINAL == 1:    
            
            BFINAL = self.readBits(1)
                            
            BTYPE = self.readBits(2)                    
            if BTYPE != 2:
                print('Error: Block %d not coded with Huffman Dynamic coding' % (numBlocks+1))
                return
            
                                    
            #!--- STUDENTS --- ADD CODE HERE
            # 
            # 

            #? Ex1
            def readBlock():
                HLIT = self.readBits(5) + 257 # Read HLIT
                HDIST = self.readBits(5) + 1 # Read HDIST
                HCLEN = self.readBits(4) + 4 # Read HCLEN
                return HLIT, HDIST, HCLEN

            #? Ex2
            def readLengths(h):
                order = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]
                lengths = [0]*19
                for i in range(h[2]):
                    lengths[order[i]] = self.readBits(3)
                return lengths

            #? Ex3
            def ex3(lengths):
                # bl_count [i] - número de símbolos a serem codificados com i bits
                bl_count = [0]*(max(lengths) + 1)
                dict = Counter(lengths)
                for i in range(len(bl_count)):
                    bl_count[i] = dict[i]
                bl_count[0] = 0

                # next_code [i] - o próximo código livre para o comprimento i
                next_code = [0]*len(bl_count)
                code = 0
                for bits in range(1, len(bl_count)):
                    code = (code + bl_count[bits-1]) << 1
                    next_code[bits] = code

                # code [i] - o código para o símbolo i
                code = [0]*len(lengths)
                for i in range(len(lengths)):
                    lens = lengths[i]
                    if lens != 0:
                        code[i] = next_code[lens]
                        next_code[lens] += 1
                return code

            def toBinary(n, length):
                s = bin(n)[2:] # remove '0b' from the beginning
                return "0" * (length-len(s)) + s # add leading zeros
            
            h = readBlock()
            lengths = readLengths(h)
            print(lengths)

            tree = ex3(lengths)

            hft = HuffmanTree()
            for i in range(len(tree)):
                if lengths[i] > 0:
                    hft.addNode(toBinary(tree[i], lengths[i]), i)
            
            #? Ex4
            def ex4(hft): # hlit
                array = []
                while len(array) < h[0]:
                    bit = self.readBits(1)
                    pos = hft.nextNode(str(bit))
                    if pos >= 0: # is leaf
                        if pos == 16: # copy the previous code length 3 - 6 times
                            n = self.readBits(2) + 3
                            for i in range(n):
                                array.append(array[-1])
                        elif pos == 17: # repeat a code length of 0 for 3 - 10 times
                            n = self.readBits(3) + 3
                            for i in range(n):
                                array.append(0)
                        elif pos == 18: # repeat a code length of 0 for 11 - 138 times
                            n = self.readBits(7) + 11
                            for i in range(n):
                                array.append(0)
                        else:
                            array.append(pos)
                        hft.resetCurNode()
                return array

            lengthsHLIT = ex4(hft)
            print(lengthsHLIT)

            #? Ex5
            def ex5(hft): # hdist
                array = []
                while len(array) < h[1]:
                    bit = self.readBits(1)
                    pos = hft.nextNode(str(bit))
                    if pos >= 0:
                        if pos == 16:
                            n = self.readBits(2) + 3
                            for i in range(n):
                                array.append(array[-1])
                        elif pos == 17:
                            n = self.readBits(3) + 3
                            for i in range(n):
                                array.append(0)
                        elif pos == 18:
                            n = self.readBits(7) + 11
                            for i in range(n):
                                array.append(0)
                        else:
                            array.append(pos)
                        hft.resetCurNode()
                return array

            lengthsHDIST = ex5(hft)
            print(lengthsHDIST)

            #? Ex6
            hfHLIT = ex3(lengthsHLIT)
            print(hfHLIT)
            hfHDIST = ex3(lengthsHDIST)

            #? Ex7
            hlitTree = HuffmanTree()
            for i in range(len(lengthsHLIT)):
                if lengthsHLIT[i] > 0:
                    print(toBinary(hfHLIT[i], lengthsHLIT[i]), i)
                    hlitTree.addNode(toBinary(hfHLIT[i], lengthsHLIT[i]), i)
            print('---------------------------------------------')
            hdistTree = HuffmanTree()
            for i in range(len(lengthsHDIST)):
                if lengthsHDIST[i] > 0:
                    print(toBinary(hfHDIST[i], lengthsHDIST[i]), i)
                    hdistTree.addNode(toBinary(hfHDIST[i], lengthsHDIST[i]), i)

            def descomprimir(hlitTree, hdistTree):
                array = []
                pos = 0
                while pos != 256:
                    length = 0
                    dist = 0
                    bitHLit = self.readBits(1)
                    pos = hlitTree.nextNode(str(bitHLit))
                    if pos >= 0:
                        if pos < 256:
                            array.append(pos)
                        else:
                            length = pos - 257 + 3
                            if 265 <= pos < 285:
                                extraBits = (pos-265)//4 + 1 # calcula o numero de bits extra
                                length = (2**extraBits)*(pos - (261 + 4*extraBits)) + (2**(extraBits + 2) + 3) + self.readBits(extraBits)
                            elif pos == 285:
                                length = 258
                            
                            # Árvore HDIST
                            pos2 = -1
                            while pos2 < 0:
                                bitHDist = self.readBits(1)
                                pos2 = hdistTree.nextNode(str(bitHDist))
                            dist = pos2 + 1
                            if 4 <= pos2 < 30:
                                aux2 = (pos2 // 2) - 1
                                dist = (2**aux2)*(pos2 - (4 + 2*(aux2-1))) + 2**(1+aux2) + 1 + self.readBits(aux2)

                            original = len(array)
                            for i in range(length):
                                array.append(array[original - dist + i])
                            
                            hdistTree.resetCurNode()
                        hlitTree.resetCurNode()
                return(array)
            
            array = descomprimir(hlitTree, hdistTree)
            print(array)
            
            #? Ex8
            output = open(self.gzh.fName, "wb")
            output.write(bytes(array))
            output.close

            # update number of blocks read
            numBlocks += 1
        
        # close file            
        
        self.f.close()    
        print("End: %d block(s) analyzed." % numBlocks)
    
    
    def getOrigFileSize(self):
        ''' reads file size of original file (before compression) - ISIZE '''
        
        # saves current position of file pointer
        fp = self.f.tell()
        
        # jumps to end-4 position
        self.f.seek(self.fileSize-4)
        
        # reads the last 4 bytes (LITTLE ENDIAN)
        sz = 0
        for i in range(4): 
            sz += self.f.read(1)[0] << (8*i)
        
        # restores file pointer to its original position
        self.f.seek(fp)
        
        return sz        
    

    
    def getHeader(self):  
        ''' reads GZIP header'''

        self.gzh = GZIPHeader()
        header_error = self.gzh.read(self.f)
        return header_error
        

    def readBits(self, n, keep=False):
        ''' reads n bits from bits_buffer. if keep = True, leaves bits in the buffer for future accesses '''

        while n > self.available_bits:
            self.bits_buffer = self.f.read(1)[0] << self.available_bits | self.bits_buffer
            self.available_bits += 8
        
        mask = (2**n)-1
        value = self.bits_buffer & mask

        if not keep:
            self.bits_buffer >>= n
            self.available_bits -= n

        return value

if __name__ == '__main__':
    # gets filename from command line if provided
    #fileName = './public/base code - python/FAQ.txt.gz' # mudar isto (para mim tem que ser assim)
    fileName = 'FAQ.txt.gz'
    if len(sys.argv) > 1:
        fileName = sys.argv[1]

    # decompress file
    gz = GZIP(fileName)
    gz.decompress()