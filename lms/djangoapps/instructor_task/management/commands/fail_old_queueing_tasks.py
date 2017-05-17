from __future__ import unicode_literals, print_function

from datetime import timedelta

from celery.states import FAILURE
from django.core.management.base import BaseCommand
from django.utils import timezone

from lms.djangoapps.instructor_task.models import InstructorTask, QUEUING


class Command(BaseCommand):
    """
    Command to manually fail old "QUEUING" tasks in the instructor task table.

    Example:
    ./manage.py lms fail_old_queueing_tasks --dry-run --days_previous 2 --task_type bulk_course_email
    """

    def add_arguments(self, parser):
        """
        Add arguments to the command parser.
        """
        parser.add_argument(
            '--days-previous',
            type=int,
            dest='days_previous',
            default=2,
            help='Manually fail instructor tasks created before or on these many days ago.',
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Return the records this command will update without updating them.',
        )

        parser.add_argument(
            '--task_type',
            dest='task_type',
            type=str,
            default=None,
            help='Specify the type of task that you want to fail.',
        )

    def handle(self, *args, **options):

        days_previous = options['days_previous']
        cutoff = timezone.now() - timedelta(days=days_previous)
        filter_kwargs = {
            "task_state": QUEUING,
            "created__lte": cutoff
        }
        if options['task_type'] is not None:
            filter_kwargs.update({"task_type": options['task_type']})

        tasks = InstructorTask.objects.filter(**filter_kwargs)

        for task in tasks:
            print(
                "Queueing task '{task_id}', of type '{task_type}', created on '{created}', will be marked as 'FAILURE'".format(
                    task_id=task.task_id,
                    task_type=task.task_type,
                    created=task.created,
                )
            )

        if not options['dry_run']:
            tasks_updated = tasks.update(
                task_state=FAILURE,
            )
            print("{tasks_updated} records updated.".format(
                tasks_updated=tasks_updated)
            )
        else:
            print("This was a dry run, so no records were updated.")
