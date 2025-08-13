from io import TextIOBase
from threading import Thread
from typing import IO, Final, TextIO, final


@final
class OutputCopier:
    def __init__(
        self,
        input_stream: IO[str],
        output_stream: TextIO | TextIOBase | None,
        *,
        close_input_on_stop: bool,
    ) -> None:
        self._input_stream: Final = input_stream
        self._output_stream: Final = output_stream
        self._thread: Final = Thread(target=self._copy_stream, daemon=True)
        self._close_input_on_stop: Final = close_input_on_stop
        self._should_stop = False

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._should_stop = True

    def _copy_stream(self) -> None:
        try:
            for line in self._input_stream:
                if self._output_stream and not self._output_stream.closed:
                    self._output_stream.write(line)
                if self._should_stop:
                    break
        except ValueError:
            pass  # "I/O operation on closed file"

        if self._close_input_on_stop and not self._input_stream.closed:
            self._input_stream.close()
