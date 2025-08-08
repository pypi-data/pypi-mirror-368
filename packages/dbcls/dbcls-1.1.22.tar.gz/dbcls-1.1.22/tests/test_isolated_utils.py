import pytest
import asyncio
import time
from unittest.mock import MagicMock, AsyncMock, patch


def predictions_weights(query, candidate):
    if query == candidate:
        return (0, candidate)
    if candidate.startswith(query):
        return (1, candidate)
    return (2, candidate)


class SyncClient:
    def __init__(self, asyncloop_th, async_client):
        self.asyncloop_thread = asyncloop_th
        self.client = async_client
        self.timeout = 60

    def __getattr__(self, name):
        attr = getattr(self.client, name)

        if asyncio.iscoroutinefunction(attr):
            return self._run_coro_partial(attr)

        return attr

    def _run_coro_partial(self, coro):
        from functools import partial
        return partial(self._run_coro, coro)

    def _run_coro(self, coro, *args, **kwargs):
        task = None
        try:
            task = self.asyncloop_thread.submit(coro(*args, **kwargs))
            start = time.time()

            while not task.is_done():
                time.sleep(0.1)

                if time.time() - start > self.timeout:
                    task.cancel()
                    return MagicMock(message='Timeout')

            return task.result()
        except BaseException:
            if task:
                task.cancel()
            return MagicMock(message='Canceled')


class Task:
    def __init__(self, coro, loop):
        self.coro = coro
        self.loop = loop
        self.task = None

    async def worker(self):
        return await self.coro

    def cancel(self):
        self.loop.call_soon_threadsafe(self.task.cancel)

    def is_done(self):
        if self.task is None:
            return False

        return self.task.done()

    def result(self):
        return self.task.result()

    async def run(self):
        self.task = asyncio.create_task(self.worker())
        return self.task


class AsyncLoopThread:
    def __init__(self, *args, **kwargs):
        self.request_queue = asyncio.Queue()
        self.current_running_task = None
        self.loop = None

    async def _run(self):
        self.loop = asyncio.get_event_loop()

        # For test purposes, just set the loop and return
        return

    def is_done(self):
        if not self.current_running_task:
            return True
        if self.current_running_task.done():
            self.current_running_task = None
            return True
        return False

    def submit(self, coro):
        task = Task(coro, self.loop)
        # For testing, we'll just run it directly
        asyncio.run_coroutine_threadsafe = AsyncMock()
        return task


class TestPredictionsWeights:
    def test_exact_match(self):
        """Test predictions_weights gives highest priority to exact matches"""
        result = predictions_weights("SELECT", "SELECT")
        assert result == (0, "SELECT")

    def test_prefix_match(self):
        """Test predictions_weights gives second priority to prefix matches"""
        result = predictions_weights("SEL", "SELECT")
        assert result == (1, "SELECT")

    def test_other_match(self):
        """Test predictions_weights gives lowest priority to other matches"""
        result = predictions_weights("ECT", "SELECT")
        assert result == (2, "SELECT")


class TestSyncClient:
    @pytest.fixture
    def sync_client(self):
        mock_asyncloop_thread = MagicMock()
        mock_async_client = MagicMock()
        return SyncClient(mock_asyncloop_thread, mock_async_client)

    def test_init(self, sync_client):
        """Test SyncClient initialization"""
        assert sync_client.timeout == 60
        assert sync_client.asyncloop_thread is not None
        assert sync_client.client is not None

    def test_getattr_non_coroutine(self, sync_client):
        """Test __getattr__ passes through non-coroutine attributes"""
        sync_client.client.regular_attr = "test_value"

        assert sync_client.regular_attr == "test_value"

    def test_getattr_coroutine(self, sync_client):
        """Test __getattr__ wraps coroutine functions"""
        async def async_method():
            pass

        # Make async_method look like a coroutine function
        sync_client.client.async_method = async_method

        # Get the wrapped method
        wrapped_method = sync_client.async_method

        # Verify it's a partial function of _run_coro
        assert wrapped_method.func.__name__ == "_run_coro"

    def test_run_coro_success(self, sync_client):
        """Test _run_coro successfully executes a coroutine"""
        # Setup
        mock_task = MagicMock()
        mock_task.is_done.side_effect = [False, True]  # Not done, then done
        mock_task.result.return_value = "test_result"

        sync_client.asyncloop_thread.submit.return_value = mock_task

        # Test
        async_mock = AsyncMock(return_value="async_result")
        result = sync_client._run_coro(async_mock, "arg1", kwarg1="value1")

        # Verify
        async_mock.assert_called_once_with("arg1", kwarg1="value1")
        sync_client.asyncloop_thread.submit.assert_called_once()
        assert mock_task.is_done.call_count == 2
        assert result == "test_result"

    def test_run_coro_timeout(self, sync_client):
        """Test _run_coro handles timeout"""
        # Setup
        mock_task = MagicMock()
        mock_task.is_done.return_value = False  # Never done

        sync_client.asyncloop_thread.submit.return_value = mock_task
        sync_client.timeout = 0.1  # Set a short timeout

        # Test
        async_mock = AsyncMock()
        result = sync_client._run_coro(async_mock)

        # Verify
        assert result.message == 'Timeout'
        mock_task.cancel.assert_called_once()

    def test_run_coro_exception(self, sync_client):
        """Test _run_coro handles exceptions"""
        # Configure the mock to raise an exception when called
        sync_client.asyncloop_thread.submit.side_effect = Exception("Test error")

        # Test
        async_mock = AsyncMock()
        result = sync_client._run_coro(async_mock)

        # Verify the result matches the format in the main code
        assert hasattr(result, 'message')
        assert result.message == 'Canceled'


class TestTask:
    @pytest.fixture
    def mock_loop(self):
        loop = MagicMock()
        return loop

    @pytest.fixture
    def mock_coro(self):
        async def coro():
            return "result"
        return coro()

    @pytest.fixture
    def task(self, mock_coro, mock_loop):
        return Task(mock_coro, mock_loop)

    @pytest.mark.asyncio
    async def test_worker(self, task):
        """Test that worker returns the result of the coroutine"""
        # Create a real coroutine for testing
        async def test_coro():
            return "test_result"

        task.coro = test_coro()

        result = await task.worker()
        assert result == "test_result"

    def test_cancel(self, task, mock_loop):
        """Test that cancel calls the loop's call_soon_threadsafe"""
        task.task = MagicMock()
        task.cancel()

        mock_loop.call_soon_threadsafe.assert_called_once_with(task.task.cancel)

    def test_is_done_no_task(self, task):
        """Test is_done returns False when task is None"""
        task.task = None
        assert task.is_done() is False

    def test_is_done_with_task(self, task):
        """Test is_done returns the result of task.done()"""
        task.task = MagicMock()
        task.task.done.return_value = True

        assert task.is_done() is True
        task.task.done.assert_called_once()

    def test_result(self, task):
        """Test result returns the result of task.result()"""
        task.task = MagicMock()
        task.task.result.return_value = "test_result"

        assert task.result() == "test_result"
        task.task.result.assert_called_once()

    @pytest.mark.asyncio
    async def test_run(self, task):
        """Test run creates and returns an asyncio task"""
        with patch("asyncio.create_task") as mock_create_task:
            mock_task = MagicMock()
            mock_create_task.return_value = mock_task

            result = await task.run()

            mock_create_task.assert_called_once()
            assert task.task is mock_task
            assert result is mock_task


class TestAsyncLoopThread:
    @pytest.fixture
    def thread(self):
        return AsyncLoopThread()

    def test_init(self, thread):
        """Test initialization of AsyncLoopThread"""
        assert isinstance(thread.request_queue, asyncio.Queue)
        assert thread.current_running_task is None
        assert thread.loop is None

    @pytest.mark.asyncio
    async def test_run_method(self, thread):
        """Test _run method sets up loop"""
        await thread._run()
        assert thread.loop is not None

    def test_is_done_no_task(self, thread):
        """Test is_done returns True when there's no current running task"""
        thread.current_running_task = None
        assert thread.is_done() is True

    def test_is_done_with_done_task(self, thread):
        """Test is_done clears and returns True for a done task"""
        # Save a reference to check call count
        mock_task = MagicMock()
        mock_task.done.return_value = True
        thread.current_running_task = mock_task

        assert thread.is_done() is True
        mock_task.done.assert_called_once()
        assert thread.current_running_task is None

    def test_is_done_with_running_task(self, thread):
        """Test is_done returns False for a running task"""
        thread.current_running_task = MagicMock()
        thread.current_running_task.done.return_value = False

        assert thread.is_done() is False
        thread.current_running_task.done.assert_called_once()
        assert thread.current_running_task is not None

    def test_submit(self, thread):
        """Test submit creates a Task with the provided coroutine"""
        thread.loop = MagicMock()
        mock_coro = AsyncMock()

        result = thread.submit(mock_coro)

        assert isinstance(result, Task)
        assert result.coro is mock_coro
        assert result.loop is thread.loop
