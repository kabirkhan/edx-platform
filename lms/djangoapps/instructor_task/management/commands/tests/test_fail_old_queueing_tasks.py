from datetime import timedelta, datetime

import ddt
import mock
from celery.states import FAILURE
from django.core.management import call_command

from lms.djangoapps.instructor_task.models import InstructorTask, QUEUING
from lms.djangoapps.instructor_task.tests.factories import InstructorTaskFactory
from lms.djangoapps.instructor_task.tests.test_base import InstructorTaskTestCase


@ddt.ddt
class TestFailOldQueueingTasksCommand(InstructorTaskTestCase):
    """
    Tests for the `fail_old_queueing_tasks` management command
    """

    def setUp(self):
        super(TestFailOldQueueingTasksCommand, self).setUp()

        # this will be the value that we'll mock django.util.timezone.now
        # to return
        self.mock_now = datetime(2017, 1, 1)

        type_1_queueing = InstructorTaskFactory.create(
            task_state=QUEUING,
            task_type="type_1",
            task_key='',
            task_id=1,
        )
        type_1_non_queueing = InstructorTaskFactory.create(
            task_state='NOT QUEUEING',
            task_type="type_1",
            task_key='',
            task_id=2,
        )

        type_2_queueing = InstructorTaskFactory.create(
            task_state=QUEUING,
            task_type="type_2",
            task_key='',
            task_id=3,
        )

        # override each task's "created" date to two days before the "mock now"
        # time
        for task in [type_1_queueing, type_1_non_queueing, type_2_queueing]:
            task.created = self.mock_now - timedelta(3)
            task.save()

    def get_tasks(self):
        """
        After the command is run, this queries again for the tasks we created
        in `setUp`.
        """
        type_1_queueing = InstructorTask.objects.get(task_id=1)
        type_1_non_queueing = InstructorTask.objects.get(task_id=2)
        type_2_queueing = InstructorTask.objects.get(task_id=3)
        return type_1_queueing, type_1_non_queueing, type_2_queueing

    @ddt.data(0, 4)
    @mock.patch('django.utils.timezone.now')
    def test_dry_run(self, days_previous, mock_timezone_now):
        """
        Tests that nothing is updated when run with the `dry_run` option
        """
        mock_timezone_now.return_value = self.mock_now

        call_command('fail_old_queueing_tasks', dry_run=True, days_previous=days_previous)

        type_1_queueing, type_1_non_queueing, type_2_queueing = self.get_tasks()
        self.assertEqual(type_1_queueing.task_state, QUEUING)
        self.assertEqual(type_2_queueing.task_state, QUEUING)
        self.assertEqual(type_1_non_queueing.task_state, 'NOT QUEUEING')

    @mock.patch('django.utils.timezone.now')
    def test_new_tasks_not_updated(self, mock_timezone_now):
        """
        Test that tasks created after the days_previous option don't get changed,
        """
        mock_timezone_now.return_value = self.mock_now
        call_command('fail_old_queueing_tasks', days_previous=4)

        type_1_queueing, type_1_non_queueing, type_2_queueing = self.get_tasks()
        self.assertEqual(type_1_queueing.task_state, QUEUING)
        self.assertEqual(type_2_queueing.task_state, QUEUING)
        self.assertEqual(type_1_non_queueing.task_state, 'NOT QUEUEING')

    @mock.patch('django.utils.timezone.now')
    def test_old_tasks_updated(self, mock_timezone_now):
        """
        Test that tasks created before the days_previous cutoff DO get updated
        """
        mock_timezone_now.return_value = self.mock_now
        call_command('fail_old_queueing_tasks')

        type_1_queueing, type_1_non_queueing, type_2_queueing = self.get_tasks()
        self.assertEqual(type_1_queueing.task_state, FAILURE)
        self.assertEqual(type_2_queueing.task_state, FAILURE)
        self.assertEqual(type_1_non_queueing.task_state, 'NOT QUEUEING')

    @mock.patch('django.utils.timezone.now')
    def test_filter_by_task_type(self, mock_timezone_now):
        """
        Task that if we specify which task types to update, only tasks with
        those types are updated
        """
        mock_timezone_now.return_value = self.mock_now
        call_command('fail_old_queueing_tasks', task_type="type_1")
        type_1_queueing, type_1_non_queueing, type_2_queueing = self.get_tasks()
        self.assertEqual(type_1_queueing.task_state, FAILURE)
        # the other type of task shouldn't be updated
        self.assertEqual(type_2_queueing.task_state, QUEUING)
        self.assertEqual(type_1_non_queueing.task_state, 'NOT QUEUEING')
