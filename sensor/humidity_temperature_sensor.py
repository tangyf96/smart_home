import time
import datetime
import board
import adafruit_dht
import RPi.GPIO as GPIO
import pickle
import os

def humidity_sensor_test():
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
    cnt = 0
    default_input = 0
    while True:
        input = GPIO.input(button_io)
        if (cnt == 0):
            prev_input = input
            default_input = input
            print("Button io is: {}".format(input))
            print("Default input is : {}".format(input))

        cnt += 1
        if (prev_input != input and input != default_input):
            print("Successfully Click button. previous input : {}, current input :{}".format(prev_input, input))
            prev_input = input
        else:
            prev_input = input
    GPIO.cleanup()

class HumidityMap():
    button_io_ = 17
    sensor_io_ = 18
    button_prev_status_ = 1
    button_cnt_ = 0
    button_default_status_ = 0
    max_data_id_ = 0
    map_points_id_ = []
    
    def __init__(self, button_io, sensor_io, map_path, area_num):
        self.button_io_ = button_io
        self.sensor_io_ = sensor_io
        self.button_cnt_ = 0
        with open(map_path, 'rb') as f:
            map_data = pickle.load(f)
            print("Map data keys is")
            print(map_data.keys())
            if (area_num == 1):
                self.map_points_id_ = map_data['area_one_point_def']
                self.max_data_id_ = self.map_points_id_[-1][-1]
            elif (area_num == 2):
                self.map_points_id_ = map_data['area_two_point_def']
                self.max_data_id_ = self.map_points_id_[-1][-1]
            else:
                print("Wrong area num {}".format(area_num))

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
            self.button_default_status_ = input
            self.button_prev_status_ = input
            self.button_cnt_ += 1
            print("Set button default status as {}".format(self.button_default_status_))
            return False
        
        if self.button_prev_status_ != input and input != self.button_default_status_:
            self.button_prev_status_ = input
            print("Click button cnt: {}".format(self.button_cnt_))
            self.button_cnt_ += 1
            isClick = True
        else:
            self.button_prev_status_ = input
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

    def GetDataId(self):
        cur_data_id = int(input("Please input your data id:    "))
        status = False
        if cur_data_id > self.max_data_id_:
            status = False
        else:
            status = True
        return status, cur_data_id

    def GetData(self, base_path):
        # Create folder
        cur_time_str = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
        folder_path = base_path + "/humidity_" + cur_time_str
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        print("Get data at time {}\n Save data in path :{}".format(cur_time_str,folder_path))

        humidity_data = []
        temperature_data = []        
        while True:
            try:
                if (self.IsClick()):
                    status, humid, tempe = self.GetSingleData()
                    if (status):
                        print("Current humidity: {}, temperature: {}".format(humid, tempe))
                        cur_time = time.time()
                        id_status, sample_id = self.GetDataId()
                        if not id_status:
                            print("Get incorrect data id: {}. It should less or equal than {}".format(sample_id, self.max_data_id_))
                            continue
                        humidity_data.append((humid, cur_time, sample_id))
                        temperature_data.append((tempe, cur_time, sample_id))
                    else:
                        continue
                    time.sleep(2)
            except KeyboardInterrupt:
                print("Kill by terminal, data len: {}".format(len(humidity_data)))
                data_dict = {"humidity":humidity_data, "temperature":temperature_data}
                # save data
                save_time_str = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
                save_path = folder_path + "/humid_temp_" + save_time_str + ".pkl"
                with open(save_path, "wb") as f:
                    pickle.dump(data_dict, f)
                
                txt_data_path = folder_path + "/humid_map_data_" + save_time_str + ".txt"
                with open(txt_data_path, 'w') as f:
                    f.write("id\ttimestamp\thumidity\ttemperature\n")
                    for i in range(len(humidity_data)):
                        assert(humidity_data[i][2] == temperature_data[i][2])
                        f.write("{}\t{}\t{}\t{}\n".format(humidity_data[i][2], humidity_data[i][1], humidity_data[i][0], temperature_data[i][0]))

                self.humid_sensor_.exit()
                GPIO.cleanup()
                exit()


if __name__ == "__main__":
    # humidity_sensor_test()
    # button_test()

    button_io = 17
    sensor_io = 18
    path = "/home/pi/smart_home/data"
    test = HumidityMap(button_io, sensor_io, map_path="/home/pi/smart_home/data/home_layout/sample_points.pkl", area_num=1)
    test.Initialize()
    test.GetData(path)