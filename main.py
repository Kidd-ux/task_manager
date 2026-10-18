from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from task_manager_exceptions import (
    EmailAlreadyExistsError,
    UserNotFoundError,
    ProjectNotFoundError,
    ProjectOwnerNotFoundError,
    TaskNotFoundError,
    CommentNotFoundError,
    InvalidCredentialsError,
    InvalidTokenError,
    ProjectForbiddenError,
    CommentForbiddenError,
    UserHasRelationsError,
    TaskForbiddenError,
    ProjectAlreadyExistsError,
)
from routers.projects import router as project_router
from routers.tasks import router as task_router
from routers.comments import router as comment_router
from routers.users import router as user_router
from routers.auth import router as auth_router

app = FastAPI()

app.include_router(task_router)
app.include_router(project_router)
app.include_router(comment_router)
app.include_router(user_router)
app.include_router(auth_router)


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
    return JSONResponse(
        status_code=401, content={"detail": "Invalid email or password"}
    )


@app.exception_handler(InvalidTokenError)
async def invalid_token_handler(request: Request, exc: InvalidTokenError):
    return JSONResponse(
        status_code=401,
        content={"detail": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(ProjectForbiddenError)
async def project_forbidden_error(request: Request, exc: ProjectForbiddenError):
    return JSONResponse(
        status_code=403, content={"detail": "You do not have permission"}
    )


@app.exception_handler(CommentForbiddenError)
async def comment_forbidden_error(request: Request, exc: CommentForbiddenError):
    return JSONResponse(
        status_code=403, content={"detail": "You do not have permission"}
    )


@app.exception_handler(TaskForbiddenError)
async def task_forbidden_error(request: Request, exc: TaskForbiddenError):
    return JSONResponse(
        status_code=403, content={"detail": "You do not have permission"}
    )


@app.exception_handler(EmailAlreadyExistsError)
async def email_exists_handler(request: Request, exc: EmailAlreadyExistsError):
    return JSONResponse(status_code=409, content={"detail": "Email already exists"})


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "User not found"})


@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Task not found"})


@app.exception_handler(ProjectNotFoundError)
async def project_not_found_handler(request: Request, exc: ProjectNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Project not found"})


@app.exception_handler(CommentNotFoundError)
async def comment_not_found_handler(request: Request, exc: CommentNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Comment not found"})


@app.exception_handler(ProjectOwnerNotFoundError)
async def project_owner_not_found_handler(
    request: Request, exc: ProjectOwnerNotFoundError
):
    return JSONResponse(status_code=404, content={"detail": "User not found"})


@app.exception_handler(UserHasRelationsError)
async def user_has_relations_error(request: Request, exc: UserHasRelationsError):
    return JSONResponse(
        status_code=409, content={"detail": "Cannot delete user with related data"}
    )


@app.exception_handler(ProjectAlreadyExistsError)
async def project_already_exists_error(
    request: Request, exc: ProjectAlreadyExistsError
):
    return JSONResponse(status_code=409, content={"detail": "Project already exists"})
