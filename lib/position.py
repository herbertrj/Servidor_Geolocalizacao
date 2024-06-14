import decimal
import json
import logging
from datetime import datetime
# import requests
from typing import Type

from dateutil import tz


class Position(object):
	__protocolo = None
	__pacote = ""
	__gps_valido = False
	__identificacao = None
	__data_dispositivo = None
	__prioridade = None
	__longitude = 0.0
	__latitude = 0.0
	__altitude = 0.0
	__curso = 0
	__qtd_satelites = 0
	__velocidade = 0.0
	__ignicao = 0
	__movimento = 0
	__sinal_gsm = 0
	__sinal_gps = 0
	__tipo_rede = 'NA'
	__bateria_externa = -1.0
	__bateria_interna = 0.0
	__acelerometro = 0
	__jamming_sinal = 0
	__tp_relogio = "G"
	__bloqueio = 0
	__clonado = 0
	__panico = 0
	__painel = 0
	__odometro = 0
	__horimetro = 0
	__temperatura = 0
	__valid_status = True
	__other = "{}"
	__ip = ""
	__porta = 0
	__id_rastreador = 0
	__id_veiculo = 0
	__id_usuario_adm = 0
	__id_localizacao = None
	__id_cliente = 0
	__placa = None
	__address = 0
	__id_veiculo_rastreador = 0
	__input2 = ""
	__input3 = ""
	__output2 = ""
	__output3 = ""
	__comando = ""
	__sleep_mode = 0
	__msg_id = "PO"
	__code_alarm = "normal"
	__ignicao_valida = True
	__mcc = ""
	__mnc = ""
	__lac = ""
	__cid = ""
	__serial = ""
	__data_dispositivo_ultima_comunicacao = None
	__tipo_location = 0
	__lbs_lat_long = False
	__reboque_ativo = 0
	__bateria_backup_ativo = 0
	__sinal_gsm_valor = 0

	ALARM_NORMAL = "normal"
	ALARM_GENERAL = "general"
	ALARM_SOS = "sos"
	ALARM_VIBRATION = "vibration"
	ALARM_MOVEMENT = "movement"
	ALARM_LOW_SPEED = "lowspeed"
	ALARM_OVERSPEED = "overspeed"
	ALARM_FALL_DOWN = "fallDown"
	ALARM_LOW_POWER = "lowPower"
	ALARM_LOW_BATTERY = "lowBattery"
	ALARM_FAULT = "fault"
	ALARM_ACC_OFF = "accOff"
	ALARM_ACC_ON = "accOn"
	ALARM_POWER_OFF = "powerOff"
	ALARM_POWER_ON = "powerOn"
	ALARM_DOOR = "door"
	ALARM_LOCK = "lock"
	ALARM_UNLOCK = "unlock"
	ALARM_GEOFENCE = "geofence"
	ALARM_GEOFENCE_ENTER = "geofenceEnter"
	ALARM_GEOFENCE_EXIT = "geofenceExit"
	ALARM_GPS_ANTENNA_CUT = "gpsAntennaCut"
	ALARM_ACCIDENT = "accident"
	ALARM_TOW = "tow"
	ALARM_IDLE = "idle"
	ALARM_HIGH_RPM = "highRpm"
	ALARM_ACCELERATION = "hardAcceleration"
	ALARM_BRAKING = "hardBraking"
	ALARM_CORNERING = "hardCornering"
	ALARM_LANE_CHANGE = "laneChange"
	ALARM_FATIGUE_DRIVING = "fatigueDriving"
	ALARM_POWER_CUT = "powerCut"
	ALARM_POWER_SAVING_MODE = 'powerSavingMode'
	ALARM_POWER_RESTORED = "powerRestored"
	ALARM_JAMMING = "jamming"
	ALARM_TEMPERATURE = "temperature"
	ALARM_PARKING = "parking"
	ALARM_BONNET = "bonnet"
	ALARM_FOOT_BRAKE = "footBrake"
	ALARM_FUEL_LEAK = "fuelLeak"
	ALARM_TAMPERING = "tampering"
	ALARM_REMOVING = "removing"
	ALARM_SHOCK = "shock"
	ALARM_SENSOR_LUMINOSIDADE = "sensorLuminosidade"
	ALARM_MALFUNCTION = 'GPSMalFunction'
	ALARM_CAR_DRIVING = 'carIsDriving'
	# ALARM_EXTERNAL_POWER_CUT = "againstExternalPowerCut"
	# ALARM_CUT_OFF_ENGINE = 'Cut off engine power (outp ut 1 on)'
	ALARM_SAVING_MODE = 'powerSavingMode'
	# ALARM_ACC = 'ACC (ignition) on'
	ALARM_GEOFENCE_ENTER_1 = 'EnterGeofence1' 	
	ALARM_GEOFENCE_EXIT_1 = 'ExitGeofence1'
	ALARM_GEOFENCE_ENTER_2 = 'EnterGeofence2'
	ALARM_GEOFENCE_EXIT_2 = 'ExitGeofence2'
	ALARM_GEOFENCE_ENTER_3 = 'EnterGeofence3'
	ALARM_GEOFENCE_EXIT_3 = 'ExitGeofence3'
	ALARM_ADC_ALARM = 'ADC'
	ALARM_HARSH_ACCELERATION ='harshAcceleration'
	ALARM_HARSH_BRAKE = 'harshBrake'
	ALARM_URGENT_BRAKE = 'urgentBrake'
	ALARM_OUTPUT = 'output2On'
	ALARM_ALARM_OTHER_CAR = 'otherCarAntiTheftDevice'
	ALARM_AIRPLANE = 'AirplaneMode'
	ALARM_SIM_CHANGE ='SimChange'
	ALARM_GPS_FIRST = 'GPSFirstFixNotice'
	ALARM_CONTROL_SOUND = 'SoundControl'
	ALARM_BASE_STATION = 'PseudoBaseStation'
	ALARM_OPEN_COVER = 'OpenCover'
	ALARM_PULL = 'Pull'
	ALARM_INSERT_BUTTON = 'InsertButton' # ST300
	ALARM_REMOVED_BUTTON = 'RemovedButton' # ST300
	ALARM_DEAD_CENTER ='DeadCenter' # ST300
	ALARM_RPM_CALIBRATIOIN_AUTOMATIC = 'RpmCalibrationAutomatic' # ST300
	ALARM_CONNECTED_MAIN_POWER = 'ConnectedMainPowerSource' # ST300 
	ALARM_DISCONNECTED_BATTERY_BACKUP = 'DisconnectedBack-upBattery' # ST300


	def __init__(self, pProtocolo, *args, **kwargs):
		self.logger = logging.getLogger(__name__)
		
		self.__protocolo = pProtocolo
		self.__ip = args[0] if len(args) >= 1 else 0
		self.__porta = args[1] if len(args) >= 1 else 0

	def setPacote(self, pPacote):
		"""SET Protocol Version"""
		self.__pacote = pPacote

	def getPacote(self, pPacote):
		return self.__pacote

	def setProtocol(self, pProtocolo):
		"""SET Protocol"""
		self.__protocolo = pProtocolo

	def getProtocol(self):
		return self.__protocolo
		
	def setUniqueId(self, pUniqueId):
		self.__identificacao = pUniqueId

	def getUniqueId(self):
		return self.__identificacao
	
	def setSerialNumber(self, pSerial): 
		self.__serial = pSerial
	
	def getSerialNumber(self):
		return self.__serial
	
	def setGPSValido(self, pGPSValido):
		self.__gps_valido = int(pGPSValido)
	
	def getGPSValido(self):
		"""
		0: LBS
		1: GPRS
		"""
		return self.__gps_valido; 

	def setDispositivoDataHora(self, pDataHora):
		""" SET string format '%d-%m-%Y %H:%M:%S' """
		self.__data_dispositivo = pDataHora

	def getDispositivoDataHora(self):
		""" GET string format '%d-%m-%Y %H:%M:%S' """
		return self.__data_dispositivo

	def setPrioridade(self, pPrioridade):
		self.__prioridade = pPrioridade
	
	def getPrioridade(self):
		return self.__prioridade

	def setLongitude(self, pLongitude):
		if (decimal.Decimal(pLongitude) >= -180.0 and decimal.Decimal(pLongitude) <= 180.0):
			self.__longitude = pLongitude
	
	def getLongitude(self):
		return self.__longitude

	def setLatitude(self, pLatitude):
		if (decimal.Decimal(pLatitude) >= -90.0 and decimal.Decimal(pLatitude) <= 90.0):
			self.__latitude = pLatitude
	
	def getLatitude(self):
		return self.__latitude

	def setAltitude(self, pAltitude):
		self.__altitude = decimal.Decimal(pAltitude)
	
	def getAltitude(self):
		return self.__altitude

	def setCurso(self, pCurso):
		"""valor inteiro de 0-360 graus """
		if (decimal.Decimal(pCurso) >= 0 and decimal.Decimal(pCurso) <= 360):
			self.__curso = pCurso
	
	def getCurso(self):
		"""valor inteiro de 0-360 graus """
		return self.__curso

	def setQtdSatelites(self, pQuantidade):
		"""quantidade de satelites em uso """
		self.__qtd_satelites = pQuantidade
	
	def getQtdSatelites(self):
		"""quantidade de satelites em uso """
		return self.__qtd_satelites

	def setVelocidade(self, pVelocidade):
		self.__velocidade = decimal.Decimal(pVelocidade)
	
	def getVelocidade(self):
		return self.__velocidade

	def setIgnicao(self, pIgnicao):
		try:
			self.__ignicao = int(pIgnicao)
		except Exception as err:
			# self.__ignicao = 0
			self.logger.error("setIgnicao: " +  str(pIgnicao) + " - " + str(err))
	
	def getIgnicao(self):
		return self.__ignicao

	def setMovimento(self, pMovimento):
		self.__movimento = pMovimento
	
	def getMovimento(self):
		return self.__movimento

	def setOther(self, pId, pValor):
		y = json.loads(self.__other)
		y[pId] = pValor

		self.__other = json.dumps(y)
	
	def getOther(self):
		return self.__other

	def setSinalGSM(self, pSinalGSM):
		self.__sinal_gsm = pSinalGSM

	def getSinalGSM(self):
		return self.__sinal_gsm

	def setSinalGPS(self, pSinalGPS):
		self.__sinal_gps = pSinalGPS

	def getSinalGPS(self):
		return self.__sinal_gps

	def setBateriaExterna(self, pBateriaExterna):
		# self.__bateria_externa = int(pBateriaExterna)
		try:
			self.__bateria_externa = int(float(pBateriaExterna))
		except Exception as err:
			self.__bateria_externa = 0
			self.logger.error("setBateriaExterna: " +  str(pBateriaExterna) + " - " + str(err))

	def getBateriaExterna(self):
		return self.__bateria_externa
	
	def setBateriaInterna(self, pBateriaInterna):
		try:
			self.__bateria_interna = int(float(pBateriaInterna))
		except Exception as err:
			self.__bateria_interna = 0
			self.logger.error("setBateriaInterna: " +  str(pBateriaInterna) + " - " + str(err))

	def getBateriaInterna(self):
		return self.__bateria_interna

	def setBloqueio(self, pBloqueio):
		self.__bloqueio = int(pBloqueio)

	def getBloqueio(self):
		return self.__bloqueio
	
	def setClonado(self, pClonado):
		self.__clonado = int(pClonado)

	def getClonado(self):
		return self.__clonado

	def setPanico(self, pPanico):
		self.__panico = int(pPanico)

	def getPanico(self):
		return self.__panico

	def setPainel(self, pPainel):
		self.__painel = int(pPainel)

	def getPainel(self):
		return self.__painel

	def setOdometro(self, pOdometro):
		self.__odometro = int(pOdometro) if type(pOdometro) is str else pOdometro

	def getOdometro(self):
		return self.__odometro

	def setHorimetro(self, pHorimetro):
		self.__horimetro = int(pHorimetro)

	def getHorimetro(self):
		return self.__horimetro
	
	def setTemperatura(self, pTemperatura):
		self.__temperatura = pTemperatura

	def getTemperatura(self):
		return self.__temperatura

	def setEndereco(self, pEndereco):
		self.__address = pEndereco

	def getEndereco(self):
		return self.__address

	def setIdRastreador(self, pIdRastreador):
		self.__id_rastreador = pIdRastreador

	def getIdRastreador(self):
		return self.__id_rastreador

	def setIdVeiculo(self, pIdVeiculo):
		self.__id_veiculo = pIdVeiculo

	def getIdVeiculo(self):
		return self.__id_veiculo

	def setIdUsuarioAdm(self, pIdUsuarioAdm):
		self.__id_usuario_adm = pIdUsuarioAdm

	def getIdUsuarioAdm(self):
		return self.__id_usuario_adm
		
	def setIdLocalizacao(self, pIdLocalizacao):
		self.__id_localizacao = pIdLocalizacao

	def getIdLocalizacao(self):
		return self.__id_localizacao

	def setIdCliente(self, pIdCliente):
		self.__id_cliente = pIdCliente

	def getIdCliente(self):
		return self.__id_cliente

	def setPlaca(self, pPlaca):
		self.__placa = pPlaca

	def getPlaca(self):
		return self.__placa

	def setAcelerometro(self, pAcelerometro):
		self.__acelerometro = pAcelerometro

	def getAcelerometro(self):
		return self.__acelerometro

	def setJamming(self, pJamming):
		self.__jamming_sinal = int(pJamming)

	def getJamming(self):
		return self.__jamming_sinal

	def setTipoRelogio(self, pTpRelogio):
		if type(pTpRelogio) is str:
			self.__tp_relogio = pTpRelogio

	def getTipoRelogio(self):
		return self.__tp_relogio

	def setInput2(self, pInput):
		self.__input2 = pInput

	def getInput2(self):
		return self.__input2

	def setInput3(self, pInput):
		self.__input3 = pInput

	def getInput3(self):
		return self.__input3

	def setOutput2(self, pOutput):
		self.__output2 = pOutput

	def getOutput2(self):
		return self.__output2

	def setOutput3(self, pOutput):
		self.__output3 = pOutput

	def getOutput3(self):
		return self.__output3

	def setComando(self, pComando):
		self.__comando = pComando

	def getComando(self):
		return self.__comando

	def setStatusValido(self, pStatus: bool):
		# self.logger.info('setStatusValido %s', str(pStatus))
		self.__valid_status = pStatus

	def getStatusValido(self):
		# self.logger.info('getStatusValido %s', str(self.__valid_status))
		return self.__valid_status

	def setSleepMode(self, pSleepMode):
		self.__sleep_mode = int(pSleepMode)

	def getSleepMode(self):
		return self.__sleep_mode

	def setMensagemId(self, pMsgId):
		self.__msg_id = pMsgId

	def getMensagemId(self):
		return self.__msg_id
		
	def setCodAlarme(self, pCodAlarme):
		self.__code_alarm = pCodAlarme

	def getCodAlarme(self):
		return self.__code_alarm

	def getIgnicaoValida(self) -> bool:
		"""
		FALSE: Quando nao tiver ignicao no pacote
		TRUE: Quando tiver ignicao no pacote
		"""
		return self.__ignicao_valida

	def setIgnicaoValida(self, pIgnicaoValida : bool):
		"""
		FALSE: Quando nao tiver ignicao no pacote
		TRUE: Quando tiver ignicao no pacote
		"""
		self.__ignicao_valida = pIgnicaoValida

	def getMCC(self):
		return self.__mcc

	def setMCC(self, pMCC):
		self.__mcc = pMCC

	def getMNC(self):
		return self.__mnc

	def setMNC(self, pMNC):
		self.__mnc = pMNC

	def getLAC(self):
		return self.__lac

	def setLAC(self, pLAC):
		self.__lac = pLAC

	def getCID(self):
		return self.__cid

	def setCID(self, pCID):
		self.__cid = pCID

	def setDispositivoDataUltimaComunicacao(self, pDataHora):
		""" SET string format '%Y-%m-%d %H:%M:%S' """
		self.__data_dispositivo_ultima_comunicacao = pDataHora

	def getDispositivoDataUltimaComunicacao(self):
		""" GET string format '%Y-%m-%d %H:%M:%S' """
		return self.__data_dispositivo_ultima_comunicacao

	def setTipoLocalizacao(self, pTipoLocalizacao: int):
		""" 
		0 - Sem Identificacao,
		1 - GPS,
		2 - GPRS,
		3 - LBS
		"""
		self.__tipo_location = pTipoLocalizacao

	def getTipoLocalizacao(self) -> int:
		""" 
		0 - Sem Identificacao,
		1 - GPS,
		2 - GPRS,
		3 - LBS
		"""
		return self.__tipo_location

	def setFlgLatLongLBS(self, pFlgLatLongLBS: bool):
		""" Se lat,long ja foi calculado por LBS """
		self.__lbs_lat_long = pFlgLatLongLBS

	def getFlgLatLongLBS(self) -> bool:
		""" Se lat,long ja foi calculado por LBS """
		return self.__lbs_lat_long

	def setTipoRede(self, pTipoRede):
		self.__tipo_rede = pTipoRede
	
	def getTipoRede(self):
		return self.__tipo_rede

	# alerta de reboque ativo/inativo
	def setReboqueAtivo(self, pReboque): 
		self.__reboque_ativo = pReboque

	# alerta de reboque ativo/inativo
	def getReboqueAtivo(self): 
		return self.__reboque_ativo

	# Carregamento bateria Backup ativado
	def setBateriaBackupAtivo(self, pBatBackupAtiv):
		self.__bateria_backup_ativo = pBatBackupAtiv

	#Carregamento bateria Backup ativado
	def getBateriaBackupAtivo(self):
		return self.__bateria_backup_ativo

	def setSinalGSMValor(self, pSinalGSMValor):
		self.__sinal_gsm_valor = pSinalGSMValor

	def getSinalGSMValor(self):
		return self.__sinal_gsm_valor
	
	def getPublishValue(self):
		vDadosPublish = []

		vDadosPublish.append(self.__protocolo)
		vDadosPublish.append(self.__pacote)
		vDadosPublish.append(self.__identificacao)
		vDadosPublish.append(self.__ip)
		vDadosPublish.append(self.__porta)
		vDadosPublish.append(self.__data_dispositivo)
		vDadosPublish.append(str(1 if self.__gps_valido else 0))
		vDadosPublish.append(self.__latitude)
		vDadosPublish.append(self.__longitude)
		vDadosPublish.append(self.__velocidade)
		vDadosPublish.append(self.__curso)
		vDadosPublish.append(self.__ignicao)
		vDadosPublish.append(self.__movimento)
		vDadosPublish.append(self.__altitude)
		vDadosPublish.append(self.__sinal_gsm)
		vDadosPublish.append(self.__bateria_externa)
		vDadosPublish.append(self.__bateria_interna)
		vDadosPublish.append(self.__qtd_satelites)
		vDadosPublish.append(self.__acelerometro)
		vDadosPublish.append(self.__jamming_sinal)
		vDadosPublish.append(self.__tp_relogio)
		vDadosPublish.append(self.__bloqueio)
		vDadosPublish.append(self.__clonado)
		vDadosPublish.append(self.__panico)
		vDadosPublish.append(self.__painel)
		vDadosPublish.append(self.__odometro)
		vDadosPublish.append(self.__horimetro)
		vDadosPublish.append(self.__temperatura)
		vDadosPublish.append(self.__comando)
		vDadosPublish.append(self.__sinal_gps)
		vDadosPublish.append(self.__msg_id)
		vDadosPublish.append(self.__code_alarm)
		vDadosPublish.append(self.__mnc)
		vDadosPublish.append(self.__mcc)
		vDadosPublish.append(self.__lac)
		vDadosPublish.append(self.__cid)
		vDadosPublish.append(self.__tipo_location)
		vDadosPublish.append(self.__lbs_lat_long)
		vDadosPublish.append(self.__valid_status)
		vDadosPublish.append(self.__tipo_rede)
		vDadosPublish.append(self.__reboque_ativo) 
		vDadosPublish.append(self.__bateria_backup_ativo)
		vDadosPublish.append(self.__sinal_gsm_valor)

		return  ",".join(map(str, vDadosPublish))
	
	def setPublishValue(self, pDados):
		# self.logger.info(pDados)
		vDadosPublish = pDados.split(',')

		self.setProtocol(vDadosPublish[0])
		# vDadosPublish.append(self.__pacote)
		self.setPacote(vDadosPublish[1])
		# vDadosPublish.append(self.__identificacao)
		self.setUniqueId(vDadosPublish[2])
		# vDadosPublish.append(self.__data_dispositivo)
		# vDadosPublish.append(self.__ip)
		# self.setIp(vDadosPublish[3])
		# vDadosPublish.append(self.__porta)
		# self.setPorta(vDadosPublish[4])
		self.setDispositivoDataHora(vDadosPublish[5])
		# vDadosPublish.append(str(1 if self.__gps_valido else 0))
		self.setGPSValido(int(vDadosPublish[6]))
		# vDadosPublish.append(self.__latitude)
		self.setLatitude(vDadosPublish[7])
		# vDadosPublish.append(self.__longitude)
		self.setLongitude(vDadosPublish[8])
		# vDadosPublish.append(self.__velocidade)
		self.setVelocidade(vDadosPublish[9])
		# vDadosPublish.append(self.__curso)
		self.setCurso(vDadosPublish[10])
		# vDadosPublish.append(self.__ignicao)
		self.setIgnicao(int(vDadosPublish[11]))
		# vDadosPublish.append(self.__movimento)
		self.setMovimento(vDadosPublish[12])
		# vDadosPublish.append(self.__altitude)
		self.setAltitude(vDadosPublish[13])
		# vDadosPublish.append(self.__sinal_gsm)
		self.setSinalGSM(vDadosPublish[14])
		# vDadosPublish.append(self.__bateria_externa)
		self.setBateriaExterna(vDadosPublish[15])
		# vDadosPublish.append(self.__bateria_interna)
		self.setBateriaInterna(vDadosPublish[16])
		# vDadosPublish.append(self.__qtd_satelites)
		self.setQtdSatelites(vDadosPublish[17])
		# vDadosPublish.append(self.__acelerometro)
		self.setAcelerometro(vDadosPublish[18])
		# vDadosPublish.append(self.__jamming_sinal)
		self.setJamming(vDadosPublish[19])
		# vDadosPublish.append(self.__tp_relogio)
		self.setTipoRelogio(vDadosPublish[20])
		# vDadosPublish.append(self.__bloqueio)
		self.setBloqueio(vDadosPublish[21])
		# vDadosPublish.append(self.__clonado)
		self.setClonado(vDadosPublish[22])
		# vDadosPublish.append(self.__panico)
		self.setPanico(vDadosPublish[23])
		# vDadosPublish.append(self.__painel)
		self.setPainel(vDadosPublish[24])
		# vDadosPublish.append(self.__odometro)
		self.setOdometro(vDadosPublish[25])
		# vDadosPublish.append(self.__horimetro)
		self.setHorimetro(vDadosPublish[26])
		# vDadosPublish.append(self.__temperatura)
		self.setTemperatura(vDadosPublish[27])
		# vDadosPublish.append(self.__comando)
		self.setComando(vDadosPublish[28])
		if 29 < len(vDadosPublish): self.setSinalGPS(vDadosPublish[29])
		if 30 < len(vDadosPublish): self.setMensagemId(vDadosPublish[30])
		if 31 < len(vDadosPublish): self.setCodAlarme(vDadosPublish[31])
		if 32 < len(vDadosPublish): self.setMNC(vDadosPublish[32])
		if 33 < len(vDadosPublish): self.setMCC(vDadosPublish[33])
		if 34 < len(vDadosPublish): self.setLAC(vDadosPublish[34])
		if 35 < len(vDadosPublish): self.setCID(vDadosPublish[35])
		if 36 < len(vDadosPublish): self.setTipoLocalizacao(vDadosPublish[36])
		if 37 < len(vDadosPublish): self.setFlgLatLongLBS(self.strtobool(vDadosPublish[37]))
		if 38 < len(vDadosPublish): self.setStatusValido(self.strtobool(vDadosPublish[38]))
		if 39 < len(vDadosPublish): self.setTipoRede(vDadosPublish[39])
		if 40 < len(vDadosPublish): self.setReboqueAtivo(self.strtobool(vDadosPublish[40]))
		if 41 < len(vDadosPublish): self.setBateriaBackupAtivo(self.strtobool(vDadosPublish[41]))
		if 42 < len(vDadosPublish): self.setSinalGSMValor(vDadosPublish[42])

	def get_publish_message_push(self) -> dict:
		dados_push = None
		vMensagem = None
		self.logger.debug("get_publish_message_push: " + self.getCodAlarme())
		if self.getCodAlarme() != self.ALARM_NORMAL:
			# longitude value within [-180, 180]
			# latitutede value within [-90, 90]
			if (self.getLatitude() >= -90 and self.getLatitude() <= 90) and (self.getLongitude() >= -180 and self.getLongitude() <= 180):
				#GERAR LINK PARA MAPA
				vLinkMapa = None

			to_zone = tz.tzlocal()
			str_date = self.getDispositivoDataHora()

			# Convert str to date
			try:
				utc_date = datetime.strptime(str_date, "%d-%m-%Y %H:%M:%S")
			except Exception as err:
				self.logger.error("utc_date: " +  self.getDispositivoDataHora() + " - " + str(err))
				return None
			
			# Convert time zone
			try:
				vDataAlerta = utc_date.astimezone(to_zone).strftime('%d/%m/%Y %H:%M:%S')
			except Exception as ex:
				self.logger.error("vDataAlerta: %s", format(ex))
				return None
			
			# if self.getCodAlarme() == self.ALARM_POWER_CUT:
			# 	# self.logger.info('%s(%s) ALARM: %s %s', str(pImei), str(pIdDevice), "0:Vehicle power off", p_sIdLocalizacao)
			# 	vIdTipoAlerta = 1
			# 	vMensagem = "Alerta de corte de energia. Data %s " % (vDataAlerta)

			# elif self.getCodAlarme() == self.ALARM_ACCIDENT:
			# 	# self.logger.info('%s(%s) ALARM: %s', str(pImei), str(pIdDevice), "1:Accident")
			# 	vIdTipoAlerta = 5
			# 	vIdSubtipoTicket = 13

			# if self.getCodAlarme() == self.ALARM_SOS:
			# 	# self.logger.info('%s ALARM: %s', str(pImei), "2:Vehicle robbery(SOS help)")
			# 	vIdTipoAlerta = 10
			# 	vIdSubtipoTicket = 12

			# elif pCodeAlarm == 3:
			# 	self.logger.info('%s ALARM: %s', str(pImei), "3:Vehicle anti-theft and alarming")
			# 	vIdTipoAlerta = None
			# 	vIdSubtipoTicket = None
			if self.getCodAlarme() == self.ALARM_LOW_SPEED:
				# self.logger.info('%s ALARM: %s', str(pImei), "4:Lowerspeed Alert")
				vIdTipoAlerta = 6
				vMensagem = "Alerta de mínimo de limite de velocidade. Data %s " % (vDataAlerta)

			if self.getCodAlarme() == self.ALARM_OVERSPEED:
				# self.logger.info('%s ALARM: %s', str(pImei), "5:Overspeed Alert")
				vIdTipoAlerta = 7
				vMensagem = "Alerta de execesso de limite de velocidade. Data %s " % (vDataAlerta)

			# if self.getCodAlarme() != self.ALARM_GEOFENCE_EXIT:
			# 	# self.logger.info('%s ALARM: %s', str(pImei), "6:Alarm when out of Geo-fence")
			# 	vIdTipoAlerta = 8
			# 	vIdSubtipoTicket = 5

			if self.getCodAlarme() == self.ALARM_MOVEMENT:
				# self.logger.info('%s ALARM: %s', str(pImei), "7:Movement Alert")
				vIdTipoAlerta = 3
				vMensagem = "Alerta de movimento. Data %s " % (vDataAlerta)

			if (self.getCodAlarme() in (self.ALARM_POWER_ON, self.ALARM_ACC_ON)):
				self.logger.info('%s ALARM: %s', self.getUniqueId(), "8:Vehicle Power On")
				vIdTipoAlerta = 11
				vMensagem = "Alerta de ignição ligada. Data %s " % (vDataAlerta)

			if self.getCodAlarme() in (self.ALARM_POWER_OFF, self.ALARM_ACC_OFF):
				self.logger.info('%s ALARM: %s', str(self.getUniqueId()), "9:Vehicle Power Off")
				vIdTipoAlerta = 12
				vMensagem = "Alerta de ignição desligada. Data %s " % (vDataAlerta)

			# if self.getCodAlarme() == self.ALARM_SENSOR_LUMINOSIDADE:
			# 	# self.logger.info('%s ALARM: %s', str(pImei), "13:Violação por sensor de luminosidade")
			# 	vIdTipoAlerta = 13
			# 	vIdSubtipoTicket = 11
			

			if vMensagem is not None:
				self.logger.info('%s ALARM: %s', self.getUniqueId(), vMensagem)
				dados_push = {}
				dados_push["mensagem"] = vMensagem
				dados_push["link_mapa"] = vLinkMapa
				dados_push["imei"] = self.getUniqueId()
				dados_push["id_tipo_alerta"] = vIdTipoAlerta

		return dados_push
	
	def strtobool(self, val):
		"""Convert a string representation of truth to true (1) or false (0).
		True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
		are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
		'val' is anything else.
		"""
		val = val.lower()
		if val in ('y', 'yes', 't', 'true', 'on', '1', 'True'):
			return True
		elif val in ('n', 'no', 'f', 'false', 'off', '0', 'False'):
			return False
		else:
			raise ValueError("invalid truth value %r" % (val,))
	
	# def get_lbs_geolocation(self, pCellID, pAreaCode, pCountryCode, pNetworkCode) -> dict:
	# 	self.logger.info('GET POSITION BY LBS')
	# 	HOST_URL = 'https://www.googleapis.com/geolocation/v1/geolocate'
	# 	params = {
	# 		"key": 'AIzaSyDmmvjsFjRc79kniVqjNLT2vRNd7CHxZSw'
	# 	}

	# 	data = json.dumps({
	# 		"considerIp": False,
	# 		"cellTowers": [
	# 			{
	# 				"cellId": pCellID,
	# 				"locationAreaCode": pAreaCode,
	# 				"mobileCountryCode": pCountryCode,
	# 				"mobileNetworkCode": pNetworkCode
	# 			}
	# 		]
	# 	})

	# 	headers = {
	# 		'content-type': "application/json",
	# 		'cache-control': "no-cache"
	# 	}

	# 	# self.logger.info(params)
	# 	# self.logger.info(data)
	# 	request = requests.post(HOST_URL, params=params, data=data, headers=headers)
	# 	if request.status_code == 200:
	# 		response = json.loads(request.text)
			
	# 		latitude = response["location"]["lat"]
	# 		longitude = response["location"]["lng"]
	# 		dados = {
	# 			"latitude": latitude,
	# 			"longitude": longitude,
	# 			"accuracy": response["accuracy"]
	# 		}
	# 		self.logger.info(dados)
	# 		return dados

	# 	else:
	# 		error_data = request.text
	# 		self.logger.error("Error Occurred in Finding Cell Tower Location")
	# 		self.logger.error(request.text)
	# 		self.logger.error(json.dumps(params))

	# 		return None