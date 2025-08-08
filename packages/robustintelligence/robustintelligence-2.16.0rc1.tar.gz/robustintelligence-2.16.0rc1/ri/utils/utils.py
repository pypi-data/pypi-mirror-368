"""Utility functions for working with the Robust Intelligence SDK."""

from time import sleep, time

from ri import RIClient
from ri.apiclient import ID, JobStatus

TERMINAL_STATUSES: list[JobStatus] = [
    JobStatus.JOB_STATUS_FAILED,
    JobStatus.JOB_STATUS_CANCELLED,
    JobStatus.JOB_STATUS_SUCCEEDED,
]


class RIUtils:
    """Utility functions for working with the Robust Intelligence SDK."""

    def __init__(self, client: RIClient):
        """Initialize the utility class with an RI client."""
        self._client = client

    def await_job_completion(
        self, job_id: ID, poll_interval: float = 1.0, timeout: float = 300.0
    ) -> JobStatus:
        """Wait until a job is finished.

        :param job_id: The job ID to wait for.
        :param poll_interval: Time in seconds to wait between status checks.  Default is 1 second.
        :param timeout: Maximum time in seconds to wait for job completion. None for no timeout.  Default is 300 seconds.
        :return: The final status of the job.
        :raises TimeoutError: If the job doesn't complete within the specified timeout.
        """
        elapsed_time = 0.0
        start_time = time()
        while True:
            print(f"Polling job {job_id} (elapsed time: {elapsed_time:.2f}s)")
            job_response = self._client.job_reader.get_job(job_id=job_id.uuid)
            current_status = job_response.job.status

            if current_status in TERMINAL_STATUSES:
                return current_status

            elapsed_time = time() - start_time
            if timeout is not None and elapsed_time >= timeout:
                raise TimeoutError(f"Job did not complete within {timeout} seconds")

            sleep(poll_interval)
