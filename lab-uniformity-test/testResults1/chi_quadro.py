#!/usr/bin/python3
'''
@authors: Giuseppe Valentino Baldi, Marco Lorini
@contact: giuseppevalentinobaldi@gmail.com, marck_91@hotmail.it 
@version: 1.0.0
@license: MIT (http://opensource.org/licenses/MIT)
'''

import sys, csv
from scipy.stats import chisquare
from scipy.stats import hmean

    
def main():
    with open('uniform.csv', newline='') as f:
        reader = csv.reader(f, delimiter=',', lineterminator="\n")
        threshold = 0
        hypothesis = 0
        pValue = 0.05
        chisquareArray = []
        pvalueArray = []
        isReject = True
        reject = 0
        for row in reader:
            threshold += 1
            p = [int(numeric_string) for numeric_string in row]
            if isReject :
                for e in p:
                    isReject = False
                    if e <= 5:
                        isReject = True
                        reject += 1
                        break
            chi = chisquare(p)
            if isReject == False:
                chisquareArray.append(chi[0])
                pvalueArray.append(chi[1])
                print("chi-square: {} \t p-value: {}".format(chi[0], chi[1]))
                if chi[1] < 0.05:
                    hypothesis += 1
        if hypothesis < threshold * 2 / 3:
            print("I accept the null hypothesis")
        else:
            print("I reject the null hypothesis")
        print("hmean(chi-square): {} \t hmean(p-value): {} \t reject: {}".format(hmean(chisquareArray), hmean(pvalueArray), reject))
        

if __name__ == "__main__":
    main()

