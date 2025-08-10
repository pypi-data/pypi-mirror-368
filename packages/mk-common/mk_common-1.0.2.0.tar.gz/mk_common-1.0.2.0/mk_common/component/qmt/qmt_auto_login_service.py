import mk_common.util.windows_util as windows_util
import mk_common.util.data_frame_util as data_frame_util
import mk_common.util.date_handle_util as date_handle_util
from datetime import datetime, timedelta
import mk_common.component.qmt.qmt_one_minute_api as qmt_one_minute_api
import time
import pyautogui as pa
import pywinauto as pw
from loguru import logger

# qmt服务进程名称
QMT_SERVER_NAME_LIST = ["XtMiniQmt.exe", 'CefviewWing.exe', 'XtItClient.exe']

QMT_EXE_NAME = 'XtMiniQmt.exe'


def qmt_auto_login(user_account, user_password, qmt_exe_path):
    if windows_util.is_process_running(QMT_EXE_NAME):
        logger.warning("QMT终端已经在运行中")
        return {"result": 'success'}
    else:
        app = pw.Application(backend='uia').start(qmt_exe_path, timeout=10)
        app.top_window()
        pa.typewrite(user_account)
        time.sleep(1)
        pa.hotkey('tab')
        pa.typewrite(user_password)
        pa.hotkey('enter')
        return {"result": 'success'}


def check_qmt_status(user_account, user_password, qmt_exe_path):
    now_date = datetime.now()

    # Get the first day of the current month
    first_day_current = now_date.replace(day=1)
    # Subtract one day to get the last day of previous month
    last_day_previous = first_day_current - timedelta(days=1)
    # Get the first day of previous month
    first_day_previous = last_day_previous.replace(day=1)

    # Format the dates
    first_day_str = first_day_previous.strftime('%Y-%m-%d')
    last_day_str = last_day_previous.strftime('%Y-%m-%d')
    retry_number = 0
    # 连续重试10次
    while retry_number <= 10:
        try:
            qmt_auto_login(user_account, user_password, qmt_exe_path)
            time.sleep(10)
            test_df = qmt_one_minute_api.get_one_minute_data('000001.SH', date_handle_util.no_slash_date(first_day_str),
                                                             date_handle_util.no_slash_date(last_day_str), '1m', True)
            if data_frame_util.is_not_empty(test_df):
                logger.info("qmt运行成功")
                return True
            else:
                kill_qmt_server()
                time.sleep(5)
                retry_number = retry_number + 1
        except BaseException as e:
            time.sleep(5)
            retry_number = retry_number + 1
            logger.info("qmt启动异常:{}", e)
    return False


def kill_qmt_server():
    all_cmd_processes = windows_util.get_all_process()
    all_cmd_processes_trader = all_cmd_processes.loc[
        (all_cmd_processes['process_name'].isin(QMT_SERVER_NAME_LIST))]
    if data_frame_util.is_not_empty(all_cmd_processes_trader):
        for processes_one in all_cmd_processes_trader.itertuples():
            try:
                process_pid = processes_one.process_pid
                windows_util.kill_process_by_pid(process_pid)
            except BaseException as e:
                logger.error("杀死进程异常:{}", e)


if __name__ == '__main__':
    qmt_auto_login('test', 'test', 'test')
