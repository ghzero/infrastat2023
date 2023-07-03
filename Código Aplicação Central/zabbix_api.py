from distutils.log import info
from pyzabbix import ZabbixAPI
from models import *
import json
import os
import datetime
from datetime import date
import calendar
import time
import crud
import models
import schemas
from dotenv import load_dotenv
from dicionario_items_zabbix import itens_de_monitoramento_de_hardware

load_dotenv(dotenv_path="./.env.local")
URL_ZABBIX = 'https://site-do-zabbix.com.br/'


class Dados:
    pass

class Busca:
    pass

class User:
    pass

def memoria_bytes_to_gb(memoria):
    tamanho = int(memoria) / 1072000000
    return round(tamanho)


def get_dados_do_ativo_no_monitoramento(dados_zabbix):
    ativo_no_zabbix = Dados()

    ativo_no_zabbix.patrimonio = dados_zabbix[0]['host']
    ativo_no_zabbix.endereco_ip = dados_zabbix[0]['inventory']['tag']
    ativo_no_zabbix.endereco_mac = dados_zabbix[0]['inventory']['macaddress_a']
    ativo_no_zabbix.endereco_mac2 = dados_zabbix[0]['inventory']['macaddress_b']
    ativo_no_zabbix.hostname = dados_zabbix[0]['inventory']['name']
    ativo_no_zabbix.zabbix_id = dados_zabbix[0]['hostid']
    ativo_no_zabbix.ultima_verificacao = dados_zabbix[0]['inventory']['date_hw_decomm']
    ativo_no_zabbix.switchmac = dados_zabbix[0]['inventory']['location']
    ativo_no_zabbix.switchporta = dados_zabbix[0]['inventory']['url_b']
    ativo_no_zabbix.switchportadesc = dados_zabbix[0]['inventory']['url_c']
    ativo_no_zabbix.switchnome = dados_zabbix[0]['inventory']['url_a']

    try:
        ativo_no_zabbix.equipe = ativo_no_zabbix.hostname[0:3]
        ativo_no_zabbix.local = ativo_no_zabbix.hostname[3:6]
    except:
        ativo_no_zabbix.equipe = ""
        ativo_no_zabbix.local = ""

    return ativo_no_zabbix


def get_informacoes_de_hardware_do_monitoramento(dados_zabbix):

    informacoes_hw_zabbix = Dados()
    arquivo_de_configuracao = open('configuracao.json')
    conf_in_json = json.load(arquivo_de_configuracao)
    itens_monitorados = conf_in_json['itens_de_monitoramento_de_hardware']

    for item in list(filter(lambda x: x["name"] in itens_monitorados.keys(), dados_zabbix[0]["items"])):
        if esta_vazio(item['lastvalue']):
            setattr(informacoes_hw_zabbix,
                    itens_monitorados[item['name']], "nodata")
        else:
            valor_coletado = item['lastvalue'].lower()
            setattr(informacoes_hw_zabbix,
                    itens_monitorados[item['name']], valor_coletado)

    if (len(informacoes_hw_zabbix.dados_de_memoria_total_em_gb) > 1):
        informacoes_hw_zabbix.dados_de_memoria_total_em_gb = memoria_bytes_to_gb(
            informacoes_hw_zabbix.dados_de_memoria_total_em_gb)
    else:
        informacoes_hw_zabbix.dados_de_memoria_total_em_gb = 0
    try:
        gpujson = json.loads(informacoes_hw_zabbix.dados_de_gpu)
        dicionario_gpu = []
        itens_para_extrair = ["adaptercompatibility", "name", "videoprocessor"]
        for gpu in gpujson:

            gpu_filtrada = dict((x, y)
                                for x, y in gpu.items() if x in itens_para_extrair)
            dicionario_gpu.append(json.dumps(gpu_filtrada))
            
        informacoes_hw_zabbix.dados_de_gpu = json.dumps(dicionario_gpu)

    except:
        informacoes_hw_zabbix.dados_de_gpu = "nodata"
    try:
        informacoes_hw_zabbix.quantidade_de_discos = len(
            json.loads(informacoes_hw_zabbix.dados_de_disco))
        informacoes_hw_zabbix.quantidade_de_memorias = len(
            json.loads(informacoes_hw_zabbix.dados_de_memoria))
    except:
        informacoes_hw_zabbix.quantidade_de_memorias = 0
        informacoes_hw_zabbix.quantidade_de_discos = 0

    return informacoes_hw_zabbix


def get_informacoes_de_sistema_do_monitoramento(dados_zabbix):

    informacoes_de_sistema = Dados()
    string_so = dados_zabbix[0]['inventory']['os_full'].replace(
        "Windows " + dados_zabbix[0]['inventory']['name'] + " ", '')  # Problem>
    string_so = string_so.replace(dados_zabbix[0]['inventory']['os_short'], '')
    informacoes_de_sistema.sistema_operacional = string_so
    informacoes_de_sistema.dados_de_administradores = dados_zabbix[0]['inventory']['contact'].replace(
        dados_zabbix[0]['inventory']['name'], 'LOCAL')
    informacoes_de_sistema.dados_de_antivirus = dados_zabbix[0]['inventory']['poc_1_notes']
    informacoes_de_sistema.dados_de_versao = dados_zabbix[0]['inventory']['os_short']
    informacoes_de_sistema.dados_de_update = dados_zabbix[0]['inventory']['serialno_a']

    return informacoes_de_sistema




def mude_nome_host_inventario(host, zabbix_api):
    try:

        inv_name = host['inventory']['asset_tag']
        #print(inv_name)
        
        inv_name = inv_name.strip().replace("_", " ")

        if (host['name'] != inv_name and inv_name != ''):
            try:
                #print (host['name'], "ATUALIZOU =>", inv_name)
                zabbix_api.host.update(
                    hostid=host['hostid'],
                    name=inv_name
                )
            except:
                a = Dados()
                a.zabbix_id = host['hostid']
                a.hostname = host['inventory']['name']

                #removehost(a)
                print('Removido', host['name'], '=>',
                      host['inventory']['name'], ' tentando renomear')

    except:
        print(host['name'], 'Nome do inventario em Branco')


def conecte_servidor_zabbix():

    try:
        zabbix_api = ZabbixAPI(URL_ZABBIX, timeout=30)
        zabbix_api.login(os.environ.get("ZBXUSER", ""),
                         os.environ.get("ZBXPASS", ""))
    except:
        return False

    return zabbix_api


def removehost(ativo):

    zabbix_api = conecte_servidor_zabbix()
    if (zabbix_api is False):
        return (False, "ERRO - Conexao com o servidor")
    try:
        print("host deletado no monitoramento -> " + ativo.hostname)
        zabbix_api.host.delete(ativo.zabbix_id)
        return True
    except:
        return False


def busca_ativo_monitorado_zabbix(tipo_de_busca, identificador_do_ativo):

    informacoes_hw_zabbix = Dados()
    resultado_da_busca = Busca()

    zabbix_api = conecte_servidor_zabbix()
    if (zabbix_api is False):
        return (False, None, None, "ERRO - Conexao com o servidor")
    print("Analisando o ativo de ID -> "+identificador_do_ativo)
    # zabbix_api.host.delete('41024')
    filtro = {tipo_de_busca: identificador_do_ativo}
    dados_host_zabbix = zabbix_api.host.get(filter=filtro, output='extend', selectInventory=[
                                            'name', 'tag', 'asset_tag',  'macaddress_a', 'macaddress_b', 'date_hw_decomm', 'location', 'url_a', 'url_b', 'url_c', 'serialno_a', 'contact', 'os_short', 'os_full', 'poc_1_notes'], selectItems=['itemid', 'name', 'lastvalue'])

    mude_nome_host_inventario(dados_host_zabbix[0], zabbix_api)
    ativo_monitorado = get_dados_do_ativo_no_monitoramento2(dados_host_zabbix)
    informacoes_hw_zabbix = get_informacoes_de_hardware_do_monitoramento(
        dados_host_zabbix)
    informacoes_sistema_zabbix = get_informacoes_de_sistema_do_monitoramento(
        dados_host_zabbix)
    if (not ativo_monitorado):
        print("erro nos dados do ativo")
    if (not informacoes_hw_zabbix):
        print("erro nos dados de hardware do ativo")

     
    resultado_da_busca.dados_do_ativo = ativo_monitorado
    resultado_da_busca.dados_de_hardware = informacoes_hw_zabbix
    resultado_da_busca.dados_de_sistema = informacoes_sistema_zabbix
    resultado_da_busca.dados_de_software = informacoes_hw_zabbix.dados_de_software
    

    if (ativo_monitorado and informacoes_hw_zabbix):
        resultado_da_busca.mensagem_da_busca = "Sucesso"
        resultado_da_busca.status = True
    else:
        resultado_da_busca.mensagem_da_busca = "Erro - Dados incompletos"
        resultado_da_busca.status = False
    
    return (resultado_da_busca)


def busque_history_text_trinta_dias(itemid):

    zabbix_api = conecte_servidor_zabbix()

    if (zabbix_api is False):
        return (False, "ERRO - Conexao com o servidor")

    timestamp_agora = datetime.datetime.now()
    utc_time = calendar.timegm(timestamp_agora.utctimetuple())

    values = zabbix_api.history.get(itemids=itemid, history=4, output='extend',
                                    time_from=utc_time-2592000, sortfield='clock', sortorder='ASC')

    return values


def busque_estatisticas_de_uso_de_ativo_trinta_dias(ativo_no_banco,informacao_de_hardware):
    patrimonio = ativo_no_banco.patrimonio
    potencia_memoria = informacao_de_hardware.quantidade_de_memorias * 2
    potencia_discos = informacao_de_hardware.quantidade_de_discos * 3
    potencia_pecas = potencia_memoria + potencia_discos + 15 #15 watts da placa mae
    dici = {"labels": [], "series": []}
    donut_uso_efetivo = {"labels": [], "series": []}
    valor_kwh = 0.72
    custo_por_minuto = 0.0023

    uso_real = busque_usuarios_logados_trinta_dias(patrimonio)
    total_de_minutos_29_dias = uso_real['uptime_30_total_dias_coletados'] * 1440
    total_minutos_hoje = uso_real['uptime_hoje'] * 60
    
    total_de_minutos = total_de_minutos_29_dias + total_minutos_hoje
    potencia_desktop = uso_real['media_consumo_30_dias_em_watts'] + int(potencia_pecas) * 1.1 #gasto de energia da fonte
    #print("potencia desktop")
    #print(potencia_desktop)
    total_de_minutos_ligado = total_de_minutos * uso_real['media_uptime_30_dias']
    print("total de minutos ligado")
    print(total_de_minutos_ligado)
    total_de_minutos_ligado_em_porcentagem = uso_real['media_uptime_30_dias'] * 100
    dicionario_minutos_ligado_7_dias = uso_real['uptime_7_dias']
    
    total_de_uso_em_minutos_30_dias = 0
    total_de_uso_em_minutos_7_dias = 0
    total_de_minutos_7_dias = 0
    lista_de_usuarios = uso_real['lista_usuarios']
    dicionario_usuarios_por_dia = uso_real['dicionario_dias']
    dia_atual = datetime.datetime.now()
    mes_ano_atual = datetime.datetime.now().strftime('%m-Y%')
    dicionario_7_dias = {}
    label_data_uso = []
    lista_retorno = []
    lista_uso_efetivo = []
    lista_minutos_ligado = []
    series_7_dias = []
    dicionario_uso_7_dias = {}
    dicionario_ligado_7_dias = {}
    for x in range(7):
        dia = dia_atual - datetime.timedelta(days=x)
        chavo = dia.strftime('%d-%m-%Y')
        
        dicionario_7_dias[str(chavo)] = 0
        #print (dia.strftime('%d-%m-%Y'))
    #print (dia.strftime('%d-%m-%Y'))
    totaldias = 0
    setedias = 0
    for key, value in uso_real['dicionario_dias'].items():
        #print("executando a chave")
        #print(key)
        if isinstance(value, dict):
            teste = value[max(value, key=value.get)]
            total_de_uso_em_minutos_30_dias = total_de_uso_em_minutos_30_dias + teste
            #print("adicionei total dias")
            totaldias = totaldias + 1
            # print(dicionario_7_dias.keys())
            if (key in dicionario_7_dias.keys()):
                #print("executando o if")
                try:
                    dicionario_valor = dicionario_uso_7_dias[key]
                    dicionario_valor['uso_no_dia'] = uso_no_dia
                    dicionario_uso_7_dias[key] = dicionario_valor
                    setedias = setedias + 1
                    uso_no_dia = value[max(value, key=value.get)]
                    total_de_uso_em_minutos_7_dias = total_de_uso_em_minutos_7_dias + uso_no_dia
                    #print("adicionei sete dias")
                except:
                    setedias = setedias + 1
                    #print("adicionei sete dias except")
                    dicionario_valor = {}
                    uso_no_dia = value[max(value, key=value.get)]
                    total_de_uso_em_minutos_7_dias = total_de_uso_em_minutos_7_dias + uso_no_dia
                    dicionario_valor['uso_no_dia'] = uso_no_dia
                    dicionario_uso_7_dias[key] = dicionario_valor
                    
    for key, value in dicionario_minutos_ligado_7_dias.items():
        label_data_uso.append(key)
        try:

            dicionario_valor = dicionario_uso_7_dias[key]
            minutos_ligado = value['total_de_horas_coletadas'] * 60
            dicionario_valor['ligado_no_dia'] = round(minutos_ligado * value['media_valor_coletado'])
            dicionario_uso_7_dias[key] = dicionario_valor

            lista_uso_efetivo.append(dicionario_valor['uso_no_dia'])
            lista_minutos_ligado.append(dicionario_valor['ligado_no_dia'])

        except:
            dicionario_valor = {}
            dicionario_valor['uso_no_dia'] = 0
            minutos_ligado = value['total_de_horas_coletadas'] * 60
            dicionario_valor['ligado_no_dia'] = round(minutos_ligado * value['media_valor_coletado'])
            dicionario_uso_7_dias[key] = dicionario_valor
            lista_uso_efetivo.append(dicionario_valor['uso_no_dia'])
            lista_minutos_ligado.append(dicionario_valor['ligado_no_dia'])
            #print("sem dados no dia")
        #maior_numero = item[max(item, key=item.get)]
    
    dicionario_para_filtrar = {}
    dicionario_para_filtrar['name'] = "uso efetivo"
    dicionario_para_filtrar['data'] = lista_uso_efetivo
    lista_retorno.append(dicionario_para_filtrar)

    dicionario_para_filtrar = {}
    dicionario_para_filtrar['name'] = "minutos ligados"
    dicionario_para_filtrar['data'] = lista_minutos_ligado
    lista_retorno.append(dicionario_para_filtrar)
    



    dici["series"] += lista_retorno
    dici["labels"] += label_data_uso
    

    calculo_de_energia_consumida = (potencia_desktop / 1000) * round(int(total_de_minutos_ligado) / 60)
    calculo_de_energia_efetiva = (potencia_desktop / 1000) * round(int(total_de_uso_em_minutos_30_dias) / 60)

    dicionario_estatisticas = {}
    dicionario_estatisticas['horas_ligado_30_dias'] = round(
        int(total_de_minutos_ligado) / 60)
    dicionario_estatisticas['horas_de_uso_30_dias'] = round(
        int(total_de_uso_em_minutos_30_dias) / 60)
    dicionario_estatisticas['horas_de_uso_7_dias'] = round(
        int(total_de_uso_em_minutos_7_dias) / 60)
    dicionario_estatisticas['porcentagem_de_tempo_ligado'] = round(
        int(total_de_minutos_ligado_em_porcentagem))
    dicionario_estatisticas['estimativa_gasto_de_energia'] = round(calculo_de_energia_consumida)
    dicionario_estatisticas['estimativa_economia_de_energia'] = round(calculo_de_energia_consumida - calculo_de_energia_efetiva)
    dicionario_estatisticas['porcentagem_de_tempo_ligado'] = round(
        int(total_de_minutos_ligado_em_porcentagem))
    dicionario_estatisticas['usuarios_que_utilizaram'] = list(lista_de_usuarios)
    dicionario_estatisticas['gasto_efetivo'] = dicionario_estatisticas['estimativa_gasto_de_energia'] - dicionario_estatisticas['estimativa_economia_de_energia']
    dicionario_estatisticas['desperdicio_em_reais'] = round(dicionario_estatisticas['estimativa_economia_de_energia'] * valor_kwh)
    dicionario_estatisticas['utilizacao_efetiva_7_dias'] = dicionario_uso_7_dias
    dicionario_estatisticas['utilizacao_por_usuarios_por_dia'] = dicionario_usuarios_por_dia
    dicionario_estatisticas['barra_utilizacao'] = dici
    

    labels_donut_uso = [ "LIGADO SEM USO","USO EFETIVO"]
    series_donut_uso = [ dicionario_estatisticas['horas_ligado_30_dias'] - dicionario_estatisticas['horas_de_uso_30_dias'], dicionario_estatisticas['horas_de_uso_30_dias']]
    donut_uso_efetivo["labels"] = labels_donut_uso
    donut_uso_efetivo["series"] = series_donut_uso
    dicionario_estatisticas['donut_uso_efetivo'] = donut_uso_efetivo

    # estatisticas 30 dias

    # tempo_ligado /em horas
    # tempo_ligado_porcentagem /em %
    # uso_efetivo /em horas
    # custo_energetico_total /em r$
    # custo_energetico_economizavel /em r$
    #usuarios_que_utilizaram /lista_de_nomes

    # grafico 7 dias
    #data - tempo_total / data - tempo_efetivo
    json2 = '{"labels":["Desktop","Notebook"],"series":[193,12]}'
    return json.dumps(dicionario_estatisticas)

def busque_estatisticas_de_uso_de_ativo_trinta_dias2(ativos_no_banco,db):
    start = time.time()
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


    dicionario_de_retorno['donut_sala1'] = 0
    dicionario_de_retorno['donut_sala2'] = 0
    dicionario_de_retorno['donut_sala3'] = 0


def busque_usuarios_logados_trinta_dias(patrimonio):
    
    zabbix_api = conecte_servidor_zabbix()
    dicionario_de_dados = {}
    if (zabbix_api is False):
        return (False, "ERRO - Conexao com o servidor")

    filtro = {"host": patrimonio}
    dados_host_zabbix = zabbix_api.host.get(
        filter=filtro, output='extend', selectItems=['itemid', 'name', 'lastvalue'])
    item_users = 0
    item_icmp = 0
    item_cpupower = 0
    if (dados_host_zabbix):
        for item in list(filter(lambda x: x["name"] == "[MON][HW]-ICMP-PING-[BOL]" or x["name"] == "[ID]-UsersRemoto" or x["name"] == "CPU-Power", dados_host_zabbix[0]["items"])):
            if (item['name'] == "[ID]-UsersRemoto"):
                item_users = item['itemid']
            if (item['name'] == "[MON][HW]-ICMP-PING-[BOL]"):
                item_icmp = item['itemid']
            if (item['name'] == "CPU-Power"):
                item_cpupower = item['itemid']    

    lista_usuarios = set([])
    dicionario_dias = {}

    trend_uptime_30_dias = busque_trend_trinta_dias(item_icmp)
    uptime_30_dias = trend_uptime_30_dias['media_valor_coletado']
    uptime_hoje = trend_uptime_30_dias['coleta_de_hoje']
    uptime_30_dias_com_coleta = trend_uptime_30_dias['dias_com_coleta']
    trend_consumo_30_dias = busque_trend_trinta_dias(item_cpupower)
    consumo_30_dias_em_watts = trend_consumo_30_dias['media_valor_coletado']

    trend_uptime_7_dias = busque_trend_sete_dias(item_icmp)

    values = busque_history_text_trinta_dias(item_users)
    
    for value in values:
       try: 
        for name in json.loads(value['value']):
            if (name):
                date_time = datetime.datetime.fromtimestamp(
                    int(value['clock']))
                dia_ocorrencia = date_time.strftime('%d-%m-%Y')

                #timestamp = datetime.datetime.strptime(dia_ocorrencia, '%d-%m-%Y').date()
                # print(type(timestamp))
                if (dicionario_dias.get(dia_ocorrencia)):
                    dici_user = dicionario_dias.get(dia_ocorrencia)
                    tempo_uso_atual = dici_user.get(name)
                    #dici_user['Clock'] = int(value['clock'])
                    if (tempo_uso_atual):
                        dici_user[name] = 5 + tempo_uso_atual
                    else:
                        dici_user[name] = 5
                    dicionario_dias[dia_ocorrencia] = dici_user

                else:
                    dici_user = {}
                    dici_user[name] = 5
                    dicionario_dias[dia_ocorrencia] = dici_user

                lista_usuarios.add(name)
       except:
              print("sem dados de usuarios")  
    # print(uptime)

    res = {element: 'User' for element in lista_usuarios}
    json_dicionario = json.dumps(dicionario_dias)
    dicionario_de_dados['dicionario_dias'] = dicionario_dias
    dicionario_de_dados['media_uptime_30_dias'] = uptime_30_dias
    dicionario_de_dados['lista_usuarios'] = lista_usuarios
    dicionario_de_dados['lista_usuarios'] = lista_usuarios
    dicionario_de_dados['uptime_7_dias'] = trend_uptime_7_dias
    dicionario_de_dados['media_consumo_30_dias_em_watts'] = consumo_30_dias_em_watts
    dicionario_de_dados['uptime_30_total_dias_coletados'] = uptime_30_dias_com_coleta
    dicionario_de_dados['uptime_hoje'] = uptime_hoje
    print("uptime 30 dias com coleta")
    print (uptime_30_dias_com_coleta)
    return dicionario_de_dados


def busque_usuarios_logados_trinta_dias2(patrimonio):
    
    zabbix_api = conecte_servidor_zabbix()
    dicionario_de_dados = {}
    if (zabbix_api is False):
        return (False, "ERRO - Conexao com o servidor")

    filtro = {"host": patrimonio}
    dados_host_zabbix = zabbix_api.host.get(
        filter=filtro, output='extend', selectItems=['itemid', 'name', 'lastvalue'])
    item_users = 0
    item_icmp = 0
    item_cpupower = 0
    if (dados_host_zabbix):
        for item in list(filter(lambda x: x["name"] == "[MON][HW]-ICMP-PING-[BOL]" or x["name"] == "[ID]-UsersRemoto" or x["name"] == "CPU-Power", dados_host_zabbix[0]["items"])):
            if (item['name'] == "[ID]-UsersRemoto"):
                item_users = item['itemid']
            if (item['name'] == "[MON][HW]-ICMP-PING-[BOL]"):
                item_icmp = item['itemid']
            if (item['name'] == "CPU-Power"):
                item_cpupower = item['itemid']    

    lista_usuarios = set([])
    dicionario_dias = {}

    trend_uptime_30_dias = busque_trend_trinta_dias(item_icmp)
    print(trend_uptime_30_dias['media_valor_coletado'])
    uptime_30_dias = trend_uptime_30_dias['media_valor_coletado']
    uptime_hoje = trend_uptime_30_dias['coleta_de_hoje']
    uptime_30_dias_com_coleta = trend_uptime_30_dias['dias_com_coleta']
    trend_consumo_30_dias = busque_trend_trinta_dias(item_cpupower)
    consumo_30_dias_em_watts = trend_consumo_30_dias['media_valor_coletado']

    

    values = busque_history_text_trinta_dias(item_users)
    
    for value in values:
       try: 
        for name in json.loads(value['value']):
            if (name):
                date_time = datetime.datetime.fromtimestamp(
                    int(value['clock']))
                dia_ocorrencia = date_time.strftime('%d-%m-%Y')

                #timestamp = datetime.datetime.strptime(dia_ocorrencia, '%d-%m-%Y').date()
                # print(type(timestamp))
                if (dicionario_dias.get(dia_ocorrencia)):
                    dici_user = dicionario_dias.get(dia_ocorrencia)
                    tempo_uso_atual = dici_user.get(name)
                    #dici_user['Clock'] = int(value['clock'])
                    if (tempo_uso_atual):
                        dici_user[name] = 5 + tempo_uso_atual
                    else:
                        dici_user[name] = 5
                    dicionario_dias[dia_ocorrencia] = dici_user

                else:
                    dici_user = {}
                    dici_user[name] = 5
                    dicionario_dias[dia_ocorrencia] = dici_user

                lista_usuarios.add(name)
       except:
              print("sem dados de usuarios")  
    # print(uptime)

    res = {element: 'User' for element in lista_usuarios}
    json_dicionario = json.dumps(dicionario_dias)
    dicionario_de_dados['dicionario_dias'] = dicionario_dias
    dicionario_de_dados['media_uptime_30_dias'] = uptime_30_dias
    dicionario_de_dados['lista_usuarios'] = lista_usuarios
    dicionario_de_dados['lista_usuarios'] = lista_usuarios
    dicionario_de_dados['media_consumo_30_dias_em_watts'] = consumo_30_dias_em_watts
    dicionario_de_dados['uptime_30_total_dias_coletados'] = uptime_30_dias_com_coleta
    dicionario_de_dados['uptime_hoje'] = uptime_hoje
    print("uptime 30 dias com coleta")
    print (uptime_30_dias_com_coleta)
    return dicionario_de_dados


def busca_icmp_por_hostid(hostid, lista_dados):

    zabbix_api = conecte_servidor_zabbix()

    if (zabbix_api is False):
        return (False, "ERRO - Conexao com o servidor")
    busca = {"name": "[MON][HW]-ICMP-PING-[BOL]"}
    values = zabbix_api.item.get(groupids=52, output='extend', search=busca)
    total_online = 0
    total_offline = 0
    for value in list(filter(lambda x: int(x["hostid"]) in lista_dados, values)):
        if (value['lastvalue'] == '1.0000'):
            total_online = total_online + 1
        else:
            total_offline = total_offline + 1
    #print([total_online, total_offline])
    return 0


def busca_icmp_todos_hosts(lista_ids_ativos_banco):

    zabbix_api = conecte_servidor_zabbix()

    if (zabbix_api is False):
        return (False, "ERRO - Conexao com o servidor")
    busca = {"name": "[MON][HW]-ICMP-PING-[BOL]"}
    inicio = time.time()
    values = zabbix_api.item.get(groupids=52, output='extend', search=busca)
    #print(time.time() - inicio)
    total_online = 0
    total_offline = 0
    lista_offline = []
    lista_online = []
    for value in list(filter(lambda x: int(x["hostid"]) in lista_ids_ativos_banco, values)):
        if (value['lastvalue'] == '1.0000'):
            total_online = total_online + 1
            lista_online.append(value['hostid'])
        else:
            total_offline = total_offline + 1
            lista_offline.append(value['hostid'])

    dicionario_icmp = {"total_online": total_online,
                       "total_offline": total_offline,
                       "ativos_online": lista_online,
                       "ativos_offline": lista_offline
                       }

    return dicionario_icmp


def busca_lista_dados_status_ativo(tipo_de_busca, identificador_do_ativo):

    dicionario_status = {}

    zabbix_api = conecte_servidor_zabbix()
    if (zabbix_api is False):
        return (False, dicionario_status, "ERRO - Conexao com o servidor")

    filtro = {tipo_de_busca: identificador_do_ativo}

    dados_host_zabbix = zabbix_api.host.get(filter=filtro, output='extend', selectInventory=[
                                            'name', 'tag', 'asset_tag', 'macaddress_a', 'macaddress_b', 'date_hw_decomm', 'contact', 'vendor', 'contract_number', 'os_full', 'os_short', 'location'], selectItems=['itemid', 'name', 'lastvalue'])
    # print(identificador_do_ativo)
    if (dados_host_zabbix):
        for item in list(filter(lambda x: x["name"] == "[MON][HW]-ICMP-PING-[BOL]" or x["name"] == "[MOM][HW]-MEMTempoReal-[NUM]" or x["name"] == "[ID]-UsersRemoto", dados_host_zabbix[0]["items"])):
            # for item in list(dados_host_zabbix[0]["items"]):
            if (item['name'] == "[ID]-UsersRemoto"):
                item_users = item['itemid']
                dicionario_status["usuarios_logados"] = item['lastvalue']
                string_so = dados_host_zabbix[0]['inventory']['os_full'].replace(
                    "Windows " + dados_host_zabbix[0]['inventory']['name'] + " ", '')  # Problema com linux no futuro
                string_so = string_so.replace(
                    dados_host_zabbix[0]['inventory']['os_short'], '')

                #dicionario_status["stat30-usuarios_logados"] = busque_usuarios_logados_trinta_dias(item_users)

            # if(item['name'] == "[MOM][HW]-MEMTempoReal-[NUM]" ):
                # print(item['itemid'])
                # print(busque_trend_sete_dias(item['itemid']))
                # print(busque_trend_um_dia(item['itemid']))

            if (item['name'] == "[MON][HW]-ICMP-PING-[BOL]"):
                if (item['lastvalue'] == '1.0000'):
                    dicionario_status["status"] = "online"
                else:
                    dicionario_status["status"] = "offline"
        string_change = dados_host_zabbix[0]['inventory']['contact'].replace(
            dados_host_zabbix[0]['inventory']['name'], 'LOCAL')
        string_users = dicionario_status["usuarios_logados"]
        try:
            json_string2 = json.loads(string_users)
        except:
            json_string2 = string_users
        try:
            json_string = json.loads(string_change)
        except:
            json_string = string_change
        dicionario_status["usuarios_logados"] = json_string2
        dicionario_status["endereco_ip"] = dados_host_zabbix[0]['inventory']['tag']
        dicionario_status["so"] = string_so
        dicionario_status["switch"] = dados_host_zabbix[0]['inventory']['location']
        dicionario_status["version"] = dados_host_zabbix[0]['inventory']['os_short']
        dicionario_status["endereco_mac1"] = dados_host_zabbix[0]['inventory']['macaddress_a']
        dicionario_status["endereco_mac2"] = dados_host_zabbix[0]['inventory']['macaddress_a']
        dicionario_status["hostname"] = dados_host_zabbix[0]['inventory']['name']
        dicionario_status["administradores"] = json_string
        dicionario_status["ultimo_user_logado"] = dados_host_zabbix[0]['inventory']['vendor']
        dicionario_status["ultimo_monitoramento"] = datetime.datetime.fromtimestamp(
            int(dados_host_zabbix[0]['inventory']['date_hw_decomm'])).strftime('%d/%m/%Y')
    else:
        dicionario_status["status"] = "naomonitorado"
        dicionario_status["usuarios_logados"] = ""
        dicionario_status["endereco_ip"] = ""
        dicionario_status["so"] = ""
        dicionario_status["switch"] = ""
        dicionario_status["version"] = ""
        dicionario_status["endereco_mac1"] = ""
        dicionario_status["endereco_mac2"] = ""
        dicionario_status["hostname"] = ""
        dicionario_status["administradores"] = ""
        dicionario_status["ultimo_user_logado"] = ""
        dicionario_status["ultimo_monitoramento"] = ""

    return (dicionario_status)


def busca_lista_todos_ativos_zabbix(grupo_de_busca):

    zabbix_api = conecte_servidor_zabbix()
    if (zabbix_api is False):
        return ("ERRO", "Conexao com servidor")
    todos_ativos_do_grupo = zabbix_api.host.get(
        groupids=grupo_de_busca, output=["hostid", "name"])
    return todos_ativos_do_grupo


def esta_vazio(parametro):
    bool = True
    tamanho = len(parametro)

    if (tamanho > 0 and parametro != "[]"):
        bool = False

    return bool


def busque_trend_trinta_dias(itemid):
    dicionario_de_retorno = {}
    set_de_dias_monitorados = set()
    zabbix_api = conecte_servidor_zabbix()
    retorno = 0
    if (zabbix_api is False):
        return (False, "ERRO - Conexao com o servidor")

    timestamp_agora = datetime.datetime.now()
    utc_hoje = calendar.timegm(timestamp_agora.utctimetuple())
    utc_time = utc_hoje - 86400
    dicionario_de_retorno['coleta_de_hoje'] = 0
    dicionario_de_retorno['media_valor_coletado'] = 0
    dicionario_de_retorno['dias_com_coleta'] = 0
    try:
     media = 0
     values = zabbix_api.trend.get(
        itemids=itemid, output='extend', time_from=utc_time-2592000, time_till=utc_time)
     valores_de_hoje = zabbix_api.trend.get(
        itemids=itemid, output='extend', time_from=utc_time)
     print(valores_de_hoje)
     soma = 0
     soma_hoje = 0
    
     for value in values:
        date_time = datetime.datetime.fromtimestamp(
                int(value['clock']))
        set_de_dias_monitorados.add(date_time.strftime('%d-%m-%Y'))
        soma = soma + float(value['value_avg'])
     for value in valores_de_hoje:
        soma_hoje = soma_hoje + float(value['value_avg'])
     if(len(values) > 0):
      media = soma/len(values)    
      dicionario_de_retorno['media_valor_coletado'] = media
      dicionario_de_retorno['dias_com_coleta'] = len(set_de_dias_monitorados)
     if(len(valores_de_hoje) > 0):
      media_de_hoje = soma_hoje/len(valores_de_hoje)
      print("media de hoje")
      media = media + media_de_hoje
      if(len(values) > 0):
       media = media / 2
      print(media_de_hoje)   
      dicionario_de_retorno['media_valor_coletado'] = media 
      dicionario_de_retorno['coleta_de_hoje'] = len(valores_de_hoje) 
     #print("hoje")
     #print(valores_de_hoje) 
    except:
     print("except")
     dicionario_de_retorno['media_valor_coletado'] = 0
     dicionario_de_retorno['dias_com_coleta'] = 0
    return dicionario_de_retorno


def busque_trend_sete_dias(itemid):
        dicionario_7_dias = {}
        zabbix_api = conecte_servidor_zabbix()
        #print(itemid)
    
        dia_atual = datetime.date.today()
        
        for x in range(7):
            dia = dia_atual - datetime.timedelta(days=x)
            utc_time = datetime.datetime.strptime(str(dia), "%Y-%m-%d").timestamp()
            dicionario_valores = {}
            values = zabbix_api.trend.get(
                itemids=itemid, output='extend', time_till=utc_time+82800, time_from=utc_time)
            dicionario_valores['total_de_horas_coletadas'] = len(values)
            
            soma = 0
            if (len(values) > 0):
             for value in values:
                #print(value)
                soma = soma + float(value['value_avg'])
            
             dicionario_valores['media_valor_coletado'] = soma/len(values)
             dicionario_7_dias[str(dia.strftime('%d-%m-%Y'))] = dicionario_valores
            #print("soma")
            #print(soma)
        print(dicionario_7_dias)
   
    #print (soma/len(values))
        return dicionario_7_dias


def busque_trend_um_dia(itemid):
    zabbix_api = conecte_servidor_zabbix()

    if (zabbix_api is False):
        return (False, "ERRO - Conexao com o servidor")

    timestamp_agora = datetime.datetime.now()
    utc_time = calendar.timegm(timestamp_agora.utctimetuple())

    values = zabbix_api.trend.get(
        itemids=itemid, output='extend', time_till=utc_time, time_from=utc_time-86400, limit='1')

    return values


def get_dados_do_ativo_no_monitoramento2(dados_zabbix):
    ativo_no_zabbix = Dados()

    ativo_no_zabbix.patrimonio = dados_zabbix[0]['host']
    ativo_no_zabbix.endereco_ip = "192.168.0." + \
        dados_zabbix[0]['inventory']['tag'][12:15]
    ativo_no_zabbix.endereco_mac = dados_zabbix[0]['inventory']['macaddress_a']
    ativo_no_zabbix.endereco_mac2 = dados_zabbix[0]['inventory']['macaddress_b']
    ativo_no_zabbix.hostname = dados_zabbix[0]['inventory']['name']
    ativo_no_zabbix.zabbix_id = dados_zabbix[0]['hostid']
    ativo_no_zabbix.ultima_verificacao = dados_zabbix[0]['inventory']['date_hw_decomm']
    ativo_no_zabbix.switchmac = dados_zabbix[0]['inventory']['location']
    ativo_no_zabbix.switchporta = dados_zabbix[0]['inventory']['url_b']
    ativo_no_zabbix.switchportadesc = dados_zabbix[0]['inventory']['url_c']
    ativo_no_zabbix.switchnome = dados_zabbix[0]['inventory']['url_a']

    try:
        ativo_no_zabbix.equipe = ativo_no_zabbix.hostname[0:3]
        ativo_no_zabbix.local = ativo_no_zabbix.hostname[3:6]
    except:
        ativo_no_zabbix.equipe = ""
        ativo_no_zabbix.local = ""

    if (ativo_no_zabbix.local == "FAP" ):
        ativo_no_zabbix.local = "EAS"
    if (ativo_no_zabbix.local == "FSE"):
        ativo_no_zabbix.local = "EBS"
    if (ativo_no_zabbix.local == "EAD"):
        ativo_no_zabbix.local = "EBQ"
    if (ativo_no_zabbix.equipe == "STG"):
        ativo_no_zabbix.equipe = "DEV"
    if (ativo_no_zabbix.equipe == "GTL"):
        ativo_no_zabbix.equipe = "ADM"
    if (ativo_no_zabbix.equipe == "NEA" or ativo_no_zabbix.equipe == "PAS" ):
        ativo_no_zabbix.equipe = "DEV"    
    ativo_no_zabbix.hostname = ativo_no_zabbix.equipe + \
        ativo_no_zabbix.local+ativo_no_zabbix.hostname[6:15]

    return ativo_no_zabbix
