import asyncio
import codecs
import json
import logging
import socket
import sys
import time
from binascii import unhexlify
from datetime import datetime

import pika

from lib.database.ConnDynamodb import ConnDynamoDb
from lib.helper.hexutil import HexUtil
from lib.position import Position
from lib.protocolo.ee23 import EE23

# from lib.queue import SimpleQueue

BUFF = 2048 # 1040
PORT = 2024  # must be input parameter @TODO
DISPOSITVO_MODELO = 48

py3k = sys.version_info >= (3, 0)

if py3k:
	from threading import Event, Thread

	thread = Thread
else:
	import _thread
	
logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s',level=logging.INFO)

logger = logging.getLogger(__name__)

# Criando Simple Queue Objeto
# QueueNovo = SimpleQueue(
# 	amqp_url='ec2-54-163-75-219.compute-1.amazonaws.com',
# 	queue="position.new",
# 	routing_key="tracker.position.new"
# )

# QueueAntigo = SimpleQueue(
# 	amqp_url='ec2-54-163-75-219.compute-1.amazonaws.com',
# 	queue="position.old",
# 	routing_key="tracker.position.old"
# )

#DICIONARIO COM COMANDOS DO MODELO EE23
_dCommands = dict([])

event = Event()

async def new_session(reader, writer):
	try:
		await asyncio.wait_for(handle_publish(reader, writer), timeout=1320)
	except asyncio.TimeoutError as te:
		logger.exception(f'time is up!{te}')
	finally:
		writer.close()
		logger.info("Session closed")

@asyncio.coroutine
def handle_publish(reader, writer):
	# CLASSE DE ACESSO AO DYNAMODB
	connDynamoDb = ConnDynamoDb()

	# ABRE CONEXAO COM RABBITMQ
	QueueNovo.connect()
	QueueAntigo.connect()
	# QueueAlerta.connect()

	Protocolo = EE23()
	vImei = None
	vCommand = None
	vIdRequestCommand = None
	vFlgEnvio = False
	vIP, vPorta = addr = writer.get_extra_info('peername')
	logger.debug("vIP " + vIP)
	count = 0

	while 1:
		data = yield from reader.read(BUFF)
		if not data:
			break
		
		##################
		# VERIFICAR EXISTENCIA DE COMANDO
		try:
			#start_time = time.time()
			if vImei is not None:
				logger.info("%s: IMEI: %s", vImei, str(str(vImei) in _dCommands))
				
				if vImei in _dCommands:
					vCommand = _dCommands[vImei]
					logger.info("%s: vCommand: %s", vImei, str(vCommand))
					if len(vCommand) > 0 and vFlgEnvio == False:
						gprs_command = vCommand[0]['gprs_command']
						command_status = vCommand[0]['command_status']
						vIdRequestCommand = vCommand[0]['id_request_command']
						vDtInclusao = vCommand[0]['dt_inclusao']

						#VERIFICAR SE COMANDO JA FOI ENVIADO ANTERIORMENTE, SE SIM EXCLUIR DA FILA
						vericar_comando = connDynamoDb.get_dy_command_by_id(vImei, vIdRequestCommand)
						logger.info("VERIFICAR: " + str(vericar_comando))
						if len(vericar_comando) > 0 and vericar_comando[0]['flg_envio'] == False:
							#GERAR COMANDO A PARTIR DE CODIGO DO BANCO
							vReturnCommand = Protocolo.genCommand(gprs_command, vImei, command_status, "0000")
							if vReturnCommand is not None:
								#RETORNAR COMANDO PARA DISPOSITIVO
								writer.write(unhexlify(vReturnCommand))
								yield from writer.drain()

								#REMOVE COMANDO DA FILA
								remover = next((cmd for cmd in vCommand if cmd["id_request_command"] == vIdRequestCommand), None)
								vCommand.remove(remover)

								#ATUALIZA FLG E DATA DE ENVIO
								if vIdRequestCommand is not None:
									connDynamoDb.post_dy_command_envio(vImei, vIdRequestCommand, vDtInclusao)
								
								logger.info("Imei: %s, SENDED: %s", vImei, vReturnCommand)
						
								vFlgEnvio = True
							else:
								#VERIFICAR SE PRECISA EXCLUIR DA FILA CASO NAO ESTEJA CONFIGURADO
								vFlgEnvio = False
								logger.error("Imei: %s, genCommand %s nao foi possivel gerar.", vImei, gprs_command)
						
						elif len(vericar_comando) > 0 and vericar_comando[0]['flg_envio'] == True:
							#REMOVE COMANDO DA FILA
							remover = next((cmd for cmd in vCommand if cmd["id_request_command"] == vIdRequestCommand), None)
							vCommand.remove(remover)


			#logger.info(vImei + " --- %s seconds ---" % (time.time() - start_time))
		except Exception:
			logger.exception("COMMANDO")	
		
		##################
		# INICIO DECODE
		try:
			logger.info("Received " + repr(data))
			logger.info("Received hex " + repr(codecs.getencoder("hex")(data)[0]))
			
			dData = codecs.getencoder('hex')(data)[0].decode()

			indice = 0
			start,indice = HexUtil.read_unsigned_short(dData, indice)
			length,indice  = HexUtil.read_unsigned_byte(dData, indice)
			if start == '7878':
				type_command,indice  = HexUtil.read_unsigned_byte(dData, indice)
			else:
				indice += 2
				type_command,indice  = HexUtil.read_unsigned_byte(dData, indice)
			
			if vImei is not None: logger.info("%s Commando %s", vImei, type_command)
		
			if (type_command == Protocolo.MSG_LOGIN):	
				vImei,indice = HexUtil.read_unsigned_long(dData, indice)
				vImei = str(int(vImei))
				vSerial,indice = HexUtil.read_unsigned_short(dData, indice)
				
				logger.debug('-- login tracker EE23 --')
				logger.info('Terminal ID: %s '% (vImei))
				logger.debug('serial number: %s '% int(vSerial, 16))
				
				vRetorno = Protocolo.genCommand(type_command,vImei,"",str(vSerial))
				logger.info("%s Login_vRetorno: %s", vImei, str(vRetorno))
				#RETORNAR COMANDO PARA DISPOSITIVO
				writer.write(unhexlify(vRetorno))
				# writer.write(vRetorno.encode())
				yield from writer.drain()
		
			elif (type_command == Protocolo.MSG_STATUS) or (type_command == Protocolo.MSG_HEARTBEAT):
				vSerial = Protocolo.decodeStatus(type_command, dData, indice)

				vRetorno = Protocolo.genCommand(type_command, None, None, vSerial)
				logger.info("%s terminal_info_vRetorno: %s", vImei, str(vRetorno.encode()))
				#RETORNAR COMANDO PARA DISPOSITIVO
				writer.write(unhexlify(vRetorno))
				yield from writer.drain()
				
			elif(type_command == Protocolo.MSG_ADDRESS):
				Protocolo.genAddrees(dData, vSerial, indice)

				vRetorno = Protocolo.genCommand(type_command,"","",str(vSerial))
				logger.info("terminal_info_vRetorno: %s", str(vRetorno))
				#RETORNAR COMANDO PARA DISPOSITIVO
				writer.write(unhexlify(vRetorno))
				yield from writer.drain()

			elif (type_command == Protocolo.MSG_STRING):
				cmdContent = dData[8:10]
				lenCmdContent = 18 + (int(cmdContent, 16) * 2) - 8
				vFlag = str(unhexlify(dData[18:lenCmdContent]).decode())
				logger.info('%s hex_msg: %s', vImei, vFlag)
				
				try:
					if vFlgEnvio and (vImei is not None and vIdRequestCommand is not None and vDtInclusao is not None):
						connDynamoDb.post_dy_command_response(vImei, vIdRequestCommand, vDtInclusao, Protocolo.MSG_COMMAND_0, vFlag)
					
					vIdRequestCommand = None
					vDtInclusao = None
					vFlgEnvio = False
				except Exception:
					logger.exception("COMMANDO_RESPONSE")

			elif Protocolo.isSupported(type_command):

				if type_command == Protocolo.MSG_LOGIN_GPS_LBS_STATUS:
					vImei,indice = HexUtil.read_unsigned_long(dData, indice)
					vImei = str(int(vImei))

				if start == '7878':
					
					positions = Protocolo.decode(vImei, vIP, vPorta, type_command, dData, indice)
					if len(positions) > 0:
						for position in positions:
							if position.getLatitude() != 0 and position.getLongitude() != 0:
							
								later_time = datetime.now()
								data_dispositivo = datetime.strptime(position.getDispositivoDataHora(), '%d-%m-%Y %H:%M:%S')
								difference = later_time - data_dispositivo
								
								dados_track = {}									
								dados_track["servidor"] = 'aws'
								dados_track["dados"] = position.getPublishValue()
								dados_track["imei"] = str(vImei)
								
								json_data = json.dumps(dados_track, ensure_ascii=False)
								logger.info('json_data %s', json_data)
								logger.info('difference.seconds %s', difference.seconds)

								if difference.seconds <= 300:
									try:
										QueueNovo.publish_message(json_data)
										# logger.info('publish_message %s', json_data)
										# if (QueueNovo._connection is not None and not QueueNovo._connection.is_closed):										
										# 	QueueNovo.publish_message(json_data)
									except (pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed) as err:                
										logger.error('Publish_New %s', err)
										QueueNovo.connect()
										QueueNovo.publish_message(json_data)
								else:
									try:
										if (QueueAntigo._connection is not None and not QueueAntigo._connection.is_closed):										
											QueueAntigo.publish_message(json_data)
											logger.info('publish_message_old: %s' % (json_data))
									except (pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed) as err:                
										logger.error('Publish_Old %s', err)
				
							if vImei is not None and position.getMensagemId() != "":
								vSerial = position.getSerialNumber()
								vRetorno = Protocolo.genCommand(type_command,"","",vSerial)
								logger.info("terminal_info_vRetorno: %s", str(vRetorno))
								#RETORNAR COMANDO PARA DISPOSITIVO
								writer.write(unhexlify(vRetorno))
								yield from writer.drain()

				
		except Exception as ex:
			logger.exception(ex)

	# if (QueueNovo._connection is not None and not QueueNovo._connection.is_closed):	
		# QueueNovo.close()
		# QueueAntigo.close()

def loadComandos(pDicCommands, pIdDispositivoModelo):
	connDynamoDb = ConnDynamoDb()
	
	# while 1:
		# start_time = time.time()
		# if pIdDispositivoModelo is not None:
		# 	aCommands = connDynamoDb.get_dy_command_by_modelo(pIdDispositivoModelo)
		# 	if aCommands is not None:
		# 		for item in aCommands:
		# 			vImei = item['unique_id']#''54684100263535'
		# 			vIdRequestCommand = item['id_request_command']

		# 			if vImei not in pDicCommands:
		# 				pDicCommands[vImei] = []
					
		# 			filtro = next((cmd for cmd in pDicCommands[vImei] if cmd["id_request_command"] == vIdRequestCommand), None)
		# 			if filtro is None:
		# 				pDicCommands[vImei].append(item)
				
		# 	if event.is_set():
		# 		break

			# logger.info(" --- %s loadComandos seconds ---" % (time.time() - start_time))
		# time.sleep(15.1)


if __name__ == "__main__":

	if len(sys.argv) >= 2:
		#print('PORTA: ' + str(sys.argv[1]))
		PORT = int(sys.argv[1])

	try:
		p = Thread(target=loadComandos, args=(_dCommands, DISPOSITVO_MODELO), daemon=True)
		p.setDaemon(True)
		p.start()
	except KeyboardInterrupt:
		event.set()

	try:
		loop = asyncio.get_event_loop()
		coro = asyncio.start_server(new_session, '', PORT, loop=loop, family=socket.AF_INET)
		server = loop.run_until_complete(coro)

		# Serve requests until Ctrl+C is pressed
		logger.info('Serving on {}'.format(server.sockets[0].getsockname()))
		try:
			loop.run_forever()
		except KeyboardInterrupt:
			pass

		# Close the server
		server.close()
		loop.run_until_complete(server.wait_closed())
		loop.close()

	except KeyboardInterrupt:
		event.set()