import logging
import binascii

class BitUtil(object):
	
	def __init__(self, *args, **kwargs):
		self.logger = logging.getLogger(__name__)

	def _chunks(self, a, chunk_size):
		for i in range(0, len(a), chunk_size):
			yield a[i:i+chunk_size]
			
	def hex_to_bits(self, a):
		return ''.join('{:08b}'.format(int(x, 16)) for x in self._chunks(a, 2))

	def byte_to_binary(self, n):
		return ''.join(str((n & (1 << i)) and 1) for i in reversed(range(8)))

	def hex_to_binary(self, h):
		return ''.join(self.byte_to_binary(ord(str(b))) for b in binascii.unhexlify(h))

	def binary_to_decimal(self, d):
		n=len(d)
		res=0
		for i in range(1,n+1):
			res=res+ int(d[i-1])*2**(n-i)

		return res

	def xor(self, other):
		"""
		Overrides xor operator in order to xor bytes.

		"""
		return bytes(x ^ y for x, y in zip(other))
		
	def bxor(self, b1, b2): # use xor for bytes
		parts = []
		for b1, b2 in zip(b1, b2):
			parts.append(bytes([b1 ^ b2]))
		return b''.join(parts)

	def check(self, n, i):
		return (n & (1 << i)) != 0

	def between(self, n, f, t):
		return (n >> f) & ((1 << t - f) - 1)

	def de(self, n, f):
		return (n >> f)

	def para(self, n, t):
		return self.between(n, 0, t)

