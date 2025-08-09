"""
Simple NATS Connection for ONQL Extension SDK
"""
import asyncio
import nats

class Connection:
    """Simple NATS connection class"""
    
    def __init__(self):
        self.nc = None
        self.connected = False
    
    async def connect(self, url="nats://localhost:4222"):
        """Connect to NATS server on default port"""
        try:
            self.nc = await nats.connect(url)
            self.connected = True
            print(f"Connected to NATS at {url}")
            return True
        except Exception as e:
            print(f"Failed to connect to NATS: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from NATS"""
        if self.nc and self.connected:
            await self.nc.close()
            self.connected = False
            print("Disconnected from NATS")
    
    def is_connected(self):
        """Check if connected"""
        return self.connected

