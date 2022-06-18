'(((a1) | (b1)) & ((a2) | (b2)) & ((a3) | (b3)) & ((a4) | (b4)) & ((a5) | (b5)) & ((G c) & (X - c)))'

def generate_antiblack_benchmark(n):
    formula = '('
    for i in range(n):
        formula += '((a{} U !c) | (b{} U !c)) & '.format(i,i)
    formula = formula + '(G c))'
    return formula

if __name__ == '__main__':
    sizes = 1001

    for size in range(0,sizes):
        formula = generate_antiblack_benchmark(size)
        print(formula)
        with open("./antiblack/O1formula{}_modified.pltl".format(size), "w") as file:
            file.write(formula)