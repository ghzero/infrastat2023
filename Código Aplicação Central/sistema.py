from queue import Empty
from datetime import date, timedelta
import re
import socket
import json
import zabbix_api
import datetime
import calendar
import time
import crud, models, schemas

def criar_alertas(db):
  crud.criar_alerta(db,"HFP","Hostname fora do Padrão -> ","Correcao","Corrigir a nomenclatura padrão para monitoramento automatizado do ativo")
  crud.criar_alerta(
                        db,
                        "INA",
                        "Hostname inativo por 15 dias -> ",
                        "Informacao",
                        "Informativo de inatividade",
                    )
  
  crud.criar_alerta(
                        db,
                        "REM",
                        "Hostname removido por inatividade 30 dias -> ",
                        "Removido",
                        "Removido do monitoramento por inatividade",
                    )
  crud.criar_alerta(
                                    db,
                                    "HIN",
                                    "Hardware Incompleto -> ",
                                    "Correcao",
                                    "Verificar porque o ativo não esta recebendo todos os dados de hardware",
                                )
  
  

  return 0

def transforme_objeto_em_json(objeto):
  jsn = json.dumps(objeto)
  #print(type(jsn))
  #print("transformei objeto em json")
  return jsn

def transforme_json_em_objeto(jsn):
  string = json.loads(jsn)
  #print(type(string))
  #print("transformei json em objeto")
  return string


def verificar_seguranca(db):
 #Retornar 
 # 1 - Ativos com administradores
   # Quantidade de ativos como administradores
   # lista de ativos com admin fora do suporte
 # 2 - Ativos atualizados e desatualizados (Por SO)
   # Quantidade de ativos atualizados e desatualizados
   # Lista de ativos desatualizados
 # 3 - Ativos com antivirus Atualizados e desatualizados
   # Quantidade de ativos com antivirus atualizados
   # Quantidade de ativos somente com Defender
   # Quantidade de ativos com Kaspersky
   # Lista de ativos com antivirus desatualizado ou somente defender
  dicionario_de_seguranca = {}
  dicionario_de_computadores_com_admin = {}
  lista_de_desatualizados = []

  update_atual = "10.0.19045"
  lista_de_informacoes_de_sistema = crud.get_informacoes_de_sistema(db)
  ativos_desatualizados = crud.get_desatualizados(db,update_atual)
  for info in ativos_desatualizados:
        computador = crud.get_ativo_com_informacao_de_sistema(db,info)
        try:      
         lista_de_desatualizados.append(computador.hostname)
        except:
          print(" computador sem hostname ") 
  json_string = json.dumps(lista_de_desatualizados, indent=4, sort_keys=True, default=str)
  json_object = transforme_json_em_objeto(json_string)
  #listajson = transforme_objeto_em_json([ob.__dict__ for ob in ativos_desatualizados])
  dicionario_de_seguranca['total_de_computadores'] = len(lista_de_informacoes_de_sistema)
  dicionario_de_seguranca['total_de_desatualizados'] = len(ativos_desatualizados)
  dicionario_de_seguranca['lista_de_desatualizados'] = json_object
  
  
  
  #print(len(lista_de_informacoes_de_sistema))
  lista_de_administradores_permitios = ["admin-suporte","Admins.dodominio","Administrador","DomainAdmins","ADMIN-SUPORTE"]
  #print (len(lista_de_informacoes_de_sistema))
  
  total_admin_gtl = 0
  total_admin_stigeo = 0
  total_admin_passageiros = 0
  total_admin_nea = 0
  total_admin_web = 0
  series = []
  dici = {"labels":[],"series":[]}
  lista_de_computadores_com_admin = []
  lista_de_computadores_com_erro_de_admin = []
  lista_de_computadores_sem_dados_de_antivirus = []
  lista_de_computadores_sem_antivirus = []
  lista_de_computadores_sem_antivirus_desabilitado = []
  lista_de_computadores_com_antivirus_desatualizado = []
  lista_de_computadores_com_antivirus_ativo = []
  quantidade_de_administradores_locais = 0
  lista_de_ativo = []
  for info in lista_de_informacoes_de_sistema:
    
    computador = crud.get_ativo_com_informacao_de_sistema(db,info)
    if (computador.hostname and len(info.dados_de_administradores) == 4):
      #print(computador.hostname)
      lista_de_computadores_com_erro_de_admin.append(computador.hostname)
    if (computador.hostname and len(info.dados_de_administradores) == 0 ):
      lista_de_computadores_com_erro_de_admin.append(computador.hostname)
    try:
     infojson = transforme_json_em_objeto(info.dados_de_administradores)
     hostname = computador.hostname
    except:
     infojson = "0"
     hostname = None
    if (hostname): 
     for info2 in infojson:
      try:
       stringnome =  info2['Name'].split("\\")
       if (stringnome[1] not in lista_de_administradores_permitios ):
        
        #if(computador.hostname not in lista_de_computadores_com_admin):
        if (hostname in dicionario_de_computadores_com_admin.keys()):
         antigovalor = dicionario_de_computadores_com_admin[hostname]
         dicionario_de_computadores_com_admin[hostname] = antigovalor + " , " + info2['Name']
         lista_de_computadores_com_admin.append(hostname)
       

        else:
          quantidade_de_administradores_locais = quantidade_de_administradores_locais + 1 
          dicionario_de_computadores_com_admin[hostname] = info2['Name']

          #remover depois
          if(computador.equipe == "TST"):
           total_admin_gtl = total_admin_gtl + 1 
          if(computador.equipe == "DEV"):
           total_admin_stigeo = total_admin_stigeo + 1
          if(computador.equipe == "WEB"):
           total_admin_web = total_admin_web + 1
          if(computador.equipe == "NEA"):
           total_admin_nea = total_admin_nea + 1
          if(computador.equipe == "PAS"):
           total_admin_passageiros = total_admin_passageiros  + 1
        #final remover depois
         #lista_de_computadores_com_admin.append(infojson)
        #print("a")
      except: 
       lista_de_computadores_com_erro_de_admin.append(hostname)
    
     try:
      infoav = transforme_json_em_objeto(info.dados_de_antivirus)
     
     except:
      infoav = {}
      lista_de_ativo.append(hostname) 
      lista_de_computadores_sem_dados_de_antivirus.append(hostname)
      #print("erro de av ->" + str(computador.hostname))

     if (len(infoav) == 1):
      #print (len(infoav))
      if(infoav[0]['productState'] == "Desabilitado"):
         #print("tem umm av e desabilitado") 
         #print(str(infoav[0]))
         lista_de_computadores_sem_antivirus_desabilitado.append(hostname)
         #lista_de_computadores_sem_antivirus_desabilitado.append(infoav[0]['displayName'])  
      else:
          if(infoav[0]['displayName'] == "Windows Defender"):
            #print("tem umm av eh nao o defender") 
           #if(computador.hostname not in lista_de_ativo): 
            lista_de_ativo.append(hostname) 
            lista_de_computadores_sem_antivirus.append(hostname)
          else:
            lista_de_ativo.append(hostname)
            lista_de_computadores_com_antivirus_ativo.append(hostname)
     else:
      for av in infoav:
       
        if(av['displayName'] != "Windows Defender"):
          #print("tem umm av e nao eh defender")
          
          if(av['productState'] == "Ativo - Atualizado"):
           nomecompleto = av['displayName'] + str(av['productState'])
           if(computador.hostname not in lista_de_ativo):
            lista_de_ativo.append(computador.hostname)
            lista_de_computadores_com_antivirus_ativo.append(computador.hostname)
            #lista_de_computadores_com_antivirus_ativo.append(av['displayName'])
          else:
           if(av['productState'] == "Ativo - Desatualizado"):
            if(computador.hostname not in lista_de_ativo):
             lista_de_ativo.append(computador.hostname)
             lista_de_computadores_com_antivirus_desatualizado.append(computador.hostname)
            #lista_de_computadores_com_antivirus_desatualizado.append(av['displayName'])
           else:  
            if(av['productState'] == "Desabilitado"):
              if(computador.hostname not in lista_de_ativo):
               lista_de_ativo.append(computador.hostname)
               lista_de_computadores_sem_antivirus_desabilitado.append(computador.hostname)
               #lista_de_computadores_com_antivirus_desatualizado.append(av['displayName'])
            else:
              if(computador.hostname not in lista_de_ativo):
               lista_de_ativo.append(computador.hostname) 
               lista_de_computadores_sem_antivirus_desabilitado.append(computador.hostname)
  lista_de_hosts_para_teste = []
  for key, value in dicionario_de_computadores_com_admin.items():
    pc_com_admin = {}
    pc_com_admin['hostname'] = key
    pc_com_admin['admins'] = value
    lista_de_hosts_para_teste.append(pc_com_admin)

  

  #print (lista_de_hosts_para_teste)
  #print (lista_de_computadores_com_admin)
  dicionario_de_seguranca['total_de_computadores_com_admin'] = quantidade_de_administradores_locais
  dicionario_de_seguranca['total_de_computadores_com_erro_de_admin'] = len(lista_de_computadores_com_erro_de_admin)
  dicionario_de_seguranca['lista_de_computadores_com_admin'] = lista_de_hosts_para_teste
  dicionario_de_seguranca['lista_de_computadores_com_erro_de_admin'] = lista_de_computadores_com_erro_de_admin
  dicionario_de_seguranca['total_de_computadores_sem_antivirus'] = len(lista_de_computadores_sem_antivirus)
  dicionario_de_seguranca['total_de_computadores_com_antivirus_desabilitado'] = len(lista_de_computadores_sem_antivirus_desabilitado)
  dicionario_de_seguranca['total_de_computadores_com_antivirus_ativo'] = len(lista_de_computadores_com_antivirus_ativo)
  dicionario_de_seguranca['total_de_computadores_sem_dados_de_antivirus'] = len(lista_de_computadores_sem_dados_de_antivirus)
  dicionario_de_seguranca['lista_de_computadores_sem_antivirus'] = lista_de_computadores_sem_antivirus
  dicionario_de_seguranca['lista_de_computadores_com_antivirus_desabilitado'] = lista_de_computadores_sem_antivirus_desabilitado
  dicionario_de_seguranca['lista_de_computadores_sem_dados_de_antivirus'] = lista_de_computadores_sem_dados_de_antivirus
  dicionario_de_seguranca['equipes'] = ["ADM","DEV"]
  dicionario_de_seguranca['numero_admin_por_equipe'] = [total_admin_gtl,total_admin_stigeo,total_admin_passageiros,total_admin_nea,total_admin_web]
  dicionario_de_seguranca['legendas_av'] = ["Com erro de deteccao","Com Antivirus Ativo e Atualizado","Desabilitados","Sem Antivirus"]
  dicionario_de_seguranca['valores_av'] = [len(lista_de_computadores_sem_dados_de_antivirus),len(lista_de_computadores_com_antivirus_ativo),len(lista_de_computadores_sem_antivirus_desabilitado),len(lista_de_computadores_sem_antivirus)]
  dicijson = transforme_objeto_em_json(dicionario_de_seguranca)
  return dicijson 



def calcular_energia_ativo(quantidade_de_discos,quantidade_de_memorias,tdp_gpu,media_gpu,media_cpu):
  gpu_watts = 0
  cpu_watts = media_cpu
  memoria_watts = quantidade_de_memorias * 3
  discos_watts = quantidade_de_discos * 3
  mobo_watts = 35

  if (tdp_gpu):
    gpu_watts = 100*tdp_gpu/media_gpu
  else:
    gpu_watts = 100*100/media_gpu


  return 0

def criar_alertas_de_alteracao_de_hardware(db,dados_do_ativo_na_busca,dados_de_hardware_no_banco,hardware_na_busca):
    print("atualizando componentes e criando alterações")
    
    alteracoes = models.informacao_hardware.alteracao(dados_de_hardware_no_banco,hardware_na_busca)
    
    print(alteracoes)
    for alt in alteracoes:
     lista_atual_valor = []
     lista_antigo_valor = []
     lista_para_adicionar = []
     lista_para_remover = []
     valor_no_banco = getattr(dados_de_hardware_no_banco, alt)
     valor_alterado = getattr(hardware_na_busca, alt)
     print(str(alt) + str(valor_no_banco) + str(valor_alterado))
     if(alt != "quantidade_de_memorias" and alt != "quantidade_de_discos" and alt != "dados_de_memoria_total_em_gb"):
      if(valor_no_banco and valor_alterado and valor_alterado != "nodata"):
        print("entrou no if")
        print(dados_do_ativo_na_busca.hostname)
        print(valor_no_banco)
        print(valor_alterado)
        antigo_valor = valor_no_banco
        if(valor_no_banco != "nodata"):  
         antigo_valor = transforme_json_em_objeto(valor_no_banco)
         atual_valor = transforme_json_em_objeto(valor_alterado)
         for valor in antigo_valor:
           lista_antigo_valor.append(valor)
         for valor in atual_valor:
           lista_atual_valor.append(valor)  
        
         if(len(antigo_valor) < len(atual_valor)):
       #   print("eh adicionar")
          for valor in atual_valor:
            if (valor not in antigo_valor):
              lista_para_adicionar.append(valor)
             
         if(len(antigo_valor) > len(atual_valor)):
        #  print("eh remover")
          for valor in antigo_valor:
            if (valor not in atual_valor):
              lista_para_remover.append(valor)

         if(len(antigo_valor) == len(atual_valor)):
         # print("eh alterar")
          for valor in atual_valor:
            if (valor not in antigo_valor):
             
              lista_para_adicionar.append(valor)
          for valor in antigo_valor:
            if (valor not in atual_valor):
              
              lista_para_remover.append(valor)
        else:
          print("eh adicionar")
          if(valor_alterado != "nodata"):
           atual_valor = transforme_json_em_objeto(valor_alterado)
           for valor in atual_valor:
            lista_para_adicionar.append(valor)
        #lista_de_componentes = crud.get_toda_biblioteca_da_informacao_de_hardware(db,informacaohardware)
        print("Alteração detectadao -> "+alt)
        #print("lista para adicionar")
        #print(lista_para_adicionar)
        #print("lista para remover")
        #print(lista_para_remover)
        if(alt == "dados_de_disco"):
          atual_valor = filtrar_componentes_de_hardware(atual_valor,"disco")
          if (antigo_valor != "nodata"):
           antigo_valor = filtrar_componentes_de_hardware(antigo_valor,"disco")
           lista_para_remover = filtrar_componentes_de_hardware(lista_para_remover,"disco")
          lista_para_adicionar = filtrar_componentes_de_hardware(lista_para_adicionar,"disco")
          
          print("alteracao de disco") 

          if (antigo_valor != "nodata"):
           for disco_rem in antigo_valor:
           
            esquema_disco = criar_esquema_biblioteca_hardware(disco_rem,"disco")
            crud.remove_componente_nos_dados_de_hardware(db,esquema_disco,dados_de_hardware_no_banco)
            print("removido -> " + str(esquema_disco))
          
          for disco_add in atual_valor:

            esquema_disco = criar_esquema_biblioteca_hardware(disco_add,"disco")
            crud.adicione_componente_nos_dados_de_hardware(db,esquema_disco,dados_de_hardware_no_banco)
            print("adicionado -> " + str(esquema_disco))

      
            
          for disco_alt_add in lista_para_adicionar:
            if (antigo_valor != "nodata"):
             crud.criar_documento_de_alteracao(db,"hardware","disco","[ADICIONADO][DISCO] -> "+str(disco_alt_add)+" no computador [" + str(dados_do_ativo_na_busca.hostname) + "] [REGISTRO ATUALIZADO]",dados_do_ativo_na_busca)  
          for disco_alt_rem in lista_para_remover:
            crud.criar_documento_de_alteracao(db,"hardware","disco","[REMOVIDO][DISCO] -> "+str(disco_alt_rem)+" no computador [" + str(dados_do_ativo_na_busca.hostname) + "] [REGISTRO ATUALIZADO]",dados_do_ativo_na_busca)  
            
           
          
        if(alt == "dados_de_memoria"):
          print("alteracao de memoria")
          atual_valor = filtrar_componentes_de_hardware(atual_valor,"memoria")
          if (antigo_valor != "nodata"):
           antigo_valor = filtrar_componentes_de_hardware(antigo_valor,"memoria")
           lista_para_remover = filtrar_componentes_de_hardware(lista_para_remover,"memoria")
          lista_para_adicionar = filtrar_componentes_de_hardware(lista_para_adicionar,"memoria")
          
          if (antigo_valor != "nodata"):
           for memoria_rem in antigo_valor:
           
            esquema_memoria = criar_esquema_biblioteca_hardware(memoria_rem,"memoria")
            crud.remove_componente_nos_dados_de_hardware(db,esquema_memoria,dados_de_hardware_no_banco)
            print("removido -> " + str(esquema_memoria))
          for memoria_add in atual_valor:

            esquema_memoria = criar_esquema_biblioteca_hardware(memoria_add,"memoria")
            
            crud.adicione_componente_nos_dados_de_hardware(db,esquema_memoria,dados_de_hardware_no_banco)
            print("adicionado -> " + str(esquema_memoria))

          for memoria_add_alerta in lista_para_adicionar:
            if (antigo_valor != "nodata"):
             crud.criar_documento_de_alteracao(db,"hardware","memoria","[ADICIONADO][MEMORIA] -> "+str(memoria_add_alerta)+" no computador [" + str(dados_do_ativo_na_busca.hostname) + "] [REGISTRO ATUALIZADO]",dados_do_ativo_na_busca)
            
          for memoria_remove_alerta in lista_para_remover:
            crud.criar_documento_de_alteracao(db,"hardware","memoria","[REMOVIDO][MEMORIA] -> "+str(memoria_remove_alerta)+" no computador [" + str(dados_do_ativo_na_busca.hostname) + "] [REGISTRO ATUALIZADO]",dados_do_ativo_na_busca)
           
        if(alt == "dados_de_gpu"):
          print("alteracao de gpu")
          atual_valor = filtrar_componentes_de_hardware(atual_valor,"gpu")
          if (antigo_valor != "nodata"):
           antigo_valor = filtrar_componentes_de_hardware(antigo_valor,"gpu")
           lista_para_remover = filtrar_componentes_de_hardware(lista_para_remover,"gpu")
          lista_para_adicionar = filtrar_componentes_de_hardware(lista_para_adicionar,"gpu")
          
          
          if (antigo_valor != "nodata"):
           for gpu_rem in antigo_valor:
           
            esquema_gpu = criar_esquema_biblioteca_hardware(gpu_rem,"gpu")
            crud.remove_componente_nos_dados_de_hardware(db,esquema_gpu,dados_de_hardware_no_banco)
            print("removido -> " + str(esquema_gpu))
          
          for gpu_add in atual_valor:

            gpu_add = criar_esquema_biblioteca_hardware(gpu_add,"gpu")
            crud.adicione_componente_nos_dados_de_hardware(db,gpu_add,dados_de_hardware_no_banco)
            print("adicionado -> " + str(gpu_add))


          for gpu_filtrada in lista_para_adicionar:
            try:
              if (antigo_valor != "nodata"):         
               crud.criar_documento_de_alteracao(db,"hardware","gpu","[ADICIONADO][GPU] -> "+str(gpu_filtrada)+" no computador [" + str(dados_do_ativo_na_busca.hostname) + "] [REGISTRO ATUALIZADO]",dados_do_ativo_na_busca)
            except:
              print(" erro de gpu ")
          for gpu_filtrada in lista_para_remover:
            try:       
              crud.criar_documento_de_alteracao(db,"hardware","gpu","[REMOVIDO][GPU] -> "+str(gpu_filtrada)+" no computador [" + str(dados_do_ativo_na_busca.hostname) + "] [REGISTRO ATUALIZADO]",dados_do_ativo_na_busca)
            except:
              print(" erro de gpu ")


        if(alt == "dados_de_processador"):
            print("alteracao de processador")
            novo_processador = valor_alterado
            antigo_processador = valor_no_banco
            novo_processador_json = transforme_json_em_objeto(novo_processador)
            
            if (antigo_valor != "nodata"):
             esquema_processador = criar_esquema_biblioteca_hardware(antigo_processador,"processador")
             crud.criar_documento_de_alteracao(db,"hardware","processador","[REMOVIDO][PROCESSADOR] -> "+str(antigo_processador)+" no computador [" + str(dados_do_ativo_na_busca.hostname) + "] [REGISTRO ATUALIZADO]",dados_do_ativo_na_busca)
             crud.remove_componente_nos_dados_de_hardware(db,esquema_processador,dados_de_hardware_no_banco)
          
            if (antigo_valor != "nodata"):
             esquema_processador = criar_esquema_biblioteca_hardware(novo_processador,"processador")
             esquema_processador.nome_monitoramento = novo_processador_json[0]['name']
             crud.criar_documento_de_alteracao(db,"hardware","processador","[ADICIONADO][PROCESSADOR] -> "+str(novo_processador)+" no computador [" + str(dados_do_ativo_na_busca.hostname) + "] [REGISTRO ATUALIZADO]",dados_do_ativo_na_busca)
             crud.adicione_componente_nos_dados_de_hardware(db,esquema_processador,dados_de_hardware_no_banco)


        if(alt == "dados_de_placamae"):
            print("alteracao de placamae")
            nova_placa_mae = valor_alterado
            antiga_placamae = valor_no_banco
            nova_placa_mae_json = transforme_json_em_objeto(nova_placa_mae)
            
            if (antigo_valor != "nodata"):
             esquema_mobo = criar_esquema_biblioteca_hardware(antiga_placamae,"placamae")
             crud.criar_documento_de_alteracao(db,"hardware","processador","[REMOVIDO][PLACAMAE] -> "+str(antiga_placamae)+" no computador [" + str(dados_do_ativo_na_busca.hostname) + "] [REGISTRO ATUALIZADO]",dados_do_ativo_na_busca)
             crud.remove_componente_nos_dados_de_hardware(db,esquema_mobo,dados_de_hardware_no_banco)
          
            if (antigo_valor != "nodata"):
             esquema_mobo = criar_esquema_biblioteca_hardware(nova_placa_mae,"placamae")
             esquema_mobo.nome_monitoramento = nova_placa_mae_json[0]['name']
             crud.criar_documento_de_alteracao(db,"hardware","processador","[ADICIONADO][PLACAMAE] -> "+str(nova_placa_mae)+" no computador [" + str(dados_do_ativo_na_busca.hostname) + "] [REGISTRO ATUALIZADO]",dados_do_ativo_na_busca)
             crud.adicione_componente_nos_dados_de_hardware(db,esquema_mobo,dados_de_hardware_no_banco)
       
            
      else:
        print("entrou no else")
        print(dados_do_ativo_na_busca.hostname)
        print("nodata ou falha nos dados")
        return False
      

    return True

def analise_estatisticas_de_uso(db):
    start = time.time()
    total_de_ativos_verificados = 0
    total_de_ativos_com_problema = 0
    dicionario_de_retorno = {}
    lista_de_ativos = []
    lista_de_computadores_sem_uso = []
    
    dicionario_de_retorno['valor_do_kwh'] = 0.72
    dicionario_de_retorno['gasto_total'] = 0
    dicionario_de_retorno['gasto_efetivo_total'] = 0
    dicionario_de_retorno['desperdicio_total'] = 0
    dicionario_de_retorno['total_computadores_sem_uso'] = 0
    dicionario_de_retorno['total_energia_gasto_computadores_sem_uso'] = 0
    dicionario_de_retorno['lista_computadores_sem_uso'] = 0

    dicionario_de_retorno['lista_de_computadores_sem_uso'] = lista_de_computadores_sem_uso
    dicionario_de_retorno['lista_de_ativos'] = lista_de_ativos


    total_sala_1 = 0
    efetivo_sala_1 = 0
    total_sala_2 = 0
    efetivo_sala_2 = 0
    total_sala_3 = 0
    efetivo_sala_3 = 0


    ativos_no_banco = crud.get_ativos(db)
    for ativo_no_banco in ativos_no_banco:
        total_de_ativos_verificados = total_de_ativos_verificados + 1  

        patrimonio = ativo_no_banco.patrimonio
        informacao_de_hardware = crud.get_informacao_de_hardware_do_ativo(db,patrimonio)
        potencia_memoria = informacao_de_hardware.quantidade_de_memorias * 2
        potencia_discos = informacao_de_hardware.quantidade_de_discos * 3
        potencia_pecas = potencia_memoria + potencia_discos + 15 #15 watts da placa mae
        valor_kwh = dicionario_de_retorno['valor_do_kwh']

        uso_real = zabbix_api.busque_usuarios_logados_trinta_dias2(patrimonio)
        total_de_minutos_29_dias = uso_real['uptime_30_total_dias_coletados'] * 1440
        total_minutos_hoje = uso_real['uptime_hoje'] * 60
        
        total_de_minutos = total_de_minutos_29_dias + total_minutos_hoje
        potencia_desktop = uso_real['media_consumo_30_dias_em_watts'] + int(potencia_pecas) * 1.1 #gasto de energia da fonte
        total_de_minutos_ligado = total_de_minutos * uso_real['media_uptime_30_dias']
        total_de_minutos_ligado_em_porcentagem = uso_real['media_uptime_30_dias'] * 100
        
        total_de_uso_em_minutos_30_dias = 0
        lista_de_usuarios = list(uso_real['lista_usuarios'])
        
        
        totaldias = 0
        for key, value in uso_real['dicionario_dias'].items():
            #print("executando a chave")
            #print(key)
            if isinstance(value, dict):
                teste = value[max(value, key=value.get)]
                total_de_uso_em_minutos_30_dias = total_de_uso_em_minutos_30_dias + teste
                #print("adicionei total dias")
                totaldias = totaldias + 1
        calculo_de_energia_consumida = round((potencia_desktop / 1000) * (int(total_de_minutos_ligado) / 60),2)
        calculo_de_energia_efetiva = round((potencia_desktop / 1000) * (int(total_de_uso_em_minutos_30_dias) / 60),2)
        calculo_de_energia_desperdicada = calculo_de_energia_consumida - calculo_de_energia_efetiva    
        if (calculo_de_energia_consumida > 0):
            
            porcentagem_desperdicio = (calculo_de_energia_desperdicada * 100) / calculo_de_energia_consumida

            dicionario_do_ativo = {}
            dicionario_do_ativo['patrimonio'] = ativo_no_banco.hostname
            dicionario_do_ativo['horas_ligado'] = str(round(int(total_de_minutos_ligado) / 60))
            dicionario_do_ativo['horas_em_uso_efetivo'] = str(round(int(total_de_uso_em_minutos_30_dias) / 60)) 
            dicionario_do_ativo['porcentagem_tempo_ligado'] = str(round(int(total_de_minutos_ligado_em_porcentagem))) + "%"
            dicionario_do_ativo['pocentagem_desperdicio'] = str(round(porcentagem_desperdicio) ) + "%"
            dicionario_do_ativo['desperdicio_em_reais'] = "R$ "+ str(round(calculo_de_energia_desperdicada * valor_kwh,2))
            string_usuarios = ""
            for usuario in lista_de_usuarios:
              string_usuarios = usuario + " " + string_usuarios

            dicionario_do_ativo['lista_de_usuarios'] = string_usuarios
            if (ativo_no_banco.local == "EAS"):
              total_sala_1 = total_sala_1 + round(int(total_de_minutos_ligado) / 60)
              efetivo_sala_1 = efetivo_sala_1 + round(int(total_de_uso_em_minutos_30_dias) / 60)
            if (ativo_no_banco.local == "EBS"):
              total_sala_2 = total_sala_2 + round(int(total_de_minutos_ligado) / 60)
              efetivo_sala_2 = efetivo_sala_2 + round(int(total_de_uso_em_minutos_30_dias) / 60)
            if (ativo_no_banco.local == "EBQ"):
              total_sala_3 = total_sala_3 + round(int(total_de_minutos_ligado) / 60)
              efetivo_sala_3 = efetivo_sala_3 + round(int(total_de_uso_em_minutos_30_dias) / 60)

            dicionario_de_retorno['gasto_total'] = round(dicionario_de_retorno['gasto_total'] + (calculo_de_energia_consumida * valor_kwh),2)
            dicionario_de_retorno['gasto_efetivo_total'] = round(dicionario_de_retorno['gasto_efetivo_total'] + (calculo_de_energia_efetiva * valor_kwh),2) 
            dicionario_de_retorno['desperdicio_total'] = round(dicionario_de_retorno['desperdicio_total'] + (calculo_de_energia_desperdicada * valor_kwh),2)

            if (porcentagem_desperdicio > 97):
              dicionario_de_retorno['total_computadores_sem_uso'] = dicionario_de_retorno['total_computadores_sem_uso'] + 1
              dicionario_de_retorno['total_energia_gasto_computadores_sem_uso'] = round(dicionario_de_retorno['total_energia_gasto_computadores_sem_uso'] + calculo_de_energia_consumida,2)
              lista_de_computadores_sem_uso.append(ativo_no_banco.hostname)
        else:
          total_de_ativos_com_problema = total_de_ativos_com_problema + 1      
        lista_de_ativos.append(dicionario_do_ativo)  
        
    end = time.time()
    print("Verificação concluída em " + str(round(end - start)) + " Segundos")

    dicionario_sala_1 = {"total": round((total_sala_1 - efetivo_sala_1) / 24), "efetivo": round((efetivo_sala_1) / 24)}
    dicionario_sala_2 = {"total": round((total_sala_2 - efetivo_sala_2) / 24), "efetivo": round((efetivo_sala_2) / 24)}
    dicionario_sala_3 = {"total": round((total_sala_3 - efetivo_sala_3) / 24), "efetivo": round((efetivo_sala_3) / 24)}
    
    
    
    dicionario_de_retorno['uso_sala_1'] = dicionario_sala_1
    dicionario_de_retorno['uso_sala_2'] = dicionario_sala_2
    dicionario_de_retorno['uso_sala_3'] = dicionario_sala_3




    resultado = json.dumps(dicionario_de_retorno)
    estatistica_de_uso_mensal = db.query(models.estatistica).filter(models.estatistica.tipo == "uso").first()
    trinta_dias = date.today() - timedelta(days=30)
    if (estatistica_de_uso_mensal):
      estatistica_de_uso_mensal.resultado = resultado
      estatistica_de_uso_mensal.total_ativos_verificados = total_de_ativos_verificados
      estatistica_de_uso_mensal.total_ativos_com_problema = total_de_ativos_com_problema
      estatistica_de_uso_mensal.data_execucao = datetime.datetime.now().strftime("%d/%m/%Y")
      estatistica_de_uso_mensal.periodo_da_estatistica =  str(trinta_dias.strftime("%d/%m/%Y")) + ' - ' + str(datetime.datetime.now().strftime("%d/%m/%Y"))
      estatistica_de_uso_mensal.tempo_execucao_segundos = str(round(end - start))
      db.commit()  
    else:
      novo_ativo_de_software = models.estatistica(tipo="uso",resultado=resultado,total_ativos_verificados=total_de_ativos_verificados,total_ativos_com_problema=total_de_ativos_com_problema,data_execucao=datetime.datetime.now(),periodo_da_estatistica=str(trinta_dias.strftime("%d/%m/%Y")) + ' - ' + str(datetime.datetime.now().strftime("%d/%m/%Y")),tempo_execucao_segundos=str(round(end - start)))
      db.add(novo_ativo_de_software)
      db.commit()  

    return resultado



def executar_analise(db):    
    start = time.time()
    arquivo_de_configuracao = open('configuracao.json')
    conf_in_json = json.load(arquivo_de_configuracao)
    grupos_de_ativos = conf_in_json['grupos_de_busca_por_tipo']
     
    #grupoDesktop = grupos_de_ativos['DESKTOP'] 
    grupoDesktop = 81 #39web #52tudo #34 #37 #43 #35 #52 
    #52 #80 =-TCC
    criar_alertas(db)
    analisar_desktops(db,grupoDesktop)

    
    end = time.time()
    print("Verificação concluída em " + str(round(end - start)) + " Segundos")
    return "update com sucesso"

def atualizar_flag_de_estado(db,dados_do_ativo_na_busca,status_do_ativo):
  #print("status do ativo eh")
  print(status_do_ativo)
  ativo_no_banco = crud.get_ativo_por_patrimonio(
                    db, dados_do_ativo_na_busca.patrimonio
                )
  if ativo_no_banco:
    ativo_no_banco.status = status_do_ativo
    crud.atualize_ativo(db, ativo_no_banco)

  if status_do_ativo == "ocioso":
    remover_do_monitoramento(db, dados_do_ativo_na_busca)


  return 0

def atualize_dados_do_ativo(db,ativo_no_banco,ativo_na_busca):
  print("Atulizando os dados principais do ativo")
  #if ativo_no_banco.endereco_ip != ativo_na_busca.endereco_ip:
      #remover_do_monitoramento(db,ativo_no_banco)
  alteracoes = models.ativo_hardware.alteracao(
      ativo_no_banco, ativo_na_busca
  )
  for alteracao in alteracoes:
      if ativo_na_busca.hostname and alteracao == "hostname":
          crud.criar_documento_de_alteracao(
              db,
              "configuracao",
              "hostname",
              "[ALTERAÇÃO][HOSTNAME] -> "
              + str(ativo_no_banco.hostname)
              + " Foi alterado para ["
              + str(ativo_na_busca.hostname)
              + "] [REGISTRO ATUALIZADO]",
              ativo_na_busca,
          )
      if ativo_na_busca.status and alteracao == "status":
          crud.criar_documento_de_alteracao(
              db,
              "configuracao",
              "hostname",
              "[ALTERAÇÃO][STATUS] -> "
              + str(ativo_no_banco.status)
              + " Foi alterado para ["
              + str(ativo_na_busca.status)
              + "] [REGISTRO ATUALIZADO]",
              ativo_na_busca,
          )
      if ativo_na_busca.local and alteracao == "local":
          crud.criar_documento_de_alteracao(
              db,
              "configuracao",
              "local",
              "[ALTERAÇÃO][LOCAL] -> "
              + str(ativo_no_banco.hostname)
              + " Foi movido para ["
              + str(ativo_na_busca.local)
              + "] [REGISTRO ATUALIZADO]",
              ativo_na_busca,
          )
      if alteracao == "endereco_mac":
          crud.criar_documento_de_alteracao(
              db,
              "configuracao",
              "endereco_mac",
              "[ALTERAÇÃO][MAC] -> "
              + str(ativo_no_banco.endereco_mac)
              + " Foi alterado para ["
              + str(ativo_na_busca.endereco_mac)
              + "] "+ str(ativo_na_busca.hostname) + " [REGISTRO ATUALIZADO]",
              ativo_na_busca,
          )
      

  crud.atualize_ativo_total(
      db, ativo_no_banco, ativo_na_busca
  )



  return 0

def atualize_dados_de_hardware_do_ativo(db,dados_de_hardware_no_banco,hardware_na_busca,ativo_no_banco):
  
  lista_de_componentes = crie_lista_de_componentes(
      db, hardware_na_busca
  )
  alertas = criar_alertas_de_alteracao_de_hardware(
      db,
      ativo_no_banco,
      dados_de_hardware_no_banco,
      hardware_na_busca,
  )
  
  atualizacao = crud.atualize_informacao_hardware(
          db,
          hardware_na_busca,
          ativo_no_banco,
          lista_de_componentes,
      )

  return atualizacao

def atualize_dados_de_sistema_do_ativo(db,sistema_no_banco,sistema_na_busca,ativo_no_banco):

  alteracoes = models.informacao_sistema.alteracao(
      sistema_no_banco, sistema_na_busca
  )
  
  #for alt in alteracoes:
   #   print(str(alt))

  crud.atualize_informacao_sistema(
      db, sistema_na_busca, ativo_no_banco
  )
  return 0

def remover_do_monitoramento(db,dados_do_host):
  zabbix_api.removehost(dados_do_host)
  try:                
    crud.criar_alerta_monitoramento(
        db,
        dados_do_host.zabbix_id,
        dados_do_host.hostname,
        "REM",
    )
  except:
    
    crud.criar_alerta_monitoramento(
        db, dados_do_host.zabbix_id, "", "REM"
    )

  return 0

def analisar_desktops(db, grupo_o):
    start = time.time()
    hosts_cadastrados = 0
    hosts_verificados = 0
    hosts_atualizados = 0
    hosts_com_erro = 0
    hosts_nao_atualizados = 0

    hosts_monitorados = zabbix_api.busca_lista_todos_ativos_zabbix(grupo_o)
    for host in hosts_monitorados:
        coletar_dados_do_ativo = zabbix_api.busca_ativo_monitorado_zabbix(
            "hostid", host['hostid']
        )

        sucesso_na_busca = coletar_dados_do_ativo.status
        dados_do_ativo_na_busca = coletar_dados_do_ativo.dados_do_ativo
        dados_de_hardware_na_busca = coletar_dados_do_ativo.dados_de_hardware
        dados_de_sistema_na_busca = coletar_dados_do_ativo.dados_de_sistema
        dados_de_software_na_busca = coletar_dados_do_ativo.dados_de_software
        mensagem_da_busca = coletar_dados_do_ativo.mensagem_da_busca
        status_do_ativo = "operacional"
        tempo_de_inatividade_em_dias = 0
    #    print("dados de software")
        lista_de_softwares = []
        lista_de_softwares.append(criar_softwares_na_busca(dados_de_sistema_na_busca.sistema_operacional.lower(),dados_de_sistema_na_busca.sistema_operacional.lower(),dados_de_sistema_na_busca.sistema_operacional.lower(),dados_de_sistema_na_busca.dados_de_versao,""))
        try:
         lista_de_dicionarios_de_software = transforme_json_em_objeto(dados_de_software_na_busca)
     #    print("deu bom")
        except:
      #   print("deu ruim")
         lista_de_dicionarios_de_software = "nodata" 


       # print (type(lista_de_dicionarios_de_software))
        if isinstance(lista_de_dicionarios_de_software, list):
         
         #dicionario_de_software = transforme_json_em_objeto(dados_de_software_na_busca)
         for software in lista_de_dicionarios_de_software:
         
         
          
          nome_do_software = software['displayname']
          nome_do_software = nome_do_software.replace("versao", "")
          nome_do_software = nome_do_software.replace("version", "")
          nome_do_software = nome_do_software.replace("release", "")

          nome_do_software = re.sub('\D[v]\d{1}', '0', nome_do_software)
          nome_do_software = re.sub('\d{1,5}\..*$', '', nome_do_software)
          nome_do_software = re.sub('\(.*$', '', nome_do_software)
          nome_do_software = re.sub('[^a-zA-Z0-9+\s.]', '', nome_do_software)
          nome_do_software = re.sub('\s{2,}', ' ', nome_do_software)
          identificador_do_software = re.sub('[^a-zA-Z0-9+.]', '', nome_do_software)

          lista_de_softwares.append(criar_softwares_na_busca(identificador_do_software,nome_do_software,software['publisher'],software['displayversion'],software['installdate']))
        
        # Verificacao de inatividade, caso o ativo esteja a mais de 15 dias sem contato e gerado um alerta para verificacao
        # 30 dias sem contato eh removido do monitoramento e considerado ocioso
        if dados_do_ativo_na_busca.ultima_verificacao and dados_do_ativo_na_busca.hostname:
            # print(dados_do_ativo_na_busca.zabbix_id)
            inatividade = verifique_inatividade(
                dados_do_ativo_na_busca.ultima_verificacao
            )
            tempo_de_inatividade_em_dias = inatividade['inatividade_em_dias']
            status_do_ativo = inatividade['flag_de_estado']
            
            atualizar_flag_de_estado(db,dados_do_ativo_na_busca,status_do_ativo)
            
        else:
            remover_do_monitoramento(db,dados_do_ativo_na_busca)
            hosts_com_erro = hosts_com_erro + 1

        if sucesso_na_busca:
        #    print("sucesso na busca")
            dados_da_busca = verifica_dados_validos_host(db, dados_do_ativo_na_busca)
            
            if dados_da_busca['validos']:  # MAC IP PATRIMONIO EQUIPE LOCAL HOSTNAME
                ativo_na_busca = criar_ativo_na_busca(dados_do_ativo_na_busca,status_do_ativo)
                hardware_na_busca = criar_hardware_na_busca(dados_de_hardware_na_busca)
                sistema_na_busca = criar_sistema_na_busca(dados_de_sistema_na_busca)
                ativo_no_banco = crud.get_ativo_por_patrimonio(
                    db, dados_do_ativo_na_busca.patrimonio
                )
         #       print(ativo_na_busca)
                if ativo_no_banco:
                    
                    hosts_verificados = hosts_verificados + 1
                    if ativo_no_banco != ativo_na_busca:
                        atualize_dados_do_ativo(db,ativo_no_banco,ativo_na_busca)
                    
                    crud.atualizar_softwares_do_ativo(db,lista_de_softwares,ativo_no_banco)
                    #verifica dados de sistema
                    if sistema_na_busca:
                        sistema_no_banco = crud.get_informacao_de_sistema_do_ativo(
                            db, ativo_no_banco.patrimonio
                        )
                        if sistema_no_banco:
                            if sistema_no_banco != sistema_na_busca:
                              atualize_dados_de_sistema_do_ativo(db,sistema_no_banco,sistema_na_busca,ativo_no_banco)
                                
                        else:
                            print(" sistema nao esta no banco cadastrando ")
                            crud.criar_informacao_sistema_do_ativo(
                                db, sistema_na_busca, ativo_no_banco
                            )
                    #verifica dados de hardware
                    print("verificando alterações...")
          #          print(tempo_de_inatividade_em_dias)
                    if hardware_na_busca and tempo_de_inatividade_em_dias < 7:
          #              print("esquema hw valido e ativo a 7 dias ou menos")
                        dados_de_hardware_no_banco = (
                            crud.get_informacao_de_hardware_do_ativo(
                                db, ativo_no_banco.patrimonio
                            )
                        )

                        if dados_de_hardware_no_banco:
                            
                            if dados_de_hardware_no_banco != hardware_na_busca:
                              print("alteração de hardware detectada, atualizando...")
                             
                              atualizar_host = atualize_dados_de_hardware_do_ativo(db,dados_de_hardware_no_banco,hardware_na_busca,ativo_no_banco)
                              if(atualizar_host):
                               crud.remove_alerta(db,dados_do_ativo_na_busca.hostname,"HIN")
                               hosts_atualizados = hosts_atualizados + 1
                              else:
                                crud.criar_alerta_monitoramento(
                                db,
                                dados_do_ativo_na_busca.zabbix_id,
                                dados_do_ativo_na_busca.hostname,
                                "HIN",
                                )
                                hosts_com_erro = hosts_com_erro + 1 

                        else:
                            lista_de_componentes = crie_lista_de_componentes(
                                db, hardware_na_busca
                            )
                            crud.criar_informacao_hardware_do_ativo(
                                db,
                                hardware_na_busca,
                                ativo_no_banco,
                                lista_de_componentes,
                            )

                else:
                    novo_ativo = crud.criar_ativo(db, ativo_na_busca)
                    print("NOVO ATIVO -> Cadastrando no sistema")
                    hosts_cadastrados = hosts_cadastrados + 1
                    if sistema_na_busca:
                        print("Criando configurações de sistema")
                        crud.criar_informacao_sistema_do_ativo(
                            db, sistema_na_busca, novo_ativo
                        )
                    if hardware_na_busca:
                        # esquema_monitor = criar_monitor_descoberto(db,dados_de_hardware_no_banco,novo_ativo)
                        print("Criando configurações de hardware")
                        lista_de_componentes = crie_lista_de_componentes(
                            db, hardware_na_busca
                        )
                        if not hardware_na_busca.dados_completos:
                            
                            crud.criar_alerta_monitoramento(
                                db,
                                dados_do_ativo_na_busca.zabbix_id,
                                dados_do_ativo_na_busca.hostname,
                                "HIN",
                            )
                        crud.criar_informacao_hardware_do_ativo(
                            db, hardware_na_busca, novo_ativo, lista_de_componentes
                        )
                    print("Adicionando informações de software")    
                    for esquema in lista_de_softwares:
                      crud.criar_informacao_de_software_do_ativo(db,esquema,novo_ativo,True)    

                if (
                    dados_do_ativo_na_busca.switchmac
                    and ativo_na_busca.tipo != "NB"
                ):
                    verificar_switch_e_conexoes(db, dados_do_ativo_na_busca)
            else:
                print("Dados do ativo incompletos")

        else:
            try:
                ativo_no_banco = crud.get_ativo_por_patrimonio(
                    db, dados_do_ativo_na_busca.patrimonio
                )
                if ativo_no_banco:
                    # log_db = crud.criar_log_erro_verificacao(db,verifique_host[1] + "[Cadastrado]")
                    hosts_com_erro = hosts_com_erro + 1
                    print(dados_do_ativo_na_busca.hostname + "[Cadastrado]")
                else:
                    # log_db = crud.criar_log_erro_verificacao(db,verifique_host[1] +  " [Nao Cadastrado]")
                    hosts_com_erro = hosts_com_erro + 1
                    print(dados_do_ativo_na_busca.hostname + " [Nao Cadastrado]")
            except:
                # log_db = crud.criar_log_erro_verificacao(db,verifique_host[1] +  " [Nao Cadastrado]")
                hosts_com_erro = hosts_com_erro + 1
                print(dados_do_ativo_na_busca.hostname + " [Nao Cadastrado]")
    end = time.time()
    tempo_execucao = end - start
    total_de_ativos = (
        hosts_cadastrados + hosts_verificados + hosts_com_erro
    )
    print(str(total_de_ativos) + " Ativos Encontrados")
    print(str(hosts_cadastrados) + " Ativos Cadastrados")
    print(str(hosts_verificados) + " Ativos Verificados")
    print(str(hosts_atualizados) + " Ativos Atualizados")
    print(str(hosts_com_erro) + " Ativos Com Erros")
    log = crud.criar_log_sistema(
        db,
        total_de_ativos,
        hosts_verificados,
        hosts_atualizados,
        hosts_cadastrados,
        hosts_com_erro,
        int(tempo_execucao),
    )
    # if (hosts_cadastrados > 0):
    # log = crud.criar_log_sucesso_cadastro(db,"[CADASTRO][SISTEMA] " + str(hosts_cadastrados) + " Ativos Cadastrados")
    # print (log.mensagem)
    # if (hosts_atualizados > 0):
    # log = crud.criar_log_sucesso_atualizacao(db,"[ATUALIZACAO][SISTEMA] " + str(hosts_atualizados) + " Ativos Atualizados")
    # print (log.mensagem)
    # if (hosts_verificados > 0):
    # log = crud.criar_log_sucesso_verificacao(db,"[VERIFICACAO][SISTEMA] " + str(hosts_verificados) + " Ativos Verificados")
    # print (log.mensagem)
    # if (hosts_com_erro > 0):
    # log = crud.criar_log_sucesso_verificacao(db,"[VERIFICACAO][SISTEMA] " + str(hosts_com_erro) + " Ativos com problema")
    # print (log.mensagem)

    return 0

  #regras de extracao de features necessarias para salvar um componente no database

# filter hardware components



def filtrar_componentes_de_hardware(lista_de_componentes,tipo):
  filtro_gpu = ["adaptercompatibility","name","videoprocessor"]
  filtro_memoria = ["capacity","memorytype","speed"]
  filtro_disco = ["model","size"]
  lista_de_componentes_filtrados = []
  for componente in lista_de_componentes:
    if(tipo == "gpu"):
      try:
        gpu_json = json.loads(componente)
        gpu_filtrada = dict((x, y) for x, y in gpu_json.items() if x in filtro_gpu)
        json_gpu_filtrada = transforme_objeto_em_json(gpu_filtrada)
        lista_de_componentes_filtrados.append(json_gpu_filtrada)       
      except:
        print(" erro de dados de gpu ")
    if(tipo == "memoria"):
      try:
        memoria_filtrada = dict((x, y) for x, y in componente.items() if x in filtro_memoria)
        memoria_filtrada['capacity'] = zabbix_api.memoria_bytes_to_gb(int(memoria_filtrada['capacity']))
        json_memoria_filtrada = transforme_objeto_em_json(memoria_filtrada)
        lista_de_componentes_filtrados.append(json_memoria_filtrada)       
      except:
        print(" erro de dados de memoria ")
    if(tipo == "disco"):
      try:
        disco_filtrado = dict((x, y) for x, y in componente.items() if x in filtro_disco)
        json_disco_filtrado = transforme_objeto_em_json(disco_filtrado)
        lista_de_componentes_filtrados.append(json_disco_filtrado)       
      except:
        print(" erro de dados de disco ")

  return lista_de_componentes_filtrados

def verificar_switch_e_conexoes(db,ativo):
          stack_do_switch = 0
          porta_do_switch = 0
          if (ativo.switchporta):
           info_do_switch = ativo.switchporta
          else:
           if (ativo.switchportadesc):
            info_do_switch = ativo.switchportadesc
           else:
            info_do_switch = ""
          mac_do_switch = ativo.switchmac
          switch_no_db = crud.busque_switch_no_database(db,mac_do_switch)
          try:
           if(switch_no_db.local != ativo.local):
            crud.criar_documento_de_alteracao(db,"configuracao","local","[ALTERAÇÃO][LOCAL] -> "+str(ativo.hostname)+" Está localizado em [" + str(switch_no_db.local) + "] [REGISTRO INCORRETO]",ativo)
            #print("Detecção de local errado, ativo de patrimonio e local -> "+str(ativo.patrimonio)+" " + str(ativo.local) + " esta conectado em switch localizado -> " + str(switch_no_db.local)) 
          except:
            print("exceção de switch no -> " + str(ativo.patrimonio))
          #verifique porta e stack
          #print(len(info_do_switch))
          if(len(info_do_switch) > 0 and len(info_do_switch) < 3):
            stack_do_switch = '1'
            porta_do_switch = info_do_switch
            #print("0 a 2 " + porta_do_switch + " --> " + stack_do_switch)

          if(len(info_do_switch) > 2 and len(info_do_switch) < 5):
             stack_do_switch = info_do_switch[0]
             porta_do_switch = info_do_switch[2:4]
             #print("0 - 3 " + porta_do_switch + " --> " + stack_do_switch)
          
          if(len(info_do_switch) > 5):
            
            digitos = ''.join(n for n in info_do_switch if n.isdigit())
            if (len(digitos) > 0):
             stack_do_switch = digitos[0]
             porta_do_switch = digitos[2:10]
             #print("> 5 " + porta_do_switch + " --> " + stack_do_switch)            

          if (switch_no_db):
            if(ativo.patrimonio):
             porta_no_db = crud.get_porta_no_db(db,switch_no_db,info_do_switch)
            
             if(porta_no_db):
               #print ("porta existe")
               if(porta_no_db.ativo_pat != ativo.patrimonio):
                 #print ("ativo diferente - atualizando")
                 crud.atualize_porta(db,switch_no_db,ativo.patrimonio,porta_no_db)
             else:  #porta existe
               #print ("criando porta inexistente")    #atualizar os dados da porta

              #porta nao existe
               if(porta_do_switch != 0):
                crud.criar_porta_switch(db,switch_no_db,ativo.patrimonio,info_do_switch,porta_do_switch,stack_do_switch)
            
          else :
            esquema_switch = criar_esquema_switch(mac_do_switch,ativo.switchnome,ativo.local)
            if(esquema_switch and porta_do_switch != 0):
             crud.criar_switch(db,esquema_switch)
             print("switch novo cadastrado") 

          return 0


def remove_discos_invalidos(dados_disco):
  discos = transforme_json_em_objeto(dados_disco)
  lista_discos = []

  for disco in discos:
     if 'deviceid' in disco:
      del disco['deviceid']
     if (disco['model'].lower().find("usb") == -1 and disco['model'].lower().find("qemu") == -1 and disco['model'].lower().find("card") == -1 and disco['model'].lower().find("slim") == -1 and disco['model'].lower().find("portable") == -1  ):
      lista_discos.append(disco)
  return transforme_objeto_em_json(lista_discos)

def verifica_dados_validos_host(db,host):
     mensagem = "[HOST][PROBLEMA]"
     dados = {}
     dados['validos'] = True
     dados['mensagem'] = mensagem
     try:
      patrimonio = host.patrimonio
      hostname = host.hostname
      mensagem = mensagem + hostname
      if (not verifica_patrimonio_valido(patrimonio)):
          mensagem = mensagem + " - Patrimonio Incorreto" + patrimonio
          
          crud.criar_alerta_monitoramento(db,host.zabbix_id,hostname,"HFP")
          #remover_do_monitoramento(db, host)
          dados['validos']=False

      if (not verifica_mac_valido(host.endereco_mac) and not verifica_mac_valido(host.endereco_mac2) ):
          mensagem = mensagem + " - MAC Inválido" + host.endereco_mac
          
          dados['validos'] = False
          
     except:
       dados['validos'] = False
     return dados

def criar_ativo_na_busca(dados_ativo_zabbix,status_do_ativo):
   ativo_criado = schemas.ativo_hardware_base(zabbix_id="",cmdb_id="",quem_cadastrou="",monitorado="",tipo="",ciclo_de_vida="",status="",endereco_mac="",patrimonio="",hostname="",equipe="",local="",endereco_ip="")
   try: 
    ativo_criado.zabbix_id = dados_ativo_zabbix.zabbix_id
    ativo_criado.quem_cadastrou = "sistema"
    ativo_criado.monitorado = "sim"
    ativo_criado.cmdb_id = ""
    ativo_criado.endereco_mac = dados_ativo_zabbix.endereco_mac
    if (verifica_mac_valido(dados_ativo_zabbix.endereco_mac)):
      ativo_criado.endereco_mac = dados_ativo_zabbix.endereco_mac
    else:
      if(verifica_mac_valido(dados_ativo_zabbix.endereco_mac2)):
        ativo_criado.endereco_mac = dados_ativo_zabbix.endereco_mac2
        #print(ativo_criado.endereco_mac)
    if (verifica_ip_valido(dados_ativo_zabbix.endereco_ip)):
      ativo_criado.endereco_ip = dados_ativo_zabbix.endereco_ip
    else:
      ativo_criado.endereco_ip = '0.0.0.0'  
    ativo_criado.ciclo_de_vida = "operação"
    ativo_criado.status = status_do_ativo
    ativo_criado.tipo = "desktop"
    if dados_ativo_zabbix.hostname.find("NB") != -1:
      ativo_criado.tipo = "notebook"
    ativo_criado.patrimonio = dados_ativo_zabbix.patrimonio
    ativo_criado.hostname = dados_ativo_zabbix.hostname
    ativo_criado.equipe = dados_ativo_zabbix.equipe
    ativo_criado.local = dados_ativo_zabbix.local
   except:
     print('Impossível cadastrar ativo')
     ativo_criado = None
   return ativo_criado

def criar_sistema_na_busca(dados_sistema_ativo_zabbix):
   esquema_de_sistema = schemas.informacao_sistema_base(sistema_operacional="",dados_de_administradores="",dados_de_antivirus="",dados_de_versao="",dados_de_update="")
   try: 
    esquema_de_sistema.sistema_operacional = dados_sistema_ativo_zabbix.sistema_operacional
    esquema_de_sistema.dados_de_administradores = dados_sistema_ativo_zabbix.dados_de_administradores
    esquema_de_sistema.dados_de_antivirus = dados_sistema_ativo_zabbix.dados_de_antivirus
    esquema_de_sistema.dados_de_versao = dados_sistema_ativo_zabbix.dados_de_versao
    esquema_de_sistema.dados_de_update = dados_sistema_ativo_zabbix.dados_de_update
   except:
     print('Impossível criar informação de sistema')
     esquema_de_sistema = None
   return esquema_de_sistema

def criar_softwares_na_busca(identificador,nome_software,publisher,versao_instalada,data_instalacao):
   esquema_de_software = schemas.informacao_de_software_base(identificador="",nome_software="",publisher="",versao_instalada="",data_instalacao="")
   try:
    esquema_de_software.identificador = identificador 
    esquema_de_software.nome_software = nome_software
    esquema_de_software.publisher = publisher
    esquema_de_software.versao_instalada = versao_instalada
    esquema_de_software.data_instalacao = data_instalacao
   except:
     print('Impossível criar informação de software')
     esquema_de_software = None
   return esquema_de_software


def criar_hardware_na_busca(dados_hw_ativo_zabbix):
    info_hw_criado = schemas.informacao_hardware_base(dados_de_processador="",dados_de_placamae="",dados_de_disco="",dados_de_gpu="",dados_de_memoria="",dados_de_memoria_total_em_gb=0,quantidade_de_discos=0,quantidade_de_memorias=0,dados_completos=True)
   #try:
    if (dados_hw_ativo_zabbix.dados_de_processador == "nodata"):
      #print ("sem dados processador")
      info_hw_criado.dados_completos = False
      info_hw_criado.dados_de_processador = dados_hw_ativo_zabbix.dados_de_processador
    else:  
     info_hw_criado.dados_de_processador = dados_hw_ativo_zabbix.dados_de_processador
    if (dados_hw_ativo_zabbix.dados_de_placamae == "nodata"):
      #print ("sem dados mobo")
      info_hw_criado.dados_completos = False
      info_hw_criado.dados_de_placamae = dados_hw_ativo_zabbix.dados_de_placamae
    else:
     info_hw_criado.dados_de_placamae = dados_hw_ativo_zabbix.dados_de_placamae  
    if (dados_hw_ativo_zabbix.dados_de_disco == "nodata"):
      #print ("sem dados dados_de_disco")
      info_hw_criado.dados_completos = False
      info_hw_criado.dados_de_disco = dados_hw_ativo_zabbix.dados_de_disco
    else: 
     info_hw_criado.dados_de_disco = remove_discos_invalidos(dados_hw_ativo_zabbix.dados_de_disco)
    
    if (dados_hw_ativo_zabbix.dados_de_gpu == "nodata" or "basic display adapter" in dados_hw_ativo_zabbix.dados_de_gpu):
      print ("sem dados dados_de_gpu")
      info_hw_criado.dados_completos = False
      info_hw_criado.dados_de_gpu = "nodata"
    else:
     print ("dados_de_gpu")
     print(dados_hw_ativo_zabbix.dados_de_gpu)
     info_hw_criado.dados_de_gpu = dados_hw_ativo_zabbix.dados_de_gpu
    if (dados_hw_ativo_zabbix.dados_de_memoria == "nodata"):
      #print ("sem dados dados_de_memoria")
      info_hw_criado.dados_completos = False
      info_hw_criado.dados_de_memoria = dados_hw_ativo_zabbix.dados_de_memoria
    else:
     info_hw_criado.dados_de_memoria = dados_hw_ativo_zabbix.dados_de_memoria
    if (dados_hw_ativo_zabbix.dados_de_memoria_total_em_gb == 0):
      #print ("sem dados dados_de_memoria_total_em_gb")
      info_hw_criado.dados_completos = False
      info_hw_criado.dados_de_memoria_total_em_gb = dados_hw_ativo_zabbix.dados_de_memoria_total_em_gb
    else:
     info_hw_criado.dados_de_memoria_total_em_gb = dados_hw_ativo_zabbix.dados_de_memoria_total_em_gb
    if (dados_hw_ativo_zabbix.dados_de_disco == "nodata"):
      #print ("sem dados dados_de_disco")
      info_hw_criado.dados_completos = False
      info_hw_criado.quantidade_de_discos = 0
    else: 
     info_hw_criado.quantidade_de_discos = len(transforme_json_em_objeto(info_hw_criado.dados_de_disco))
    if (dados_hw_ativo_zabbix.quantidade_de_memorias == 0):
      #print ("sem dados quantidade_de_memorias")
      info_hw_criado.dados_completos = False
      info_hw_criado.quantidade_de_memorias = 0
    else: 

     info_hw_criado.quantidade_de_memorias = dados_hw_ativo_zabbix.quantidade_de_memorias
   #except:
    # info_hw_criado = None
    return info_hw_criado

def criar_monitor_descoberto(db,dados_hw_ativo_zabbix,dados_ativo):
   info_monitor_descoberto = schemas.monitor_descoberto_base(identificador="",serial="",fabricante="",modelo="",ativo_id=dados_ativo.id)
   #print(dados_hw_ativo_zabbix.dados_de_tela)
   
   try:
    if(dados_hw_ativo_zabbix.dados_de_tela):
     dados_de_tela_json = transforme_json_em_objeto(dados_hw_ativo_zabbix.dados_de_tela)
     listateste = ["instancename","userfriendlyname","fabricante"]
     for tela in dados_de_tela_json:
      
      discos_filtrado = dict((x, y) for x, y in tela.items() if x in listateste)
      modelo_extraido = str(discos_filtrado['instancename'])
      modelo_extraido = modelo_extraido.replace("\\","$$$")
      modelo_extraido = modelo_extraido.split("$$$")

      discos_filtrado['instancename'] = modelo_extraido[1][0:6]
      userfrin = discos_filtrado['userfriendlyname']
      discos_filtrado['userfriendlyname'] = modelo_extraido[1][3:6]
      discos_filtrado['fabricante'] = modelo_extraido[1][0:3]
      #print(modelo_extraido[1])
      #print(discos_filtrado['instancename'])
      dumpdisk = transforme_objeto_em_json(discos_filtrado)
      #print(dumpdisk)
      #print("entrou no for")
      discos_db = crud.busque_componente_biblioteca_detalhes(db,dumpdisk)
      
      if (not discos_db):
        #print("not db")
        esquema_disco = criar_esquema_biblioteca_hardware(dumpdisk,"monitor")
          #print (discos_filtrado['Model'])
          #print (discos_filtrado['Model'].lower().find("usb"))  
        esquema_disco.nome_monitoramento = discos_filtrado['fabricante']+" "+modelo_extraido[1]+" "+userfrin
        discos = crud.crie_componente_biblioteca_hardware(db,esquema_disco)
        
      else:
        crud.adicione_unidade_de_componente_biblioteca_hardware(db,discos_db)            
        #print ("tela ja existia add")
      #print(tela['fabricante'])
    
   except:
     info_monitor_descoberto = None
     #print ("excecao")
   return info_monitor_descoberto

def criar_esquema_switch(mac,modelo,local):
   db_switch = schemas.switch_base(mac="",modelo="",local="",stack="",regexporta="")
   try:
    db_switch.mac = mac
    db_switch.modelo = modelo
    db_switch.local = local
    db_switch.stack = ""
    db_switch.regexporta = ""

   except:
     db_switch = None
   return db_switch



def criar_esquema_biblioteca_hardware(componente,tipo):
    
    db_componente = schemas.biblioteca_hardware_base(cmdb_id="",cmdb_typeid="",tipo="",nome_monitoramento="",detalhes="")
    try:
      db_componente.tipo = tipo
      db_componente.detalhes = componente
      
    except:
      db_componente = None
    return db_componente
     

def verifica_patrimonio_valido(patrimonio):
  retorno = False
  
  if (len(patrimonio)==6 and int(patrimonio)):
    retorno = True 
  
  return retorno


def verifica_mac_valido(str):
 
    regex = ("^([0-9A-Fa-f]{2}[:-])" +
             "{5}([0-9A-Fa-f]{2})|" +
             "([0-9a-fA-F]{4}\\." +
             "[0-9a-fA-F]{4}\\." +
             "[0-9a-fA-F]{4})$")
    p = re.compile(regex)
 
    if (str == None):
        return False
    if(re.search(p, str)):
        return True
    else:
        return False

def verifica_ip_valido(endereco_ip):
    try: 
        socket.inet_aton(endereco_ip)
        return True
    except:
        return False

def get_json_status_icmp_todos_ativos(db):
  inicio = time.time()
  lista_ativos_banco = crud.get_lista_zabbixid_ativos_no_banco(db)
  dicionario_status_icmp = zabbix_api.busca_icmp_todos_hosts(lista_ativos_banco)
  json_icmp = transforme_objeto_em_json(dicionario_status_icmp)
  
  
  
  return json_icmp

def get_json_status_ativo(db,ativo_na_busca):
  start = time.time()
  zabbix_id = ativo_na_busca.zabbix_id
  
  
  #print(json2)
  dados_zabbix = zabbix_api.busca_lista_dados_status_ativo("hostid",zabbix_id)
  #print (dados_zabbix)
   
  dicionario = {
   "endereco_ip":"ip" }
  


  json_dicionario = transforme_objeto_em_json(dados_zabbix)
  end = time.time()
  print(end - start)
  return json_dicionario

def get_json_dados_hardware_ativo(hardware_no_db):
   try:
    processador = transforme_json_em_objeto(hardware_no_db.dados_de_processador)[0]['name'].upper()
   except:
    processador = ""
   try:
    placa_mae = transforme_json_em_objeto(hardware_no_db.dados_de_placamae)[0]['product'].upper()
   except:
    placa_mae = ""
   try:
    memorias = transforme_json_em_objeto(hardware_no_db.dados_de_memoria)
    lista_memorias = []
   except:
    lista_memorias = []
    memorias = ""
   try:
    gpus = transforme_json_em_objeto(hardware_no_db.dados_de_gpu)
    lista_gpus = []
   except:
    lista_gpus = []
    gpus = ""
   try: 
    discos = transforme_json_em_objeto(hardware_no_db.dados_de_disco)
    lista_discos = []
   except:
    lista_discos = []
    discos = ""
   try: 
    quantidade_de_memorias = hardware_no_db.quantidade_de_memorias
    ip = hardware_no_db.ativo_id.endereco_ip
    mac = hardware_no_db.ativo_id.endereco_mac
   except:
    quantidade_de_memorias = ""
    ip = ""
    mac = ""
   

             
   for memorial_filtrada in memorias:
     try:
      nome_memoria = memorial_filtrada['manufacturer'] + " " + str(zabbix_api.memoria_bytes_to_gb(memorial_filtrada['capacity'])) + "GB " + memorial_filtrada['memorytype']
     except:
       nome_memoria = ""
       #print(memorial_filtrada)
     lista_memorias.append(nome_memoria.upper())

   for gpu in gpus:
     teste = transforme_json_em_objeto(gpu)
     nome_gpu = teste['name']
     lista_gpus.append(nome_gpu.upper())

   for disco in discos:
      nome_disk = disco['model'] + " " + str(zabbix_api.memoria_bytes_to_gb(disco['size'])) + "GB"
      lista_discos.append(nome_disk.upper())

   
   
   dicionario = {
   "endereco_ip":ip,
   "endereco_mac":mac,
   "processador" : processador,
   "mobo" : placa_mae,
   "gpu" : lista_gpus,
   "memorias" : lista_memorias,
   "discos" : lista_discos,
   "quantidade_de_memorias" : hardware_no_db.quantidade_de_memorias,
   "quantidade_de_discos" : len(lista_discos)}


   
   json_dicionario = transforme_objeto_em_json(dicionario)

   return json_dicionario

def verifique_inatividade(ultimo_update):
    print("verificando inatividade")
    #print(ultimo_update)
    dicionario_inatividade = {}
    inatividade = 0
    status_do_ativo = ""
    timestamp_agora = datetime.datetime.now()
    utc_time = calendar.timegm(timestamp_agora.utctimetuple())
    diferenca = (float(str(utc_time))-float(str(ultimo_update)))/(60*60*24)
    #print(int(diferenca))
    #print("a diferenca eh em cima")
    if(int(diferenca) <= 7):
      inatividade = int(diferenca)
      status_do_ativo = "operacional"
    if(int(diferenca) > 7 and int(diferenca) <= 15):
      inatividade = 14
      status_do_ativo = "operacional"
    if(int(diferenca) > 15 and int(diferenca) < 30 ):
      inatividade = 15
      status_do_ativo = "alerta"   
    if(int(diferenca) > 30):
      inatividade = 30
      status_do_ativo = "ocioso"

    dicionario_inatividade['flag_de_estado'] = status_do_ativo
    dicionario_inatividade['inatividade_em_dias'] = inatividade

      
    return dicionario_inatividade


def teste_json_switch():
  
 itens_de_monitoramento_de_hardware = { 
     #chave_monitoramento_zabbix   #nome_banco_de_dados 
"[HW][CPU]-Detalhes-[JSN]" : "dados_de_processador"  , #Detalhes processador
"[HW][PLM]-Modelo-[TXT]"   : "dados_de_placamae" ,     #Detales PlacaMae
"[HW][DSK]-Detalhes-[JSN]" : "dados_de_disco",         #Detalhes Disco
"[HW][GPU]-Detalhes-[JSN]" : "dados_de_gpu" ,          #Detalhes GPU
"[HW][MEM]-Detalhes-[JSN]" : "dados_de_memoria" ,      #Detalhes Memoria
"[HW][MEM]-Total-[NUM]"    : "dados_de_memoria_total",    #Memoria Total GB
}
  
 inventario_de_monitoramento_do_ativo = { 
   
      
"name" : "hostname"  ,
"tag" : "endereco_ip"  , 
"macaddress_a"   : "endereco_mac" ,     
"macaddress_b" : "endereco_mac2",         
"ultimo_monitoramento" : "date_hw_decomm" ,          
"switch_mac" : "location" ,      
"switch_porta"    : "url_b",    
"switch_portadesc"    : "url_c",
"switch_nome"    : "url_a",
}
   
 grupos_de_busca_por_tipo = { 
  
"DESKTOP"    : 43,     #Estacoes[Windows]
"NOTEBOOK"   : 2,     #Detales PlacaMae
"IMPRESSORA" : 3,     #Detalhes Disco
"ROTEADOR"   : 4

}

 json_de_config = {
  "itens_de_monitoramento_de_hardware" : itens_de_monitoramento_de_hardware,
  "inventario_de_monitoramento_do_ativo" : inventario_de_monitoramento_do_ativo,
  "grupos_de_busca_por_tipo" : grupos_de_busca_por_tipo


 }


 return transforme_objeto_em_json(json_de_config )

def crie_lista_de_componentes(db, hardware_na_busca):
        
        lista_de_componentes = []
        #processador
        if (hardware_na_busca.dados_de_processador != "nodata"):
         processador = crud.busque_componente_biblioteca_detalhes(db,hardware_na_busca.dados_de_processador)
         if (not processador):
          processador_json = transforme_json_em_objeto(hardware_na_busca.dados_de_processador)
          if (len(processador_json[0])==4):            
            esquema_processador = criar_esquema_biblioteca_hardware(hardware_na_busca.dados_de_processador,"processador")  
            esquema_processador.nome_monitoramento = processador_json[0]['name']
            processador = crud.crie_componente_biblioteca_hardware(db,esquema_processador)
            #crud.adicione_unidade_de_componente_biblioteca_hardware(db,processador)
            lista_de_componentes.append(processador) 
         else:
          
          lista_de_componentes.append(processador)
        #placamae
        if (hardware_na_busca.dados_de_placamae != "nodata"):
          placamae = crud.busque_componente_biblioteca_detalhes(db,hardware_na_busca.dados_de_placamae)
          if (not placamae):
           try:
            placamae_json = transforme_json_em_objeto(hardware_na_busca.dados_de_placamae)
            if (len(placamae_json[0])==3):
             esquema_placame = criar_esquema_biblioteca_hardware(hardware_na_busca.dados_de_placamae,"placamae")  
             esquema_placame.nome_monitoramento = placamae_json[0]['product'] 
             placamae = crud.crie_componente_biblioteca_hardware(db,esquema_placame)
             #crud.adicione_unidade_de_componente_biblioteca_hardware(db,placamae)
             lista_de_componentes.append(placamae)  
           except:
            placamae_json = None 
          else:
           #crud.adicione_unidade_de_componente_biblioteca_hardware(db,placamae)
           lista_de_componentes.append(placamae)
        #memoria
        if (hardware_na_busca.dados_de_memoria != "nodata"):   
         memoriajson = transforme_json_em_objeto(hardware_na_busca.dados_de_memoria)               
         memorias_filtradas = filtrar_componentes_de_hardware(memoriajson,"memoria")
         for memoria in memorias_filtradas:
                    
          memorial_filtrada = transforme_json_em_objeto(memoria)
          dumpmemoria = transforme_objeto_em_json(memorial_filtrada)
          memoria_db = crud.busque_componente_biblioteca_detalhes(db,dumpmemoria)
          
          if (not memoria_db):
            if (len(memorial_filtrada)==3):
              
                esquema_memoria = criar_esquema_biblioteca_hardware(dumpmemoria,"memoria")
                try:  
                 esquema_memoria.nome_monitoramento = str(memorial_filtrada['capacity']) + "GB " + str(memorial_filtrada['memorytype']) + " " + str(memorial_filtrada['speed']) 
                except:
                 esquema_memoria.nome_monitoramento = str(memorial_filtrada['capacity']) + "GB " + str(memorial_filtrada['memorytype']) 
                memorias = crud.crie_componente_biblioteca_hardware(db,esquema_memoria)
                lista_de_componentes.append(memorias)
              
          else:
           
           #crud.adicione_unidade_de_componente_biblioteca_hardware(db,memoria_db)
           lista_de_componentes.append(memoria_db)
        #gpu
        if (hardware_na_busca.dados_de_gpu == "nodata"):
          print("Sem dados de GPU")  
        if (hardware_na_busca.dados_de_gpu != "nodata"):
          #print("gpu nao eh nodata")
          
          gpujson = transforme_json_em_objeto(hardware_na_busca.dados_de_gpu)
          #print(str(len(gpujson)) + " Qtd de placas")
          #print(gpujson)
          #print("gpujson")                  
          itens_para_extrair = ["adaptercompatibility","name","videoprocessor"]
          for gpu in gpujson:
           gpu_dados_selecionados = transforme_json_em_objeto(gpu)
           #print (gpu_dados_selecionados)
           gpu_no_db = crud.busque_componente_biblioteca_detalhes(db,gpu)
           if (not gpu_no_db):
            #print(len(gpu_dados_selecionados))  
            if (len(gpu_dados_selecionados)==3):
              
              esquema_gpu = criar_esquema_biblioteca_hardware(gpu,"gpu")
              esquema_gpu.nome_monitoramento = gpu_dados_selecionados['name']
              print("salvei gpu no db")
              gpu_salva_no_db = crud.crie_componente_biblioteca_hardware(db,esquema_gpu)  
              if (gpu_salva_no_db):  
                #crud.adicione_unidade_de_componente_biblioteca_hardware(db,gpu_salva_no_db)
                lista_de_componentes.append(gpu_salva_no_db) 
           else:
            #print("gpu esta no db")  
            #crud.adicione_unidade_de_componente_biblioteca_hardware(db,gpu_no_db)
            lista_de_componentes.append(gpu_no_db)                      


        #discos   
        if (hardware_na_busca.dados_de_disco != "nodata"):
         discosjson = transforme_json_em_objeto(hardware_na_busca.dados_de_disco)               
         listateste = ["model","size"]
         for disco in discosjson:

          discos_filtrado = dict((x, y) for x, y in disco.items() if x in listateste)
          dumpdisk = transforme_objeto_em_json(discos_filtrado)
          
          discos_db = crud.busque_componente_biblioteca_detalhes(db,dumpdisk)
          if (not discos_db):
            esquema_disco = criar_esquema_biblioteca_hardware(dumpdisk,"disco")
             #print (discos_filtrado['Model'])
             #print (discos_filtrado['Model'].lower().find("usb"))  
            esquema_disco.nome_monitoramento = discos_filtrado['model']
            discos = crud.crie_componente_biblioteca_hardware(db,esquema_disco)
            if(discos):
              lista_de_componentes.append(discos) 
          else:
           #crud.adicione_unidade_de_componente_biblioteca_hardware(db,discos_db)            
           lista_de_componentes.append(discos_db)
        #telas
        
           #lista_de_componentes.append(telas)  
#GPU
        # gpujson = transforme_json_em_objeto(hardware_na_busca.dados_de_gpu)
        # for gpu in gpujson:
        #   string_gpu = transforme_objeto_em_json(gpu)
        #   gpu_db = crud.busque_componente_biblioteca_detalhes(db,string_gpu)
        #   #print(gpu)
        #   #print(len(gpu))
        #   if (not gpu_db):
        #      if (len(gpu)==4):
              
        #       esquema_gpu = criar_esquema_biblioteca_hardware(string_gpu,"gpu")  
        #       esquema_gpu.nome_monitoramento = gpu['Name']
        #       gpu_nova = crud.crie_componente_biblioteca_hardware(db,esquema_gpu)
        #       if (gpu_nova):  
        #         #crud.adicione_unidade_de_componente_biblioteca_hardware(db,memorias)
        #         lista_de_componentes.append(gpu_nova) 
        #   else:
        #    crud.adicione_unidade_de_componente_biblioteca_hardware(db,gpu_db)
        #    lista_de_componentes.append(gpu_db)


        return lista_de_componentes