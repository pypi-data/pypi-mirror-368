#!/usr/bin/python3

import pytest, random, string, asyncio, os, time
from camagick import stash

@pytest.mark.asyncio
async def _test_stash_lock():
    rnd = ''.join(random.choice(string.ascii_lowercase) for i in range(24))

    st = stash.ZarrStash("/tmp/storage"+rnd, lockKey=rnd)

    #print("Waiting for lock...")
    await st.asyncWaitLock()

    pid = os.fork()

    if pid == 0:

        await st.asyncWaitLock()
        
        # parent, child is `pid`
        time.sleep(1.0)

        #print("Unlocking")
        st.unlock()
        
    else:
        # child
        #print("Try to relock (should fail)")
        assert st.tryLock() == False

        time.sleep(2.0)

        #print("Try to relock (should work)")
        assert st.tryLock() == True
        
        #print("Unlocking again")
        st.unlock()


@pytest.mark.asyncio
async def _test_stash_context():
    rnd = ''.join(random.choice(string.ascii_lowercase) for i in range(24))

    async with stash.ZarrStash("/tmp/storage"+rnd, lockKey=rnd) as st:

        pid = os.fork()
        
        if pid == 0:
            # parent
            await st.asyncWaitLock()
            time.sleep(1.0)
        
        else:
            # child
            assert st.tryLock() == False
            time.sleep(2.0)
            assert st.tryLock() == True
            st.unlock()
        
        
