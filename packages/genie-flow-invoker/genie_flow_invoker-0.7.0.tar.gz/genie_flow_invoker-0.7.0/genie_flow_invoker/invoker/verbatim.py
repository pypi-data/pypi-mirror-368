from genie_flow_invoker import GenieInvoker


class VerbatimInvoker(GenieInvoker):

    @classmethod
    def from_config(cls, config: dict):
        return cls()

    def invoke(self, content: str) -> str:
        """
        Invokes the verbatim invoker that just copies the content as a result.

        :param content: Any text content
        :returns: the `str` version of the content
        """
        return str(content)
