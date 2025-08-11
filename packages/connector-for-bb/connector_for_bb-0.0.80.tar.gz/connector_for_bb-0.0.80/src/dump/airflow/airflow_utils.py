import asyncio

from airflow.notifications.basenotifier import BaseNotifier
from telegram import Bot

from dump.config_utils import load_config


class TelegramNotification(BaseNotifier):
    def __init__(
        self,
        tg_notification_config_name: str = "tg_notification.ini",
        tg_notification_config_section: str = "default",
    ):
        self.__config = load_config(
            filename=tg_notification_config_name,
            section=tg_notification_config_section,
        )

    @staticmethod
    async def send_tg_notifier(
        notifier_message,
        telegram_bot_token,
        telegram_chat_id,
    ):

        bot = Bot(token=telegram_bot_token)
        await bot.sendMessage(
            chat_id=telegram_chat_id,
            text=notifier_message,
            parse_mode="Markdown",
        )

    def notify(self, context):
        telegram_bot_token, telegram_chat_id, airflow_url = self.__config.values()

        task_id = context["ti"].task_id.replace("_", "\_")
        task_state = context["ti"].state.replace("_", "\_")
        task_log_url = (
            context["ti"]
            .log_url.replace("http://localhost:8080", airflow_url)
            .replace("_", "\_")
        )
        dag_name = context["ti"].dag_id.replace("_", "\_")

        message_template = (
            f"***Dag name:*** {dag_name} \n"
            f"***Task id:*** {task_id} \n"
            f"***Task State:*** \N{Cross mark}{task_state}\N{Cross mark} \n"
            f"***Task Log URL:*** {task_log_url} \n"
        )

        asyncio.run(
            self.send_tg_notifier(
                notifier_message=message_template,
                telegram_bot_token=telegram_bot_token,
                telegram_chat_id=telegram_chat_id,
            )
        )
