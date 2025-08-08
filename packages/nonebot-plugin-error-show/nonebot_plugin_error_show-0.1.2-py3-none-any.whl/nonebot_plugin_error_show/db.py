import traceback
import uuid

from nonebot import require
from nonebot.adapters import Bot, Event

require("nonebot_plugin_orm")
require("nonebot_plugin_uninfo")

from nonebot_plugin_orm import AsyncSession, Model
from nonebot_plugin_uninfo import Uninfo
from sqlalchemy import String, delete, select
from sqlalchemy.orm import Mapped, mapped_column


class TraceLog(Model):
    """错误记录"""

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bot: Mapped[str] = mapped_column(String)
    event: Mapped[str] = mapped_column(String)
    exception: Mapped[str] = mapped_column(String)


class TraceSub(Model):
    """错误推送订阅"""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bot_id: Mapped[str] = mapped_column(String)
    adapter: Mapped[str] = mapped_column(String)
    session_id: Mapped[str] = mapped_column(String)
    session_type: Mapped[str] = mapped_column(String)


class TraceLogOper:
    def __init__(
        self,
        session: AsyncSession,
        bot: Bot | None = None,
        event: Event | None = None,
        exception: Exception | None = None,
        uuid_str: str | None = None,
    ):
        """
        错误操作
        :param session: 数据库会话
        :param bot: nonebot Bot
        :param event: nonebot Event
        :param exception: 异常对象（可选）
        :param uuid_str: 查询的 UUID（可选）
        """
        self.session: AsyncSession = session

        if uuid_str:
            self.id: str = uuid_str
        else:
            self.id: str = str(uuid.uuid4())

        self.bot: Bot = bot
        self.event: Event = event
        if exception:
            self.exception: str = "".join(
                traceback.format_exception(type(exception), exception, exception.__traceback__)
            )

    async def add(self) -> str:
        """
        添加错误记录
        :return: TraceLog Model
        """
        log = TraceLog(id=self.id, bot=str(self.bot), event=str(self.event), exception=self.exception)

        self.session.add(log)

        return log.id

    async def get(self) -> TraceLog | None:
        """
        获取错误记录
        :return:
        """
        log = await self.session.get(TraceLog, self.id)
        return log


class TraceSubOper:
    def __init__(self, session: AsyncSession, user_info: Uninfo):
        self.session: AsyncSession = session

        self.bot_id: str | None = None
        self.adapters: str | None = None
        self.session_id: str | None = None
        self.session_type: str | None = None

        self.bot_id = user_info.self_id
        self.adapters = user_info.adapter.name
        self.session_id = user_info.scene.id
        self.session_type = user_info.scene.type.name

    async def add(self) -> TraceSub:
        """
        添加订阅
        :return: TraceSub Model
        """
        result = await self.session.execute(
            TraceSub.__table__.select().where(
                (TraceSub.bot_id == self.bot_id)
                & (TraceSub.adapter == self.adapters)
                & (TraceSub.session_id == self.session_id)
                & (TraceSub.session_type == self.session_type)
            )
        )
        existing_sub = result.scalar_one_or_none()

        if not existing_sub:
            sub = TraceSub(
                bot_id=self.bot_id,
                adapter=self.adapters,
                session_id=self.session_id,
                session_type=self.session_type
            )
            self.session.add(sub)
            await self.session.commit()
            return sub

        return existing_sub

    async def delete(self) -> bool:
        """
        删除订阅
        :return: 受影响的行数
        """
        try:
            await self.session.stream(
                delete(TraceSub).where(
                    (TraceSub.bot_id == self.bot_id)
                    & (TraceSub.adapter == self.adapters)
                    & (TraceSub.session_id == self.session_id)
                    & (TraceSub.session_type == self.session_type)
                )
            )
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            return False
        finally:
            return True

    async def get(self) -> list[TraceSub]:
        """
        获取订阅
        :return: TraceSub Model 列表
        """
        result = await self.session.stream(
            select(TraceSub).where(
                (TraceSub.bot_id == self.bot_id)
                & (TraceSub.adapter == self.adapters)
                & (TraceSub.session_id == self.session_id)
                & (TraceSub.session_type == self.session_type)
            )
        )
        subs = await result.scalars()
        return subs

    async def get_all(self) -> list[TraceSub]:
        """
        获取所有订阅
        :return: TraceSub Model 列表
        """
        result = await self.session.stream(select(TraceSub))
        subs = await result.scalars().all()

        return subs
