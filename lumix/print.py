import datetime

async def log(message):
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    print(f'[{current_time}] {message}')
