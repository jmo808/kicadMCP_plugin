import json
import time
import urllib.error
import urllib.request

from kbd_engine.exceptions import RouterError
from kbd_engine.pcbnew_adapter import PcbnewAdapter
from kbd_engine.router import Router
from kbd_engine.routers.freerouting import FreeRoutingRouter
from kbd_engine.routing_models import RoutingRequest, RoutingResult


class QuilterRouter(Router):
    """Router implementation that delegates to the external Quilter API."""

    def __init__(
        self,
        api_key: str,
        api_url: str = "https://api.quilter.ai/v1",
        timeout: float = 120,
        poll_interval: float = 2,
    ) -> None:
        """Initialize the Quilter API router.

        Args:
            api_key: The API key for authenticating with the Quilter service.
            api_url: Base URL for the Quilter API.
            timeout: Max duration in seconds to wait for routing completion.
            poll_interval: Polling frequency in seconds.
        """
        self.api_key = api_key
        self.api_url = api_url
        self.timeout = timeout
        self.poll_interval = poll_interval

    def route(self, request: RoutingRequest) -> RoutingResult:
        """Route the board using Quilter API.

        Args:
            request: The routing request containing netlist, board, and rules.

        Returns:
            A RoutingResult containing the trace segments, vias, and status.

        Raises:
            RouterError: If authentication, connection, or routing fails.
        """
        if not self.api_key:
            raise RouterError("Quilter API key is missing or empty")

        # Reuse FreeRouting's DSN exporter to serialize board coordinates
        freerouting_router = FreeRoutingRouter()
        adapter = PcbnewAdapter()
        try:
            adapter.load(request.board_file)
            dsn_content = freerouting_router.export_dsn(adapter, request)
        except Exception as e:
            raise RouterError(f"Failed to export DSN for Quilter: {e}") from e

        # 1. Submit job to Quilter API
        job_id = self._submit_job(dsn_content)

        # 2. Poll for job completion
        ses_content = self._poll_job(job_id)

        # 3. Parse session result using S-expression parser
        try:
            result = freerouting_router.parse_ses(ses_content)
        except Exception as e:
            raise RouterError(f"Failed to parse Quilter SES output: {e}") from e

        # 4. Write back tracks and vias to the board
        if result.success:
            for trace in result.traces:
                adapter.add_track(
                    start_x=trace.start[0],
                    start_y=trace.start[1],
                    end_x=trace.end[0],
                    end_y=trace.end[1],
                    layer=trace.layer,
                    width=trace.width,
                )
            for via in result.vias:
                adapter.add_via(
                    x=via.position[0],
                    y=via.position[1],
                    drill=via.drill,
                    diameter=via.diameter,
                )
            try:
                adapter.save(request.board_file)
            except Exception as e:
                raise RouterError(f"Failed to save board after Quilter routing: {e}") from e

        return result

    def _submit_job(self, dsn_content: str) -> str:
        url = f"{self.api_url}/jobs"
        payload = json.dumps({"dsn": dsn_content}).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                resp_data = json.loads(response.read().decode("utf-8"))
                job_id = resp_data.get("job_id")
                if not job_id:
                    raise RouterError("Quilter response missing job_id")
                return str(job_id)
        except urllib.error.HTTPError as e:
            self._handle_http_error(e)
        except Exception as e:
            raise RouterError(f"Failed to submit Quilter job: {e}") from e

        raise RouterError("Failed to submit Quilter job")

    def _poll_job(self, job_id: str) -> str:
        url = f"{self.api_url}/jobs/{job_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        start_time = time.time()
        while time.time() - start_time < self.timeout:
            req = urllib.request.Request(url, headers=headers, method="GET")
            try:
                with urllib.request.urlopen(req) as response:
                    resp_data = json.loads(response.read().decode("utf-8"))
                    status = resp_data.get("status")
                    if status == "completed":
                        ses = resp_data.get("ses")
                        if not ses:
                            raise RouterError("Quilter job completed but missing SES output")
                        return str(ses)
                    elif status == "failed":
                        reason = resp_data.get("error", "Unknown error reason")
                        raise RouterError(f"Quilter job failed: {reason}")
                    elif status in ("pending", "running"):
                        time.sleep(self.poll_interval)
                        continue
                    else:
                        raise RouterError(f"Unknown Quilter job status: {status}")
            except urllib.error.HTTPError as e:
                self._handle_http_error(e)
            except Exception as e:
                raise RouterError(f"Failed to poll Quilter job status: {e}") from e

        raise RouterError(f"Quilter job timed out after {self.timeout} seconds")

    def _handle_http_error(self, e: urllib.error.HTTPError) -> None:
        try:
            error_data = json.loads(e.read().decode("utf-8"))
            msg = error_data.get("error", e.reason)
        except Exception:
            msg = e.reason

        if e.code in (401, 403):
            raise RouterError(f"Quilter API authentication failed: {msg}") from e
        elif e.code == 429:
            raise RouterError(f"Quilter API rate limit exceeded: {msg}") from e
        else:
            raise RouterError(f"Quilter API HTTP error {e.code}: {msg}") from e
