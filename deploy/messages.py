import datadog
import slackweb


class Message():
    def __init__(
            self,
            config,
            branch,
            commit,
            repo,
            test=False,
            *args,
            **kwargs):
        self.config = config
        self.branch = branch
        self.commit = commit
        self.repo = repo
        self.test = test

    def send_datadog(self, alert_type="info"):
        print(">> Enviando mensagem para Datadog")
        if self.test:
            return
        options = {
            'api_key': self.config['datadog_api_key'],
            'app_key': self.config['datadog_app_key']
        }

        datadog.initialize(**options)

        title = "DEPLOY INICIADO: {}/{}".format(self.repo, self.branch.name)
        text = self.commit
        tags = ["deploy"]

        datadog.api.Event.create(
            title=title,
            text=text,
            tags=tags,
            alert_type=alert_type
        )

    def send_slack(self):
        print(">> Enviando mensagem para Slack")
        if self.test:
            return
        slack = slackweb.Slack(
            url=self.config['slack_url']
        )

        text = "DEPLOY INICIADO: {}/{}\n{}".format(
            self.repo,
            self.branch.name,
            self.commit
        )

        slack.notify(
            text=text,
            channel="#{}".format(self.config['slack_channel']),
            username=self.config['slack_user'],
            icon_emoji=":{}:".format(self.config['slack_icon'])
        )
