import scalecodec
import sqlalchemy
import sqlalchemy.ext.asyncio

from turbobt.simulator import db
from turbobt.simulator.pallets.author import Author
from turbobt.simulator.pallets.chain import Chain
from turbobt.simulator.pallets.state import State
from turbobt.simulator.pallets.system import System
from turbobt.simulator.runtime.metadata import Metadata
from turbobt.simulator.runtime.neuron_info import NeuronInfoRuntimeApi
from turbobt.simulator.runtime.subnet_info import SubnetInfoRuntimeApi
from turbobt.simulator.runtime.subtensor_module import SubtensorModule
from turbobt.substrate._scalecodec import load_type_registry_v15_types


class MockedSubtensor:
    # def __init__(self, url="sqlite+aiosqlite:///memdb1?mode=memory&cache=shared"):
    def __init__(self, url="sqlite+aiosqlite:///:memory:"):
        self.db_engine = sqlalchemy.ext.asyncio.create_async_engine(
            url,
            echo=True,
        )
        self.db_session = sqlalchemy.ext.asyncio.async_sessionmaker(
            bind=self.db_engine,
            expire_on_commit=False,
        )

        self.chain = Chain(self)
        self.author = Author(self)
        self.state = State(self)
        self.system = System(self)

        self.SubtensorModule = SubtensorModule(self)
        self.Metadata = Metadata(self)
        self.NeuronInfoRuntimeApi = NeuronInfoRuntimeApi(self)
        self.SubnetInfoRuntimeApi = SubnetInfoRuntimeApi(self)

        self._subscriptions = {}

    def __call__(self, rpc, **params):
        api_name, method_name = rpc.split("_", 1)

        try:
            api = getattr(self, api_name)
            method = getattr(api, method_name)
        except AttributeError:
            raise NotImplementedError

        return method(**params)

    async def init(self):
        async with self.db_engine.begin() as conn:
            await conn.run_sync(db.Base.metadata.create_all)

        async with self.db_session.begin() as session:
            block0 = db.Block(
                number=0,
                # hash="0x" + bytes([69] * 32).hex(),
            )
            block = db.Block(
                number=1,
            )

            session.add(block0)
            session.add(block)

        runtime_config = scalecodec.base.RuntimeConfigurationObject()
        runtime_config.update_type_registry(
            scalecodec.type_registry.load_type_registry_preset(name="core"),
        )

        # patching-in MetadataV15 support
        runtime_config.update_type_registry_types(load_type_registry_v15_types())
        runtime_config.type_registry["types"]["metadataall"].type_mapping.append(
            ["V15", "MetadataV15"],
        )

        self._registry = runtime_config

        metadata = self._registry.create_scale_object(
            "Option<Vec<u8>>",
            data=scalecodec.ScaleBytes(await self.Metadata.metadata_at_version("0xff0000")),
        )
        metadata.decode()

        if not metadata.value:
            return None

        metadata = self._registry.create_scale_object(
            "MetadataVersioned",
            data=scalecodec.ScaleBytes(metadata.value),
        )
        metadata.decode()

        self._metadata = metadata

        metadata15 = metadata.value[1]["V15"]

        runtime_config.add_portable_registry(metadata)

        self._apis = {
            api["name"]: api | {
                "methods": {
                    api_method["name"]: api_method
                    for api_method in api["methods"]
                }
            }
            for api in metadata15["apis"]
        }

    def subscribe(self, subscription_id):
        return self._subscriptions[subscription_id]
    
    def unsubscribe(self, subscription_id):
        return self._subscriptions.pop(subscription_id, None)
