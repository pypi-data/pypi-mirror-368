
## diskcache

```python
import os
import pandas as pd
import diskcache as dc
from pydataset import data

# set cache location
cache = dc.Cache('/Users/benvanvliet/desktop/data')


def get_diamonds(key='diamonds', expire=10):

    # check if key is in cache
    if 'diamonds' in cache:
        print('from cache')
        df = cache[key]
    else:
        print('caching')
        df = pd.DataFrame()
        for i in range(10):
            df_i = data('diamonds')
            df = df.append(df_i).reset_index(drop=True)
        cache.set(key=key, value=df, expire=expire)
    return df


# caching
df = get_diamonds()

# from cache
df = get_diamonds()

# clear
cache.clear()
os.system('rm -rfv ' + cache.directory)
```
