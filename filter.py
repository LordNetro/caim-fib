import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

a = 1.2 # Parametro a

def is_roman_numeral(s):
    if s.upper() not in ['MIX', 'I', 'DIV', 'DIX']:
        pattern = '^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$'
        return bool(re.match(pattern, s.upper()))
    
#Zipf's law formula
def zipf_formula(x, b, c):
    return c/(x+b)**a

def zipf_plot(ranks:list, freqs:list, fits:list, ranksLog:list, freqsLog:list, fitsLog:list, isLog:bool, b, c):
    if not isLog:
        plt.plot(ranks, freqs, 'b-', label='Frecuencias en Log')
        plt.plot(ranks, fits,'r-',label='Zipf fit en Log')
        plt.legend()
        plt.xlabel('x = Log del Rank de la palabra')
        plt.ylabel('y = Log de la Frecuencia de la palabra')
        plt.title(f'a = {a} b = {b} c = {c}')
        plt.show()
    else:
        plt.plot(ranksLog, freqsLog, 'b-', label='Frecuencias')
        plt.plot(ranksLog, fitsLog,'r-',label='Zipf fit')
        plt.legend()
        plt.xlabel('x = Rank de la palabra')
        plt.ylabel('y = Frecuencia de la palabra')
        plt.title(f'a = {a} b = {b} c = {c}')
        plt.show()
    
def zipf(freqs:list, freqsLog:list, isLog=True):
    ranks = range(1, len(freqs) + 1)
    ranksLog = np.log(ranks) # Rango de log(1) a log(wordCount)
    popt, pcov = curve_fit(zipf_formula, ranks, freqs)
    b = popt[0]
    c = popt[1]
    print(f'Zipf optimal parameters: b = {b}, c = {c}')
    fits = []
    fitsLog = []
    for num in ranks:
        fits.append(zipf_formula(num,*popt))
        fitsLog.append(np.log(zipf_formula(num,*popt)))

    zipf_plot(ranks, freqs, fits, ranksLog, freqsLog, fitsLog, isLog, b, c)

    
if __name__ == '__main__':
    input_text = input('Enter the input text file path: ')

    freqs = []  # Lista para recolectar los números
    freqsLog = []  # Lista para recolectar los números con log

    with open(input_text, 'r') as infile:
        inlines = infile.readlines()  # Lee todas las líneas en una lista
        inlines.reverse()  # Invierte la lista para recorrerla al revés
        
        output_text = input('Enter the output text file name: ')
        # Cambiado 'rw' a 'w' ya que 'rw' no es un modo válido.
        with open(output_text, 'w') as outfile:
            for line in inlines:
                if ',' in line:
                    number, word = line.strip().split(', ')
                    if re.match("^[a-zA-Z]*'?[a-zA-Z]*$", word) and not is_roman_numeral(word):
                        outfile.write(number+', '+word + '\n')
                        # Asumo que number es un valor entero.
                        freqs.append(int(number))
                        freqsLog.append(np.log(int(number)))

    zipf(freqs, freqsLog)
    
    # Crear gráfica de los números en escala logarítmica
    plt.plot(freqs)
    plt.xlabel('Rank')
    plt.ylabel('Ocurrencias')
    plt.title('Numero de ocurrences de cada palabra')
    plt.show()