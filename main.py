import numpy as np

'''
1. Crie um método que leia o formato do bloco (i.e., devolva o valor
correspondente a HLIT, HDIST e HCLEN), de acordo com a estrutura de
cada bloco

5 BITS HLIT > 5 BITS HDIST > 4 BITS HCLEN
'''
def read_block_format(block):
    # HLIT
    hlit = block[0:5]
    # HDIST
    hdist = block[5:10]
    # HCLEN
    hclen = block[10:14]

    return hlit, hdist, hclen

'''
Crie um método que armazene num array os comprimentos dos códigos
do “alfabeto de comprimentos de códigos”, com base em HCLEN:
    * Tenha em atenção que as sequências de 3 bits a ler correspondem à
    ordem 16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15 no array
    de códigos
'''

def main():
    # Read file
    block = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]
    # Read block format
    hlit, hdist, hclen = read_block_format(block)

    print('HLIT: ', hlit)
    print('HDIST: ', hdist)
    print('HCLEN: ', hclen)


if __name__ == '__main__':
    main()