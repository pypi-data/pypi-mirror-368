# QPool

## Description

Multiprocessing with Process Pools implemented using Processes and Shared Memory objects.

- Built in progress bar.
- Traits for rate-limiting, exponential backoff and retry, logging, and more.
- Graceful shutdown by default (CTRL+C 2x, will kill immediately).- Allows re-use of pool after join, cutting down on process spawning time.

# Debugging Tips
- If hanging, investigate stop_workers, specifically the point of joining the processes, unclosed queues and resources can prevent process closure.

