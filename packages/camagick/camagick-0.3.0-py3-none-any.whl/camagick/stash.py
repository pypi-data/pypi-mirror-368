#!/usr/bin/pyton3

''' Various stash access helpers '''

import fcntl, asyncio, logging, xarray, random, time

class ZarrStash:
    ''' Stashes the data in a Zarr archive on disk.

    Synchronizes seed/crop access using lock files.
    '''

    def __init__(self, storage, lockKey, data=None):
        ''' Intializes stash system.

        Args:
            storage: Storage path (zarr folder)
            lockKey: Key detail for locking. This is used to generate
              a unique lock file based on the storage path.
            data: (optional) xarray data to store.
        '''
        self.storage = storage
        self.lockKey = lockKey
        self.lockPath = storage+lockKey+".lock" if lockKey is not None else None
        self.lockFile = None
        self.myLock = False

        self.contextCnt = 0


    def tryLock(self):
        ''' Attempts to lock, returns True on success or False otherwise. '''

        # disable lock of key is None
        if self.lockKey is None:
            return True
        
        try:
            self.lockFile = open(self.lockPath, 'w+')
            fcntl.flock(self.lockFile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.myLock = True
            return True
        except FileNotFoundError:
            raise
        except IOError as e:
            return False
        

    def unlock(self):
        ''' Frees the lock. '''
        if self.lockKey:
            return
        
        fcntl.flock(self.lockFile.fileno(), fcntl.LOCK_UN)
        self.lockFile = None
        self.myLock = False

    def nolockSave(self, data, keys=None):
        data.to_zarr(store=self.storage, mode='a')

    def nolockLoad(self, keys=None):
        return xarray.load_dataset(self.storage, engine='zarr')        
        
    def save(self, data, keys=None):
        with self:
            return self.nolockSave(data, keys)

    def load(self, keys=None):
        with self:
            return self.nolockLoad(keys)

    def __enter__(self):
        self.contextCnt += 1
        self.waitLock()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.contextCnt > 1:
            self.contextCnt -= 1
        if self.contextCnt == 0:
            self.unlock()

    async def waitLock(self, pollPeriod=1e-5):
        ''' Asynchronously wait for a lock on the stash.
        '''
        while not self.tryLock():
            time.sleep(pollPeriod+pollPeriod*random.random()*0.01)
    

    async def __aenter__(self):
        self.contextCnt += 1
        await self.asyncWaitLock()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.contextCnt > 1:
            self.contextCnt -= 1
        if self.contextCnt == 0:
            self.unlock()    
    
    async def asyncWaitLock(self, pollPeriod=1e-5):
        ''' Asynchronously wait for a lock on the stash.
        '''
        while not self.tryLock():
            await asyncio.sleep(pollPeriod+pollPeriod*random.random()*0.01)
    
    async def asyncSave(self, data, keys=None):
        async with self:
            self.nolockSave(data, keys)
            
    async def asyncLoad(self, keys=None):
        async with self:
            return self.nolockLoad(keys)
