import time

import fseconomy.data

fseconomy.set_user_key('0015D19A457E2FCD')
fseconomy.set_service_key('ACC8CD693E664194')

t1 = fseconomy.data.flight_logs_by_reg_from_id(18394434, 'D-FLOW')
time.sleep(5)
t2 = fseconomy.data.flight_logs_by_key_from_id(18394434)

if t1 is not None:
    print("By Reg from ID: {}".format(len(t1.data)))

if t2 is not None:
    print("By Key from ID: {}".format(len(t2.data)))
