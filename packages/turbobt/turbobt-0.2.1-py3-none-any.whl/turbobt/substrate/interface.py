from turbobt.substrate.pallets.author import Author
from turbobt.substrate.pallets.chain import Chain
from turbobt.substrate.pallets.state import State
from turbobt.substrate.pallets.system import System
from turbobt.substrate.runtime.metadata import Metadata


class SubstrateInterface:
    author: Author
    chain: Chain
    metadata: Metadata
    state: State
    system: System