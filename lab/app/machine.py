import json
import logging
import os
import random
import threading
import time
import uuid
from typing import Iterable

import requests
from flask import Flask, jsonify, request
from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.metrics import Observation
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode


MACHINE_NAME = os.getenv("MACHINE_NAME", "machine")
SERVICE_NAME = os.getenv("SERVICE_NAME", MACHINE_NAME)
SERVICE_NAMESPACE = os.getenv("SERVICE_NAMESPACE", "signoz-lab")
DEPLOYMENT_ENVIRONMENT = os.getenv("DEPLOYMENT_ENVIRONMENT", "test")
PORT = int(os.getenv("PORT", "8000"))
OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://signoz-otel-collector:4318").rstrip("/")
DOWNSTREAM_URL = os.getenv("DOWNSTREAM_URL", "").rstrip("/")
TRAFFIC_TARGET_URL = os.getenv("TRAFFIC_TARGET_URL", "").rstrip("/")
TRAFFIC_INTERVAL_SECONDS = float(os.getenv("TRAFFIC_INTERVAL_SECONDS", "0"))
FAILURE_RATE = float(os.getenv("FAILURE_RATE", "0.05"))
BASE_LATENCY_MS = int(os.getenv("BASE_LATENCY_MS", "100"))


resource = Resource.create(
    {
        "service.name": SERVICE_NAME,
        "service.namespace": SERVICE_NAMESPACE,
        "service.version": "1.0.0",
        "deployment.environment": DEPLOYMENT_ENVIRONMENT,
        "host.name": MACHINE_NAME,
        "lab.machine": MACHINE_NAME,
    }
)

trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{OTLP_ENDPOINT}/v1/traces"))
)
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(__name__)

metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=f"{OTLP_ENDPOINT}/v1/metrics"),
    export_interval_millis=5000,
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)

logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(OTLPLogExporter(endpoint=f"{OTLP_ENDPOINT}/v1/logs"))
)
set_logger_provider(logger_provider)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(
    logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s machine=%(machine)s message=%(message)s"
    )
)
otel_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)

logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(logging.INFO)
logger.handlers = []
logger.addHandler(stream_handler)
logger.addHandler(otel_handler)
logger.propagate = False

RequestsInstrumentor().instrument()

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

request_counter = meter.create_counter(
    "lab_requests_total", description="Total requests processed by the lab services."
)
error_counter = meter.create_counter(
    "lab_errors_total", description="Total errors produced by the lab services."
)
heartbeat_counter = meter.create_counter(
    "lab_heartbeat_total", description="Synthetic loop iterations emitted by the lab."
)
duration_histogram = meter.create_histogram(
    "lab_request_duration_ms",
    unit="ms",
    description="Request duration for the synthetic lab services.",
)

queue_lock = threading.Lock()
queue_depth = 0


def common_attributes() -> dict[str, str]:
    return {
        "machine": MACHINE_NAME,
        "service.name": SERVICE_NAME,
        "service.namespace": SERVICE_NAMESPACE,
        "deployment.environment": DEPLOYMENT_ENVIRONMENT,
    }


def queue_observer(_: object) -> Iterable[Observation]:
    with queue_lock:
        current = queue_depth
    return [Observation(current, common_attributes())]


meter.create_observable_gauge(
    "lab_queue_depth",
    callbacks=[queue_observer],
    description="Approximate in-flight workload depth for the synthetic machine.",
)


def log(level: int, message: str, **fields: object) -> None:
    payload = json.dumps(fields, sort_keys=True)
    logger.log(level, f"{message} fields={payload}", extra={"machine": MACHINE_NAME})


def add_queue(delta: int) -> None:
    global queue_depth
    with queue_lock:
        queue_depth = max(0, queue_depth + delta)


def simulate_latency(multiplier: float = 1.0) -> None:
    jitter = random.randint(0, 120)
    latency_ms = max(15, int(BASE_LATENCY_MS * multiplier) + jitter)
    time.sleep(latency_ms / 1000)


def maybe_fail(operation: str) -> None:
    if random.random() < FAILURE_RATE:
        raise RuntimeError(f"{operation} failed on {MACHINE_NAME}")


def call_downstream(trace_id: str) -> dict[str, object]:
    if not DOWNSTREAM_URL:
        return {"downstream": None}

    response = requests.get(
        f"{DOWNSTREAM_URL}/api/store",
        headers={"x-lab-trace-id": trace_id},
        params={"source": MACHINE_NAME},
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


@app.route("/")
def index() -> tuple[object, int]:
    return (
        jsonify(
            {
                "machine": MACHINE_NAME,
                "service": SERVICE_NAME,
                "downstream": DOWNSTREAM_URL or None,
                "traffic_target": TRAFFIC_TARGET_URL or None,
            }
        ),
        200,
    )


@app.route("/health")
def health() -> tuple[object, int]:
    return jsonify({"status": "ok", "machine": MACHINE_NAME}), 200


@app.route("/api/process")
def process() -> tuple[object, int]:
    started = time.perf_counter()
    attrs = common_attributes()
    request_counter.add(1, attrs)
    add_queue(1)
    trace_id = request.headers.get("x-lab-trace-id", str(uuid.uuid4()))
    source = request.args.get("source", "external")

    with tracer.start_as_current_span("machine.process") as span:
        span.set_attribute("lab.machine", MACHINE_NAME)
        span.set_attribute("lab.source", source)
        span.set_attribute("lab.trace_id", trace_id)
        try:
            simulate_latency()
            downstream_payload = call_downstream(trace_id)
            maybe_fail("process")
            payload = {
                "machine": MACHINE_NAME,
                "service": SERVICE_NAME,
                "source": source,
                "trace_id": trace_id,
                "downstream": downstream_payload,
                "status": "processed",
            }
            log(logging.INFO, "request processed", endpoint="/api/process", trace_id=trace_id, source=source)
            return jsonify(payload), 200
        except Exception as exc:
            error_counter.add(1, attrs)
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR))
            log(
                logging.ERROR,
                "request failed",
                endpoint="/api/process",
                trace_id=trace_id,
                source=source,
                error=str(exc),
            )
            return jsonify({"status": "error", "machine": MACHINE_NAME, "error": str(exc)}), 500
        finally:
            add_queue(-1)
            duration_histogram.record((time.perf_counter() - started) * 1000, attrs)


@app.route("/api/store")
def store() -> tuple[object, int]:
    started = time.perf_counter()
    attrs = common_attributes()
    request_counter.add(1, attrs)
    add_queue(1)
    trace_id = request.headers.get("x-lab-trace-id", str(uuid.uuid4()))
    source = request.args.get("source", "machine-2")

    with tracer.start_as_current_span("machine.store") as span:
        span.set_attribute("lab.machine", MACHINE_NAME)
        span.set_attribute("lab.source", source)
        span.set_attribute("lab.trace_id", trace_id)
        try:
            simulate_latency(multiplier=1.4)
            maybe_fail("store")
            payload = {
                "machine": MACHINE_NAME,
                "service": SERVICE_NAME,
                "source": source,
                "trace_id": trace_id,
                "status": "stored",
            }
            log(logging.INFO, "write completed", endpoint="/api/store", trace_id=trace_id, source=source)
            return jsonify(payload), 200
        except Exception as exc:
            error_counter.add(1, attrs)
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR))
            log(
                logging.WARNING,
                "write failed",
                endpoint="/api/store",
                trace_id=trace_id,
                source=source,
                error=str(exc),
            )
            return jsonify({"status": "error", "machine": MACHINE_NAME, "error": str(exc)}), 500
        finally:
            add_queue(-1)
            duration_histogram.record((time.perf_counter() - started) * 1000, attrs)


def traffic_loop() -> None:
    if not TRAFFIC_TARGET_URL or TRAFFIC_INTERVAL_SECONDS <= 0:
        return

    session = requests.Session()

    while True:
        trace_id = str(uuid.uuid4())
        attrs = common_attributes()
        heartbeat_counter.add(1, attrs)
        with tracer.start_as_current_span("machine.synthetic_traffic") as span:
            span.set_attribute("lab.machine", MACHINE_NAME)
            span.set_attribute("lab.target", TRAFFIC_TARGET_URL)
            span.set_attribute("lab.trace_id", trace_id)
            try:
                response = session.get(
                    TRAFFIC_TARGET_URL,
                    headers={"x-lab-trace-id": trace_id},
                    params={"source": MACHINE_NAME},
                    timeout=5,
                )
                log(
                    logging.INFO,
                    "synthetic traffic sent",
                    target=TRAFFIC_TARGET_URL,
                    trace_id=trace_id,
                    status_code=response.status_code,
                )
            except Exception as exc:
                error_counter.add(1, attrs)
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR))
                log(
                    logging.ERROR,
                    "synthetic traffic failed",
                    target=TRAFFIC_TARGET_URL,
                    trace_id=trace_id,
                    error=str(exc),
                )
            time.sleep(TRAFFIC_INTERVAL_SECONDS)


def noise_loop() -> None:
    while True:
        heartbeat_counter.add(1, common_attributes())
        log(
            logging.INFO,
            "machine heartbeat",
            queue_depth=queue_depth,
            downstream=DOWNSTREAM_URL or None,
        )
        time.sleep(10)


if __name__ == "__main__":
    log(
        logging.INFO,
        "machine booting",
        otlp_endpoint=OTLP_ENDPOINT,
        downstream=DOWNSTREAM_URL or None,
        traffic_target=TRAFFIC_TARGET_URL or None,
    )
    threading.Thread(target=traffic_loop, daemon=True).start()
    threading.Thread(target=noise_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT, debug=False)
