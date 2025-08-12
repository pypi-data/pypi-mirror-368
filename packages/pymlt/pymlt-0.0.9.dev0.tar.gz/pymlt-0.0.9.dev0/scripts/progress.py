"""A demonstration script that shows a progress bar with a Mario-themed success chime.

This script uses the rich library to display a progress bar and the chime library
to play a Mario-themed success sound upon completion. It simulates a task by
sleeping for short intervals while updating the progress bar.

Dependencies:
    - rich: For progress bar visualization
    - chime: For sound effects
"""

import time

import chime
from rich.progress import track

for i in track(range(20), description="progress:"):
    time.sleep(0.05)

# ['big-sur', 'chime', 'mario', 'material', 'pokemon', 'sonic', 'zelda']
chime.theme("mario")
chime.success()
