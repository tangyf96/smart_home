'''
Author: Yifan Tang
Date: 2021-09-05 13:19:13
LastEditTime: 2021-09-05 13:19:51
FilePath: /smart_home/sensor/human_infrared_sensor.py
'''
import time 
import RPi.GPIO as gpio

def find_human(input_gpio):
    gpio.setmode(gpio.BCM)
    print("Input gpio is: {}".format(input_gpio))
    gpio.setup(input_gpio, gpio.IN)
    cnt = 0

    for i in range(1000):
        print("gpio no " + str(input_gpio) + ": " + str(gpio.input(input_gpio)))
        try: 
            inValue = gpio.input(input_gpio)
            #print(inValue)
            #print("GPIO {} value is : {}".format(input_gpio, inValue))
            if (inValue == True):
                #print("Find Human {}".format(cnt))
                cnt += 1
            else:
                print("Don't get information!")
        except Exception as error:
            raise error
        time.sleep(2)
    
    gpio.cleanup()


def test():
    gpio.setmode(gpio.BCM)

    gpios = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
            12, 13, 16, 17, 18, 19, 20, 21,
            22, 23, 24, 25, 26, 27]

    # Setup all GPIOs to input
    for gpio_code in gpios:
        gpio.setup(gpio_code, gpio.IN)
        
    # Read state for each GPIO
    for gpio_code in gpios:
        print("gpio no " + str(gpio_code) + ": " + str(gpio.input(gpio_code)))
        
    # Cleanup all GPIOs - state will be different after that!
    gpio.cleanup(gpios)

if __name__ == "__main__":
    input_gpio = 25
    #find_human(input_gpio)
    test()
