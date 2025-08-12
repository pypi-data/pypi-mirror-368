import abc
import json
from typing import Any

from loguru import logger


class AbstractInputDecoder(abc.ABC):

    @abc.abstractmethod
    def _decode_input(self, content: str) -> Any:
        """
        The generic interface to decode an input from string to a
        dictionary. Must be implemented by subclasses.

        :param content: the string representation of the content to decode
        :return: the decoded content
        """
        raise NotImplementedError()


class AbstractOutputEncoder(abc.ABC):

    @abc.abstractmethod
    def _encode_output(self, output: Any) -> str:
        """
        The generic interface to encode an output to a string.

        :param output: the output to encode
        :return: a string representation of the encoded output
        """
        raise NotImplementedError()


class JsonInputDecoder(AbstractInputDecoder):
    """
    This decoder takes a string input and interprets that as a JSON string.

    The decode input method raises a ValueError if the json decoding
    fails for any reason.

    Overriding the method `object_pair_decode` enables the user of this class
    to define their own decoding of `key` and `value` pairs.
    """

    def object_pair_decode(self, object_pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        """

        :param object_pairs: a list of tuples (key, value) pairs for which an overriding
        class may interpret certain values differently.

        :return: a dictionary containing the decoded content
        """
        return dict(object_pairs)

    def _decode_input(self, content: str) -> dict:
        try:
            return json.loads(content, object_pairs_hook=self.object_pair_decode)
        except json.JSONDecodeError:
            logger.error("Could not decode JSON")
            raise ValueError("Could not decode JSON")


class JsonOutputEncoder(AbstractOutputEncoder):
    """
    This encoder takes an object as input and encodes it to a JSON string.

    The encode input method raises a ValueError if the json encoding
    fails for any reason.

    Overriding the `default_encoder` enables the user of this class
    to override the default JSON encoder class.
    """

    @property
    def default_encoder(self):
        """
        The default JSON encoder class. Can be overridden by subclasses to
        override the default JSON encoder class.

        :return: type[json.JSONEncoder]
        """
        return json.JSONEncoder

    def _encode_output(self, output: Any) -> str:
        try:
            return json.dumps(output, cls=self.default_encoder)
        except TypeError:
            logger.error("Could not encode JSON")
            raise ValueError("Could not encode JSON")
