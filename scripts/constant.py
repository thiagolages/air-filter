########### INFOS GERAIS ##########
# -*- coding: utf-8 -*-

VCC = 3.3 # Tensao de referência para o conversor AD, em volts

######## VALORES QUE PODEM SER ALTERADOS ##########

########### PRESSAO #############
PRESSAO_MAXIMA 			= 550	# Em mm de coluna d'agua
TOLERANCIA_PRESSAO_SATURADO 	= 1	# Quantos % da pressao maxima ja devemos considerar filtro SATURADO. Numero de 0 a 1 representando pocentagem! exemplo: 0.9 = 90%
TOLERANCIA_PRESSAO_FURADO 	= 0.10 	# Quantos % abaixo da pressao anterior ja devemos considerar filtro furado. Numero de 0 a 1 representando pocentagem! exemplo: 0.10 = 10%

########### ROTACAO #############
NUM_SENSORES 			= 1 	# Indica quantos objetos por volta serão detectados pelo sensor indutivo de rotacao, em unidades
ROTACAO_AVG_NOMINAL		= 1600 	# Rotacao para verificar filtro FURADO  , em RPM
ROTACAO_MAX_NOMINAL		= 2200 	# Rotacao para verificar filtro SATURADO, em RPM
TOLERANCIA_ROTACAO_AVG_NOMINAL 	= 5	# Numero de 0 a 100, indicando a porcentagem (5%)
TOLERANCIA_ROTACAO_MAX_NOMINAL 	= 5 	# Numero de 0 a 100, indicando a porcentagem (5%)

############ ALARMES ############
NUM_ALERTAS	= 6		# Numero de alertar dados EM SEQUENCIA pelo LED (acendendo e apagando)
TIME_LED_ON  	= 0.1 	# Tempo que o LED ficara ACESO quando estiver em alerta
TIME_LED_OFF 	= 0.1 	# Tempo que o LED ficara APAGADO quando estiver em alerta
TIME_LED_WAIT	= 5		# Tempo que o LED ficara EM REPOUSO, após alertar NUM_ALERTAS vezes

# Tempo de 'soneca' dos alarmes (EM SEGUNDOS)
SLEEP_FILTRO_SATURADO 	= 30 # Tempo de descanso no alarme sonoro, depois de o operador apertar o botao de SLEEP, em segundos
SLEEP_FILTRO_FURADO	= 10 # Tempo de descanso no alarme sonoro, depois de o operador apertar o botao de SLEEP, em segundos

#####################################################################
#####################################################################
################### NAO MUDE NADA DAQUI PRA BAIXO ###################
#####################################################################
#####################################################################


RESOLUTION 	= 2**10 		# 1024 valores (10 bits)
V_RESOLUTION 	= VCC/RESOLUTION 	# Resolucao em volts = VCC/(resolucao)


#################### ROTACAO ####################
###### AVG - Para medicao de FILTRO FURADO ######
ROTACAO_AVG 		= NUM_SENSORES*ROTACAO_AVG_NOMINAL # Rotacao final obtida, em RPM
TOLERANCIA_ROTACAO_AVG 	= TOLERANCIA_ROTACAO_AVG_NOMINAL/100.

##### MAX - Para medicao de FILTRO SATURADO #####
ROTACAO_MAX 		= NUM_SENSORES*ROTACAO_MAX_NOMINAL # Rotacao final obtida, em RPM
TOLERANCIA_ROTACAO_MAX 	= TOLERANCIA_ROTACAO_MAX_NOMINAL/100.


#################### PRESSAO ####################
P_MIN_SENSOR    = 0             #mm H20
P_MAX_SENSOR    = 1019.78       #mm H20
V_MIN_SENSOR    = 0.2           # Volts
V_MAX_SENSOR    = 4.7           # Volts
FUNDO_DE_ESCALA = 0.237		# Volts

VOLTS_POR_MM    = (V_MAX_SENSOR - V_MIN_SENSOR)/(P_MAX_SENSOR - P_MIN_SENSOR)
#VOLTS_POR_MM			= 0.004412716

P_MAX_IN_V 			= PRESSAO_MAXIMA*VOLTS_POR_MM # correspondente a 500mm, 2.23V # em volts - definido por experimentacao (metade da escala)

P_MAX				= (P_MAX_IN_V-FUNDO_DE_ESCALA)*(RESOLUTION-1)/VCC # pressao maxima em numeros inteiros do ADC
LIMIAR_PRESSAO_SATURADO		= TOLERANCIA_PRESSAO_SATURADO*PRESSAO_MAXIMA
