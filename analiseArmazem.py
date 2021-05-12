
# baixando biblioteca simpy
!pip install simpy

# importação de bibliotecas
import simpy
import random

tempom_caminhao = 25 #Tempo medio chegada de caminhoes 
tempom_portc = 5 #Tempo medio de chegada na portaria 
tempom_ports = 7 #Tempo medio saida da portaria
desvports = 2 #Desvio saida portaria
tempomdesca = 30 #Tempo medio de a
desvdesca = 6 #Desvio de a
mindescb = 30 #Minimo tempo b
modadescb = 38 #Moda do tempo de b
maxdescb = 50 #Maximo tempo b
tempomedionfr = 7 #Tempo medio fiscal
desvnfr = 2 #Desvio fiscal
temposimulacao = 10000 #Tempo da simulação
vetor = [] #vetor de estrutura caminhão

#define a estrutura caminhão

class Caminhao:
  #construtor do caminhão 
  def __init__(self):
    self.id = 0
    self.tipoCarga = 0
    self.horaEntrada = 0
    self.horaPortaria = 0
    self.entradaPortaria = 0
    self.tempoPortaria = 0
    self.saidaPortaria = 0
    self.entradaDoca = 0
    self.saidaDoca = 0
    self.tempoDoca = 0
    self.entradaFiscal = 0
    self.saidaFiscal = 0
    self.tempoFiscal = 0

  #metodo gerar caminhão
  def entrarCaminhao(self, id, tipoCarga, horaEntrada):
      self.id = id
      self.tipoCarga = tipoCarga
      self.horaEntrada = horaEntrada

  #metodo entrar portaria
  def entrarPortaria(self, entradaPortaria, saidaPortaria):
    self.entradaPortaria = entradaPortaria
    self.saidaPortaria = saidaPortaria
    self.tempoPortaria = saidaPortaria - entradaPortaria
  #metodo entrar docas
  def entrarDoca(self, entradaDoca, saidaDoca):
    self.entradaDoca = entradaDoca
    self.saidaDoca = saidaDoca
    self.tempoDoca = saidaDoca - entradaDoca
  #metodo entrar fiscal
  def entrarFiscal(self, entradaFiscal, saidaFiscal):
    self.entradaFiscal = entradaFiscal
    self.saidaFiscal = saidaFiscal
    self.tempoFiscal = saidaFiscal - entradaFiscal

def imprimirCaminhao(vetor):
  for i in range(len(vetor)):
    print("O caminhao {} carregando o material do tipo {}, entrou no sistema no minuto {}".format(vetor[i].id, vetor[i].tipoCarga,vetor[i].horaEntrada))
    if (vetor[i].entradaPortaria!=0 or i==0):
      print("chegou a portaria no minuto {}, esperou por {} minutos e saiu no minuto {} ".format(vetor[i].entradaPortaria, vetor[i].tempoPortaria, vetor[i].saidaPortaria))
      if (vetor[i].entradaDoca!=0):
       print("entrou na doca no minuto {}, descarregou por {} minutos e saiu no minuto {}".format(vetor[i].entradaDoca, vetor[i].tempoDoca, vetor[i].saidaDoca))
       if (vetor[i].entradaFiscal!=0): 
         print("chegou no fiscal no tempo {}, esperou por {} minutos e se dirigiu a saida no minuto {} ".format(vetor[i].entradaFiscal, vetor[i].tempoFiscal, vetor[i].saidaFiscal))
         print("\n")
       else:
          print(" E não entrou no fiscal porque o processo terminou")
          print("\n")
      else:
       print(" E não entrou na doca porque o processo terminou")
       print("\n")
    else:
     print(" E não entrou na portaria porque o processo terminou")
     print("\n")

# gerar caminhões

def gerarCaminhao(env):

  id_caminhao = 0
  while True:
    vetor.insert(id_caminhao, Caminhao())
    
    #define o tipo de materia
    if random.random() < 0.3:
      tipo_materia = 'A' 
    else:
      tipo_materia = 'B' 


    tempo = round(env.now)
    vetor[id_caminhao].entrarCaminhao(id_caminhao,tipo_materia,tempo)

    # envia o caminhao a portaria
    env.process(portaria(env, id_caminhao, 'chegando', env.now, portaria_r))
    yield env.timeout(random.expovariate(1.0/tempom_caminhao))

    # gera o proximo id do caminhao
    id_caminhao += 1

# implementação da portaria
def portaria(env, id_caminhao, chegando_ou_saindo, entradaPortaria, portaria_r):
 
  global cont_doca_b1
  global cont_doca_b2
  #verifica condição de chegada do caminhão
  if chegando_ou_saindo == 'chegando':
    # entra na portaria
    with portaria_r.request(priority=2) as request:
      # fila da portaria
      yield request
      entradaPortaria = round(env.now) #inicio do atendimento para entrada do caminhão
    
      #tempo atendimento portaria
      yield env.timeout(random.expovariate(1.0/tempom_portc))
      saidaPortaria = (round(env.now)) 
      vetor[id_caminhao].entrarPortaria(entradaPortaria,saidaPortaria)
      # libera a portaria
      yield portaria_r.release(request)

     
      

      if vetor[id_caminhao].tipoCarga == 'A':
        # inicia descarga na doca A
        env.process(docaA(env, id_caminhao, entradaPortaria, doca_a))

      elif vetor[id_caminhao].tipoCarga == 'B':
        
        if cont_doca_b2 < cont_doca_b1:
          # inicia descarga na doca B2
          env.process(docaB2(env, id_caminhao, entradaPortaria, doca_b2))
        else:
          # inicia descarga na doca B1
          env.process(docaB1(env, id_caminhao, entradaPortaria, doca_b1))
   
  
  
  else:
    # verifica prioridade de saida
    with portaria_r.request(priority=3) as request:
      
      # tempo espera saida
      yield request
      tempoPortaria=(round(env.now, 2)) #inicio vistoria para saida

      # tempo final de saida
      yield env.timeout(random.normalvariate(tempom_ports, desvports))
      saidaPortaria=(round(env.now)) #final vistoria de saida
     
      # libera a saida
      yield portaria_r.release(request)

# implementação da doca A
def docaA(env, id_caminhao,  entradaPortaria, doca_a):
  # ocupa a doca e realiza a descarga
  request = doca_a.request()

   # espera na fila
  entradaDoca = (round(env.now)) #camhinão aguardando liberação doca A
  yield request
  # tempo de descarregamento
  yield env.timeout(random.normalvariate(tempomdesca, desvdesca))
  saidaDoca = (round(env.now)) #finalizando descarga doca A
  vetor[id_caminhao].entrarDoca(entradaDoca,saidaDoca)
  #libera a doca a
  yield doca_a.release(request)

  # inicia processo do fiscalizaçao
  env.process(notaRecibo(env, id_caminhao, saidaDoca, nota_recibo))

# implementação da doca B1
def docaB1(env, id_caminhao, entradaPortaria, doca_b1):
  global cont_doca_b1

 # ocupa a doca e começa a descarregar
  request = doca_b1.request()

  # espera na fila
  cont_doca_b1 += 1
  entradaDoca = (round(env.now)) #aguardando liberação da doca B1
  yield request
  tempoDoca = (round(env.now)) #finiciando descarga caminhão doca B1

  # tempo de descarregamento
  yield env.timeout(random.triangular(mindescb, modadescb, maxdescb))
  saidaDoca = (round(env.now)) #finalizando descarga doca B1
  vetor[id_caminhao].entrarDoca(entradaDoca,saidaDoca)
  #libera doca b1
  cont_doca_b1 -= 1
  yield doca_b1.release(request)
  

  # inicia processo do fiscalizaçao
  env.process(notaRecibo(env, id_caminhao,  saidaDoca, nota_recibo))

# implementação da doca B2
def docaB2(env, id_caminhao,horarioPortaria, doca_b2):
  global cont_doca_b2

  # ocupa a doca e começa a descarregar
  request = doca_b2.request()

  # espera na fila
  cont_doca_b2 += 1
  entradaDoca =(round(env.now)) #aguardando liberação da doca B2
  yield request


  # tempo de descarregamento
  yield env.timeout(random.triangular(mindescb, modadescb, maxdescb))
  saidaDoca = (round(env.now)) #finalizando descarga doca B1
  vetor[id_caminhao].entrarDoca(entradaDoca,saidaDoca)
  #libera doca b2
  cont_doca_b2 -= 1
  yield doca_b2.release(request)
  

  # inicia processo de fiscalização
  env.process(notaRecibo(env, id_caminhao, saidaDoca, nota_recibo))

# implementação do recurso do setor de notas fiscais e recibos da carga
def notaRecibo(env, id_caminhao, saidaDoca, nota_recibo):
  # ocupa o setor de notas fiscais e recibo
  request = nota_recibo.request()

  # entra no fiscal
  yield request
  entradaFiscal =(round(env.now)) #inico entrega notas fiscais
 
  
  # sai do fiscal
  yield env.timeout(random.normalvariate(tempomedionfr, desvnfr))
  saidaFiscal = (round(env.now)) #final entrega notas fiscais
  
  vetor[id_caminhao].entrarFiscal(entradaFiscal,saidaFiscal)
  #libera o fiscal
  yield nota_recibo.release(request)

  # inicia o processo de saida
  env.process(portaria(env, id_caminhao,  None, 'saindo', portaria_r))

random.seed()                                            # gera uma semente randomica
cont_doca_b1 = 0                                         # contador fila de B2
cont_doca_b2 = 0                                         # contador fila de B1
env = simpy.Environment()                                # cria o ambiente
portaria_r = simpy.PriorityResource(env, capacity=1)     # cria o recurso da portaria
doca_a = simpy.Resource(env, capacity=1)                 # cria a doca A
doca_b1 = simpy.Resource(env, capacity=1)                # cria a doca B1
doca_b2 = simpy.Resource(env, capacity=1)                # cria o setor de notas e recibos
nota_recibo = simpy.Resource(env, capacity=1)            # cria a doca B2
env.process(gerarCaminhao(env))                          # geração de caminhoes A

env.run(until=temposimulacao)
imprimirCaminhao(vetor)
