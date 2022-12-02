# %%
import pandas as pd
import numpy as np


# Enter xrange, yrange, zrange as lists or np arrays
# We know x motor is slowest, z is fastest.
# Want to cover all 3D points with fewest moves (and fewest by slowest)


# Start with 2D
xrange = [-1,1]
yrange = [-1,1,2,3]
zrange = [0,1]
curpos = [10,10,10]
init_curpos = curpos

Nx = len(xrange)
Ny = len(yrange)
Nz = len(zrange)
X, Y, Z = np.meshgrid(xrange, yrange, zrange)
df = pd.DataFrame(columns=['x','y', 'z','xidx','yidx','zidx','score'])
df.x = X.ravel()
df.y = Y.ravel()
df.z = Z.ravel()
df.xidx = df.x.apply(lambda x: xrange.index(x))
df.yidx = df.y.apply(lambda y: yrange.index(y))
df.zidx = df.z.apply(lambda z: zrange.index(z))

# Sort by score
df.score = ( 
    df.xidx*Ny*Nz + 
    ((df.xidx+1)%2 * df.yidx + (df.xidx%2) * (Ny-1-df.yidx))*Nz + 
    ((df.yidx+1)%2 * df.zidx + (df.yidx%2) * (Nz-1-df.zidx))
    )
df = df.sort_values(by='score')
df.x += curpos[0]
df.y += curpos[1]
df.z += curpos[2]
print(df)

# Move to first location

for _, row in df.iterrows():
    eps = 1e-6
    dx = row.x - curpos[0]
    dy = row.y - curpos[1]
    dz = row.z - curpos[2]
    if abs(dx)>eps:
        print(f'Move {dx} in x')
        curpos[0] += dx
        # move(dx, motor=0)
    elif abs(dy)>eps:
        print(f'Move {dy} in y')
        curpos[1] += dy
        # move(dy, motor=1)
    elif abs(dz)>eps:
        print(f'Move {dz} in z')
        curpos[2] += dz
        # move(dz, motor=2)
    else:
        print('No movement')




# Sort by slowest



# %%
