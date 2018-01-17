import sys, csv
from scipy.stats import chisquare

    
def main():
    with open('uniform.csv', newline='') as f:
        reader = csv.reader(f, delimiter=',', lineterminator="\n")
        #threshold = 0
        #hypothesis = 0
        #pValue = 0.05
        for row in reader:
            #threshold += 1
            desired_array = [int(numeric_string) for numeric_string in row]
            chi = chisquare(desired_array)
            print("chi-square: {} \t p-value: {}".format(chi[0], chi[1]))
            #if chi[1] < 0.05:
                #hypothesis += 1
        #if hypothesis < threshold * 2 / 3:
            #print("I accept the null hypothesis")
        #else:
            #print("I reject the null hypothesis")   
        

if __name__ == "__main__":
    main()