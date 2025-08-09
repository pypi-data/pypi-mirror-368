from atlib import GSM_Device, Status
import time

gsm = GSM_Device("/dev/ttyUSB5", baudrate=115200)

gsm.wait_for_call()
gsm.accept_call()

"""
counter = 0
while counter < 5:
    print(f"Call {counter}")
    result = gsm.call("+4368110549549", False)

    time.sleep(20)

    result = gsm.disconnect()

    counter += 1

    time.sleep(23)
"""

"""
operator = gsm.get_current_operator()
print(operator)

operators = gsm.get_available_operators()
print(operators)

gsm.set_operator("A1")

operator = gsm.get_current_operator()
print(operator)

gsm.set_operator_auto()
operator = gsm.get_current_operator()
print(operator)

nr = input("Phone number: ")
msg = input("Message: ")

if gsm.send_sms(nr, msg) != Status.OK:
    print("Error sending message.")
"""