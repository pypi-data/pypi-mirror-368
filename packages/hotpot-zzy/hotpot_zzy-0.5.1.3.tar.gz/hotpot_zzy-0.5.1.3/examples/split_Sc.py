import pandas as pd

df = pd.read_excel('SclogK1.xlsx')
l = df['SolRatio']

ll, m, n = [], [], []
for v in l:
    if not isinstance(v, str):
        ll.append(v)
        m.append(v)
        n.append(v)
        continue

    f,s = v.split(':')

    for i in range(len(s)):
        if s[i:].isalpha():
            break
    s1, s2 = s[:i], s[i:]
    ll.append(f)
    m.append(s1)
    n.append(s2)

print(f'll: {len(ll)}', f'm: {len(m)}', f'n:{len(n)}')

import numpy as np

arr = np.array([ll, m, n]).T
print(type(arr[0, 0]))
print(arr)

rows, cols = np.where(arr != 'nan')

print(arr[rows, cols])
