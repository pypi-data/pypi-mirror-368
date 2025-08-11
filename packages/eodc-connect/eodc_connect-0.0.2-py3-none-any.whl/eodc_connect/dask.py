import logging
from typing import Optional

from dask_gateway import Gateway, GatewayCluster
from eodc_connect import auth, settings

logger = logging.getLogger(__name__)


class EODCDaskGateway(Gateway):
    def __init__(self, username: str) -> None:
        self.authenticator = auth.DaskOIDC(username=username)
        super().__init__(
            address=settings.DASK_URL,
            proxy_address=settings.DASK_URL_TCP,
            auth=self.authenticator,
        )

    def __new__(cls, *args, **kwargs):
        """There should only ever be one Gateway object instantiated -> singleton."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance


class EODCCluster(GatewayCluster):
    def __init__(self, image: Optional[str] = None):
        self.gateway = EODCDaskGateway()

        cluster_options = self.gateway.cluster_options(use_local_defaults=False)
        if image is not None:
            cluster_options.image = image
        logger.info(f"Provisioning Dask cluster from {self.gateway.address}")

        super().__init__(
            address=self.gateway.address,
            cluster_options=cluster_options,
            shutdown_on_close=True,
        )
        logger.info(f"Initialised Dask Cluster at {self.scheduler_address}")
