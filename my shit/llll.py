def isPrime(n, k=20):
	
	primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]
	
	if n in primes:
		return True
	for p in primes:
		if n % p == 0:
			return False
	d = n-1
	s = 0
	
	while d % 2 == 0:
		d //= 2
		s += 1
		
	for i in range(k):
		a = 2 + randbelow(n - 3)
		x = pow(a,d,n)
		if x == 1 or x == n-1:
			continue
			
		for _ in range(s-1):
			x = pow(x,2,n)
			if x == n-1:
				break
		else: 
			return False
			
	return True	


def prime_factors(n):
    factors = []
    divisor = 2

    while n > 1:
        while n % divisor == 0:
            factors.append(divisor)
            n //= divisor
        divisor += 1

    return factors


while True:
    try:
        num = int(input("Enter a non-prime integer: "))

        if is_prime(num):
            print("That number is prime. Try again.\n")
        elif num <= 1:
            print("Please enter an integer greater than 1.\n")
        else:
            factors = prime_factors(num)
            print(f"Prime factors of {num}: {factors}")
            break

    except ValueError:
        print("Invalid input. Please enter an integer.\n")
