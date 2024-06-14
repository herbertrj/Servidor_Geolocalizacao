import logging
import re
import decimal
import crcmod
from typing import List
from ..position import Position
from dateutil import tz
from datetime import datetime
from binascii import unhexlify
from ..helper.binutil import BitUtil
from ..helper.hexutil import HexUtil
from typing import Tuple, Any

class MsgStatus(object):
	
	oil = None
	gps = None
	alarm = None	
	charge = None
	acc = 0
	corte = None
	bateria = -1.0
	sinal_gsm = 0
	code_alarm = 0
	bateria_94 = -1

class EE23(object):
	__protocolo = "EE23"
	__nomina_tim = 0
	__nomina_tim_host = 'ec2-3-210-126-116.compute-1.amazonaws.com'

	MSG_LOGIN = '01'
	MSG_LOCATION = '12' # # MSG_GPS_LBS_1 = '12'
	MSG_LOCATION_TR05 = '17'
	MSG_STATUS = '13'	
	MSG_HEARTBEAT = '23'	
	MSG_STRING = '15'
	MSG_ALARM = '16'
	MSG_ALARM_2 = '26'
	MSG_ADDRESS = '1A'
	MSG_COMMAND_0 = '80'
	MSG_GPS_LBS_2 = '22'
	MSG_LOGIN_GPS_LBS_STATUS = '53'
	MSG_INFORMATION = '94'
	MSG_LBS = '28'
	MSG_LBS_WIFI = '2C'

	battery_level = 0

	def __init__(self, pNominaTimEnabled = 0, pNominatimHost = 'ec2-3-210-126-116.compute-1.amazonaws.com', *args, **kwargs):
		self.logger = logging.getLogger(__name__)

		self.__nomina_tim = pNominaTimEnabled
		self.__nomina_tim_host = pNominatimHost
		self.BitUtil = BitUtil()
		self.Status = MsgStatus()

		if kwargs is not None:
			if 'protocolo' in kwargs:
				self.__protocolo = kwargs['protocolo']
				self.logger.info('PROTOCOLO: ' + self.__protocolo )
	
	def hasGPS(self, pTipo):
		"""Retorna: msg location - msg_gps_lbs2 - msg_alarm"""
		pTipo = str(pTipo)
		return bool( pTipo == self.MSG_LOCATION or pTipo == self.MSG_GPS_LBS_2 or pTipo == self.MSG_ALARM or pTipo == self.MSG_LOGIN_GPS_LBS_STATUS or pTipo == self.MSG_ALARM_2 or pTipo == self.MSG_LOCATION_TR05)

	def hasStatus(self, pTipo):
		"""Retorna: msg_status - msg_alarm"""
		pTipo = str(pTipo)
		return  bool(pTipo == str(self.MSG_STATUS) or pTipo == self.MSG_ALARM or pTipo == self.MSG_LOGIN_GPS_LBS_STATUS or pTipo == self.MSG_ALARM_2 or pTipo == self.MSG_LOCATION_TR05)

	def hasLBS(self, pTipo):
		""" Retorna: msg_location - msg_gps_lbs_2 - msg_alarm"""
		pTipo = str(pTipo)
		return bool( pTipo == str(self.MSG_LOCATION) or pTipo == self.MSG_GPS_LBS_2 or pTipo == self.MSG_ALARM or pTipo == self.MSG_LOGIN_GPS_LBS_STATUS or pTipo == self.MSG_ALARM_2 or pTipo == self.MSG_LOCATION_TR05)

	def isSupported(self, pTipo):
		"""Retorna: hasGps - hasLBS - hasStatus"""
		return self.hasGPS(pTipo) or self.hasLBS(pTipo) or self.hasStatus(pTipo)

	def readStatus(self, pInfo):
		""" Status de oleo - Gps - alarme - Gps - ignicao - carga """
		bInfo = str(self.BitUtil.hex_to_bits(pInfo))
		# " 01000110 "
		self.Status.oil = bInfo[0]
		self.Status.gps = bInfo[1]
		self.Status.alarm = bInfo[2] + bInfo[3] + bInfo[4]
		self.Status.charge = bInfo[5]
		self.Status.acc = bInfo[6]
		self.Status.corte = bInfo[7]

		self.logger.info('StatusInfo: %s', str(bInfo))  

	def genAddrees(self, pData, pType, indice):
		""" Gera o comando de endereco com data e hora, localizacao, velocidade, curso/estado e telefone"""
		self.logger.info('--- Information Adrress Tracker EE23 ---')

		# Data-Hora
		str_date,indice = self.read_date(pData,indice)
		# self.logger.info('Data : %s '%(str_date))

		# GPS Information
		value,indice = HexUtil.read_unsigned_byte(pData, indice)
		vLenght_gps = int (value[:1], 16)
		vSatellites_number = int(value[1:], 16)
		self.logger.info(f'Bit Lenght: {value[:1]} = {vLenght_gps} | quantity of satellites: {value[1:]} = {vSatellites_number}')

		# Latitude
		value,indice  = HexUtil.read_unsigned_int(pData, indice)
		vLatitude = float(int(value, 16))/60.0/30000.0
		latitude = -float(vLatitude)
		self.logger.info('latitude: %s - %s' % (value, latitude))

		# Longitude
		value,indice = HexUtil.read_unsigned_int(pData, indice)
		vLongitude = float(int(value, 16))/60.0/30000.0
		longitude = -float(vLongitude)
		self.logger.info('longitude: %s - %s' % (value, longitude))

		# Velocidade
		value,indice = HexUtil.read_unsigned_byte(pData,indice)
		vVelocidade = int(int(value, 16) * 1)
		self.logger.info('velocidade: %s - %sKm/h' % (value, vVelocidade))

		# Curso \ estado
		value,indice = HexUtil.read_unsigned_short(pData,indice)
		bStatus = self.BitUtil.hex_to_bits(value) 
		# self.logger.info('bit status %s ' %(bStatus))

		# Status
		bit5 = bStatus[-14:-13] 
		self.logger.info('Status: Real time GPS %s' %(bit5)) if bit5 == '0' else self.logger.info('differential positioning %s' %(bit5))

		bit4 = bStatus[-13:-12]
		self.logger.info('Status: GPS having been positioning %s' %(bit4)) if bit4 == '1' else self.logger.info('Status: GPS not positioning %s' %(bit4))
		
		bit3 = bStatus[-12:-11]
		self.logger.info('Status: East Longitude %s' %(bit3)) if bit3 == "1" else self.logger.info('Status: West Longitude %s' %(bit3))
	
		bit2 = bStatus[-11:-10]
		self.logger.info('Status: North Latitude %s' %(bit2)) if bit2 == "0" else self.logger.info('Status: South Latitude %s' %(bit2))

		# Curso
		vCurso = bStatus[-10:]
		dCurso = self.BitUtil.binary_to_decimal(vCurso)
		self.logger.info('Curso: %s - %sº\n' %(vCurso,dCurso))

		# Mobile Country Code (MCC)
		value,indice = HexUtil.read_unsigned_short(pData,indice)
		vMcc = int(value, 16)
		self.logger.info('mobile country code: %s - %s' % (value,vMcc))

		# Mobile Network Code (MNC)
		value,indice  = HexUtil.read_unsigned_byte(pData,indice)
		vMnc = int(value, 16)
		self.logger.info('mobile Network Code: %s - %s' %(value,vMnc))
		#position.setMNC(vMnc)

		# Location Area Code (LAC)
		value,indice = HexUtil.read_unsigned_short(pData,indice)
		vLac = int(value, 16)
		self.logger.info('location Code Area: %s - %s' % (value, vLac))
		#position.setLAC(vLac)

		# Cell ID
		qtd_bit = 4 if pType == self.MSG_LOGIN_GPS_LBS_STATUS else 3
		value,indice = HexUtil.read_unsigned_len(pData,qtd_bit,indice)
		vCell_id = int(value, 16)
		self.logger.info('cell Tower ID: %s - %s' % (value, vCell_id))
		#position.setCID(vCell_id)

		# if (vMcc is not None and vMcc != 0) and (vMnc is not None and vMnc != 0) and (vLac is not None and vLac != 0) and (vCell_id is not None and vCell_id != 0):
		# 	position.setFlgLatLongLBS(False)
		# else:
		# 	position.setFlgLatLongLBS(True)

		# Informacao do dispositivo
		indice = self.decodeTerminalInformation(pType, pData, indice)
		# indice = self.decodeStatus(pType, pData, indice)

		# Nivel de voltage de Bateria 0~6
		if pType == self.MSG_STATUS or pType ==self.MSG_LOGIN_GPS_LBS_STATUS or pType == self.MSG_ALARM or pType == self.MSG_ALARM_2 or pType == self.MSG_LOCATION_TR05:
			hBattery,indice = HexUtil.read_unsigned_byte(pData, indice)
			porcentagem,voltagem = self.voltageLevel(hBattery)
			self.Status.bateria = voltagem
		self.logger.info("BATERIA: " + str(self.Status.bateria))
	
		value,indice  = HexUtil.read_unsigned_byte(pData,indice)
		self.logger.info('byte: %s' %(value))
		
		value,indice = HexUtil.read_unsigned_short(pData, indice)
		self.logger.info('short: %s' %(value))

		indice = HexUtil.skip_bytes(3, indice)

		# # Telefone
		# value,indice = HexUtil.read_unsigned_len(pData,21,indice)
		# cell = (int(value, 16))
		# self.logger.info('Phone Number: %s - %s' %(value, cell))

		vSerial,indice = HexUtil.read_unsigned_short(pData, indice)
		#self.Status.serial = 
		self.logger.info('SERIAL: %s' % vSerial)

		return vSerial

	def decode(self, pImei, pIP, pPorta, pType, pData, indice) -> List[Position]:
		aRetorno = []

		# d = "7878"
		# aDados = [d + e for e in pData.split(d) if e]

		d = "0d0a"
		aDados = [e + d for e in pData.split(d) if e]

		for line in aDados:
			vLenPacote = int(line[4:6], 16) * 2
			self.logger.info("vLenPacote: " + line[4:6] + " - " + str(vLenPacote))
			#INDICE INTERNO DO DECODE
			dIndice = indice

			position = Position("ee23", pIP, pPorta)
			position.setComando(pType)
			position.setCodAlarme(Position.ALARM_NORMAL)
		
			if self.hasGPS(pType):
				dIndice = self.decodeGPS(position, line, pImei, pType, dIndice)
			else:
				self.logger.info("getLastLocation")

			if self.hasLBS(pType):
				dIndice = self.decodeLBS(position, line, pImei, pType, dIndice, self.hasStatus(pType))

			if pType == self.MSG_GPS_LBS_2:
				if int(vLenPacote) >= 66:
					# 00 - ACC  status
					value,dIndice = HexUtil.read_unsigned_byte(line,dIndice)
					vIgnicao = int(value, 16)
					position.setIgnicao(vIgnicao > 0)
					self.logger.info("vIgnicao: %s, %s" % (value, str(vIgnicao)))

					# 00 - Updata mode
					value,dIndice = HexUtil.read_unsigned_byte(line,dIndice)
					self.logger.info("Updata mode: %s" % (value))

				self.logger.info("dIndice: %s, %s" % (str(dIndice), str(vLenPacote)))
				
				if int(vLenPacote) == 76:
					# 00 - gps upload mode
					value,dIndice = HexUtil.read_unsigned_byte(line,dIndice)
					self.logger.info("gps upload mode: %s" % (value))

					# 00000000 milestone - odometro
					value,dIndice = HexUtil.read_unsigned_int(line,dIndice)
					vOdometro = int(value, 16)
					self.logger.info("vOdometro: %s, %s" % (value, str(vOdometro)))
					position.setOdometro(vOdometro)

			if self.hasStatus(pType):
				self.logger.info(str(pType) + " hasStatus: " + str(self.hasStatus(pType)))
				dIndice = self.decodeStatus(pType, line, dIndice)
				
				if pType == self.MSG_LOCATION_TR05:
					hMileage,indice = HexUtil.read_unsigned_len(pData,3,indice)
					mileage = int(hMileage, 16)
					position.setOdometro(mileage)
					self.logger.info("MILEAGE: " + hMileage + " - " + str(mileage))

				if pType == self.MSG_ALARM or pType == self.MSG_LOGIN_GPS_LBS_STATUS or pType == self.MSG_ALARM or pType == self.MSG_ALARM_2:
					self.logger.info("ALARM: " + self.Status.code_alarm)
					self.type_alarm(position)

			value,dIndice = HexUtil.read_unsigned_short(line, dIndice)
			vSerial = int(value, 16)
			self.logger.info("Serial: %s, %s" % (value, str(vSerial)))

			position.setSinalGSM(self.Status.sinal_gsm)
			position.setSinalGSMValor(self.Status.valor_sinal_gsm)
			position.setSerialNumber(value)
			position.setMensagemId(vSerial)

			if pType != self.MSG_GPS_LBS_2: position.setIgnicao(self.Status.acc)
			# position.setBateriaExterna(self.Status.bateria)
			position.setBateriaExterna(self.Status.bateria_94 if self.Status.bateria_94 != -1 else self.Status.bateria)

			aRetorno.append(position)

		return aRetorno
	
	def decodeTerminalInformation(self, pType, pData, indice):
		# Informacao do dispositivo
		value,indice = HexUtil.read_unsigned_byte(pData, indice)
		self.readStatus(value)

		return indice
	

	def decodeInformation(self, pType, pdata, indice):
		""" Protocolo pode ser customizado com varias informacoes"""
		hInformation, indice = HexUtil.read_unsigned_byte(pdata, indice)
		self.logger.info('Type information: %s' %hInformation)
		
		if hInformation == '00':
			hBattery, indice = HexUtil.read_unsigned_short(pdata, indice)
			self.Status.bateria_94 = int(hBattery, 16)

			bateria_formatada = "{:.2f}v".format(self.Status.bateria_94) 
			self.logger.info("External Power Voltage: " + bateria_formatada)
		else:
			self.logger.info('Tratar')	
		
		return indice

	def decodeStatus(self, pType, pData, indice):
		""" Gera o status do dispositivo - voltagem da bateria - sinal Gsm - tipo de alarme - serial """
		self.logger.info('--- status Information Tracker EE23 ---')   
		
		# Informacao do dispositivo
		value,indice = HexUtil.read_unsigned_byte(pData, indice)
		self.readStatus(value)
		
		# Nivel de voltage de Bateria 0~6
		if pType == self.MSG_STATUS or pType ==self.MSG_LOGIN_GPS_LBS_STATUS or pType == self.MSG_ALARM or pType == self.MSG_ALARM_2 or pType == self.MSG_LOCATION_TR05:
			hBattery,indice = HexUtil.read_unsigned_byte(pData, indice)
			# self.logger.info("TESTE BATERIA %s" % hBattery)
			porcentagem,voltagem = self.voltageLevel(hBattery)
			self.Status.bateria = voltagem
			self.logger.info("BATERIA %: " + hBattery + " - " + str(self.Status.bateria))
		else:
			hBattery,indice = HexUtil.read_unsigned_short(pData, indice)
			# self.logger.info("TESTE CHEGADA BATERIA: %s" % hBattery)
			self.Status.bateria = int(hBattery, 16)
			self.logger.info("BATERIA: " + hBattery + " - " + str(self.Status.bateria))
		
		# Sinal Gsm
		gsm,indice = HexUtil.read_unsigned_byte(pData, indice)
		self.Status.valor_sinal_gsm = gsm
		if str(pType) == str(self.MSG_LOCATION_TR05) or self.__protocolo.upper() == 'tr05'.upper():
			self.Status.sinal_gsm = int(gsm, 16)
			self.logger.info("SINAL_GSM: " + gsm + " - " + str(self.Status.sinal_gsm))
		else:
			self.Status.sinal_gsm = self.gsmSinal(gsm) 
			self.logger.info("INTENSIDADE_SINAL_GSM: " + gsm + " - " + str(self.Status.sinal_gsm))
			
		if (pType == self.MSG_HEARTBEAT and self.__protocolo.upper() == 'tr05'.upper()) or (pType == self.MSG_LOCATION_TR05 and self.__protocolo.upper() == 'tr05'.upper()):
			hExternalVol,indice = HexUtil.read_unsigned_byte(pData, indice)
			self.Status.bateria = int(hExternalVol, 16) * 100
			self.logger.info("BATERIA: " + hExternalVol + " - " + str(self.Status.bateria))
		
		if self.__protocolo.upper() != 'tr05'.upper() or (pType == self.MSG_ALARM and self.__protocolo.upper() == 'tr05'.upper()):
			# Type Alarme/ language 
			hType_alarme,indice = HexUtil.read_unsigned_byte(pData, indice)	
			self.Status.code_alarm = hType_alarme# self.type_alarm(hType_alarme)

		vIdioma, indice = HexUtil.read_unsigned_byte(pData, indice)
		
		# # Serie
		# vSerial,indice = HexUtil.read_unsigned_short(pData, indice)
		# #self.Status.serial = 
		# self.logger.info('SERIAL: %s' % vSerial)

		return indice
		
	def type_alarm(self, position:Position):
		""" tipo de alarme - sos - normal - shock alarm """
		if self.Status.code_alarm == '00':
			self.logger.info(f'Alarm Type: Normal')
			position.setCodAlarme(Position.ALARM_NORMAL)

		elif self.Status.code_alarm == '01':
			self.logger.info(f'Alarm Type: SOS')
			position.setCodAlarme(Position.ALARM_SOS)

		elif self.Status.code_alarm == '02':
			self.logger.info(f'Alarm Type: Power Cut Alarm')
			position.setCodAlarme(Position.ALARM_POWER_CUT)

		elif self.Status.code_alarm == '03':
			self.logger.info(f'Alarm Type: Shock Alarm')
			position.setCodAlarme(Position.ALARM_SHOCK)

		elif self.Status.code_alarm == '04':
			self.logger.info(f'Alarm Type: Fence In Alarm')
			position.setCodAlarme(Position.ALARM_GEOFENCE_ENTER)

		elif self.Status.code_alarm == '05':
			self.logger.info(f'Alarm Type: Fence Out Alarm')     
			position.setCodAlarme(Position.ALARM_GEOFENCE_EXIT)

		elif self.Status.code_alarm == '06':
			self.logger.info('Alarm Type: Over speed alarm')
			position.setCodAlarme(Position.ALARM_OVERSPEED)
				
		elif self.Status.code_alarm == '09':
			self.logger.info('Alarm Type: Displacement alarm')
			position.setCodAlarme(Position.ALARM_MOVEMENT)
				
		elif self.Status.code_alarm == '0A':
			self.logger.info('Alarm Type: Enter GPS blind zone alarm')
			position.setCodAlarme(Position.ALARM_GEOFENCE_ENTER_1)
			
		elif self.Status.code_alarm == '0B':
			self.logger.info('Alarm Type: Exit of GPS blind zone alarm')
			position.setCodAlarme(Position.ALARM_GEOFENCE_EXIT_1)
				
		elif self.Status.code_alarm == '0C':
			self.logger.info('Alarm Type: power on alarm')
			position.setCodAlarme(Position.ALARM_POWER_ON)		
		
		elif self.Status.code_alarm == '0D':
			self.logger.info('Alarm GPS first fix notice')
			position.setCodAlarme(Position.ALARM_GPS_FIRST)

		elif self.Status.code_alarm == '0E':
			self.logger.info('Alarm Type: Low battery alarm')
			position.setCodAlarme(Position.ALARM_LOW_BATTERY)
					
		elif self.Status.code_alarm == '0F':
			self.logger.info('Alarm Type: Low battery protection alarm')
			position.setCodAlarme(Position.ALARM_LOW_BATTERY)

		elif self.Status.code_alarm == '10':
			self.logger.info('Alarm SIM change notice')
			position.setCodAlarme(Position.ALARM_REMOVING)

		elif self.Status.code_alarm == '11':
			self.logger.info('Alarm Type: Power low-off alarm')
			position.setCodAlarme(Position.ALARM_LOW_POWER)
		
		elif self.Status.code_alarm == '12':
			self.logger.info('Alarm type: airplane mode alarm')
			position.setCodAlarme(Position.ALARM_AIRPLANE)
			
		elif self.Status.code_alarm == '13':
			self.logger.info('Alarm Type: Disassemble alarm')
			# position.setCodAlarme(Position.ALARM_DISASSEMBLE) - incluir no position

		elif self.Status.code_alarm == '14':
			self.logger.info('Alarm Type: door alarm')
			position.setCodAlarme(Position.ALARM_DOOR)
	
		elif self.Status.code_alarm == '15':
			self.logger.info('Alarm Type: shutdown')
			# position.setCodAlarme(Position.ALARM_POWER_OFF)
			position.setCodAlarme(Position.ALARM_NORMAL)

		elif self.Status.code_alarm == 'ff':
			self.logger.info(f'Alarm Type: Acc OFF')     
			position.setCodAlarme(Position.ALARM_ACC_OFF)

		elif self.Status.code_alarm == 'fe':
			self.logger.info(f'Alarm Type: Acc ON')     
			position.setCodAlarme(Position.ALARM_ACC_ON)
	
	def gsmSinal(self,pSinal):
		"""Intensidade do sinal """ 
		sinal = ""
		if pSinal == '00':
			self.logger.info(f'Sinal Gsm {pSinal} - 0% no signal')
			sinal = 0 
		elif pSinal == '01':
			self.logger.info(f'{pSinal} Sinal Gsm: 25% extremely weak signal')
			sinal =  25	
		elif pSinal == '02': 
			self.logger.info(f'{pSinal} Sinal Gsml: 50% very weak signal')
			sinal = 50
		elif pSinal == '03':
			self.logger.info(f'{pSinal} Sinal Gsm: 75% good signal')
			sinal = 75
		elif pSinal == '04':
			self.logger.info(f'{pSinal} Sinal Gsm - 100% strong signal')  
			sinal = 100
		
		return sinal
	
	def voltageLevel(self,pvol):
		"""voltage Level e voltagem de bateria"""

		nivel_atual = 6 #str(pvol)		
		# self.logger.info('TESTE voltagem %s' %nivel_atual)
		if pvol == '00':			
			self.logger.info('%s Battery: No power - off:', str(pvol))
			nivel_atual = 0
		elif pvol == '01':
			self.logger.info('%s Battery: Extremely Low Battery "not enough for calling or sending text messages, etc.")', str(pvol))
			nivel_atual = 1				
		elif pvol == '02':
			self.logger.info('%s Battery: Very Low Battery "Low Battery Alarm" ', str(pvol))
			nivel_atual = 2
		elif pvol == '03':
			self.logger.info('%s Battery: Lower power but can work normally',str(pvol))
			nivel_atual = 3
		elif pvol == '04':
			self.logger.info('%s Battery: Medium ',str(pvol))
			nivel_atual = 4
		elif pvol == '05':
			self.logger.info('%s Battery: High  ',str(pvol))
			nivel_atual = 5
		elif pvol == '06':
			self.logger.info('%s Battery: Very High ',str(pvol))
			nivel_atual = 6

		porcentagem = nivel_atual / 6 * 100
		voltagem = (1200 * porcentagem)/100
		
		self.logger.info(f'voltage level {pvol}: {porcentagem}%, {voltagem}v')

		return int(porcentagem), int(voltagem)
	
	def read_date(self, b, i):
		""" Data, hora e conversao time zone """

		from_zone = tz.tzutc()
		to_zone = tz.tzlocal()
		# self.logger.info(b[i:])

		vAno,i = HexUtil.read_unsigned_byte(b,i)
		vAno = int(vAno, 16)
		# self.logger.info('value: %s', value)

		vMes,i = HexUtil.read_unsigned_byte(b,i)
		vMes = int(vMes, 16)

		vDia,i = HexUtil.read_unsigned_byte(b,i)
		vDia = int(vDia, 16)

		vHora,i = HexUtil.read_unsigned_byte(b,i)
		vHora = int(vHora, 16)

		vMinuto,i = HexUtil.read_unsigned_byte(b,i)
		vMinuto = int(vMinuto, 16)

		vSegundo,i = HexUtil.read_unsigned_byte(b,i)
		vSegundo = int(vSegundo, 16)

		str_date = "%s-%s-%s %s:%s:%s" % (vAno, vMes, vDia, vHora, vMinuto, vSegundo)
		# self.logger.info('str_date: %s', str_date)

		if (str_date == "00-00-00 00:00:00"):
			return -1, i

		try:
			utc_date = datetime.strptime(str_date, '%y-%m-%d %H:%M:%S')
		except Exception as err:
			self.logger.error("utc_date: " +  str(b) + " - " + str(err))
			return -2, i
		
		utc_date = utc_date.replace(tzinfo=from_zone)

		# Convert time zone
		try:
			str_date = utc_date.astimezone(to_zone).strftime('%d-%m-%Y %H:%M:%S')
		except Exception as ex:
			self.logger.error("str_date: %s", format(ex))
			return -3, i

		self.logger.info('str_date: %s',  str(str_date))
		
		return str_date, i

	def decodeGPS(self, position: Position, pData, pImei, pType, indice) -> int:
		position.setComando(pType)	
		position.setUniqueId(pImei)

		# Data e hora 	
		str_date,indice = self.read_date(pData,indice)
		position.setDispositivoDataHora(str_date)

		# Quantify of Gps Information satellites 
		value,indice = HexUtil.read_unsigned_byte(pData, indice)
		vLenght_gps = int (value[:1], 16)
		vSatellites_number = int(value[1:], 16)
		self.logger.info(f'Bit Lenght: {value[:1]} = {vLenght_gps} | quantity of satellites: {value[1:]} = {vSatellites_number}')
		position.setQtdSatelites(vSatellites_number)

		# Latitude
		value,indice  = HexUtil.read_unsigned_int(pData, indice)
		vLatitude = float(int(value, 16))/60.0/30000.0
		latitude = -float(vLatitude)
		self.logger.info('latitude: %s - %s' % (value, latitude))
		position.setLatitude(latitude)
		
		# Longitude
		value,indice = HexUtil.read_unsigned_int(pData, indice)
		vLongitude = float(int(value, 16))/60.0/30000.0
		longitude = -float(vLongitude)
		self.logger.info('longitude: %s - %s' % (value, longitude))
		position.setLongitude(longitude)

		# Altitude
		if pType == self.MSG_LOGIN_GPS_LBS_STATUS:
			hAltitude,indice = HexUtil.read_unsigned_short(pData, indice)
			vAltitude = int(hAltitude, 16)
			self.logger.info("Altitude %s - %i" %(hAltitude, vAltitude)) 

		# Velocidade
		value,indice = HexUtil.read_unsigned_byte(pData,indice)
		vVelocidade = int(value, 16)
		self.logger.info('Speed: %s - %sKm/h' % (value, vVelocidade))
		position.setVelocidade(vVelocidade)

		# Curso \ estado
		value,indice = HexUtil.read_unsigned_short(pData,indice)
		bStatus = self.BitUtil.hex_to_bits(value) 
		self.logger.info('bit status %s ' %(bStatus))

		bit5 = bStatus[2:3] 
		self.logger.info('Status: Real time GPS %s ' %(bit5)) if bit5 == '0' else self.logger.info('differential positioning %s '%(bit5))

		bit4 = bStatus[3:4]
		self.logger.info('Status: GPS having been positioning %s '%(bit4)) if bit4 == '1' else self.logger.info('Status: GPS not positioning  %s ' %(bit4))
		position.setGPSValido(True) if bit4 == '1' else position.setGPSValido(False)
		position.setTipoLocalizacao(1 if bit4 == '1' else 2)
		position.setFlgLatLongLBS(True)

		bit3 = bStatus[4:5]	
		self.logger.info('Status: East Longitude %s ' %(bit3)) if (bit3 == "1") else self.logger.info('Status: West Longitude %s ' %(bit3))

		bit2 = bStatus[5:6]	
		self.logger.info('Status: North Latitude %s ' %(bit2)) if (bit2 == "0") else self.logger.info('Status: South Latitude %s ' %(bit2))

		# Curso
		vCurso = bStatus[7:]
		dCurso = self.BitUtil.binary_to_decimal(vCurso)
		self.logger.info('Curso: %s - %sº' %(vCurso,dCurso))
		position.setCurso(dCurso)

		return indice
		
	def decodeLBS(self, position: Position, pData, pImei, pType, indice, hasLength: bool) -> int:
		""" ********** LBS INFORMATION ************ """		
		self.logger.info('-- packet location lbs information --')
		length = 0
		if hasLength and pType not in (self.MSG_LOGIN_GPS_LBS_STATUS, self.MSG_LOCATION_TR05):
			value,indice  = HexUtil.read_unsigned_byte(pData,indice)
			length = int(value, 16)
		self.logger.info("decodeLBS length: " + str(length))

		# Mobile Country Code (MCC)
		value,indice = HexUtil.read_unsigned_short(pData,indice)
		vMcc = int(value, 16)
		self.logger.info('mobile country code: %s - %s' % (value,vMcc))
		position.setMCC(vMcc)

		# Mobile Network Code (MNC)
		value,indice  = HexUtil.read_unsigned_byte(pData,indice)
		vMnc = int(value, 16)
		self.logger.info('mobile Network Code: %s - %s' %(value,vMnc))
		position.setMNC(vMnc)

		# Location Area Code (LAC)
		value,indice = HexUtil.read_unsigned_short(pData,indice)
		vLac = int(value, 16)
		self.logger.info('location Code Area: %s - %s' % (value, vLac))
		position.setLAC(vLac)

		# Cell ID
		qtd_bit = 4 if pType == self.MSG_LOGIN_GPS_LBS_STATUS else 3
		value,indice = HexUtil.read_unsigned_len(pData,qtd_bit,indice)
		
		vCell_id = int(value, 16)
		self.logger.info('cell Tower ID: %s - %s' % (value, vCell_id))
		position.setCID(vCell_id)

		if (vMcc is not None and vMcc != 0) and (vMnc is not None and vMnc != 0) and (vLac is not None and vLac != 0) and (vCell_id is not None and vCell_id != 0):
			position.setFlgLatLongLBS(False)
		else:
			position.setFlgLatLongLBS(True)

		return indice

	def package_lbs(self,pData,indice):
		""" Esse Pacote de LBS é Enviado separado do LBS de GPS e Alarme"""
		self.logger.info('*** Pacote LBS somente ***')
		# Data e hora 	
		str_date,indice = self.read_date(pData,indice)
		
		# Mobile Country Code (MCC)
		value,indice = HexUtil.read_unsigned_short(pData,indice)
		vMcc1 = int(value, 16)
		self.logger.info('Mobile country code : %s - %s' % (value,vMcc1))
		# MNC
		value,indice  = HexUtil.read_unsigned_byte(pData,indice)
		vMnc1 = int(value, 16)
		self.logger.info('mobile Network code : %s - %s' %(value,vMnc1))
		# Location Area Code (LAC) #1
		value,indice = HexUtil.read_unsigned_short(pData,indice)
		vLac1 = int(value, 16)
		self.logger.info('location Code Area: %s - %s' % (value, vLac1))
		# CELL ID #1
		value, indice = HexUtil.read_unsigned_len(pData,3,indice)
		vCell_id1 = int(value, 16)
		self.logger.info('cell Tower ID: %s - %s' % (value, vCell_id1))
		# RSSi
		value, indice = HexUtil.read_unsigned_byte(pData, indice)
		vRssi1 = int(value, 16)
		self.logger.info('RSSI: %s -', vRssi1)
		# Location Area Code (LAC) #1
		value,indice = HexUtil.read_unsigned_short(pData,indice)
		vLac2 = int(value, 16)
		self.logger.info('location Code Area: %s - %s' % (value, vLac2))
		# Cell Id 1
		value, indice = HexUtil.read_unsigned_len(pData,3,indice)
		vCell_id2 = int(value, 16)
		self.logger.info('cell Tower ID: %s - %s' % (value, vCell_id2))
		# # RSSi 1
		value, indice = HexUtil.read_unsigned_byte(pData, indice)
		vRssi2 = int(value, 16)
		self.logger.info('RSSI: %s -', vRssi2)
		# Location Area Code (LAC) #2
		value,indice = HexUtil.read_unsigned_short(pData,indice)
		vLac3 = int(value, 16)
		self.logger.info('location Code Area: %s - %s' % (value, vLac3))
		# Cell Id #2
		value, indice = HexUtil.read_unsigned_len(pData,3,indice)
		vCell_id3 = int(value, 16)
		self.logger.info('cell Tower ID: %s - %s' % (value, vCell_id3))
		
		# RSSi #2
		value, indice = HexUtil.read_unsigned_byte(pData, indice)
		vRssi3 = int(value, 16)
		self.logger.info('RSSI %s:', vRssi3)
		# Location Area Code (LAC) #3
		value,indice = HexUtil.read_unsigned_short(pData,indice)
		vLac4 = int(value, 16)
		self.logger.info('location Code Area: %s - %s' % (value, vLac4))
		value, indice = HexUtil.read_unsigned_len(pData,3,indice)
		vCell_id4 = int(value, 16)
		self.logger.info('cell Tower ID: %s - %s' % (value, vCell_id4))
		#RSSi # 3
		value, indice = HexUtil.read_unsigned_byte(pData, indice)
		vRssi4 = int(value, 16)
		self.logger.info('RSSI %s:', vRssi4)
		# lac #4
		value,indice = HexUtil.read_unsigned_short(pData,indice)
		vLac5 = int(value, 16)
		self.logger.info('location Code Area: %s - %s' % (value, vLac5))
		# cell id 4
		value, indice = HexUtil.read_unsigned_len(pData,3,indice)
		vCell_id5 = int(value, 16)
		self.logger.info('cell Tower ID: %s - %s' % (value, vCell_id5))
		# RSSi 4
		value, indice = HexUtil.read_unsigned_byte(pData, indice)
		vRssi5 = int(value, 16)
		self.logger.info('RSSI %s:', vRssi5)
		value,indice = HexUtil.read_unsigned_short(pData,indice)
		vLac6 = int(value, 16)
		self.logger.info('location Code Area: %s - %s' % (value, vLac6))
		value, indice = HexUtil.read_unsigned_len(pData,3,indice)
		vCell_id6 = int(value, 16)
		self.logger.info('cell Tower ID: %s - %s' % (value, vCell_id6))
		value, indice = HexUtil.read_unsigned_byte(pData, indice)
		vRssi6 = int(value, 16)
		self.logger.info('RSSI %s:', vRssi6)
		value,indice = HexUtil.read_unsigned_short(pData,indice)
		vLac7 = int(value, 16)
		self.logger.info('location Code Area: %s - %s' % (value, vLac7))
		value, indice = HexUtil.read_unsigned_len(pData,3,indice)
		vCell_id7 = int(value, 16)
		self.logger.info('cell Tower ID: %s - %s' % (value, vCell_id7))
		value, indice = HexUtil.read_unsigned_byte(pData, indice)
		vRssi7 = int(value, 16)
		self.logger.info('RSSI %s:', vRssi7)
		# time advance - Time of signal from Mobile Station to Location base supposed the distance is 0
		value, indice = HexUtil.read_unsigned_byte(pData, indice)
		timing_advance = int(value, 16)
		self.logger.info('timing_advance %s:', timing_advance)
		# vLanguage
		value, indice = HexUtil.read_unsigned_short(pData,indice)
		vLanguage  = int(value, 16)
		self.logger.info('Language: %s', vLanguage)
		value, indice = HexUtil.read_unsigned_short(pData,indice)
		vSerial = int(value,16)
		self.logger.info('Serial Number: %s', vSerial)

	def genCommand(self, pTipoCmd, pImei, pContent, pSerialNumber):
		crc32_func = crcmod.predefined.mkCrcFun("x-25")#("crc-ccitt-false")

		if (pTipoCmd.upper() == self.MSG_LOGIN):
			hex_string = "0501" + str(pSerialNumber)

		elif(pTipoCmd.upper() == self.MSG_ALARM ) or (pTipoCmd.upper() == self.MSG_ALARM_2):  
			hex_string = "05" + str(pTipoCmd) + str(pSerialNumber)	
		
		elif (pTipoCmd.upper() == self.MSG_STATUS) or (pTipoCmd.upper() == self.MSG_HEARTBEAT) or (pTipoCmd.upper() == self.MSG_LOGIN_GPS_LBS_STATUS):
			hex_string = "05" + str(pTipoCmd) + str(pSerialNumber)
		
		elif(pTipoCmd.upper()== self.MSG_ADDRESS): 
			# Agreement No.	97   
			# ServerFlagBit 00000001
			# LenPacket = Protocol Number + Information Content + Information Serial Number + Error Check (1+1+4+N+2+2)
			# LenCommand = Server Flag Bit + Length of Command Content
			Language = "0001"
			ServerFlagBit = "00000001" #AEEI
			vAddress = '41444452455353'
			vPhoneNumber = '000000000000000000000000000000000000000000'
			vLenPacket = "{:02x}".format(1 + 1 + 4 + int(len(vAddress)) + 2 + int(len(pContent)/2) + 2 + int(len(vPhoneNumber)) + 2) # + int(len(Language)/2))
			vLenCommand = "{:02x}".format(4 + int(len(pContent)/2)) #0C/12, 0F/15, 16/10, 19/25

			hex_string = vLenPacket + "97" + vLenCommand + ServerFlagBit + vAddress + '2626' + pContent + '2626' + vPhoneNumber + '2323' + str(pSerialNumber) 
			# Verificar se retorno do comando esta correto pagina 35 6.7.2.2

		# elif (pTipoCmd.upper()== self.MSG_LOCATION_TR05) or (pTipoCmd.upper() == self.MSG_IMSI):
		#     hex_string = "05" + str(pTipoCmd) + str(pSerialNumber)
										
		elif (pTipoCmd.upper()== self.MSG_LOCATION) or (pTipoCmd.upper() == self.MSG_GPS_LBS_2):
			hex_string = "05" + str(pTipoCmd) + str(pSerialNumber)
		
		elif (pTipoCmd.upper() == self.MSG_COMMAND_0):
			# Agreement No.			80
			# Instruction length 	0F
			# Server flag			0001A958
			# Instruction content 	
			# Language				0001
			
			# LenPacket = Protocol Number + Information Content + Information Serial Number + Error Check (1+1+4+N+2+2)
			# LenCommand = Server Flag Bit + Length of Command Content
			# v_sCRC = “Packet Length” and “Information Serial Number”		
			###########################
			#BLOQUEAR
			#strEnviar = '787815800F000000014459442C30303030303023000189A70D0A'
			#			  78781580 0F 0001A958 4459442C30303030303023 00A0 DCF1 0D0A
			# pContent = '4459442c30303030303023' #= DYD,000000#
														
			#DESBLOQUEAR
			#strEnviar = '787816801000000001484659442C30303030303023000128AF0D0A'	
		
			ServerFlagBit = "0001A958" #AEEI
			# pContent = '484659442c30303030303023' = HFYD,000000#
			Language = "0001"
			vLenCommand = "{:02x}".format(4 + int(len(pContent)/2)) #0C/12, 0F/15, 16/10, 19/25
			InfSerialNumber = pSerialNumber  + hex(int(pSerialNumber,16) + 1).lstrip("0x")
			vLenPacket = "{:02x}".format(1 + 1 + 4 + int(len(pContent)/2) + 2 + 2) # + int(len(Language)/2))
						
			hex_string = vLenPacket + self.MSG_COMMAND_0 + vLenCommand + ServerFlagBit + pContent + InfSerialNumber[-4:]
			
			##7878 16 80 100001A963 484659442C30303030303023 00A0 7BDC 0D0A
			##7878 16 80 100001A958 484659442C30303030303023 0001 A96E 0D0A
		
		s = unhexlify(hex_string)
		v_sCRC = str(hex(crc32_func(s))).lstrip("0x") 
		if len(v_sCRC) == 3:
			v_sCRC = "0" + v_sCRC
		
		hex_string = "7878" + hex_string + v_sCRC + "0d0a"

		self.logger.info('hex_string %s', hex_string)
		return hex_string.upper()
