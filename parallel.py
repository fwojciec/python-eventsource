import asyncio
from signal import SIGINT, SIGTERM


async def app1():
    try:
        while True:
            print("App 1 is running")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("App 1 is shutting down")


async def app2():
    try:
        while True:
            print("App 2 is running")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("App 2 is shutting down")


def signal_handler(sig):
    loop = asyncio.get_running_loop()
    for task in asyncio.all_tasks(loop=loop):
        task.cancel()
    print(f"Got signal: {sig!s}, shutting down.")
    loop.remove_signal_handler(SIGTERM)
    loop.add_signal_handler(SIGINT, lambda: None)


async def main():
    loop = asyncio.get_running_loop()
    for sig in (SIGTERM, SIGINT):
        loop.add_signal_handler(sig, signal_handler, sig)

    try:
        await asyncio.gather(app1(), app2())
    except asyncio.CancelledError:
        print("All apps are shutting down.")


if __name__ == "__main__":
    asyncio.run(main())
