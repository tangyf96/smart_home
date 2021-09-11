import time
import datetime
import board
import adafruit_dht
import RPi.GPIO as GPIO
import pickle

def humidity_sensor():
    # Initial the dht device, with data pin connected to:
    dhtDevice = adafruit_dht.DHT11(board.D18)

    # you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
    # This may be necessary on a Linux single board computer like the Raspberry Pi,
    # but it will not work in CircuitPython.
    # dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

    while True:
        try:
            # Print the values to the serial port
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            print("Temp:  {} C    Humidity: {}% ".format(temperature_c, humidity))

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error

        time.sleep(2.0)

def button_test():
    button_io = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(button_io, GPIO.IN)
    isClick = False
    cnt = 0
    while True:
        input = GPIO.input(button_io)
        print("Button io is: {}".format(input))
        if (cnt == 0):
            prev_input = input
        cnt += 1
        if (input != prev_input):
            prev_input = input
            print("Click button")
            isClick = True
        else:
            print("Not click the button")
    GPIO.cleanup()

class HumidityMap():
    button_io_ = 17
    sensor_io_ = 18
    button_prev_status_ = 1
    button_cnt_ = 0

    def __init__(self, button_io, sensor_io):
        self.button_io_ = button_io
        self.sensor_io_ = sensor_io
        self.button_cnt_ = 0

    def Initialize(self):
        # define mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_io_, GPIO.IN)
        # Define sensors
        self.humid_sensor_ = adafruit_dht.DHT11(board.D18)

    """
    判断开关电信号变化
    """
    def IsClick(self):
        input = GPIO.input(self.button_io_)
        isClick = False
        if (self.button_cnt_ == 0):
            self.button_prev_status_ = input
            self.button_cnt_ += 1
            return False
        
        if (input != self.button_prev_status_ or input == 0):
            self.button_prev_status_ = input
            print("Click button cnt: {}".format(self.button_cnt_))
            self.button_cnt_ += 1
            isClick = True
        else:
            isClick = False
        return isClick

    """
    Get the current data by one click
    """
    def GetSingleData(self):
        status = False
        try:
            # Print the values to the serial port
            temperature_c = self.humid_sensor_.temperature
            humidity = self.humid_sensor_.humidity
            status = True
            return (status, humidity, temperature_c)
        except RuntimeError as error:
            print(error.args[0])
        except Exception as error:
            self.humid_sensor_.exit()
            print("Exit humidity sensor due to Exception")
            raise error
        time.sleep(2)
        return (False, 0, 0)

    def GetData(self, base_path):
        humidity_data = []
        temperature_data = []
        
        print("begin to get data")
        while True:
            try:
                if (self.IsClick()):
                    status, humid, tempe = self.GetSingleData()
                    if (status):
                        print("Current humidity: {}, temperature: {}".format(humid, tempe))
                        humidity_data.append(humid)
                        temperature_data.append(temperature_data)
                    else:
                        continue
                    time.sleep(2)
            except KeyboardInterrupt:
                print("Kill by terminal, data len: {}".format(len(humidity_data)))
                data_dict = {"humidity":humidity_data, "temperature":temperature_data}
                # save data
                dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                save_path = base_path + "/humid_temp_" + dt + ".pkl"
                with open(save_path, "wb") as f:
                    pickle.dump(data_dict, f)
                
                dhtDevice.exit()
                GPIO.cleanup()
                exit()


if __name__ == "__main__":
    # humidity_sensor()
    # button_test()

    button_io = 17
    sensor_io = 18
    path = "/home/pi/smart_home"
    test = HumidityMap(button_io, sensor_io)
    test.Initialize()
    test.GetData(path)