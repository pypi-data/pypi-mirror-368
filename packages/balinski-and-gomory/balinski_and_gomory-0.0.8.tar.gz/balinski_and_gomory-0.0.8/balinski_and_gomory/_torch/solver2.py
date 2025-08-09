import torch

def solve_1bc(n, X, k, l, B, R, Q):
    # R = torch.full((n,), n)
    # Q = torch.full((n,), n)
    # Q[l] = k

    # for j in range(n):
    #     if Q[j] != n:
    #         R[X[:, j].argmax().item()]  = j
    rows = X.argmax(dim=0)  # shape: (n,)
    mask = Q != n           # shape: (n,)
    # print('mask', mask, 'X', X)
    R[rows[mask]] = torch.arange(n, device='cuda')[mask]

    # Brush conditions
    B_zero = (B == 0)                          # shape (n, n)
    valid_rows = (torch.arange(n, device='cuda') != k) & (R != n)  # shape (n,)
    Q_unset = (Q == n)                         # shape (n,)

    # Expand to match matrix
    row_brush = valid_rows[:, None]           # shape (n, 1)
    col_brush = Q_unset[None, :]              # shape (1, n)

    # Brushing intersection
    brush_mask = B_zero & row_brush & col_brush  # shape (n, n)

    row_indices = torch.arange(n, device='cuda').unsqueeze(1).expand(-1, n)  # (n, n)
    collapsed = torch.where(brush_mask, row_indices, n)    # n is dummy invalid

    min_i_for_j = collapsed.min(dim=0).values  # shape (n,)

    # Build final Q update: only update where a valid i was found
    valid_mask = min_i_for_j < n
    Q[valid_mask] = min_i_for_j[valid_mask]


    # for i in range(n):
    #     if i != k:
    #         if R[i] != n:
    #             for j in range(n):
    #                 if B[i, j] == 0 and Q[j] == n:
    #                     Q[j] = i

    return R, Q


def solve_from_kl(n, C, X, k, l, U, V, B):
    # R = [None] * n
    # Q = [None] * n
    R = torch.full((n,), n, device='cuda')
    Q = torch.full((n,), n, device='cuda')

    
    # 1
    Q[l] = k
    # raise
    
    
    s = 0
    while s < n:
        # print("what X",s,  X)

        R, Q = solve_1bc(n, X, k, l, B, R, Q)
        s += 1
        # print('Q', Q)
    
    
    # 2
    # if R[k] is not None and R[k] != l:
    if R[k] != n and R[k] != l:
    
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

        J &= (R[:, None] != n) & (Q[None, :] == n)
        # for i in range(n):
        #     for j in range(n):
        #         J[i, j] = J[i, j] and (R[i] != n) and (Q[j] == n)
    
        if J.any():
            epsilon = B[J].min()
        else:
            epsilon = -B[k, l]
    
        U[R != n] += epsilon
        # for i in range(n):
        #     if R[i] != n: #is not None:
        #         U[i] = U[i] + epsilon
    
        V[Q != n] -= epsilon
        # for j in range(n):
        #     if Q[j] != n: #is not None:
        #         V[j] = V[j] - epsilon
    
        B = C - U.unsqueeze(1) - V
    
        if B[k, l] < 0:
    
            return X, k, l, U, V, B
    
        else:

            neg_indices = (B < 0).nonzero(as_tuple=False)

            if neg_indices.numel() > 0:
                i, j = neg_indices[0].tolist() # any of them is ok
                return X, i, j, U, V, B    
            # for i in range(n):
            #     for j in range(n):
            #         if B[i, j] < 0:
            #             return X, i, j, U, V, B
    
            else:
                return X, None, None, U, V, None


def solve(C, X=None, U=None, V=None):
    n = len(C)
    
    if X == None:
        X = torch.eye(n, dtype=torch.long, device='cuda')
    if V is not None:
        if U is None:
            U = ((C - V) * X).sum(1)
        else:
            assert ((C - U.unsqueeze(1) - V) * X == 0).all()
    else:
        if U is None:
            U = torch.zeros(n, device='cuda')
        V = ((C - U.unsqueeze(1)) * X).sum(0)
    
    B = C - U.unsqueeze(1) - V
    
    k, l = divmod(B.argmin().item(), n)

    steps = 0#temp
        
    while True:
        if k is not None:
            print(steps)
            steps += 1
            X, k, l, U, V, B = solve_from_kl(n, C, X, k, l, U, V, B)
    
            if B is None:
                return X, U, V
        else:
            k, l = divmod(B.argmin().item(), n)
