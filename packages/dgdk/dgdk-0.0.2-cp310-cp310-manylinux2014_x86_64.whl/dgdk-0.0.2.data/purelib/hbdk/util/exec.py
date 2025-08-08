import sys
import signal


def exit_gracefully_by_sig(sig, _):
    print("Receive signal {}. Exit".format(sig), file=sys.stderr, flush=True)
    while True:
        raise KeyboardInterrupt


def register_exit_gracefully_handler():
    signals = [
        signal.SIGTERM, signal.SIGQUIT, signal.SIGHUP, signal.SIGUSR1,
        signal.SIGUSR2
    ]
    for s in signals:
        signal.signal(s, exit_gracefully_by_sig)
