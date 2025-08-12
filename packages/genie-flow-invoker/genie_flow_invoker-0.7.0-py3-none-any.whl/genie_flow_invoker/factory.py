from queue import Queue
from typing import Optional, Type

from genie_flow_invoker import GenieInvoker, InvokersPool
from genie_flow_invoker.class_utils import get_class_from_fully_qualified_name


class InvokerFactory:

    def __init__(
        self,
        config: Optional[dict],
    ):
        self.config = config or dict()

    def create_invoker(self, invoker_config: dict) -> GenieInvoker:
        """
        Create a new invoker, as specified by `invoker_config`. Uses the application's
        configuration as a base. Any configuration specified in `invoker_config` takes
        precedence over any other configuration specified in the application's configuration.

        :param invoker_config: The invoker config to create.
        :return: The created invoker.
        :raises ValueError: If the invoker is not registered or the invoker is invalid.
        """
        try:
            invoker_type = invoker_config["type"]
        except KeyError:
            raise ValueError(f"Invalid invoker config: {invoker_config}")

        cls = get_class_from_fully_qualified_name(invoker_type)
        if not issubclass(cls, GenieInvoker):
            raise ValueError(
                f"Invalid invoker type: {invoker_type}, should be a "
                f"subclass of genie_flow_invoker.genie.GenieInvoker. "
                f"See https://gitlab.stopstaringatme.org/bidgenie/core/"
                f"middleware/invokers/genie-flow-invoker/-/wikis/home")

        config = self.config.get(invoker_type, dict())
        config.update(invoker_config)
        return cls.from_config(config)

    def create_invoker_pool(self, pool_size: int, config: dict) -> InvokersPool:
        assert pool_size > 0, f"Should not create invoker pool of size {pool_size}"

        queue = Queue()
        for _ in range(pool_size):
            queue.put(self.create_invoker(config))

        return InvokersPool(queue)
