import os

config = {'log_level': os.environ.get('LOG_LEVEL'),
          'slack_api': os.environ.get('SLACK_API')
          }
