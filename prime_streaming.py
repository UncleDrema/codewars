from collections import defaultdict

class Primes:
    primes = []

    @staticmethod
    def is_prime(n: int) -> bool:
        for p in Primes.primes:
            if n % p == 0:
                return False
        Primes.primes.append(n)
        return True

    @staticmethod
    def stream():
        n = 2
        Primes.primes = [n]
        yield n
        while True:
            n += 1
            if Primes.is_prime(n):
                yield n

    @staticmethod
    def eratosphene():
        lp = defaultdict(lambda: 0)
        pr = []
        i = 2
        while True:
            if lp[i] == 0:
                lp[i] = i
                pr.append(i)
                yield i
            for p in pr:
                if p > lp[i]:
                    break
                lp[p * i] = p
            i += 1




s = Primes.eratosphene()
for i in range(10):
    n = next(s)
    print(n)