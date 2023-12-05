import os
import socket
import sys
import time
import traceback
import threading

from collections import deque

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QApplication

from hmi import *


########## Global variables

# Create the main queue object, if can't then exit the app.
MAX_QUEUE_SIZE = 100
try:
    MAIN_QUEUE = deque(maxlen=MAX_QUEUE_SIZE)
except:
    print('---It failed to create the main queue object! System exits!---')
    sys.exit(traceback.format_exc())
else:
    STATE = 'INITIALIZE'
    DATA =  None
    MAIN_QUEUE.append({'STATE':STATE, 'DATA':DATA})
finally:
    pass

# Controller connected
CONTROLLER_CONNECTED = False

# Global exit
GLOBAL_EXIT = False

# Global message handling loop error
GLOBAL_MHL_ERROR_DATA = None
GLOBAL_MHL_ERROR_ERROR = False
GLOBAL_MHL_ERROR = {'ERROR':GLOBAL_MHL_ERROR_ERROR, 'DATA':GLOBAL_MHL_ERROR_DATA}

# Global GUI-event loop error
GLOBAL_EHL_ERROR_DATA = None
GLOBAL_EHL_ERROR_ERROR = False
GLOBAL_EHL_ERROR = {'ERROR':GLOBAL_EHL_ERROR_ERROR, 'DATA':GLOBAL_EHL_ERROR_DATA}

# Maximum UDP bytes
MAX_BYTES = 65535

########## Functions
pass

########## Classes

# PyQt5 application window
class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_hmi()
        self.ui.setupUi(self)

        # Setting  the fixed size of window
        width = 800
        height = 400
        self.setFixedSize(width, height)

        # Define callback functions
        self.ui.Exit_Btn.clicked.connect(self.exit_btn)
        self.ui.Connect_Controller_Btn.clicked.connect(self.connect_controller_btn)
        self.ui.Run_Control_Btn.clicked.connect(self.run_control_btn)
        self.ui.Stop_Control_Btn.clicked.connect(self.stop_control_btn)
        self.ui.Update_Control_Config_Btn.clicked.connect(self.update_control_config_btn)
        self.ui.Update_Setpoint_Edit.returnPressed.connect(self.update_setpoint_edit)

        self.timer_for_timeout = QTimer()
        self.timer_for_timeout.timeout.connect(self.timer_for_timeout_fcn)
        self.timer_for_timeout.start(100)  # add a timeout to the event loop!

        self.show()
        return None

    def exit_btn(self):
        # print(MAIN_QUEUE)
        self.close()  # This will call the function self.closeEvent
        return None

    def connect_controller_btn(self):
        STATE = 'CONNECT CONTROLLER'
        DATA =  None
        MAIN_QUEUE.append({'STATE':STATE, 'DATA':DATA})  # MAIN_QUEUE.append(...) doesn't generate exceptions.
                                                         # When appending, if the queue is full, an exisiting
                                                         # element will be removed!
        # print(MAIN_QUEUE)
        return None

    def stop_control_btn(self):
        STATE = 'STOP CONTROL'
        DATA =  None
        MAIN_QUEUE.append({'STATE':STATE, 'DATA':DATA})
        # print(MAIN_QUEUE)
        return None

    def run_control_btn(self):
        STATE = 'RUN CONTROL'
        DATA =  None
        MAIN_QUEUE.append({'STATE':STATE, 'DATA':DATA})
        # print(MAIN_QUEUE)
        return None

    def update_control_config_btn(self):
        STATE = 'UPDATE CONTROL CONFIG'
        DATA = {'Kp':1.0, 'Ki':1.0, 'Kd':1.0, 'High':1.0, 'Low':0.0}
        MAIN_QUEUE.append({'STATE':STATE, 'DATA':DATA})
        # print(MAIN_QUEUE)
        return None

    def update_setpoint_edit(self):
        STATE = 'UPDATE SETPOINT'
        try:
            setpoint = float(self.ui.Update_Setpoint_Edit.text())
        except:
            pass
        else:
            DATA =  {'Setpoint':setpoint}
            MAIN_QUEUE.append({'STATE':STATE, 'DATA':DATA})
        finally:
            pass
        # print(MAIN_QUEUE)
        return None

    def closeEvent(self, event):
        print('---Cleaning, flushing queue, closing ports, etc.---')
        # Close network socket


        STATE = 'EXIT'
        DATA =  None
        MAIN_QUEUE.append({'STATE':STATE, 'DATA':DATA})  # Add 'EXIT' state so that the MHL will terminate.
        event.accept()  # or event.ignore()
        print('---Application is closed!---')
        return None

    def timer_for_timeout_fcn(self):
        # Chech global GLOBAL_EXIT.
        if GLOBAL_EXIT:
            MAIN_QUEUE.appendleft({'STATE':'EXIT', 'DATA':None})
            self.close()
        return None

# Thread for the message handling loop
class MessageHandlingLoop(threading.Thread):
    def __init__(self, app_window):
        threading.Thread.__init__(self)
        self.app_window = app_window
        return None

    def run(self):
        print('---The message handling loop starts---')
        while True:
            # Dequeue elements: create a function names dequeue_manager(),
            # input arg/s   : MAIN_QUEUE
            # output/s      : state_name and state_data
            # The function should handle exceptions and return error.
            # Implement an early function-return with True at the end of try-clause, if no exceptions occured.
            # Implement an early function-return with False in finally section, if exceptions occured.
            try:
                dequed_data = MAIN_QUEUE.popleft()
            except:
                state_name = ''
                state_data = None
            else:  # Execute if the try clause does not raise an exception
                state_name = dequed_data['STATE']
                state_data = dequed_data['DATA']
                print(state_name)
            finally:
                pass

            # Implement the state machine: create a function for the state machine (?).
            if state_name == 'INITIALIZE':
                # Do something and update GLOBAL_MHL_ERROR, add create to MAIN_QUEUE if necessary, ...
                pass
            elif state_name == 'EXIT':
                # Do something and update GLOBAL_MHL_ERROR, add create to MAIN_QUEUE if necessary, ...
                MAIN_QUEUE.clear()
                print('---The event handler ends---')
                return None
            elif state_name == 'CONNECT CONTROLLER':
                # Do something and update GLOBAL_MHL_ERROR, add create to MAIN_QUEUE if necessary, ...

                # Create a TCP socket (SOCK_STREAM)
                controller_ip_addr = self.app_window.ui.Controller_IP_Addr_Edit.text()
                controller_ip_port = int(self.app_window.ui.Controller_IP_Port_Edit.text())
                try:
                    self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    text = 'test'
                    data = text.encode('ascii')
                    self.socket_udp.sendto(data, (controller_ip_addr, controller_ip_port))
                    data, address = self.socket_udp.recvfrom(MAX_BYTES)
                    text = data.decode('ascii')
                    print('The server {} replied {!r}'.format(address, text))
                except socket.error as err:
                    print('Failed to crate a socket')
                    print('Reason: %s' %str(err))
                    # Update GLOBAL_MHL_ERROR here
                else:
                    self.app_window.ui.Connect_Controller_Status_Edit.setText('Yes')
                    self.socket_udp.close()
                finally:
                    pass
            elif state_name == 'STOP CONTROL':
                # Do something and update GLOBAL_MHL_ERROR, add create to MAIN_QUEUE if necessary, ...
                pass
            elif state_name == 'RUN CONTROL':
                # Do something and update GLOBAL_MHL_ERROR, add create to MAIN_QUEUE if necessary, ...
                pass
            elif state_name == 'UPDATE CONTROL CONFIG':
                # Do something and update GLOBAL_MHL_ERROR, add create to MAIN_QUEUE if necessary, ...
                pass
            elif state_name == 'UPDATE SETPOINT':
                # Do something and update GLOBAL_MHL_ERROR, add create to MAIN_QUEUE if necessary, ...
                pass
            elif state_name == 'ERROR':
                # Do something and update GLOBAL_MHL_ERROR, add create to MAIN_QUEUE if necessary, ...
                pass
            else:  # Undefined state
                # Do something and update GLOBAL_MHL_ERROR, add create to MAIN_QUEUE if necessary, ...
                pass

            # Queue Manager: add state to the queue

            # Check for GLOBAL_ERROR, then add ERROR state.
            if GLOBAL_MHL_ERROR['ERROR']:
                MAIN_QUEUE.appendleft({'STATE':'ERROR', 'DATA':GLOBAL_MHL_ERROR['DATA']})

            # Chech global GLOBAL_EXIT.
            if GLOBAL_EXIT:
                MAIN_QUEUE.appendleft({'STATE':'EXIT', 'DATA':None})

        print('---The message handling loop ends---')
        return None

########## Run main.py
if __name__=="__main__":
    app = QApplication(sys.argv)
    app_window = AppWindow()
    thread_message_handling_loop = MessageHandlingLoop(app_window)
    thread_message_handling_loop.dameon = False
    thread_message_handling_loop.start()
    app_status = app.exec_()
    thread_message_handling_loop.join()  # Even though the thread runs an infinite while loop,
                                         # the state 'EXIT' will return the function run().
    sys.exit(app_status)
