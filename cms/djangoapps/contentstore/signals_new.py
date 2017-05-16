from django.dispatch import Signal

# TODO (Alex Dusenbery 2017-05-16):
# Currently needed to avoid a circular import in course_grading.py.
# This goes away once Greg merges his PR to separate signals and handlers
# into different files.

# Signal that indicates that a course grading policy has been updated.
# This signal is generated when a grading policy change occurs within
# modulestore for either course or subsection changes.
GRADING_POLICY_CHANGED = Signal(
    providing_args=[
        'user_id',  # Integer User ID
        'course_id',  # Unicode string representing the course
    ]
)
