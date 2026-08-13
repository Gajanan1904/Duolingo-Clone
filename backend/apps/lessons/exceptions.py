class DomainError(Exception):
    """Base exception for domain/business logic errors."""

    default_code = "DOMAIN_ERROR"
    default_message = "A domain error occurred."

    def __init__(self, message=None, code=None):
        self.code = code or self.default_code
        self.message = message or self.default_message
        super().__init__(self.message)


class LessonNotFoundError(DomainError):
    default_code = "LESSON_NOT_FOUND"
    default_message = "Lesson does not exist."


class ExerciseNotFoundError(DomainError):
    default_code = "EXERCISE_NOT_FOUND"
    default_message = "Exercise does not exist."


class InvalidExerciseError(DomainError):
    default_code = "INVALID_EXERCISE"
    default_message = "Exercise configuration or type is invalid."


class InvalidAnswerError(DomainError):
    default_code = "INVALID_ANSWER"
    default_message = "Answer payload is invalid."


class OutOfHeartsError(DomainError):
    default_code = "OUT_OF_HEARTS"
    default_message = "You have no hearts remaining."


class LessonAlreadyCompletedError(DomainError):
    default_code = "LESSON_ALREADY_COMPLETED"
    default_message = "Lesson has already been completed."


class LessonNotCompletedError(DomainError):
    default_code = "LESSON_NOT_COMPLETED"
    default_message = "Lesson completion requirements have not been met."


class SkillLockedError(DomainError):
    default_code = "SKILL_LOCKED"
    default_message = "This skill is locked."


class InvalidAttemptError(DomainError):
    default_code = "INVALID_ATTEMPT"
    default_message = "Lesson attempt is invalid or unavailable."