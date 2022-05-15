import asyncio


waiting_time = 5

async def print_stuff():
    print(f"Start printing and wait {waiting_time} seconds")
    await asyncio.sleep(waiting_time)
    print("I finished waiting and finished printing")
    return "Ok"

async def parallel_stuff():
    print("This is the way to parallelize stuff in Asyncio")
    print("I am done and print is still on going")
    return "Return from parallel universe"

async def main():
    print("Main program started")
    
    ret = await asyncio.gather(             # Run in "parallel"
        print_stuff(),
        parallel_stuff()
    )
    print(f"Main finished :-) with return {ret}")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())