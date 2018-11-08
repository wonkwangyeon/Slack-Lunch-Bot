import re
from slackclient import SlackClient
from SqlLite.DB import DB
import time
import datetime
from Menu.MenuManager import MenuManager
from config import config
from toollib.logger import Logger


class SlackBot(object):
    logger = Logger("SlackBot")

    def __init__(self):
        self.slack_client = SlackClient(config.get('slack_api'))

        self.starterbot_id = None
        self.RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
        self.EXAMPLE_COMMAND = "do"
        self.MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
        self.cook_slave = MenuManager()


    def parse_bot_commands(self, slack_events):
        """
            Parses a list of events coming from the Slack RTM API to find bot commands.
            If a bot command is found, this function returns a tuple of command and channel.
            If its not found, then this function returns None, None.
        """
        for event in slack_events:
            if event["type"] == "message" and not "subtype" in event:
                user_id, message = self.parse_direct_mention(event["text"])
                if user_id == self.starterbot_id:
                    return message, event["channel"]
        return None, None

    def parse_direct_mention(self, message_text):
        """
            Finds a direct mention (a mention that is at the beginning) in message text
            and returns the user ID which was mentioned. If there is no direct mention, returns None
        """
        matches = re.search(self.MENTION_REGEX, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def handle_command(self, command, channel):

        response = None
        try:
            if command == "help" or command == "도움말":
                response = "※SQL인젝션 금지-----\n1. 밥추천/추천/메뉴추천/메뉴 추천 ex) 밥추천\n2. 추가/밥추가/메뉴추가 ex)밥추가 돈가스\n" \
                           "3. 삭제/밥삭제/메뉴삭제 ex) 삭제 돈가스\n4. 확인/메뉴기록/메뉴로그 ex) 확인 2018-11-07\n" \
                           "5. 초기화/재세팅 ex) 초기화\n 6. 모든메뉴 ex) 모든메뉴\n7. 기타설명"

            elif command.startswith("밥추천") or command.startswith("추천") or command.startswith("메뉴추천") or command.startswith("메뉴 추천"):
                response = self.cook_slave.menu_recommend()

            elif command.startswith("추가"):
                if len(command) > 2:
                    result = self.cook_slave.menu_insert(command.split(' ')[1])
                    response = "(" + command.split(' ')[1] + ") " + result

            elif command.startswith("밥추가") or command.startswith("메뉴추가"):
                if len(command) > 3:
                    result = self.self.cook_slave.menu_insert(command.split(' ')[1])
                    response = "(" + command.split(' ')[1] + ") " + result

            elif command.startswith("삭제"):
                if len(command) > 2:
                    result = self.cook_slave.menu_delete(command.split(' ')[1])
                    response = "(" + command.split(' ')[1] + ") " + result

            elif command.startswith("밥삭제") or command.startswith("메뉴삭제"):
                if len(command) > 3:
                    result = self.cook_slave.menu_delete(command.split(' ')[1])
                    response = "(" + command.split(' ')[1] + ") " + result

            elif command.startswith("확인"):
                if len(command) > 2:
                    result = self.cook_slave.find_menu_log(command.split(' ')[1])
                    response = result

            elif command.startswith("메뉴기록") or command.startswith("메뉴로그"):
                if len(command) > 3:
                    result = self.cook_slave.find_menu_log(command.split(' ')[1])
                    response = result

            elif command.startswith("초기화") or command.startswith("재세팅"):
                    result = self.cook_slave.menu_setting()
                    response = result

            elif command.startswith("모든메뉴"):
                    response = self.cook_slave.all_menu_check()

            elif command.startswith("기타설명"):
                    response = "1. 초기화/재세팅은 매주마다 먹은 음식이 겹치지 않도록 하는 것이며, 월요일 오전 9시마다 자동으로 재세팅 되는 것이므로" \
                               "따로 입력을 하지 않아도 되나, 하는 것은 자유이다.\n2. 로그는 항상 YYYY-MM-DD로 입력해야 한다."
            else:
                response = "help 또는 도움말 라고 입력해주세요"

        except Exception as e:
            self.logger.debug(e)
            response = "※ SQL인젝션 금지------\nhelp 또는 도움말을 통해 설명을 다시 확인해주세요"
        # Sends the response back to the channel
        self.slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response
        )


    def start(self):
        if self.slack_client.rtm_connect(with_team_state=False):
            self.logger.debug("Starter Bot connected and running!")
            # Read bot's user ID by calling Web API method `auth.test`
            self.starterbot_id = self.slack_client.api_call("auth.test")["user_id"]
            self.cook_slave.menu_setting()
            while True:
                command, channel = self.parse_bot_commands(self.slack_client.rtm_read())
                time_check = time.strftime('%H%M%S')
                r = datetime.datetime.today().weekday()
                if r == 0 and time_check == "090000": #월요일 9시에 데이터 초기화
                    self.cook_slave.menu_setting()

                if time_check == "110000":
                    self.handle_command("추천", "C96UMUYDN")

                if command:
                    self.handle_command(command, channel)
                time.sleep(self.RTM_READ_DELAY)
        else:
            self.logger.debug("Connection failed. Exception traceback printed above.")
