export class TargetMutex {
  private queue = Promise.resolve();
  private owner?: string;
  private depth = 0;
  private nextResolver?: () => void;
  private waiters = 0;

  /**
   * Acquire the lock.
   * – If nobody owns it, we wait in FIFO order.
   * – If the same `target` already owns it, we return immediately (re-entrant).
   *
   * The returned function **must** be called exactly once to release.
   */
  async lock(target: string): Promise<() => void> {
    // Fast path: re-entrant for the same target only if no other waiters are queued
    if (this.owner === target && this.waiters === 0) {
      ++this.depth;
      return () => {
        this.release();
      };
    }

    // Slow path: queue like a normal mutex
    // Someone else is waiting — track it so re-entrance becomes fair
    this.waiters++;

    // Create a ticket for FIFO ordering
    let unlockNext!: () => void;
    const ticket = new Promise<void>(r => (unlockNext = r));

    const unlock = this.queue.then(() => {
      // We are next in line – we're no longer waiting
      this.waiters--;
      this.owner = target;
      this.depth = 1;
      // Remember who to wake once this target fully releases
      this.nextResolver = unlockNext;
      return () => {
        // Release one nesting level. If that makes the mutex free, the resolver will be invoked inside `release()`.
        this.release();
      };
    });
    this.queue = this.queue.then(() => ticket);
    return unlock;
  }

  /**
   * Release one nesting level. Returns whether the mutex became free.
   */
  private release(): boolean {
    if (--this.depth === 0) {
      this.owner = undefined;
      // Wake the next waiter (if any)
      if (this.nextResolver) {
        this.nextResolver();
        this.nextResolver = undefined;
      }
      return true;
    }
    return false;
  }
}