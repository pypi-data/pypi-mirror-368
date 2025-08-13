# -*- coding: utf-8 -*-
import concurrent.futures as futures
from datetime import datetime
import pytz


def timeout(timelimit):
    def decorator(func):
        def decorated(*args, **kwargs):
            with futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    result = future.result(timelimit)
                except futures.TimeoutError:
                    print('Time out!')
                    raise TimeoutError from None
                else:
                    print(result)
                executor._threads.clear()
                futures.thread._threads_queues.clear()
                return result
        return decorated
    return decorator

def get_current_time(timezone="Asia/Taipei"):
    current_time_utc = datetime.utcnow()
    target_timezone = pytz.timezone(timezone)
    target_current_time = current_time_utc.replace(
        tzinfo=pytz.utc).astimezone(target_timezone)
    return target_current_time

def get_account_status(userid, profile_soup=None):
    if userid == "":
        return "missing"
    else:
        private_span = profile_soup.find(
            "span", class_="ident private icon icon_lock")
        if private_span:
            return "private"
        return "public"