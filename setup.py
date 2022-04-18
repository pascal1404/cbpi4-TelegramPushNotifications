from setuptools import setup

setup(name='cbpi4-TelegramPushNotifications',
      version='0.2.2',
      description='Plugin to send CraftBeerPi Notifications to a Telegram-Chat',
      author='Pascal Scholz',
      author_email='pascal1404@gmx.de',
      url='https://github.com/pascal1404/cbpi4-TelegramPushNotifications',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4-TelegramPushNotifications': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4-TelegramPushNotifications'],
      install_requires=[
            'telethon',
            'influxdb-client',
            'matplotlib',
            'pandas',
            'cryptg',
      ],
     )