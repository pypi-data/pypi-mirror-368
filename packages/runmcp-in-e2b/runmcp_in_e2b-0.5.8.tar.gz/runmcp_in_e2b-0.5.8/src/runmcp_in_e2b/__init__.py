import asyncio

#from .runmcp import main as _main
from .bomcfault import main as _main

def main():
    asyncio.run(_main())

if __name__ == "__main__":
    main()