from ib_insync import IBC, IB, Watchdog
import os
import logging
from ib_account import IBAccount
import signal
import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

pre_date = datetime.datetime.now().date()
all_count = 0
today_count = 0

def ping():
    def timeout_handler(signum, frame):
        signal.alarm(0)
        raise TimeoutError('IB gateway timed out, please check your account & password')
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(120)

    ib = IB()
    while not ib.isConnected():
        try:
            IB.sleep(1)
            ib.connect('localhost', 4001, clientId=2)
        except (ConnectionRefusedError, OSError) as e:
            if type(e) is TimeoutError:
                raise e
            logging.warning('Still waiting gateway connection..({})'.format(e))
    
    ib.disconnect()

def onConnected():
    # logging.INFO(ib.accountValues())
    logging.info('ib onConnected event')
    all_count += 1
    n_time = datetime.datetime.now().date()
    if pre_date < n_time:
        today_count = 1
    else:
        today_count +=1
    logging.info('ib restart, all: {}, today: {}'.format(all_count, today_count))

if __name__ == "__main__":
    ib_gateway_version = int(os.listdir("/root/Jts/ibgateway")[0])
    account = IBAccount.account()
    password = IBAccount.password()
    trade_mode = IBAccount.trade_mode()
    ib = IB()
    ib.connectedEvent += onConnected
    ibc = IBC(ib_gateway_version, gateway=True, tradingMode=trade_mode, userid=account, password=password)
    watchdog = Watchdog(ibc, ib, port=4001, connectTimeout=60, appStartupTime=60*10, appTimeout=59, retryDelay=30)
    watchdog.start()
    ib.run()
    # ibc.start()
    # ping()
    # logging.info('IB gateway is ready.')
    
