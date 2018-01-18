#!/usr/bin/python3
'''
@authors: Giuseppe Valentino Baldi, Marco Lorini
@contact: giuseppevalentinobaldi@gmail.com, marck_91@hotmail.it 
@version: 1.0.0
@license: MIT (http://opensource.org/licenses/MIT)
'''

import sys, csv
from scipy.stats import chisquare

    
def main():
    with open('uniform.csv', newline='') as f:
        reader = csv.reader(f, delimiter=',', lineterminator="\n")
        threshold = 0
        hypothesis = 0
        pValue = 0.05
        transitory = input("Inserisci il tuo transitorio:")
        W = int(transitory)
        for row in reader:
            threshold += 1
            desired_array = [int(numeric_string) for numeric_string in row]
            slice_obj = slice(W, len(desired_array))
            array_without_transitory = desired_array[slice_obj]
            chi = chisquare(array_without_transitory)
            print("chi-square: {} \t p-value: {}".format(chi[0], chi[1]))
            if chi[1] < 0.05:
                hypothesis += 1
        if hypothesis < threshold * 2 / 3:
            print("I accept the null hypothesis")
        else:
            print("I reject the null hypothesis")   
        

if __name__ == "__main__":
    main()

