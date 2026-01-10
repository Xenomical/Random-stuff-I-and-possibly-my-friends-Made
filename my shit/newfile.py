from secrets import randbits
from secrets import randbelow

def keygen():
	p,q = random_bit(2), random_bit(2)
	while p == q:
		q = random_bit(2)
		

	n = p*q
	phi = (p-1)*(q-1)
	
	e = 65537
	while gcd(e,phi) != 1 or e >= phi:
		e = 2 + randbelow(phi-3)
		
	d = modInverse(e,phi)
	
	public_key = [n,e]
	private_key = [n,d]
	print(f"Your public key is {public_key}\nYour private key is {private_key}")
	
def gcd(a,b):
	while b != 0:
		a, b = b, a%b
	return a
	
def modInverse(A, M):
    m0 = M
    y = 0
    x = 1
    if (M == 1):
        return 0

    while (A > 1):
        q = A // M
        t = M
   
        M = A % M
        A = t
        t = y
        y = x - q * y
        x = t
    if (x < 0):
        x = x + m0
    return x

def isPrimeA(n, k=20):
	
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

def random_bit(bits=2048):
    while True:
    	n = randbits(bits-1)  
    	n |= 1              
    	n |= (1 << bits-1)  
    	if isPrimeA(n):
    		return n

keygen()