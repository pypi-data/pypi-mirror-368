import time

import structlog
from google.cloud.monitoring_v3 import TimeSeries
from grpc import Call, RpcError, StatusCode
from opentelemetry.exporter.cloud_monitoring import MAX_BATCH_WRITE, CloudMonitoringMetricsExporter
from typing_extensions import Any, override

logger = structlog.getLogger(__name__)

DEFAULT_MAX_ATTEMPTS = 5
INITIAL_BACKOFF = 1.0
MAX_BACKOFF = 10.0
BACKOFF_MULTIPLIER = 2.0


class RetryableCloudMonitoringMetricsExporter(CloudMonitoringMetricsExporter):
    def __init__(
        self,
        *args: Any,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self._max_attempts = max_attempts

    @override
    def _batch_write(self, series: list[TimeSeries]) -> None:
        for write_ind in range(0, len(series), MAX_BATCH_WRITE):
            batch = series[write_ind : write_ind + MAX_BATCH_WRITE]
            backoff = INITIAL_BACKOFF
            for attempt in range(1, self._max_attempts + 1):
                try:
                    self.client.create_time_series(
                        name=self.project_name,
                        time_series=batch,
                    )
                    logger.debug(
                        "sent metrics",
                        batch_size=len(batch),
                        attempt=attempt,
                    )
                    break
                except RpcError as e:
                    if e.code() in [StatusCode.UNAVAILABLE, StatusCode.RESOURCE_EXHAUSTED]:  # pylint: disable=no-member
                        if attempt == self._max_attempts:
                            logger.warning(
                                "failed to send metrics after max retries",
                                error=str(e),
                                code=str(e.code()),
                                attempts=attempt,
                            )
                            return
                        time.sleep(backoff)
                        backoff = min(backoff * BACKOFF_MULTIPLIER, MAX_BACKOFF)
                    else:
                        logger.warning(
                            "failed to send metrics",
                            error=str(e),
                            code=str(e.code()) if isinstance(e, Call) else "unknown",
                            attempts=attempt,
                            max_retry_limit_reached=attempt == self._max_attempts,
                        )
                        return
