#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import numpy as np
import time
import constant # Import file with necessary constants for the program
# ADC
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
# LCD
import I2C_LCD_driver # to work with the LCD display in I2C mode

# GLOBALS
pressure_array = np.array([-1]) #global because it will be accessed by functions outside main
RPM = 0

# Definitions
						#BEFORE PCB
LED 		= 17 	#6
BOTAO_SLEEP 	= 27	#26
BUZZER 		= 4   	#27
SENSOR_ROTACAO	= 26	#12
BOTAO_RESET 	= 19	# didnt exist

last_time = time.time()
this_time = time.time()

##### LCD #####
lcd = I2C_LCD_driver.lcd()

def setup_GPIOs():

	GPIO.setup(BOTAO_SLEEP	 , GPIO.IN)
	GPIO.setup(BOTAO_RESET	 , GPIO.IN)
	GPIO.setup(SENSOR_ROTACAO, GPIO.IN)

	GPIO.setup(LED 			, GPIO.OUT)
	GPIO.setup(BUZZER 		, GPIO.OUT)

	GPIO.output(BUZZER 	, False)
	GPIO.output(LED 	, False)

# callback that will be called when we detect rising border
def EventsPerTime(GPIO_ENTRADA):
        global RPM, this_time, last_time
        if GPIO.input(GPIO_ENTRADA) > 0.5:
                this_time = time.time()
                RPM = (1/(this_time - last_time))*60 	# in RPM
                #RPM = 1/(this_time - last_time)		# in Hz
                #print ("Current RPM = ",RPM)
                last_time = this_time

##### ADC - MCP3008 ######
# Import SPI library (for hardware SPI) and MCP3008 library.
#import Adafruit_GPIO.SPI as SPI
#import Adafruit_MCP3008

# Software SPI configuration:
		#ANTES DA PCB
CLK  = 22	#18
MISO = 10	#23
MOSI = 9	#24
CS   = 11	#15

mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)


def setup():
	print ("Setting up...")
	#GPIO.setmode(GPIO.BOARD)
	GPIO.setmode(GPIO.BCM)

	setup_GPIOs()

	# to detect rising bordedr and calculate frequency
	GPIO.add_event_detect(SENSOR_ROTACAO, GPIO.RISING, callback=EventsPerTime, bouncetime=1)

	#GPIO.setup(SENSOR_PRESSAO, GPIO.IN)
	#GPIO.setup(SENSOR_ROTACAO, GPIO.IN)	

def rpmToHz(rpm):

	return rpm/60

def getRotation():

	return RPM

def getPressure():
	reading=[0]
	try:
		reading = mcp.read_adc(1)
	except:
		print("erro no MCP")
	#print reading, constant.V_RESOLUTION, constant.FUNDO_DE_ESCALA, constant.VOLTS_POR_MM
	return ((reading*constant.V_RESOLUTION)-constant.FUNDO_DE_ESCALA)/constant.VOLTS_POR_MM #3.3/1023 #/constant.VOLTS_POR_MM

def verifyRotation(r): # will call the two functions below to check in which operating point the motor is
	if (verifyRotationAVG(r) == True):
		return 'AVG'

	elif (verifyRotationMAX(r) == True):
		return 'MAX'

	else:
		pass

def verifyRotationAVG(rotation): # 'average' rotation indicates the point where we check if the filter is punctured
	lower_lim = constant.ROTACAO_AVG*(1-constant.TOLERANCIA_ROTACAO_AVG)
	upper_lim = constant.ROTACAO_AVG*(1+constant.TOLERANCIA_ROTACAO_AVG)
	return (rotation >= lower_lim and rotation <= upper_lim)

def verifyRotationMAX(rotation): # 'maximum' rotation indicates the point where we check if the filter is SATURATED
	lower_lim = constant.ROTACAO_MAX*(1-constant.TOLERANCIA_ROTACAO_MAX)
	upper_lim = constant.ROTACAO_MAX*(1+constant.TOLERANCIA_ROTACAO_MAX)
	return (rotation >= lower_lim and rotation <= upper_lim)

def verifyPressureAVG(p): # tests if the read pressure is lower than the previous, to detect a PUNCTURE
	global pressure_array
#	print("verifyPressureAVG")
	while (estaFurado(p)): # as long as it is PUNCTURED

		printLCD("FILTRO DE AR OU\nTUBULACAO FURADA") # FILTER OR PIPES PUNCTURED
    		print("FILTRO DE AR OU\nTUBULACAO FURADA")# FILTER OR PIPES PUNCTURED
		alarme()
		#EVEN IF THE OPERATOR PRESSES THE BUTTON< WE SHOULD WAIT A FIXED AMOUNT OF TIME TO WARN HIS AGAIN ABOUT PUNCTURED FILTER

		if (GPIO.input(BOTAO_RESET) == True): # In case the RESET button is pressed, indicating that the filter has been changed, we get out of the while() loop
			lcd.lcd_clear()
			GPIO.output(BUZZER      ,False)
                        GPIO.output(LED         ,False)
			pressure_array = np.array([-1])
			break

def verifyPressureMAX(p): # tests if the read pressure is less than the previous ones, to detect SATURATED filter
	global pressure_array
#	print("verifyPressureMAX")
	#print("TESTE")
	#print(constant.LIMIAR_PRESSAO_SATURADO)

	while (estaSaturado(p)): # as long as it is SATURATED
	# it is necessary to obtain new pressure values in a way that, when the filter is cleaned, a values below the threshold is read, and the program follows its execution normally
	#OBS.: the values read during saturation are not kept, and at athe end of this loop, previous stored values are erased, because a new filter will be used
		printLCD("FILTRO SATURADO!")
	    	print("FILTRO SATURADO!")
		alarme()
		# EVEN IF THE OPERATOR PRESSES THE BUTTON, WE SHOULD WAIT A CERTAIN AMOUNT OF TIME TO WARN HIM AGAIN ABOUT THE SATURATED FILTER

		if (GPIO.input(BOTAO_RESET) == True): # In case the RESET button is pressed, indicating the filter has been changed, we get out of the while() loop
                        lcd.lcd_clear()
			GPIO.output(BUZZER      ,False)
                        GPIO.output(LED         ,False)
			pressure_array = np.array([-1])
			break

def alarme(): # routine to ring the alarm and flash the LED
	print("alarme")
	while (GPIO.input(BOTAO_SLEEP) != True or GPIO.input(BOTAO_RESET) != True): # while we dont press the button

	        for i in range(constant.NUM_ALERTAS): # sound and LED
			GPIO.output(BUZZER	,True)
			GPIO.output(LED 	,True)
			time.sleep(constant.TIME_LED_ON)
			GPIO.output(BUZZER 	,False)
		        GPIO.output(LED 	,False)
			time.sleep(constant.TIME_LED_OFF)
			t_now = time.time()

	    	t_prev = time.time()

		while((t_now - t_prev) < constant.TIME_LED_WAIT): # wait some time before sending sound alarm again, but keeps LED flasing
			GPIO.output(LED 	,True)
			time.sleep(constant.TIME_LED_ON)
			GPIO.output(LED 	,False)
			time.sleep(constant.TIME_LED_OFF)
			t_now = time.time()

			if (GPIO.input(BOTAO_RESET) == True): # In case the RESET button is pressed, indicating the filter has been changed, we get out of the while() loop
        	                print("BOTAO RESET ACIONADO !") # RESET BUTTON PRESSED !
				lcd.lcd_clear()
				GPIO.output(BUZZER      ,False)
                        	GPIO.output(LED         ,False)
	                        pressure_array = np.array([-1])
        	                return
			elif(GPIO.input(BOTAO_SLEEP) == True):
				sleep(constant.SLEEP_FILTRO_FURADO)
				return



def sleep(tempo): # snooze time for the filter alarm
	print("sleep")
	sleep_base 	= time.time()
	sleep_now 	= time.time()
	while ((sleep_now - sleep_base) < tempo):
		GPIO.output(LED,True)
		time.sleep(constant.TIME_LED_ON)
        	GPIO.output(LED,False)
		time.sleep(constant.TIME_LED_OFF)
		sleep_now = time.time()
		# update sleep_now
		#if (GPIO.input(BOTAO_SLEEP) == True): # se apertarmos o BOTAO_SLEEP novamente, nao precisamos esperar o tempo completo
		#	break

def estaSaturado(p): # checks if the filter is SATURATED
	#print(constant.LIMIAR_PRESSAO_SATURADO)
	return (p >= constant.LIMIAR_PRESSAO_SATURADO)

def estaFurado(p): # checks if the filter is PUNCTURED
#	print("estaFurado")
	curr_reading = p
	last_reading = pressure_array[-1]
	print("curr = " + str(curr_reading))
	print("last = " + str(last_reading))

 	return (curr_reading < last_reading*(1-constant.TOLERANCIA_PRESSAO_FURADO)) # if the value read is smaller than previous readings

def storePressure(p):
	global pressure_array
#	print("storePressure")
	pressure_array = np.append(pressure_array, p)

	if (pressure_array.size > 1000): # keep only last 1000 readings
		pressure_array = pressure_array[1:1001]
	print ("\nPressao armazenada = "+str(p)+" !\n")
	time.sleep(0.5) # avoid storing many times

def printLCD(x):
	#print("printLCD")
	lcd.lcd_clear()
	if (x.find('\n') != -1): # if there's any line break
		x1, x2 = x.split('\n')
		lcd.lcd_display_string(str(x1), 1)
		lcd.lcd_display_string(str(x2), 2)
	else:
		lcd.lcd_display_string(str(x), 1)
	#time.sleep(1)
if __name__ == "__main__":

	setup()

	try:
		while(True):
			r = getRotation()
			p = getPressure()
			print("Rotacao = "+str(r)+" RPM"),
			print("\tPressao = "+str(p)+"mm H20")
			printLCD("Rotacao = "+str(r)+"\nPressao = "+str(p))
			time.sleep(0.1)
			x = verifyRotation(r)
			# if rotation is 'in the middle' of the scale (motor@1600RPM), and IF we detect a PUNCTURED filter
			if (x == 'AVG'):
				verifyPressureAVG(p)
				# Store read pressure to create a history of readings and check if pressure has lowered
				storePressure(p)
			# if rotation is 'at the end' of the scale (motor@2200RPM) and IF we detect SATURATED filter
			elif (x == 'MAX'):
				verifyPressureMAX(p)

			else:
				pass # do nothing

	except KeyboardInterrupt:
		GPIO.cleanup()
		lcd.lcd_clear()
