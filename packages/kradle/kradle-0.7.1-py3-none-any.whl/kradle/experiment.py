"""
Experiment runner for Kradle challenges.

An experiment is a collection of multiple runs of the same challenge and same agent(s).

Used for evaluating the performance of agents over several runs.
"""

import json
import time
import concurrent.futures
import os
from typing import Any, Optional
from kradle.api.client import KradleAPI
from kradle.models import Run, RunRequest, ExperimentResult, ExperimentParticipantResult
from kradle.logger import KradleLogger


class Experiment:
    """
    A class to run experiments with Kradle challenges.

    This class handles creating runs, monitoring their progress, and fetching logs from the run.
    """

    def __init__(
        self,
        api_client: Optional[KradleAPI] = None,
        fetch_run_logs: Optional[bool] = True,
        use_studio: Optional[bool] = True,
    ):
        """
        Initialize the experiment runner.

        Args:
            api_client: Optional API client for Kradle. If not provided, will use environment variable
            fetch_run_logs: Whether to fetch logs after each run. Default is True, set to False to disable
                for performance.
            use_studio: Whether to use local Kradle Studio for job creation (saves cloud resources). Default is True.
        """
        self._logger = KradleLogger()
        self._fetch_run_logs = fetch_run_logs
        self.use_studio = use_studio

        # Setup API client
        if api_client:
            self._internal_api_client = api_client
        else:
            # If use_studio is True, configure the API client to use Studio URL for jobs
            if use_studio:
                # Get Studio URL from environment or use default (always with trailing slash)
                studio_url = os.environ.get("KRADLE_STUDIO_URL", "http://localhost:2998/")

                self._logger.log_info(f"Using Kradle Studio for experiment job creation: {studio_url}")
                # Override the API base URL just for the jobs endpoint
                os.environ["KRADLE_API_URL"] = studio_url

            self._internal_api_client = KradleAPI()

        self.runs: dict[str, Run] = {}  # keyed by run id
        self.logs: dict[str, list[dict[str, Any]]] = {}  # keyed by run id

    def evaluate(
        self, runs: list[RunRequest], num_concurrent_runs: int = 1, skip_sanity_checks: bool = False
    ) -> ExperimentResult:
        """
        Executes an experiment with the specified challenge and participants.

        Args:
            runs: List of run requests to evaluate
            num_concurrent_runs: Number of runs to execute concurrently (default: 1)

        Returns:
            ExperimentResult
        """
        start_time = time.time()

        challenge_slugs = set([run.challenge_slug for run in runs])
        print(f"Challenge slugs: {challenge_slugs}")

        if not skip_sanity_checks:
            for challenge_slug in challenge_slugs:
                # do some sanity checks on all the challenge slugs
                try:
                    challenge = self._internal_api_client.challenges.get(challenge_slug)
                    if not challenge["slug"] == challenge_slug:
                        raise ValueError(
                            f"Challenge slug {challenge_slug}"
                            f"does not match challenge slug in API response {challenge['slug']}"
                        )
                except Exception as e:
                    raise ValueError(f"Failed to query challenge {challenge_slug} from Kradle") from e

            participant_names = set()
            for run in runs:
                if run.participants:
                    for participant in run.participants:
                        participant_names.add(participant["agent"])

            print(f"Participants: {participant_names}")
            # do some sanity checks on all the participants
            for participant_name in participant_names:
                try:
                    participant_response = self._internal_api_client.agents.get(participant_name)
                    if not participant_response["username"]:
                        raise ValueError("Participant agent username not found in API response")
                except Exception as e:
                    raise ValueError(f"Failed to query participant {participant_name} from Kradle") from e

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent_runs) as executor:
            futures: list[concurrent.futures.Future[Optional[Run]]] = []

            for _run_idx, run_request in enumerate(runs):
                futures.append(executor.submit(self._create_and_monitor_run, _run_idx, run_request))

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    print(f"Run {result.id} finished with status: {result.status}") if result else None
                except Exception as e:
                    print(f"Error when creating and monitoring run in future: {e}")

        finished_runs = [run for run in self.runs.values() if run.status == "finished"]
        results: dict[str, ExperimentParticipantResult] = {}

        for result in finished_runs:
            if not result.participant_results:
                continue

            for participant_id in result.participant_results:
                participant_result = result.participant_results[participant_id]
                if participant_id not in results:
                    results[participant_id] = ExperimentParticipantResult(
                        agent=participant_result.agent,
                        num_runs_finished=0,
                        win_count=0,
                        total_score=0,
                        average_score=0,
                        times_to_success=[],
                        average_time_to_success=0,
                    )
                results[participant_id].num_runs_finished += 1
                results[participant_id].total_score += participant_result.score or 0
                results[participant_id].average_score = (
                    results[participant_id].total_score / results[participant_id].num_runs_finished
                )

                if participant_result.winner:
                    results[participant_id].win_count += 1
                    results[participant_id].times_to_success.append(participant_result.time_to_success or 0)
                    results[participant_id].average_time_to_success = sum(
                        results[participant_id].times_to_success
                    ) / len(results[participant_id].times_to_success)

        duration = time.time() - start_time
        return ExperimentResult(
            num_runs=len(runs),
            num_runs_finished=len(finished_runs),
            results=results,  # keyed by participant id to ExperimentParticipantResult
            runs=self.runs,
            logs=self.logs,
            duration=duration,
        )

    def _create_and_monitor_run(self, run_idx: int, run_request: RunRequest, max_retries: int = 3) -> Optional[Run]:
        run_id: Optional[str] = None
        run: Optional[Run] = None

        num_retries = 0
        while num_retries < max_retries:
            try:
                try:
                    # Print debug info before API call
                    if self.use_studio:
                        studio_url = os.environ.get("KRADLE_API_URL", "http://localhost:2998/")
                        print(f"DEBUG: Calling Studio API at {studio_url}/jobs with:")
                        print(f"  - Challenge: {run_request.challenge_slug}")
                        print(f"  - Participants: {run_request.participants}")

                    # Attempt to create run
                    run_api_response = self._internal_api_client.runs.create(
                        challenge_slug=run_request.challenge_slug, participants=run_request.participants
                    )
                except Exception as e:
                    # If using Studio, provide clearer messages for common errors
                    if self.use_studio:
                        studio_url = os.environ.get("KRADLE_STUDIO_URL", "http://localhost:2998/")

                        # Handle connection errors
                        if "connection" in str(e).lower():
                            error_message = (
                                f"Failed to connect to Kradle Studio at {studio_url}. "
                                "Please ensure Kradle Studio is running or set use_studio=False."
                            )
                            self._logger.log_error(error_message)
                            # Wrap the error with a more informative message
                            raise Exception(error_message) from e

                        # Handle challenge not found errors
                        if "Challenge Not Found" in str(e) or "CHALLENGE_NOT_FOUND" in str(e):
                            error_message = (
                                f"Challenge '{run_request.challenge_slug}' not found in Kradle Studio. "
                                "Please ensure the challenge exists locally in Studio by syncing it from "
                                "Kradle Cloud or creating it in Studio."
                            )
                            self._logger.log_error(error_message)
                            # Wrap the error with a more informative message
                            raise Exception(error_message) from e

                    # For other errors, just raise normally
                    raise
                if "runIds" in run_api_response:
                    run_ids = run_api_response["runIds"]
                    run_id = run_ids[0]

                if run_id:
                    run_api_response = self._internal_api_client.runs.get(run_id)
                    run = Run.from_api_response(run_api_response)
                    if run.id == run_id:
                        self.runs[run_id] = run
                        self._logger.log_info(f"Run #{run_idx} created successfully with id: {run_id}")
                        break
                    else:
                        self._logger.log_error(f"Error creating run #{run_idx}: run id not expected")
                else:
                    self._logger.log_error(f"Error creating run #{run_idx}: no run id returned")
            except Exception as e:
                self._logger.log_error(f"Error creating run #{run_idx}: {str(e)}")
                num_retries += 1
                if num_retries >= max_retries:
                    raise e

        if run_id:
            run_id = str(run_id)
            run = self._monitor_run(run_idx, run_id, poll_interval=1)
            if run:
                self._logger.log_info(
                    f"Run #{run_idx} id {run_id} "
                    f"ended with status: {run.status} {f'({run.finished_status})' if run.finished_status else ''}"
                )
                self.runs[run_id] = run

            if self._fetch_run_logs:
                self.logs[run_id] = self._internal_api_client.logs.dump(run_id)

        return run

    def _monitor_run(self, run_idx: int, run_id: str, poll_interval: int = 1, max_retries: int = 3) -> Optional[Run]:
        """Monitor a run until it finishes or times out."""
        run: Optional[Run] = None

        run_status = ""
        num_retries = 0
        while True:
            # Get run status
            try:
                run_api_response = self._internal_api_client.runs.get(run_id)
                run = Run.from_api_response(run_api_response)

                if run_status != run.status:
                    # only log the run if the status has changed
                    run_status = run.status
                    self._logger.log_info(
                        f"Run #{run_idx} id: {run_id}"
                        f"status: {run_status} (elapsed: "
                        f"{'0' if not run.total_time else f'{run.total_time / 1000:.1f}s'})"
                    )
                    self.runs[run_id] = run

                # If the run is finished, break out of the loop
                if run_status == "finished":
                    break
                elif run_status == "failed" or run_status == "error":
                    self._logger.log_error(f"Run #{run_idx} id: {run_id} errored or failed!")
                    self._logger.log_error(json.dumps(run, indent=4))
                    break
            except Exception as e:
                self._logger.log_error(f"Error monitoring run #{run_idx} id: {run_id}: {str(e)}")
                num_retries += 1
                if num_retries > max_retries:
                    self._logger.log_error(f"Run #{run_idx} id: {run_id} failed after max retries ({max_retries})")
                    break

            # Wait before polling again
            time.sleep(poll_interval)
        return run

    def fetch_run_logs(self) -> dict[str, list[dict[str, Any]]]:
        """Dumps all logs for all runs."""
        for run_id in self.runs.keys():
            self.logs[run_id] = self._internal_api_client.logs.dump(run_id)
        return self.logs
