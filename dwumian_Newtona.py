

def dwumian(n, k):
    wynik = 1

    if n/2 > k:
        k = n-k

    for i in range(k+1, n+1):
        wynik *= i

    for i in range(1, n-k+1):
        wynik /= i

    return wynik

print(4*dwumian(48,6) + 6*dwumian(48,5) + 4*dwumian(48,4) + dwumian(48, 3))






