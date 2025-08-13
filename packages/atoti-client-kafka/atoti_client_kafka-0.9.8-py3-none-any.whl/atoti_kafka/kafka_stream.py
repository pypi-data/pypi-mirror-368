from dataclasses import KW_ONLY
from datetime import timedelta
from typing import final

from atoti._collections import FrozenMapping, frozendict
from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from atoti._typing import Duration
from atoti.data_stream import DataStream
from pydantic.dataclasses import dataclass
from typing_extensions import override


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
# Unlike the other plugin symbols, this one repeats the plugin key in its name (i.e. it is not just `Stream`).
# The reasons are:
# - Class names should be nouns but `Stream` can read as a verb (`KafkaStream` reads a noun, as opposed to `StreamKafka`).
# - It avoids stuttering: `table.stream(Stream())`.
class KafkaStream(DataStream):
    """Consume a Kafka topic and stream its records in the table.

    The records' key deserializer default to `StringDeserializer <https://kafka.apache.org/21/javadoc/org/apache/kafka/common/serialization/StringDeserializer.html>`__.

    The records' message must be a JSON object with columns' name as keys.

    See Also:
        The other :class:`~atoti.data_stream.DataStream` implementations.

    """

    bootstrap_server: str
    """``host[:port]`` that the consumer should contact to bootstrap initial cluster metadata."""

    topic: str
    """Topic to subscribe to."""

    group_id: str
    """The name of the consumer group to join."""

    _: KW_ONLY

    batch_duration: Duration = timedelta(seconds=1)
    """Time spent batching received events before publishing them to the table in a single transaction."""

    consumer_config: FrozenMapping[str, str] = frozendict()
    """Mapping containing optional parameters to set up the KafkaConsumer.

    The list of available params can be found `here <https://kafka.apache.org/10/javadoc/index.html?org/apache/kafka/clients/consumer/ConsumerConfig.html>`__.
    """

    @property
    @override
    def _options(
        self,
    ) -> dict[str, object]:
        return {
            "additionalParameters": self.consumer_config,
            "batchDuration": int(self.batch_duration.total_seconds() * 1000),
            "bootstrapServers": self.bootstrap_server,
            "consumerGroupId": self.group_id,
            "keyDeserializerClass": "org.apache.kafka.common.serialization.StringDeserializer",
            "topic": self.topic,
        }

    @property
    @override
    def _plugin_key(self) -> str:
        return "KAFKA"
