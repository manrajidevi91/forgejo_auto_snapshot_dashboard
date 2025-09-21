from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from utils.logger import app_logger as logger
import atexit

class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler(daemon=True)

    def start(self):
        """Starts the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started.")
            # Ensure the scheduler shuts down when the app exits
            atexit.register(self.shutdown)

    def shutdown(self):
        """Shuts down the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shut down.")

    def schedule_snapshot(self, project_id, func, interval_seconds):
        """
        Schedules a snapshot job for a project.
        Removes any existing job for the project before creating a new one.
        """
        job_id = f"snapshot_{project_id}"
        self.remove_job(job_id)  # Ensure no duplicate jobs exist
        
        self.scheduler.add_job(
            func,
            'interval',
            seconds=interval_seconds,
            id=job_id,
            args=[project_id],
            replace_existing=True
        )
        logger.info(f"Scheduled snapshot job for project {project_id} every {interval_seconds} seconds.")

    def pause_snapshot(self, project_id):
        """Pauses a scheduled snapshot job."""
        job_id = f"snapshot_{project_id}"
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Paused job for project {project_id}.")
        except JobLookupError:
            logger.warning(f"Could not find job {job_id} to pause.")

    def resume_snapshot(self, project_id):
        """Resumes a paused snapshot job."""
        job_id = f"snapshot_{project_id}"
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Resumed job for project {project_id}.")
        except JobLookupError:
            logger.warning(f"Could not find job {job_id} to resume.")

    def remove_job(self, job_id):
        """Removes a job from the scheduler."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job {job_id} from scheduler.")
        except JobLookupError:
            # This is not an error, it just means the job wasn't scheduled
            pass

# Singleton instance
scheduler_service = SchedulerService()