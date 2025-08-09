"""Tests for the RIUtils class."""

import pytest
from pytest_mock import MockFixture

from ri import RIClient
from ri.apiclient.models import ID, JobStatus
from ri.utils.utils import RIUtils


@pytest.fixture
def mock_client(mocker: MockFixture) -> RIClient:
    """Create a mock RIClient object."""
    mock_client = mocker.Mock(spec=RIClient)
    mock_client.job_reader.get_job = mocker.Mock()
    return mock_client


class TestRIUtils:
    """Test suite for RIUtils class."""

    @pytest.mark.parametrize(
        "job_status",
        [
            JobStatus.JOB_STATUS_SUCCEEDED,
            JobStatus.JOB_STATUS_FAILED,
            JobStatus.JOB_STATUS_CANCELLED,
        ],
    )
    def test_await_job_completion(
        self, mocker: MockFixture, mock_client: RIClient, job_status: JobStatus
    ) -> None:
        """Test await_job_completion for various job statuses."""
        utils = RIUtils(client=mock_client)
        mock_response = mocker.Mock()
        mock_response.job.status = job_status
        mock_client.job_reader.get_job.return_value = mock_response
        job_id = ID(uuid="test-job-id")

        status = utils.await_job_completion(job_id=job_id)
        assert status == job_status

    def test_await_job_completion_polling(
        self, mocker: MockFixture, mock_client: RIClient
    ) -> None:
        """Test polling behavior of await_job_completion."""
        expected_call_count = 6  # 1 initial + 5 polls
        utils = RIUtils(client=mock_client)
        mock_response = mocker.Mock()
        mock_response.job.status = JobStatus.JOB_STATUS_RUNNING
        mock_client.job_reader.get_job.return_value = mock_response
        job_id = ID(uuid="test-job-id")

        mocker.patch("time.sleep")
        with pytest.raises(TimeoutError):
            utils.await_job_completion(job_id=job_id, timeout=1.0, poll_interval=0.2)

        assert mock_client.job_reader.get_job.call_count == expected_call_count

    def test_await_job_completion_raises_timeout(
        self, mocker: MockFixture, mock_client: RIClient
    ) -> None:
        """Test that await_job_completion raises TimeoutError."""
        utils = RIUtils(client=mock_client)
        mock_response = mocker.Mock()
        mock_response.job.status = JobStatus.JOB_STATUS_RUNNING
        mock_client.job_reader.get_job.return_value = mock_response
        job_id = ID(uuid="test-job-id")

        mocker.patch("time.time", side_effect=[0, 0.5, 1.0, 1.5])
        with pytest.raises(TimeoutError):
            utils.await_job_completion(job_id=job_id, timeout=1.0)

    def test_await_job_completion_handles_exception(
        self, mock_client: RIClient
    ) -> None:
        """Test error handling in await_job_completion."""
        utils = RIUtils(client=mock_client)
        mock_client.job_reader.get_job.side_effect = Exception("API Error")
        job_id = ID(uuid="test-job-id")

        with pytest.raises(Exception, match="API Error"):
            utils.await_job_completion(job_id=job_id)
