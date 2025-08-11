# GYM CAS

[![PyPI - Version](https://img.shields.io/pypi/v/gym-cas.svg)](https://pypi.org/project/gym-cas)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gym-cas.svg)](https://pypi.org/project/gym-cas)
![Coverage](../../downloads/coverage.svg)

Anvend Python som CAS (Computational Algebra System) i gymnasiet.
Bygger på følgende moduler:

- Algebra/beregninger:
    - [SymPy](https://docs.sympy.org/latest/index.html)
    - [NumPy](https://numpy.org/)
- Afbildninger:
    - [SymPy Plot Backends](https://sympy-plot-backends.readthedocs.io/en/latest/modules/index.html)
    - [Matplotlib](https://matplotlib.org/)

## Installation

```console
pip install gym-cas
```

eller

```console
py -m pip install gym-cas
```

## Cheatsheet

I nedenstående afsnit antages det at `gym_cas` først importeres således:

```py
from gym_cas import *
```

### B1. Tal- og bogstavregning

```py
expand( udtryk )
factor( udtryk )
```

### B2. Ligninger og uligheder

```py
solve( udtryk )
solve( [udtryk1, udtryk2] )
nsolve( udtryk, startgæt )
solve_interval( udtryk, start, slut )
```

Bemærk at den nemmeste måde at bruge `solve` i `SymPy` er ved at omforme sin ligning så en af siderne er lig 0. Hvis man fx vil løse ligningen `x/2 = 10` så kan det skrives `solve(x/2-10)`.

### B3. Geometri og trigonometri

```py
Sin( vinkel )
Cos( vinkel )
Tan( vinkel )
aSin( forhold )
aCos( forhold )
aTan( forhold )
```

### B4. Analytisk plangeometri

```py
plot_list( X_list ,Y_list, is_point=True)
plot( funktion )
plot_implicit( udtryk ,xlim=( x_min, x_max),ylim=( y_min, y_max))
plot_geometry( Geometrisk objekt )
```

#### Flere grafer i en afbildning

```py
p1 = plot( udtryk1 )
p2 = plot( udtryk2 )
p = p1 + p2
p.show()
```

### B5. Vektorer

```py
a = vector(x,y)
a.dot(b)
plot_vector( vektor )
plot_vector( start, vektor )
plot_vector( [vektor1, vektor2, ...])
```

### B6. Deskriptiv Statistik

#### Ugrupperet

```py
max( data )
min( data )
mean( data )
median( data )
var( data, ddof )
std( data, ddof ) 
kvartiler( data )
percentile( data , procenter )
frekvenstabel( data )
boxplot( data ) 
plot_sum( data )
```

#### Grupperet

```py
group_mean( data, grupper )
group_percentile( data, grupper, procenter )
group_var( data, grupper, ddof )
group_std( data, grupper, ddof ) 
frekvenstabel( data, grupper )
boxplot( data, grupper ) 
plot_sum( data, grupper )
plot_hist( data, grupper )
```

### B8. Funktioner

```py
def f(x):
    return funktionsudtryk
f(3)

def f(x):
    return Piecewise(( funktion1, betingelse1), (funktion2, betingelse2))

plot( funktion , yscale="log")
plot( funktion , (variabel, start, stop), xscale="log", yscale="log")
regression_poly(X,Y, grad)
regression_power(X,Y)
regression_exp(X,Y)
```

### B9. Differentialregning

```py
limit( udtryk, variabel, grænse, retning )
diff( funktion )
def df(xi):
    return diff( funktion ).subs( variabel, xi )
```

### B10. Integralregning

```py
integrate( udtryk )
integrate( udtryk, ( variabel, start, slut ))
plot3d_revolution( udtryk , (x, a, b),parallel_axis="x")
```

### A1. Vektorer i rummet

```py
a = vector(1,2,3)
a.cross(b)
plot3d_list( X, Y, is_point=True)
plot_vector( a )
plot3d_line( a + t * r )
plot3d_plane( a + s * r1 + t * r2 )
plot3d_implicit( ligning, backend=PB ) # Kræver Plotly eller K3D
```

### A4. Differentialligninger

```py
f = Function('f')
dsolve( ode )
plot_ode( ode, (x, start, stop), (f, start, stop))
```

### A5. Diskret Matematik

```py
X = [ udregning for x in range(start,slut)]
X = [ startbetingelse ]
for i in range(start, slut):
    X.append( rekursionsligning )
```
