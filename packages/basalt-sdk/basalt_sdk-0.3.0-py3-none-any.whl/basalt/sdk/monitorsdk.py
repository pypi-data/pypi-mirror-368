from typing import Dict, Optional, Any, Tuple
import asyncio

from ..utils.protocols import IApi, ILogger
from ..ressources.monitor.trace_types import TraceParams
from ..ressources.monitor.experiment_types import ExperimentParams
from ..ressources.monitor.generation_types import GenerationParams
from ..ressources.monitor.log_types import LogParams
from ..objects.trace import Trace
from ..objects.generation import Generation
from ..objects.log import Log
from ..objects.experiment import Experiment
from ..utils.flusher import Flusher
from ..endpoints.monitor.create_experiment import CreateExperimentEndpoint, CreateExperimentDTO

class MonitorSDK:
    """
    SDK for monitoring and tracing in Basalt.
    """
    def __init__(
            self,
            api: IApi,
            logger: ILogger
        ):
        self._api = api
        self._logger = logger

    def create_experiment(
        self,
        feature_slug: str,
        params: ExperimentParams
    ) -> Tuple[Optional[Exception], Optional[Experiment]]:
        """
        Creates a new experiment for monitoring.

        Args:
            feature_slug (str): The feature slug for the experiment.
            params (Dict[str, Any]): Parameters for the experiment.

        Returns:
            Experiment: A new Experiment instance.
        """
        return self._create_experiment(feature_slug, params)
        
    async def async_create_experiment(
        self,
        feature_slug: str,
        params: ExperimentParams
    ) -> Tuple[Optional[Exception], Optional[Experiment]]:
        """
        Asynchronously creates a new experiment for monitoring.

        Args:
            feature_slug (str): The feature slug for the experiment.
            params (Dict[str, Any]): Parameters for the experiment.

        Returns:
            Experiment: A new Experiment instance.
        """
        return await self._async_create_experiment(feature_slug, params)


    def create_trace(
        self,
        slug: str,
        params: Optional[TraceParams] = None
    ) -> Trace:
        """
        Creates a new trace for monitoring.

        Args:
            slug (str): The unique identifier for the trace.
            params (TraceParams): Parameters for the trace.

        Returns:
            Trace: A new Trace instance.
        """
        if params is None:
            params = {}

        trace_params = TraceParams(**params)

        return self._create_trace(slug, trace_params)
        
    async def async_create_trace(
        self,
        slug: str,
        params: Optional[TraceParams] = None
    ) -> Trace:
        """
        Asynchronously creates a new trace for monitoring.

        Args:
            slug (str): The unique identifier for the trace.
            params (TraceParams): Parameters for the trace.

        Returns:
            Trace: A new Trace instance.
        """
        if params is None:
            params = {}

        trace_params = TraceParams(**params)

        return await self._async_create_trace(slug, trace_params)

    def create_generation(
        self,
        params: Dict[str, Any]
    ) -> Generation:
        """
        Creates a new generation for monitoring.

        Args:
            params (Dict[str, Any]): Parameters for the generation.

        Returns:
            Generation: A new Generation instance.
        """
        generation_params = GenerationParams(**params)
        return self._create_generation(generation_params)
        
    async def async_create_generation(
        self,
        params: Dict[str, Any]
    ) -> Generation:
        """
        Asynchronously creates a new generation for monitoring.

        Args:
            params (Dict[str, Any]): Parameters for the generation.

        Returns:
            Generation: A new Generation instance.
        """
        generation_params = GenerationParams(**params)
        return await self._async_create_generation(generation_params)

    def create_log(
        self,
        params: Dict[str, Any]
    ) -> Log:
        """
        Creates a new log for monitoring.

        Args:
            params (Dict[str, Any]): Parameters for the log.

        Returns:
            Log: A new Log instance.
        """
        log_params = LogParams(**params)
        return self._create_log(log_params)
        
    async def async_create_log(
        self,
        params: Dict[str, Any]
    ) -> Log:
        """
        Asynchronously creates a new log for monitoring.

        Args:
            params (Dict[str, Any]): Parameters for the log.

        Returns:
            Log: A new Log instance.
        """
        log_params = LogParams(**params)
        return await self._async_create_log(log_params)

    def _create_experiment(
        self,
        feature_slug: str,
        params: ExperimentParams
    ) -> Tuple[Optional[Exception], Optional[Experiment]]:
        """
        Internal implementation for creating an experiment.

        Args:
            feature_slug (str): The feature slug for the experiment.
            params (ExperimentParams): Parameters for the experiment.

        Returns:
            Experiment: A new Experiment instance.
        """
        dto = CreateExperimentDTO(
            feature_slug=feature_slug,
            name=params.get("name"),
        )

        # Call the API endpoint
        err, result = self._api.invoke(CreateExperimentEndpoint, dto)

        if err is None:
            return None, Experiment(result.experiment)

        return err, None
        
    async def _async_create_experiment(
        self,
        feature_slug: str,
        params: ExperimentParams
    ) -> Tuple[Optional[Exception], Optional[Experiment]]:
        """
        Internal implementation for asynchronously creating an experiment.

        Args:
            feature_slug (str): The feature slug for the experiment.
            params (ExperimentParams): Parameters for the experiment.

        Returns:
            Experiment: A new Experiment instance.
        """
        dto = CreateExperimentDTO(
            feature_slug=feature_slug,
            name=params.get("name"),
        )

        # Call the API endpoint
        err, result = await self._api.async_invoke(CreateExperimentEndpoint, dto)

        if err is None:
            return None, Experiment(result.experiment)

        return err, None


    def _create_trace(
        self,
        slug: str,
        params: TraceParams
    ) -> Trace:
        """
        Internal implementation for creating a trace.

        Args:
            slug (str): The unique identifier for the trace.
            params (TraceParams): Parameters for the trace.

        Returns:
            Trace: A new Trace instance.
        """
        flusher = Flusher(self._api, self._logger)
        # Convert TraceParams to a dictionary before passing to Trace
        params_dict = {
            "input": params.input,
            "output": params.output,
            "name": params.name,
						"ideal_output": params.ideal_output,
            "start_time": params.start_time,
            "end_time": params.end_time,
            "user": params.user,
            "organization": params.organization,
            "metadata": params.metadata,
            "experiment": params.experiment,
            "evaluators": params.evaluators,
            "evaluationConfig": params.evaluation_config
        }
        trace = Trace(slug, params_dict, flusher, self._logger)
        return trace
        
    async def _async_create_trace(
        self,
        slug: str,
        params: TraceParams
    ) -> Trace:
        """
        Internal implementation for asynchronously creating a trace.

        Args:
            slug (str): The unique identifier for the trace.
            params (TraceParams): Parameters for the trace.

        Returns:
            Trace: A new Trace instance.
        """
        flusher = Flusher(self._api, self._logger)
        # Convert TraceParams to a dictionary before passing to Trace
        params_dict = {
            "input": params.input,
            "output": params.output,
            "name": params.name,
            "start_time": params.start_time,
            "end_time": params.end_time,
            "user": params.user,
            "organization": params.organization,
            "metadata": params.metadata,
            "experiment": params.experiment,
            "evaluators": params.evaluators,
            "evaluationConfig": params.evaluation_config
        }
        trace = Trace(slug, params_dict, flusher, self._logger)
        return trace

    def _create_generation(
        self,
        params: GenerationParams
    ) -> Generation:
        """
        Internal implementation for creating a generation.

        Args:
            params (GenerationParams): Parameters for the generation.

        Returns:
            Generation: A new Generation instance.
        """
        # Convert GenerationParams to a dictionary before passing to Generation
        params_dict = {
            "name": params.name,
            "trace": params.trace,
            "prompt": params.prompt,
            "input": params.input,
            "output": params.output,
            "variables": params.variables,
            "parent": params.parent,
            "metadata": params.metadata,
            "start_time": params.start_time,
            "end_time": params.end_time,
            "options": params.options
        }
        return Generation(params_dict)
        
    async def _async_create_generation(
        self,
        params: GenerationParams
    ) -> Generation:
        """
        Internal implementation for asynchronously creating a generation.

        Args:
            params (GenerationParams): Parameters for the generation.

        Returns:
            Generation: A new Generation instance.
        """
        # Convert GenerationParams to a dictionary before passing to Generation
        params_dict = {
            "name": params.name,
            "trace": params.trace,
            "prompt": params.prompt,
            "input": params.input,
            "output": params.output,
            "variables": params.variables,
            "parent": params.parent,
            "metadata": params.metadata,
            "start_time": params.start_time,
            "end_time": params.end_time,
            "options": params.options
        }
        return Generation(params_dict)

    def _create_log(
        self,
        params: LogParams
    ) -> Log:
        """
        Internal implementation for creating a log.

        Args:
            params (LogParams): Parameters for the log.

        Returns:
            Log: A new Log instance.
        """
        # Convert LogParams to a dictionary before passing to Log
        params_dict = {
            "name": params.name,
            "trace": params.trace,
            "input": params.input,
            "output": params.output,
            "parent": params.parent,
            "metadata": params.metadata,
            "start_time": params.start_time,
            "end_time": params.end_time
        }
        return Log(params_dict)
        
    async def _async_create_log(
        self,
        params: LogParams
    ) -> Log:
        """
        Internal implementation for asynchronously creating a log.

        Args:
            params (LogParams): Parameters for the log.

        Returns:
            Log: A new Log instance.
        """
        # Convert LogParams to a dictionary before passing to Log
        params_dict = {
            "name": params.name,
            "trace": params.trace,
            "input": params.input,
            "output": params.output,
            "parent": params.parent,
            "metadata": params.metadata,
            "start_time": params.start_time,
            "end_time": params.end_time
        }
        return Log(params_dict)