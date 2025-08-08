from turbobt.substrate.exceptions import SubstrateException
from turbobt.subtensor.exceptions import SUBSTRATE_CUSTOM_ERRORS, SubtensorException

from .._models import Request, Response
from .base import BaseTransport


class MockTransport(BaseTransport):

    def __init__(self, subtensor):
        self.subtensor = subtensor

    async def send(self, request: Request) -> Response:
        try:
            response = await self.subtensor(request.method, **request.params)
        except SubtensorException as e:
            if type(e) in SUBSTRATE_CUSTOM_ERRORS.values():
                return Response(
                    request=request,
                    result=None,
                    error={
                        "code": 1010,
                        "data": next(
                            data
                            for data, exc in SUBSTRATE_CUSTOM_ERRORS.items()
                            if isinstance(e, exc)
                        ),
                        "message": e.__doc__,
                    },
                )

            return Response(
                request=request,
                result=None,
                error={
                    "code": 1010,
                    "name": type(e).__name__,
                    "docs": [type(e).__doc__],
                },
            )
        except SubstrateException as e:
            return Response(
                request=request,
                result=None,
                error=e,    # TODO
            )

        return Response(
            request=request,
            result=response,
            #TODO error
        )

    def subscribe(self, subscription_id):
        return self.subtensor.subscribe(subscription_id)
    
    def unsubscribe(self, subscription_id):
        self.subtensor.unsubscribe(subscription_id)
