import logging
from typing import Callable, Any

from arpakitlib.ar_exception_util import exception_to_traceback_str
from sqlalchemy.orm import Session

from project.core.util import setup_logging
from project.sqlalchemy_db_.sqlalchemy_db import get_cached_sqlalchemy_db
from project.sqlalchemy_db_.sqlalchemy_model import StoryLogDBM

_logger = logging.getLogger(__name__)


def sync_execute_with_story_log(
        func: Callable,
        *,
        func_args: tuple | None = None,
        func_kwargs: dict | None = None,
        session_: Session | None = None,
        story_log_level: str = StoryLogDBM.Levels.error,
        story_log_type: str = StoryLogDBM.Types.error_in_sync_execute_with_story_log,
        story_log_title: str | None = None,
        story_log_extra_data: dict | None = None,
) -> Any:
    if func_args is None:
        func_args = tuple()
    if func_kwargs is None:
        func_kwargs = {}
    if story_log_extra_data is None:
        story_log_extra_data = {}

    try:
        return func(*func_args, **func_kwargs)
    except Exception as exception:
        _logger.error(f"Error in {func.__name__}", exc_info=True)

        if story_log_title is None:
            story_log_title = f"Error in func {func.__name__}: {type(exception).__name__}: {exception}"
        story_log_extra_data.update({
            "exception": str(exception),
            "exception_traceback": exception_to_traceback_str(exception=exception),
            "exception_type_name": type(exception).__name__
        })

        if session_ is not None:
            story_log_dbm = StoryLogDBM(
                level=story_log_level,
                type=story_log_type,
                title=story_log_title,
                extra_data=story_log_extra_data
            )
            session_.add(story_log_dbm)
            session_.commit()
        else:
            with get_cached_sqlalchemy_db().new_session() as session:
                story_log_dbm = StoryLogDBM(
                    level=story_log_level,
                    type=story_log_type,
                    title=story_log_title,
                    extra_data=story_log_extra_data
                )
                session.add(story_log_dbm)
                session.commit()

        raise exception


def __example():
    setup_logging()

    def hello_world():
        print(1)
        raise ValueError("1111111")

    sync_execute_with_story_log(
        func=hello_world
    )


if __name__ == '__main__':
    __example()
