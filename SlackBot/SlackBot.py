import re
from slackclient import SlackClient
import time
import datetime
from Menu.MenuManager import MenuManager
from toollib.logger import Logger
from config import config


class SlackBot(object):
    logger = Logger("SlackBot")

    def __init__(self):
        self.slack_client = SlackClient(config.get("slack_api"))
        self.starterbot_id = None
        self.RTM_READ_DELAY = 1
        self.EXAMPLE_COMMAND = "do"
        self.MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
        self.cook_slave = MenuManager()
        self.alarm_time = "110000"  # default time
        self.channel_url = None

    def parse_bot_commands(self, slack_events):

        for event in slack_events:
            if event["type"] == "message" and not "subtype" in event:
                user_id, message = self.parse_direct_mention(event["text"])
                if user_id == self.starterbot_id:
                    return message, event["channel"]
        return None, None

    def parse_direct_mention(self, message_text):

        matches = re.search(self.MENTION_REGEX, message_text)

        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def handle_command(self, command, channel):

        response = None
        try:
            if self.channel_url is None:
                if command == "등록":
                    self.channel_url = channel
                    response = "등록되었습니다."
                else:
                    response = "채널등록 먼저 해주세요 슬랙에서 등록이라고 치면 됩니다. ex) 등록"

            elif command == "help" or command == "도움말":
                response = "※SQL인젝션 금지-----\n1. 밥추천/추천/메뉴추천/메뉴 추천 ex) 밥추천\n2. 추가/밥추가/메뉴추가 ex)밥추가 돈가스\n" \
                           "3. 삭제/밥삭제/메뉴삭제 ex) 삭제 돈가스\n4. 확인/메뉴기록/메뉴로그 ex) 확인 2018-11-07\n" \
                           "5. 초기화/재세팅 ex) 초기화\n 6. 모든메뉴 ex) 모든메뉴\n7. 알람설정 ex) 알람설정 110000\n8. 기타설명\n" \
                           "9. 채널변경 및 등록 ex) 등록"

            elif command == "alert":
                response = "오늘의 메뉴는 " + self.cook_slave.menu_rand_select() + " 입니다."

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

            elif command.startswith("알람설정"):
                if len(command) > 4:
                    alarm = command.split(' ')[1]
                    result = self.cook_slave.set_alarm_time(alarm)
                    if result is True:
                        self.alarm_time = alarm
                        response = "매일 " + alarm + " 시간에 메뉴와 알림이 옵니다"
                    else:
                        response = result

            elif command.startswith("모든메뉴"):
                response = self.cook_slave.all_menu_check()

            elif command.startswith("기타설명"):
                response = "1. 초기화/재세팅은 매주마다 먹은 음식이 겹치지 않도록 하는 것이며, 월요일 오전 9시마다 자동으로 재세팅 되는 것이므로" \
                               "따로 입력을 하지 않아도 되나, 하는 것은 자유이다.\n2. 로그는 항상 YYYY-MM-DD로 입력해야 한다." \
                               "\n3. 알람설정은 매일 같은시간에 점심메뉴를 추천해주는 알림을 제공해주며 기본값은 110000이고" \
                               "153030은 3시30분30초라는 의미이다."
            elif command == "등록":
                self.channel_url = channel
                response = "등록되었습니다."
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

                if r == 0 and time_check == "090000":   #월요일 9시에 데이터 초기화
                    self.cook_slave.menu_setting()

                if time_check == self.alarm_time and self.channel_url is not None:
                    self.handle_command("alert", self.channel_url)

                if command:
                    self.handle_command(command, channel)
                time.sleep(self.RTM_READ_DELAY)
        else:
            self.logger.debug("Connection failed. Exception traceback printed above.")
