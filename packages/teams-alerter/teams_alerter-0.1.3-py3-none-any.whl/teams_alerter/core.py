import json
import traceback

from google.cloud import pubsub_v1
from .utils import ErrorUtils, DateUtils


class TeamsAlerter:

    def __init__(
        self,
        utils: ErrorUtils,
        teams_channel: str,
        detail,
        level,
        environment=None,
        url_log=None,
        timestamp=None,
        teams_template=None,
    ):
        self.utils = utils
        self.teams_channel = teams_channel
        self.detail = detail
        self.environment = environment
        self.level = level
        self.timestamp = timestamp
        self.url_log = url_log
        self.teams_template = teams_template

    @staticmethod
    def handle_error(error: Exception, utils: ErrorUtils) -> None:
        error_type = type(error).__name__
        error_message = str(error)
        error_traceback = traceback.format_exc()

        teams_alerter = TeamsAlerter(
            utils=utils,
            teams_channel=f"datastream-{utils['env']}-alerts",
            detail=f"Error type: {error_type}\nError message: {error_message}\nError traceback: {error_traceback}",
            level="ERROR",
        )

        teams_alerter.publish_alert()

    def publish_alert(self):
        # Formatage du payload
        utc_timestamp_minus_5min = DateUtils.get_str_utc_timestamp_minus_5min()
        utc_timestamp = DateUtils.get_str_utc_timestamp()
        payload = json.dumps(
            {
                "app_name": self.utils["app_name"],
                "teams_channel": self.teams_channel,
                "detail": self.detail,
                "level": self.level,
                "environment": self.utils["env"],
                "url_log": f"https://console.cloud.google.com/logs/query;query=resource.type%3D%22gce_instance%22%0Aresource.labels.project_id%3D%22{self.utils['app_project_id']}%22;cursorTimestamp={utc_timestamp_minus_5min};duration=PT10M?referrer=search&hl=fr&inv=1&invt=Ab3WcQ&project={self.utils['app_project_id']}",
                "timestamp": utc_timestamp,
                "teams_template": "card",
            }
        )

        # Création d'un éditeur
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(self.utils["topic_project_id"], self.utils["topic_id"])

        # Message à publier
        data = payload.encode("utf-8")

        # Publier le message
        try:
            publish_future = publisher.publish(topic_path, data)
            publish_future.result()

        except Exception as e:
            self.utils["logger"](f"🟥Une erreur s'est produite lors de la publication du message : {e}")
