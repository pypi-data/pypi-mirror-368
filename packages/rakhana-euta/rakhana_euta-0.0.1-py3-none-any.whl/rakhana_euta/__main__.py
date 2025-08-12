import sys,pickle,os



if len(sys.argv) < 2:
    f = open("where.txt")
    where = int(f.read())
    f.close()
    f = open('toSend.txt','rb')
    toReturn = pickle.load(f)
    f.close()
    while True:
        input("")
        os.system('cls' if os.name == 'nt' else 'clear')
        print(toReturn[where])
        where += 1
        if where >= len(toReturn):
            where = 0
        f = open("where.txt",'w')
        f.write(str(where))
        

else:
    argument = sys.argv[1]


    toReturn = None
    if argument == "newton_rhapson":
        toReturn = """
    import numpy as np
    def NewtonRaphsonSystem(F, J, X, p=4, N=100):
    tol = 0.5*10**(-p)
    X0 = np.array(X, dtype=float)
    for i in range(N):
    if abs(np.linalg.det(J(X0))) < 5e-9:
    print("Error: Singular system detected!")
    return None
    H = np.linalg.solve(J(X0), -F(X0))
    X1 = X0 + H
    err = max(abs(H))
    X0 = X1.copy()
    if err < tol:
    return np.round(X1, p)
    else:
    print("Error: Not convergent!")
    return None
    ABA ARU AUCHA
    def f1(x):
    return np.array([
    x[0]**2 - x[1]**2 - 5,
    x[0]**2 + x[1]**2 - 25
    ])

    1

    def j1(x):
    return np.array([
    [ 2*x[0], -2*x[1] ],
    [ 2*x[0], 2*x[1] ]
    ])
    X1 = NewtonRaphsonSystem(f1, j1, [2, 3])
    print("Solution: ", X1)
    print("F(x,y): ", np.round(f1(X1), 4))
    """
    elif argument == "gauss_jordan":
        toReturn = """
import numpy as np
def GaussJordan(a, b):
A = np.array(a, dtype=float)
B = np.array(b, dtype=float)
if A.ndim != 2 or B.ndim != 1 \
or A.shape[0] != A.shape[1] \
or A.shape[0] != B.shape[0]:
print("Error! Incorrect dimension(s).")
return None

1

n = len(B)
# Diagonalization
for j in range(n):
if abs(A[j][j]) < 0.5e-9:
print(f"Error! Pivot[{j+1},{j+1}] is zero or close to zero.")
return None
for i in range(n):
ratio = A[i][j] / A[j][j]
if i != j:
k = range(j, n)
A[i][k] -= ratio * A[j][k]
B[i] -= ratio * B[j]

# Solution
X = np.zeros(n, dtype=float)
for i in range(n):
X[i] = B[i] / A[i][i]
return X
        """
    elif argument == "gauss_elimination":
        toReturn =  '''
import numpy as np
def GaussElimination(a, b):
A = np.array(a, dtype=float)
B = np.array(b, dtype=float)
if A.ndim != 2 or B.ndim != 1 or A.shape[0] != A.shape[1] \
or A.shape[0] != B.shape[0]:
print("Error! Incorrect dimension(s).")
return None

1

n = len(B)
# Forward Elimination: Reduction to Upper Triangular form
for j in range(n-1):
if abs(A[j][j]) < 0.5e-9:
print(f"Error! Pivot[{j+1},{j+1}] is zero or close to zero.")
return None
for i in range(j+1, n):
ratio = A[i][j] / A[j][j]
k = range(j, n)
A[i][k] -= ratio * A[j][k]
B[i] -= ratio * B[j]
if abs(A[n-1][n-1]) < 0.5e-9:
print(f"Error! Pivot[{n},{n}] is zero or close to zero.")
return None
# Backward Substitution
X = np.zeros(n, dtype=float)
for i in range(n-1, -1, -1):
j = range(i+1, n)
X[i] = (B[i] - np.sum(A[i, j] * X[j]))/ A[i][i]
return X
'''
    elif argument == "newton_forward":
        toReturn = '''
import numpy as np
import matplotlib.pyplot as plt
def NewtonForward(X, Y, xp, showTable=False):
# Check for equal spacing
Dx = np.diff(X)
h = Dx[0]
if not np.all(Dx == h):
return None
n = len(Y)
# Difference table construction
D = np.zeros((n,n), dtype=float)
D[:, 0] = Y.copy()
for j in range(1, n):
for i in range(n-j):
D[i, j] = round(D[i+1, j-1] - D[i, j-1],3)
if showTable:
print("Forward Difference Table:")
for i in range(n):
print(f"{X[i]:10.2f}", end="")
for j in range (n-i):
print(f"{D[i, j]:10.4f}", end="")
print()

1

# Main formula implementation
p = (xp - X[0]) / h
yp = Y[0]
prod = 1.0
for j in range(n-1):
prod *= (p-j) / (j+1)
yp += prod * D[0, j+1]
return yp
'''
    elif argument == "cubic_spline":
        toReturn = '''
import numpy as np
import matplotlib.pyplot as plt
def CubicSpline(X, Y, xp):
if len(X) != len(Y):
return None
n = len(X) - 1
h = np.diff(X)
Dy = np.diff(Y)
A = np.zeros((n-1, n+1), dtype=float)
B = np.zeros(n-1, dtype=float)
M = np.zeros(n+1, dtype=float)
## For computing the Second derivatives
for j in range(n-1):
A[j, j] = h[j]
A[j, j+1] = 2*(h[j] + h[j+1])
A[j, j+2] = h[j+1]
B[j] = 6 * (Dy[j+1] / h[j+1] - Dy[j] / h[j])
M[1:n] = np.linalg.solve(A[:, 1:n], B)
# Find the appropriate index of the cubic spline equation
i = np.clip(np.searchsorted(X, xp)-1, 0, n-1)
P = M[i+1] / (6 * h[i])
Q = M[i] / (6 * h[i])
R = (Y[i+1] / h[i]) - (M[i+1] * h[i] / 6)
S = (Y[i] / h[i]) - (M[i] * h[i] / 6)
yp = P*(xp-X[i])**3 - Q*(xp-X[i+1])**3 + R*(xp-X[i]) - S*(xp-X[i+1])
return yp
aba visualization
xVals = np.linspace(min(X), max(X), 501)
yVals = CubicSpline(X, Y, xVals)
plt.figure(figsize=(8, 4))
plt.scatter(X, Y, color="red", label="Data Points")
plt.plot(xVals, yVals, color="blue", label="Cubic Spline")
plt.xlabel("x")
plt.xlabel("y")
plt.grid()
plt.legend()
plt.show()
        '''
    elif argument == "integration_all":
        toReturn = '''
def Trapezoidal(F, a, b, n):
h = (b - a) / n
result = F(a) + F(b)
for i in range(1, n):
result += 2 * F(a+i*h)
result *= h/2
return result
def Simp1by3(F, a, b, n):
if n%2 != 0:
print("Error: For Simpson's 1/3 Rule, n must be a multiple of 2.")
return None
h = (b - a) / n
result = F(a) + F(b)
for i in range(1, n):
if i%2 == 0:
m = 2
else:
m = 4
result += m * F(a+i*h)
result *= h/3
return result
def Simp3by8(F, a, b, n):
if n%3 != 0:
print("Error: For Simpson's 3/8 Rule, n must be a multiple of 3.")
return None
h = (b - a) / n
result = F(a) + F(b)
for i in range(1, n):
if i%3 == 0:
m = 2
else:
m = 3
result += m * F(a+i*h)
result *= 3*h/8
return result
def Boole(F, a, b, n):
if n%4 != 0:
print("Error: For Boole's Rule, n must be a multiple of 4.")
return None
h = (b - a) / n
result = 7*(F(a)+F(b))
for i in range(1, n):
if i%4 == 0:
m = 14
elif i%2 == 0:
m = 12
else:
m = 32
result += m * F(a+i*h)
result *= 2*h/45
return result
def Weddle(F, a, b, n):
if n%6 != 0:
print("Error: For Weddle's Rule, n must be a multiple of 6.")
return None
h = (b - a) / n
result = F(a) + F(b)
for i in range(1, n):
if i%6 == 0:
m = 2
elif i%3 == 0:
m = 6
elif i%2 == 0:
m = 1
else:
m=5
result += m * F(a+i*h)
result *= 3*h/10
return result
        '''
    elif argument == "runge_kutta":
        toReturn = '''
import numpy as np
import matplotlib.pyplot as plt
def RK4(F, x0, y0, xn, n):
h = (xn-x0) / n
X = np.zeros(n+1, dtype=float)
Y = np.zeros(n+1, dtype=float)
X[0], Y[0] = x0, y0
for i in range(n):
k1 = h * F(X[i], Y[i])
k2 = h * F(X[i] + h/2, Y[i] + k1/2)
k3 = h * F(X[i] + h/2, Y[i] + k2/2)
k4 = h * F(X[i] + h, Y[i] + k3)
k = (k1 + 2*k2 + 2*k3 + k4)/6
X[i+1] = X[i] + h
Y[i+1] = Y[i] + k
return X, Y

        '''
    elif argument == "runge_kutta_2":
        toReturn = '''
import numpy as np
import matplotlib.pyplot as plt
def RK4(F1, F2, X0, Y0, Z0, Xn, n):
h = (Xn-X0) / n
X = np.zeros(n+1, dtype=float)
Y = np.zeros(n+1, dtype=float)
Z = np.zeros(n+1, dtype=float)
X[0], Y[0], Z[0] = X0, Y0, Z0
for i in range(n):
k1 = h * F1(X[i], Y[i], Z[i])
l1 = h * F2(X[i], Y[i], Z[i])
k2 = h * F1(X[i]+h/2, Y[i]+k1/2, Z[i]+l1/2)
l2 = h * F2(X[i]+h/2, Y[i]+k1/2, Z[i]+l1/2)
k3 = h * F1(X[i]+h/2, Y[i]+k2/2, Z[i]+l2/2)
l3 = h * F2(X[i]+h/2, Y[i]+k2/2, Z[i]+l2/2)
k4 = h * F1(X[i]+h, Y[i]+k3, Z[i]+l3)
l4 = h * F2(X[i]+h, Y[i]+k3, Z[i]+l3)
k = (k1 + 2*k2 + 2*k3 + k4)/6
l = (l1 + 2*l2 + 2*l3 + l4)/6
X[i+1] = X[i] + h
Y[i+1] = Y[i] + k
Z[i+1] = Z[i] + l
return X, Y, Z
'''
    elif argument == "laplace":
        toReturn = '''
import numpy as np
import matplotlib.pyplot as plt
def LaplacePDE(nx, ny, h, bottom, top, left, right, precision=4, N=10000):
tol = 0.5*10**(-precision)
u = np.zeros((nx+1, ny+1), dtype=float)
u[:, 0] = bottom
u[:, -1] = top
u[0, 1:-1] = left
u[-1, 1:-1] = right
#Gauss-Seidal Iteration
for count in range(N):
uold = u.copy()
for i in range(1, nx):
for j in range(1, ny):
u[i, j] = (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1]) / 4
max_diff = np.max(np.abs(uold - u))
if max_diff < tol:
return np.round(np.flipud(u.T), precision)
else:
print("Exhausted !")
return None
bottom = np.array([0., 50., 100., 50., 0.])
top = np.array([0., 50., 100., 50., 0.])
left = np.array([100., 200., 100.])
right = np.array([100., 200., 100.])

1

x0, y0 = 0, 0
nx, ny = 4, 4
h = 0.25
xn, yn = x0+nx*h, y0+ny*h
u = LaplacePDE(nx, ny, h, bottom, top, left, right)
print("Solution: ")
print(u)
'''
    elif argument == "possion":
        toReturn  = """import numpy as np
import matplotlib.pyplot as plt
def PoissonPDE(F, x0, y0, nx, ny, h, bottom, top, left, right, precision=4,␣
↪N=10000):
tol = 0.5*10**(-precision)
u = np.zeros((nx+1, ny+1), dtype=float)
u[:, 0] = bottom
u[:, -1] = top
u[0, 1:-1] = left
u[-1, 1:-1] = right
#Gauss-Seidal Iteration
for count in range(N):
uold = u.copy()
for i in range(1, nx):
for j in range(1, ny):
u[i, j] = (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1] \

- h**2*F(x0+i*h, y0+j*h)) / 4

max_diff = np.max(np.abs(uold - u))
if max_diff < tol:
return np.round(np.flipud(u.T), precision)
else:
print("Exhausted !")
return None
bottom = np.array([0., 0., 0., 0.])
top = np.array([0., 0., 0., 0.])
left = np.array([0., 0.])
right = np.array([0., 0.])

1

f = lambda x, y: -729 * x**2* y**2
x0, y0 = 0, 0
nx, ny = 3, 3
h = 1/3
xn, yn = x0+nx*h, y0+ny*h
u = PoissonPDE(f, x0, y0, nx, ny, h, bottom, top, left, right)
print("Solution: ")
print(u)

"""
    elif argument  == "help":
        toReturn = '''
possion
laplace
runge_kutta_2
runge_kutta
integration_all
cubic_spline
newton_forward
gauss_elimination
gauss_jordan    
newton_rhapson
'''

    f = open('toSend.txt','wb')
    pickle.dump(toReturn.split('\n'), f)
    f.close()
    f = open("where.txt",'w')
    f.write("0")
    f.close()

