import torch

def solve_1bc(n, X, k, l, B, R, Q):
	for j in range(n):
		if Q[j] is not None:
			R[X[:, j].argmax().item()]  = j
	
	for i in range(n):
		if i != k:
			if R[i] is not None:
				for j in range(n):
					if B[i, j] == 0 and Q[j] is None:
						Q[j] = i
	
	return R, Q


def solve_from_kl(n, C, X, k, l, U, V, B):
	R = [None] * n
	Q = [None] * n
	
	# 1
	Q[l] = k
	
	s = 0
	while s < n:
		R, Q = solve_1bc(n, X, k, l, B, R, Q)
		s += 1
	
	
	# 2
	if R[k] is not None and R[k] != l:
	
		k_ = k
		l_ = l
	
		while True:
			X[k_, l_] = 1
			l_ = R[k_]
			X[k_, l_] = 0
			k_ = Q[l_]
	
			if k_ == k and l_ == l:
				break
	
		epsilon = -B[k, l]
	
		V[l] = V[l] - epsilon
	
		B = C - U.unsqueeze(1) - V
	
		return X, None, None, U, V, B
	
	else:
		J = B >= 0
	
		for i in range(n):
			for j in range(n):
				J[i, j] = J[i, j] and (R[i] is not None) and (Q[j] is None)
	
		if J.any():
			epsilon = B[J].min()
		else:
			epsilon = -B[k, l]
	
		for i in range(n):
			if R[i] is not None:
				U[i] = U[i] + epsilon
	
		for j in range(n):
			if Q[j] is not None:
				V[j] = V[j] - epsilon
	
		B = C - U.unsqueeze(1) - V
	
		if B[k, l] < 0:
	
			return X, k, l, U, V, B
	
		else:
	
			for i in range(n):
				for j in range(n):
					if B[i, j] < 0:
						return X, i, j, U, V, B
	
	
			return X, None, None, U, V, None


def solve(C, X=None, U=None, V=None):
	n = len(C)
	
	if X == None:
		X = torch.diag(torch.ones(n, dtype=torch.long))
	if V is not None:
		if U is None:
			U = ((C - V) * X).sum(1)
		else:
			assert ((C - U.unsqueeze(1) - V) * X == 0).all()
	else:
		if U is None:
			U = torch.zeros(n)
		V = ((C - U.unsqueeze(1)) * X).sum(0)
	
	B = C - U.unsqueeze(1) - V
	
	k, l = divmod(B.argmin().item(), n)
	
	
	while True:
		if k is not None:
			X, k, l, U, V, B = solve_from_kl(n, C, X, k, l, U, V, B)
	
			if B is None:
				return X, U, V
		else:
			k, l = divmod(B.argmin().item(), n)
