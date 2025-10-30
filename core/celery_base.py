"""
Base Celery task classes with built-in retry logic and error handling
"""
from celery import Task
from celery.utils.log import get_task_logger
from django.core.cache import cache
import time

logger = get_task_logger(__name__)


class BaseTask(Task):
    """Base task with automatic retry and error handling"""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log task failure"""
        logger.error(f'Task {self.name}[{task_id}] failed: {exc}')
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log task retry"""
        logger.warning(f'Task {self.name}[{task_id}] retrying: {exc}')
        super().on_retry(exc, task_id, args, kwargs, einfo)
    
    def on_success(self, retval, task_id, args, kwargs):
        """Log task success"""
        logger.info(f'Task {self.name}[{task_id}] succeeded')
        super().on_success(retval, task_id, args, kwargs)


class IdempotentTask(BaseTask):
    """Task that prevents duplicate execution using cache lock"""
    
    def apply_async(self, args=None, kwargs=None, task_id=None, **options):
        """Check for duplicate task before execution"""
        lock_key = f'task_lock:{self.name}:{args}:{kwargs}'
        
        if cache.get(lock_key):
            logger.info(f'Task {self.name} already running, skipping')
            return None
        
        # Set lock for task duration (default 1 hour)
        cache.set(lock_key, True, timeout=3600)
        
        try:
            return super().apply_async(args, kwargs, task_id, **options)
        except Exception as e:
            cache.delete(lock_key)
            raise e


class RateLimitedTask(BaseTask):
    """Task with rate limiting"""
    
    rate_limit = '10/m'  # 10 tasks per minute
    
    def apply_async(self, args=None, kwargs=None, **options):
        """Apply rate limiting before execution"""
        rate_key = f'rate_limit:{self.name}'
        current_count = cache.get(rate_key, 0)
        
        if current_count >= 10:
            logger.warning(f'Rate limit exceeded for {self.name}')
            time.sleep(6)  # Wait 6 seconds
        
        cache.set(rate_key, current_count + 1, timeout=60)
        return super().apply_async(args, kwargs, **options)
