import time


END_TIME_NO_VALUE: float = 999999.9

class Timer:
    """
    Class to measure how long certain methods take
    to execute and complete. Just call the
    `.start()` method before the code is executed
    and the `.stop()` when it finishes.

    It can be used as a context manager with this:
    - `with Timer():`
    """

    @property
    def time_elapsed(
        self
    ) -> float:
        """
        The time elapsed between the 'start' and the
        'stop' methods call.
        """
        return self.end_t - self.start_t

    @property
    def time_elapsed_str(
        self
    ) -> str:
        """
        The time elapsed between the 'start' and the
        'stop' method call, but as a printable string.
        """
        return str(round(self.time_elapsed, 2))

    def __init__(
        self
    ):
        self.start_t: float = 0
        """
        The start time moment.
        """
        self.end_t: float = END_TIME_NO_VALUE
        """
        The end time moment.
        """

    def start(
        self
    ) -> None:
        """
        Start the timer.
        """
        self.start_t = time.perf_counter()
        self.end_t = END_TIME_NO_VALUE

    def stop(
        self
    ) -> None:
        """
        Stop the timer. This will raise an exception
        if the timer hasn't been started previously.
        """
        if self.start_t is None:
            raise Exception('The timer was not started.')
        
        self.end_t = time.perf_counter()
    
    def print(
        self
    ) -> None:
        """
        Print the time elapsed in the console.
        """
        print(f'Time elapsed: {self.time_elapsed_str}')

    # Allowing 'with Timer():' context below
    def __enter__(
        self
    ) -> 'Timer':
        self.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb
    ):
        self.stop()
        self.print()