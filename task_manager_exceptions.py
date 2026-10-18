class EmailAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class ProjectNotFoundError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


class CommentNotFoundError(Exception):
    pass


class ProjectOwnerNotFoundError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class ProjectForbiddenError(Exception):
    pass


class TaskForbiddenError(Exception):
    pass


class CommentForbiddenError(Exception):
    pass


class UserHasRelationsError(Exception):
    pass


class ProjectAlreadyExistsError(Exception):
    pass
