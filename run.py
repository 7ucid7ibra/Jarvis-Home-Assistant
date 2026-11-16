#!/usr/bin/env python3
import multiprocessing as mp


def main() -> None:
    from jarvis_assistant.app.controller import JarvisController

    controller = JarvisController()
    controller.run()


if __name__ == "__main__":
    mp.freeze_support()
    main()
