"""
Cleanup Scheduler
Runs periodic cleanup of old generations based on retention policies
"""

import threading
import time
from datetime import datetime
import generation_history as gh


class CleanupScheduler:
    """Background scheduler for cleaning up old generations"""

    def __init__(self, interval_hours=3, image_retention_days=7, video_retention_days=2):
        """
        Initialize cleanup scheduler

        Args:
            interval_hours: Hours between cleanup runs (default: 3)
            image_retention_days: Days to keep image generations (default: 7)
            video_retention_days: Days to keep video generations (default: 2)
        """
        self.interval = interval_hours * 60 * 60  # Convert to seconds
        self.image_retention_days = image_retention_days
        self.video_retention_days = video_retention_days
        self.running = False
        self.thread = None
        self.last_cleanup = None
        self.stats = {
            'total_runs': 0,
            'total_deleted': 0,
            'total_files_deleted': 0,
            'total_errors': 0
        }

    def run_cleanup(self):
        """Execute a cleanup cycle"""
        print(f"\n{'='*60}")
        print(f"[Cleanup Scheduler] Starting cleanup cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        try:
            # Run cleanup
            cycle_stats = gh.cleanup_old_generations(
                image_retention_days=self.image_retention_days,
                video_retention_days=self.video_retention_days,
                delete_files=True
            )

            # Update stats
            self.stats['total_runs'] += 1
            self.stats['total_deleted'] += cycle_stats['deleted_count']
            self.stats['total_files_deleted'] += cycle_stats['files_deleted']
            self.stats['total_errors'] += cycle_stats['errors']
            self.last_cleanup = datetime.now()

            print(f"[Cleanup Scheduler] Cleanup complete:")
            print(f"  - Database records deleted: {cycle_stats['deleted_count']}")
            print(f"  - Files deleted: {cycle_stats['files_deleted']}")
            print(f"  - Errors: {cycle_stats['errors']}")
            print(f"{'='*60}\n")

            return cycle_stats

        except Exception as e:
            print(f"[Cleanup Scheduler] Error during cleanup: {str(e)}")
            import traceback
            traceback.print_exc()
            self.stats['total_errors'] += 1
            return {'error': str(e)}

    def scheduler_loop(self):
        """Main loop that runs cleanup periodically"""
        print(f"[Cleanup Scheduler] Starting scheduler loop")
        print(f"  - Cleanup interval: {self.interval / 3600} hours")
        print(f"  - Image retention: {self.image_retention_days} days")
        print(f"  - Video retention: {self.video_retention_days} days")

        # Run cleanup immediately on start
        self.run_cleanup()

        # Then run on schedule
        while self.running:
            try:
                # Calculate next run time
                next_run = datetime.now().timestamp() + self.interval
                next_run_time = datetime.fromtimestamp(next_run).strftime('%Y-%m-%d %H:%M:%S')

                print(f"[Cleanup Scheduler] Next cleanup scheduled for {next_run_time}")

                # Sleep until next run
                time.sleep(self.interval)

                # Run cleanup if still running
                if self.running:
                    self.run_cleanup()

            except Exception as e:
                print(f"[Cleanup Scheduler] Error in scheduler loop: {str(e)}")
                import traceback
                traceback.print_exc()
                time.sleep(60)  # Wait a minute before retrying

    def start(self):
        """Start the cleanup scheduler"""
        if self.running:
            print("[Cleanup Scheduler] Scheduler is already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self.scheduler_loop, daemon=True, name="CleanupScheduler")
        self.thread.start()

        print(f"[Cleanup Scheduler] ✓ Scheduler started successfully")

    def stop(self):
        """Stop the cleanup scheduler"""
        if not self.running:
            print("[Cleanup Scheduler] Scheduler is not running")
            return

        print("[Cleanup Scheduler] Stopping scheduler...")
        self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)

        print("[Cleanup Scheduler] ✓ Scheduler stopped")

    def get_status(self):
        """Get scheduler status and statistics"""
        return {
            'running': self.running,
            'interval_hours': self.interval / 3600,
            'image_retention_days': self.image_retention_days,
            'video_retention_days': self.video_retention_days,
            'last_cleanup': self.last_cleanup.isoformat() if self.last_cleanup else None,
            'stats': self.stats
        }


# Global scheduler instance
_scheduler = None


def init_scheduler(interval_hours=3, image_retention_days=7, video_retention_days=2):
    """
    Initialize and start the global cleanup scheduler

    Args:
        interval_hours: Hours between cleanup runs
        image_retention_days: Days to keep image generations
        video_retention_days: Days to keep video generations

    Returns:
        CleanupScheduler instance
    """
    global _scheduler

    if _scheduler is not None:
        print("[Cleanup Scheduler] Scheduler already initialized")
        return _scheduler

    _scheduler = CleanupScheduler(
        interval_hours=interval_hours,
        image_retention_days=image_retention_days,
        video_retention_days=video_retention_days
    )

    _scheduler.start()
    return _scheduler


def get_scheduler():
    """Get the global scheduler instance"""
    return _scheduler


def stop_scheduler():
    """Stop the global scheduler"""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None


if __name__ == '__main__':
    # Test the scheduler
    print("Testing Cleanup Scheduler...")
    print("This will run a cleanup every 30 seconds for testing purposes")
    print("Press Ctrl+C to stop\n")

    scheduler = CleanupScheduler(
        interval_hours=30 / 3600,  # 30 seconds for testing
        image_retention_days=7,
        video_retention_days=2
    )

    scheduler.start()

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        scheduler.stop()
        print("Scheduler stopped. Goodbye!")
