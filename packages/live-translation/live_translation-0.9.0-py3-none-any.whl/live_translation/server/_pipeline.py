# _pipeline.py

import os
import multiprocessing as mp
import signal
import time
from ._ws import WebSocketIO
from .._audio._processor import AudioProcessor
from .._transcription._transcriber import Transcriber
from .._translation._translator import Translator
from . import config


class PipelineManager:
    def __init__(self, cfg: config.Config):
        """
        Initialize config, queues, stop event, thread, and processes.
        """
        self._cfg = cfg

        # Multiprocessing context and manager
        ctx = mp.get_context()
        self._manager = ctx.Manager()
        self._stop_event = self._manager.Event()
        self._parent_pid = os.getpid()

        # Queues for inter-process communication
        self._raw_audio_queue = mp.Queue()
        self._processed_audio_queue = mp.Queue()
        self._transcription_queue = mp.Queue()
        self._output_queue = mp.Queue()

        # Thread
        self.ws_io = WebSocketIO(
            self._cfg.WS_PORT,
            self._raw_audio_queue,
            self._output_queue,
            self._stop_event,
            self._cfg,
        )
        # Processes
        self._audio_processor = AudioProcessor(
            self._raw_audio_queue,
            self._processed_audio_queue,
            self._stop_event,
            self._cfg,
        )

        self._transcriber = Transcriber(
            self._processed_audio_queue,
            self._transcription_queue,
            self._stop_event,
            self._cfg,
            self._output_queue,
        )

        if not self._cfg.TRANSCRIBE_ONLY:
            self._translator = Translator(
                self._transcription_queue,
                self._stop_event,
                self._cfg,
                self._output_queue,
            )

        # List of pipeline components
        self._threads = [self.ws_io]
        self._processes = [self._audio_processor, self._transcriber]
        if not self._cfg.TRANSCRIBE_ONLY:
            self._processes.append(self._translator)

    def signal_handler(self, sig, frame):
        """Handle Ctrl+C: Parent process only should handles it."""
        if os.getpid() != self._parent_pid:
            return  # Ignore SIGINT in child processes

        print("\n🛑 Stopping the pipeline...\n")
        self._stop_event.set()

    def _start_pipeline(self):
        """Start the audio thread and processes."""
        print("🚀 Starting the pipeline...")

        # Register all components as daemon processes
        for thread in self._threads:
            thread.daemon = True

        for process in self._processes:
            process.daemon = True

        # Start all components
        for thread in self._threads:
            thread.start()

        for process in self._processes:
            process.start()

    def _stop_pipeline(self):
        """Gracefully stop all components."""

        # Allow all components to finish processing
        for thread in self._threads:
            thread.join(timeout=5)

        for process in self._processes:
            process.join(timeout=5)

        # Forcefully terminate any stuck processes
        for process in self._processes:
            if process.is_alive():
                print(
                    f"🚨 {process.__class__.__name__} did not stop gracefully."
                    "Terminating."
                )
                process.terminate()

        print("✅ All server pipeline processes stopped.")

    def run(self):
        """Run the pipeline manager and handle shutdown signals."""
        # Register signal handler only in the parent process
        if os.getpid() == self._parent_pid:
            signal.signal(signal.SIGINT, self.signal_handler)

        try:
            self._start_pipeline()

            while not self._stop_event.is_set():
                time.sleep(0.1)
        finally:
            self._stop_pipeline()

    def run_async(self):
        """Run the pipeline manager for non-blocking execution."""
        self._start_pipeline()
        return self

    def stop(self):
        """Stop the pipeline."""
        self._stop_event.set()
        self._stop_pipeline()
