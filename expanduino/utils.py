import asyncio
import os
import traceback

async def run_coroutines(*coroutines):
  tasks = [
    asyncio.ensure_future(coroutine)
    for coroutine in coroutines
  ]
  ex = []
  while tasks:
    try:
      await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
    except asyncio.CancelledError:
      pass
    except Exception as e:
      traceback.print_exc()
      ex.append(e)

    finally:
      pending = []
      for task in tasks:
        if not task.done():
          task.cancel()
          pending.append(task)
        else:
          try:
            task.result()
          except asyncio.CancelledError:
            pass
          except Exception as e:
            traceback.print_exc()
            ex.append(e)
      tasks = pending
  if ex:
    raise ex[0]



def mklink(to, format):
  i=0
  while True:
    try:
      link = format % (i,)
      os.symlink(to, link)
      return link
    except FileExistsError:
      i += 1


def create_link(to, format):
  class Context:
    def __init__(self):
      self.link = None
    
    async def __aenter__(self):
      self.link = mklink(to, format)
      print("Created", self.link, "=>", to)
      return self.link

    async def __aexit__(self, exc_type, exc, tb):
      os.remove(self.link)
      print("Removed", self.link, "=>", to)
      self.link = None

  return Context()


def fd_reader(fd, callback, n=1024):
  class Context:
    async def __aenter__(self):
      def readFunc():
        buffer = os.read(fd, n)
        callback(buffer)
      asyncio.get_event_loop().add_reader(fd, readFunc)

    async def __aexit__(self, exc_type, exc, tb):
      asyncio.get_event_loop().remove_reader(fd)

  return Context()

async def forever():
  while True:
    await asyncio.Future()
