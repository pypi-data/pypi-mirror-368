"""provider.py."""
from typing import Dict, Optional, Union

import strangeworks as sw
from qiskit.providers.models.backendproperties import BackendProperties

from strangeworks_azure.job import StrangeworksQuantumJob


class StrangeworksBackend:
    """The Strangeworks Provider allows access to Strangeworks backends
    for the Microsoft Azure services"""

    def __init__(
        self,
        name: str,
        status: Optional[str] = None,
        slug: Optional[str] = None,
        **kwargs,
    ):
        self.name = name
        self.slug = slug

        self.status = status

    def run(
        self,
        task_specification: Union[Dict, str],
        shots: Optional[int],
        *args,
        **kwargs,
    ) -> StrangeworksQuantumJob:
        """Run a task on the device.
        Parameters
        ----------
        task_specification: Union[QuantumCircuit, str]
            The task specification.
        shots: Optional[int]
            The number of shots to run the task for. Defaults to 1000.
        Returns
        -------
        task: Job (StrangeworksQuantumJob)
            The task that was run.
        """
        return StrangeworksQuantumJob.submit(
            self.name, task_specification, shots or 1000, *args, **kwargs
        )

    @staticmethod
    def get_backends(
        arns: Optional[list[str]] = None,
        names: Optional[list[str]] = None,
        statuses: Optional[list[str]] = None,
    ):  # -> list[StrangeworksBackend]:
        """Get a list of devices.
        Parameters
        ----------
        arns: Optional[list[str]
            Filter by list of device ARNs. Defaults to None.
        names: Optional[list[str]]
            Filter by list of device names. Defaults to None.
        statuses: Optional[list[str]]
            Filter by list of device statuses. Defaults to None.
        Returns
        -------
        devices: list[SwDevice]
            List of devices that match the provided filters.
        """
        backends = sw.backends(product_slugs=["azure-quantum"])
        devices = []
        for backend in backends:
            if arns and backend.remote_backend_id not in arns:
                continue
            if names and backend.name not in names:
                continue
            if statuses and backend.remote_status not in statuses:
                continue

            devices.append(
                StrangeworksBackend(
                    backend.name,
                    backend.remote_status,
                    backend.slug,
                )
            )

        return devices

    def properties(self):
        """Return properties of backend."""
        return (
            BackendProperties.from_dict(self.sw_properties)
            if self.sw_properties
            else None
        )
