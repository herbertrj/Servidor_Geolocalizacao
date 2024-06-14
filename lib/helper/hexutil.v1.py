def get_unsigned_short(b, i):
	res=b[i:i+4]
	
	return res

def read_unsigned_byte(b, i):
	res=b[i:i+2]
	
	return res,i+2

def read_unsigned_short(b, i):
	res=b[i:i+4]
	
	return res,i+4

def read_unsigned_int(b, i):
	end = i+8
	res=b[i:end]
	return res,end

def read_unsigned_long(b, i):
	end = i+16
	res=b[i:end]
	return res,end

def read_unsigned_len(b, l, i):
	last = i + (l * 2)
	res = b[i:last]

	return res,last

def skip_bytes(l, i):
	return i+(l * 2)

def twos_comp(val, bits):
	"""compute the 2's complement of int value val
	https://stackoverflow.com/questions/1604464/twos-complement-in-python
	"""
	if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
		val = val - (1 << bits)        # compute negative value
	return val                         # return positive value as is