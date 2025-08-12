import logging
from behave.configuration import Configuration
from behave.model import Feature, Step
from behave.runner import ITestRunner, Runner as BehaveRunner
from behave.runner import Context
from behave.formatter._registry import make_formatters

from .pool import PoolExecutor
from .task import FeatureTaskAllocator, TaskAllocator
from .worker import ThreadWorker, WorkerPoolExecutor

log = logging.getLogger(__name__)


class WorkerRunner(BehaveRunner):
    """Runner subclass for executing features inside a worker
    (thread/process).

    Behaviour:
    - Initializes one `Context` per worker (created once in `start()`).
    - Loads hooks and step definitions once.
    - Exposes `run_feature()` to execute features dynamically, one by one.
    - `finish()` finalizes the run (after_all, cleanups, formatter close,
      reporter end).
    """

    _is_started: bool
    _is_failed: bool
    _index: int

    def __init__(self, config: Configuration, index: int):
        super().__init__(config)
        self._is_started = False
        self._is_failed = False
        self._index = index

    @property
    def index(self) -> int:
        return self._index

    def __str__(self):
        return f"{self.__class__.__name__}-{self.index}"

    def __repr__(self) -> str:
        return "self[%s]" % self.__str__()

    def start(self) -> None:
        """Prepare the worker runner once per worker.

        - Setup paths
        - Create `Context`
        - Load hooks and step definitions
        - Initialize formatters
        - Run `before_all`
        """
        if self._is_started:
            return
        # Setup import paths and base_dir similar to Behave's `run()`
        with self.path_manager:
            self.setup_paths()

        # Create fresh context for this worker and preload hooks/steps
        self.context = Context(self)
        self.load_hooks()
        self.load_step_definitions()

        # Initialize formatters once per worker
        stream_openers = self.config.outputs
        self.formatters = make_formatters(
            self.config,
            stream_openers,
        )

        # Run before_all hook once per worker
        self.hook_failures = 0
        self.run_hook("before_all")
        self._is_started = True

    def run_feature(self, feature: Feature) -> bool:
        """Run a single Feature with the worker's context.

        Returns True if the feature failed.
        """
        self.start()

        is_failed = False
        if not self.aborted:
            try:
                self.feature = feature
                for formatter in self.formatters:
                    if getattr(feature, "filename", None):
                        formatter.uri(feature.filename)
                is_failed = feature.run(self)
            except KeyboardInterrupt:
                self.abort(reason="KeyboardInterrupt")
                is_failed = True

        for reporter in self.config.reporters:
            reporter.feature(feature)

        self._is_failed |= is_failed
        return is_failed

    def finish(self) -> bool:
        """Finalize the worker run. Returns True if the worker-run failed."""
        if not self._is_started:
            return False
        cleanups_failed = False
        self.run_hook_with_capture("after_all")
        try:
            self.context._do_remaining_cleanups()
        except Exception:
            cleanups_failed = True

        if self.aborted:
            print("\nABORTED: By user.")
        for formatter in self.formatters:
            formatter.close()
        for reporter in self.config.reporters:
            reporter.end()

        self._is_failed |= (
            self.aborted
            or (self.hook_failures > 0)
            or (len(self.undefined_steps) > 0)
            or cleanups_failed
        )
        return self._is_failed

    @property
    def is_failed(self) -> bool:
        return self._is_failed


class WorkerRunnerPoolExecutor(PoolExecutor[WorkerRunner]):

    def __init__(self, config: Configuration):
        super().__init__(config, WorkerRunner)


class ParallelRunner(ITestRunner):

    config: Configuration
    task_allocator: TaskAllocator
    worker_pool_executor: WorkerPoolExecutor
    runner_pool_executor: WorkerRunnerPoolExecutor

    def __init__(
        self,
        config: Configuration,
        task_allocator: TaskAllocator,
        worker_pool_executor: WorkerPoolExecutor,
        runner_pool_executor: WorkerRunnerPoolExecutor,
    ):
        super().__init__(config)
        self.task_allocator = task_allocator
        self.worker_pool_executor = worker_pool_executor
        self.runner_pool_executor = runner_pool_executor

    def run(self) -> bool:
        while not (self.task_allocator.empty() and self.worker_pool_executor.done()):
            if not self.task_allocator.empty():
                for index, worker in enumerate(self.worker_pool_executor):
                    if worker.done():
                        runner = self.runner_pool_executor[index]
                        runner.start()
                        feature = self.task_allocator.allocate(index)
                        worker.do(runner.run_feature, feature)
        for runner in self.runner_pool_executor:
            runner.finish()
        return any(runner.is_failed for runner in self.runner_pool_executor)

    @property
    def undefined_steps(self) -> list[Step]:
        return [
            step
            for runner in self.runner_pool_executor
            for step in runner.undefined_steps
        ]


class FeatureParallelRunner(ParallelRunner):

    def __init__(self, config: Configuration):
        super().__init__(
            config=config,
            task_allocator=FeatureTaskAllocator(config),
            worker_pool_executor=WorkerPoolExecutor(config, ThreadWorker),
            runner_pool_executor=WorkerRunnerPoolExecutor(config),
        )


ITestRunner.register(FeatureParallelRunner)
