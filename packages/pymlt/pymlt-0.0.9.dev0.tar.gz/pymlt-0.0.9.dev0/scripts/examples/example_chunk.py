"""
example file
"""

size = 30_000
chunk_size = 10_000

for i in list(range(0, size, chunk_size)):
    print(f"select * from table where rownum > {i} and rownum <= {i + chunk_size}")
