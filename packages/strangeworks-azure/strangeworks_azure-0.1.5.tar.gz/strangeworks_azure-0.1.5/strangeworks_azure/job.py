from __future__ import annotations

import json
import time
from functools import singledispatch
from typing import Any, Dict, Optional, Tuple, Union

import strangeworks as sw
from qiskit import QuantumCircuit
from qiskit.compiler import assemble
from qiskit.providers import JobV1 as Job
from strangeworks_core.errors.error import StrangeworksError
from strangeworks_core.types.job import Job as StrangeworksJob
from strangeworks_core.types.job import Status


class StrangeworksQuantumJob:
    _product_slug = "azure-quantum"

    def __init__(self, job: StrangeworksJob, *args, **kwargs):
        self.job: StrangeworksJob = job

    @property
    def id(self) -> str:
        """The id of the task.

        Returns
        -------
        id: str
            The id of the task. This is the id of the job in Strangeworks.
        """
        return self.job.slug

    def cancel(self) -> None:
        """Cancel the task.

        Raises
        ------
        StrangeworksError
            If the task has not been submitted yet.

        """
        if not self.job.external_identifier:
            raise StrangeworksError(
                "Job has not been submitted yet. Missing external_identifier."  # noqa: E501
            )

        resource = sw.get_resource_for_product(StrangeworksQuantumJob._product_slug)
        cancel_url = f"{resource.proxy_url()}/jobs/{self.job.external_identifier}"
        # todo: strangeworks-python is rest_client an optional thing. i dont think it should be # noqa: E501
        # this is something we should discuss
        sw.client.rest_client.delete(url=cancel_url)

    def status(self) -> str:
        """Get the state of the task.

        Returns
        -------
        state: str
            The state of the task.

        Raises
        ------
        StrangeworksError
            If the task has not been submitted yet.
            Or if we find are not able to find the status.
        """
        if not self.job.external_identifier:
            raise StrangeworksError(
                "Job has not been submitted yet. Missing external_identifier."  # noqa: E501
            )

        res = sw.execute_get(
            StrangeworksQuantumJob._product_slug,
            endpoint=f"jobs/{self.job.external_identifier}",
        )
        if res.get("job_data") and isinstance(res.get("job_data"), str):
            res["job_data"] = json.loads(res.get("job_data"))
        self.job = StrangeworksQuantumJob._transform_dict_to_job(res)

        if not self.job.status:
            raise StrangeworksError("Job has no status")
        return self.job.status.value

    def result(self) -> Dict:
        """Get the result of the task.

        Returns
        -------
        result: Union[GateModelQuantumTaskResult, AnnealingQuantumTaskResult]
            The result of the task.

        Raises
        ------
        StrangeworksError
            If the task has not been submitted yet.
            Or if the task did not complete successfully.
            Or unable to fetch the results for the task.
        """
        if not self.job.external_identifier:
            raise StrangeworksError(
                "Job has not been submitted yet. Missing external_identifier."  # noqa: E501
            )
        while self.job.status not in {
            Status.COMPLETED,
            Status.FAILED,
            Status.CANCELLED,
        }:
            res = sw.execute_get(
                StrangeworksQuantumJob._product_slug,
                endpoint=f"jobs/{self.job.external_identifier}",
            )
            if res.get("job_data") and isinstance(res.get("job_data"), str):
                res["job_data"] = json.loads(res.get("job_data"))
            self.job = StrangeworksQuantumJob._transform_dict_to_job(res)
            time.sleep(2.5)

        if self.job.status != Status.COMPLETED:
            raise StrangeworksError("Job did not complete successfully")
        # sw.jobs will return type errors until it updates their type hints
        # todo: update strangeworks-python job type hints
        # todo: at this point in time, sw.jobs returns a different type than sw.execute
        jobs = sw.jobs(slug=self.job.slug)
        if not jobs:
            raise StrangeworksError("Job not found.")
        if len(jobs) != 1:
            raise StrangeworksError("Multiple jobs found.")
        job: Job = jobs[0]
        if not job.files:
            raise StrangeworksError("Job has no files.")
        # for now the strangeworks-python library still returns the Job.files as Files not JobFiles # noqa: E501
        files = list(
            filter(lambda f: f.file_name == "job_results_azure.json", job.files)
        )
        if len(files) != 1:
            raise StrangeworksError("Job has multiple files")

        file = files[0]
        if not file.url:
            raise StrangeworksError("Job file has no url")

        task_result = sw.download_job_files([file.url])
        if not task_result:
            raise StrangeworksError("Unable to download result file.")
        if len(task_result) != 1:
            raise StrangeworksError("Unable to download result file.")

        return task_result[0]

    @staticmethod
    def from_strangeworks_slug(id: str) -> StrangeworksQuantumJob:
        """Get a task from a strangeworks id.

        Parameters
        ----------
        id: str
            The strangeworks id of the task.

        Returns
        -------
        task: StrangeworksQuantumTask
            The task.

        Raises
        ------
        StrangeworksError
            If no task is found for the id.
            Or if multiple tasks are found for the id.
        """
        # todo: at this point in time, sw.jobs returns a different type than sw.execute
        jobs = sw.jobs(slug=id)
        if not jobs:
            raise StrangeworksError("No jobs found for slug")
        if len(jobs) != 1:
            raise StrangeworksError("Multiple jobs found for slug")
        job = jobs[0]
        return StrangeworksQuantumJob(job)

    @staticmethod
    def submit(
        device_name: str,
        task_specification: Union[QuantumCircuit, str],
        shots: int,
        backend_parameters: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        *args,
        **kwargs,
    ) -> StrangeworksQuantumJob:
        """Create a task.

        Parameters
        ----------
        device_arn: str
            The name of the device to run the task on.
        task_specification: Union[Circuit, Problem, OpenQasmProgram]
            The task specification.
        shots: int
            The number of shots to run the task for.
        device_parameters: Optional[Dict[str, Any]]
            The device parameters.
        tags: Optional[Dict[str, str]]
            The tags to add to the strangeworks job.

        Returns
        -------
        task: StrangeworksQuantumTask
            The task.

        Raises
        ------
        StrangeworksError
            If the task specification is not a circuit, or openqasm program.

        """
        circuit_type, circuit = _sw_task_specification(task_specification)
        jobs_req = {
            "circuit_type": circuit_type,
            "circuit": circuit,
            "backend": device_name,
            "backend_parameters": backend_parameters if backend_parameters else {},
            "shots": shots,
        }

        res = sw.execute_post(
            StrangeworksQuantumJob._product_slug,
            {"payload": jobs_req},
            endpoint="jobs",
        )
        if res.get("job_data") and isinstance(res.get("job_data"), str):
            res["job_data"] = json.loads(res.get("job_data"))
        sw_job = StrangeworksQuantumJob._transform_dict_to_job(res)
        # todo: can i use sw to create tags ?
        return StrangeworksQuantumJob(sw_job)

    # create a method that transforms the dict into a job
    # first it must convert the json keys from snake_case to camelCase
    # then it must create a job from the dict
    @staticmethod
    def _transform_dict_to_job(d: Dict[str, Any]) -> Job:
        # todo: this is unfortunate. dont like that we need to do this.
        def to_camel_case(snake_str):
            components = snake_str.split("_")
            # We capitalize the first letter of each component except the first one
            # with the 'title' method and join them together.
            return components[0] + "".join(x.title() for x in components[1:])

        remix = {to_camel_case(key): value for key, value in d.items()}
        return StrangeworksJob.from_dict(remix)


@singledispatch
def _sw_task_specification(
    task_specification: Union[QuantumCircuit, str]
) -> Tuple[str, str]:
    raise NotImplementedError


# register a function for each type
@_sw_task_specification.register
def _sw_task_specification_circuit(
    task_specification: QuantumCircuit,
) -> Tuple[str, str]:
    qobj = assemble(task_specification)
    qobj_dict = qobj.to_dict()
    return "Qobj", qobj_dict


@_sw_task_specification.register
def _sw_task_specification_openqasm(
    task_specification: str,
) -> Tuple[str, str]:
    return "Qasm", task_specification
