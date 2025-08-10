import logging
import logging.handlers
import os
import traceback
from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager
from functools import lru_cache
from asgi_correlation_id import CorrelationIdMiddleware, CorrelationIdFilter

import dotenv
import watchtower
from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.engine import URL
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from . import database
from .const import LOG_FMT, LOG_FMT_NO_DT, LOG_DT_FMT, DEFAULT_LOGGER_NAME, APS_EVENT_CODE, \
    CORRELATION_ID_HEADER_KEY_NAME
from .exception.base_exception import InternalBaseException
from .exception.internal_exception import BadGatewayException, GatewayTimeoutException
from .ext.amazon import aws
from .http.requests import send_webhook_message
from .http.responses import async_response
from .utils import update_dict_with_cast


class BaseFactory(metaclass=ABCMeta):
    DEFAULT_APP_NAME = ""
    API_VERSION = "v0.0.0"

    @abstractmethod
    def init_modules(self, app):
        """
        Each factory should define what modules it wants.
        """

    @abstractmethod
    def init_modules_job(self, app):
        """
        Each factory should define what modules job it wants.
        """

    @abstractmethod
    @lru_cache()
    def get_app_config(self):
        """
        Each factory should define what config it wants.
        """

    def create_app(self, title=None) -> FastAPI:
        lifespan = None

        @asynccontextmanager
        async def lifespan(app: FastAPI):

            await self.__init_apscheduler(app)

            yield
            if app.state.db._engine is not None:
                await app.state.db.close()

            app.state.scheduler.shutdown()
            app.state.logger.warn("Apscheduler shutdown")

        if title is None:
            title = self.DEFAULT_APP_NAME

        if self.get_app_config().DEBUG:
            app = FastAPI(openapi_url=self.get_app_config().OPEN_API_URL, title=title,
                          debug=self.get_app_config().DEBUG,
                          version=self.API_VERSION, lifespan=lifespan)
        else:
            app = FastAPI(openapi_url=self.get_app_config().OPEN_API_URL, title=title,
                          debug=self.get_app_config().DEBUG,
                          version=self.API_VERSION, lifespan=lifespan, docs_url=None, redoc_url=None)

        origins = ["*"]

        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=[CORRELATION_ID_HEADER_KEY_NAME]
        )

        app.add_middleware(
            CorrelationIdMiddleware,
            header_name=CORRELATION_ID_HEADER_KEY_NAME,
            update_request_header=True
        )

        self.__load_local_config()
        app.state.config = self.get_app_config()
        self.__setup_main_logger(app, level=logging.DEBUG)
        app.state.aws_session = aws.init_app(app)
        self.__setup_cloud_log(app)
        self.__load_cloud_config(app)

        db = database.MariaDB(self.get_app_config().DATABASE_USERNAME, self.get_app_config().DATABASE_PASSWORD,
                              self.get_app_config().DATABASE_HOST, self.get_app_config().DATABASE_PORT,
                              self.get_app_config().DATABASE_NAME)

        app.state.db = db
        app.state.config = self.get_app_config()
        self.__init_modules(app)
        self.__init_builtin_api(app)

        @app.exception_handler(InternalBaseException)
        async def http_exception_handler(request: Request, exc: InternalBaseException):
            detail = exc.detail

            if isinstance(exc, BadGatewayException):
                message = f"【{self.DEFAULT_APP_NAME}】Bad gateway, request:{request.__dict__}, exc:{exc}"
                await send_webhook_message(app, message)
            elif isinstance(exc, GatewayTimeoutException):
                message = f"【{self.DEFAULT_APP_NAME}】Gateway timeout, request:{request.__dict__}, exc:{exc}"
                await send_webhook_message(app, message)

            return await async_response(data=detail.get("data"), code=detail.get("code"), message=detail.get("message"),
                                        status_code=exc.status_code)

        @app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            data = {"detail": exc.errors()}
            if exc.body:
                data["body"] = exc.body
            return await async_response(data=data,
                                        code="error_unprocessable_entity", message="參數或格式錯誤",
                                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

        @app.exception_handler(Exception)
        async def http_exception_handler(request: Request, exc: Exception):
            app.state.logger.warn(f"Exception, request:{request.__dict__}, exc:{exc}")
            app.state.logger.warn(traceback.format_exc())
            message = f"【{self.DEFAULT_APP_NAME}】Unprocessed Exception, request:{request.__dict__}, exc:{exc}"
            await send_webhook_message(app, message)

            return await async_response(code="error_internal_server", message="系統錯誤",
                                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return app

    def __load_local_config(self):
        dotenv.load_dotenv(override=True)
        update_dict_with_cast(self.get_app_config(), os.environ)

    def __load_cloud_config(self, app):
        if not app.state.aws_session or not self.get_app_config().AWS_PARAMETER_PATH_PREFIX:
            app.state.logger.warn("No AWS session or Parameter Storage configuration, ignore cloud config")
            return

        cloud_conf = {}

        params = {
            "Path": self.get_app_config().AWS_PARAMETER_PATH_PREFIX,
            "Recursive": True,
            "WithDecryption": True
        }

        # AWS only give us 10 parameters per api call
        ssm_client = app.state.aws_session.client("ssm")
        while True:
            result = ssm_client.get_parameters_by_path(**params)
            cloud_conf.update({para["Name"].split("/")[-1]: para["Value"] for para in result["Parameters"]})
            if not result.get("NextToken"):
                break
            params.update({"NextToken": result["NextToken"]})

        update_dict_with_cast(self.get_app_config(), cloud_conf)

    def __init_modules(self, app):
        self.init_modules(app)

    def __setup_main_logger(self, app, logger_name=DEFAULT_LOGGER_NAME, level=logging.INFO):
        logger = self.__setup_logger(app, logger_name, level)
        app.state.logger = logger

    #
    def __setup_logger(self, app, logger_name, level=logging.INFO):
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(fmt=LOG_FMT))
        stream_handler.addFilter(CorrelationIdFilter())
        logger.addHandler(stream_handler)

        return logger

    def __setup_cloud_log(self, app):
        if app.state.aws_session and self.get_app_config().AWS_LOGGROUP_NAME:
            logs_client = app.state.aws_session.client("logs")
            watchtower_handler = watchtower.CloudWatchLogHandler(
                log_group_name=self.get_app_config().AWS_LOGGROUP_NAME,
                boto3_client=logs_client, create_log_group=False)
            watchtower_handler.setFormatter(logging.Formatter(fmt=LOG_FMT_NO_DT, datefmt=LOG_DT_FMT))
            watchtower_handler.addFilter(CorrelationIdFilter())
            app.state.logger.addHandler(watchtower_handler)

            # 获取和设置 SQLAlchemy 的日志器
            sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
            sqlalchemy_logger.setLevel(logging.DEBUG)  # 根据需要设置日志级别
            sqlalchemy_logger.addHandler(watchtower_handler)

    def __init_builtin_api(self, app):

        @app.get(f'/health', tags=["System"])
        async def health():
            return await async_response()

        @app.get(f'/hello', tags=["System"])
        async def hello():
            return await async_response(data={"API version": app.version})

    async def __init_apscheduler(self, app):
        sql_url = URL.create("mysql+pymysql",
                             username=self.get_app_config().DATABASE_USERNAME,
                             password=self.get_app_config().DATABASE_PASSWORD,
                             host=self.get_app_config().DATABASE_HOST,
                             port=self.get_app_config().DATABASE_PORT,
                             database=self.get_app_config().DATABASE_NAME)
        sql_url = sql_url.render_as_string(False)
        scheduler = AsyncIOScheduler(jobstores={'default': SQLAlchemyJobStore(url=sql_url)})
        app.state.scheduler = scheduler
        app.state.logger.info("Apscheduler initialized")
        self.init_modules_job(app)
        app.state.logger.info("Modules job initialized")

        from apscheduler.events import EVENT_JOB_ADDED, EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED, \
            EVENT_JOB_REMOVED, EVENT_JOB_SUBMITTED

        def job_event(event):
            app.state.logger.info(f'Job event occur, job: {event.job_id}, event: {APS_EVENT_CODE.get(event.code)}')

        app.state.scheduler.add_listener(
            job_event,
            EVENT_JOB_ADDED | EVENT_JOB_ERROR | EVENT_JOB_EXECUTED | EVENT_JOB_MISSED | EVENT_JOB_REMOVED | EVENT_JOB_SUBMITTED
        )

        app.state.scheduler.start()
