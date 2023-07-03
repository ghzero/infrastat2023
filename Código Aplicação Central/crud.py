from datetime import date, timedelta
import datetime
from sqlalchemy.orm import Session
from typing import List
import zabbix_api
import json
from collections import OrderedDict
import itertools
import schemas
import models


def get_ativo(db: Session, ativo_hardware_id: int):
    return db.query(models.ativo_hardware).filter(models.ativo_hardware.id == ativo_hardware_id).first()


def get_processadores(db: Session):
    return db.query(models.biblioteca_hardware).filter(models.biblioteca_hardware.tipo == "processador").all()


def get_informacoes_de_sistema(db: Session):
    return db.query(models.informacao_sistema).all()


def get_desatualizados(db: Session, update_atual: str):
    return db.query(models.informacao_sistema).filter(models.informacao_sistema.dados_de_versao != update_atual).all()


def get_desatualizados_w11(db: Session, update_atual: str):
    return db.query(models.informacao_sistema).filter(models.informacao_sistema.dados_de_versao != update_atual).all()


def get_desatualizados_w7(db: Session, update_atual: str):
    return db.query(models.informacao_sistema).filter(models.informacao_sistema.dados_de_versao != update_atual).all()


def get_memorias(db: Session):
    return db.query(models.biblioteca_hardware).filter(models.biblioteca_hardware.tipo == "memoria").all()


def get_ativo_por_patrimonio(db: Session, patrimonio: str):
    return db.query(models.ativo_hardware).filter(models.ativo_hardware.patrimonio == patrimonio).first()

def get_estatisticas_de_uso(db: Session):
    return db.query(models.estatistica).filter(models.estatistica.tipo == "uso").first()


def busque_switch_no_database(db: Session, mac: str):
    return db.query(models.switch).filter(models.switch.mac == mac).first()


def get_lista_zabbixid_ativos_no_banco(db: Session, skip: int = 0, limit: int = 500):
    ids_no_db = db.query(models.ativo_hardware.zabbix_id).offset(
        skip).limit(limit).all()
    lista_ids = list(map(lambda t: t[0], ids_no_db))
    return list(lista_ids)


def get_ativos(db: Session, skip: int = 0, limit: int = 15000):
    return db.query(models.ativo_hardware).offset(skip).limit(limit).all()


def get_ativos2(db: Session, skip: int = 0, limit: int = 500):
    todos = db.query(models.ativo_hardware).offset(skip).limit(limit).all()
    dicionario = []
    for ativo in todos:
        dici = ativo.as_dict()
        dicionario.append(dici)
    #print (dicionario)
    return dicionario


def get_alteracoes_por_tipo(db: Session, tipo: str, skip: int = 0, limit: int = 500):
    todos = db.query(models.documento_de_alteracao).filter(
        models.documento_de_alteracao.tipo == tipo).offset(skip).limit(limit).all()
    dicionario = []
    for alteracao in todos:
        alteracao.data_alteracao = alteracao.data_alteracao.strftime(
            "%d/%m/%Y")
        timestamp = datetime.datetime.strptime(
            alteracao.data_alteracao, "%d/%m/%Y").timestamp()
        dici = alteracao.as_dict()
        dici['timestamp'] = timestamp

        dicionario.append(dici)
    #print (dicionario)
    return dicionario

def remove_alerta(db: Session,detalhes : str,tipo :str):
    alerta_id_db = db.query(models.alerta).filter(
        models.alerta.codigo == tipo).first()
    alerta_no_db = db.query(models.alerta_monitoramento).filter(models.alerta_monitoramento.alerta_id == alerta_id_db.id and models.alerta_monitoramento.detalhes == detalhes).first()    
    if(alerta_no_db):
     try: 
      db.delete(alerta_no_db)
      print("alerta de dados incompletos removido")
      return True
     except:
      print("Nao existe alerta para removar")
      return False    
    else:
     return False





def get_alertas_por_tipo(db: Session, codigo: str, skip: int = 0, limit: int = 500):
    alerta_db = db.query(models.alerta).filter(
        models.alerta.codigo == codigo).first()
    todos = db.query(models.alerta_monitoramento).filter(
        models.alerta_monitoramento.alerta_id == alerta_db.id).all()
    dicionario = []
    for alerta in todos:
        alertaz = {}
        alerta.data_ocorrencia = alerta.data_ocorrencia.strftime("%d/%m/%Y")
        timestamp = datetime.datetime.strptime(
            alerta.data_ocorrencia, "%d/%m/%Y").timestamp()
        alertaz['data_alteracao'] = alerta.data_ocorrencia
        alertaz['detalhes_alteracao'] = alerta_db.mensagem + alerta.detalhes
        alertaz['tipo'] = alerta_db.tipo_acao
        alertaz['timestamp'] = timestamp

        dicionario.append(alertaz)
    #print (dicionario)
    return dicionario


def get_informacao_de_hardware_do_ativo(db: Session, patrimonio: str):
    ativo = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.patrimonio == patrimonio).first()
    try:
        info_no_banco = db.query(
            models.informacao_hardware).with_parent(ativo).first()
        #print (info_no_banco.ativo_id)
        return info_no_banco
    except:
        info_no_banco = None
        return info_no_banco
    

def get_informacao_de_software_do_ativo(db: Session, patrimonio: str):
    ativo = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.patrimonio == patrimonio).first()
    lista_de_softwares = []
    try:
       
        info_no_banco = db.query(
            models.informacao_de_software).with_parent(ativo).all()
        #print (info_no_banco.ativo_id)
        for info in info_no_banco:
         dicionario_de_dados = {}
         dicionario_de_dados['nome'] = info.nome_software
         try:
                if (len(info.data_instalacao) == 8):
                    data = info.data_instalacao
                    newdate = "{}-{}-{}".format(data[6:], data[4:6], data[:4])
                    dicionario_de_dados['data_de_instalacao'] = newdate
                else:
                    dicionario_de_dados['data_de_instalacao'] = info.data_instalacao
         except:
                dicionario_de_dados['data_de_instalacao'] = info.data_instalacao
         dicionario_de_dados['versao_instalada'] = info.versao_instalada
         lista_de_softwares.append(dicionario_de_dados)
        return lista_de_softwares
    except:
        info_no_banco = None
        return info_no_banco



def get_toda_biblioteca_da_informacao_de_hardware(db: Session, info_hardware: models.informacao_hardware):

    try:
        biblioteca_no_banco = db.query(
            models.biblioteca_hardware).with_parent(info_hardware).all()
        #print (info_no_banco.ativo_id)
        return biblioteca_no_banco
    except:
        biblioteca_no_banco = None
        return biblioteca_no_banco


def get_ativo_com_informacao_de_sistema(db: Session, informacao: models.informacao_sistema):

    try:
        info_no_banco = db.query(
            models.ativo_hardware).with_parent(informacao).first()
        #print (info_no_banco.ativo_id)
        return info_no_banco
    except:
        info_no_banco = None
        return info_no_banco


def get_informacao_de_sistema_do_ativo(db: Session, patrimonio: str):

    try:
        ativo_no_banco = db.query(models.ativo_hardware).filter(
            models.ativo_hardware.patrimonio == patrimonio).first()
        info_no_banco = db.query(models.informacao_sistema).with_parent(
            ativo_no_banco).first()
        #print (info_no_banco.ativo_id)
        return info_no_banco
    except:
        info_no_banco = None
        return info_no_banco


def get_porta_no_db(db: Session, switch: models.switch, porta: str):
    ps_no_db = db.query(models.porta_switch).filter(
        models.porta_switch.switch_id == switch.id).filter(models.porta_switch.info == porta).first()

    return ps_no_db


def get_dados_porta_no_db(db: Session, switch_mac: str, porta: str):
    switch_no_db = db.query(models.switch).filter(
        models.switch.mac == switch_mac).first()
    retorno = None
    if (switch_no_db):
        #print("encontrei switch no DB")
        ps_no_db = db.query(models.porta_switch).filter(
            models.porta_switch.switch_id == switch_no_db.id).filter(models.porta_switch.porta == porta).first()
        if (ps_no_db):

            #print('encontrei a porta no db')
            lista = []
            lista.append(
                {"patrimonio": ps_no_db.ativo_pat, "data": 10101010101})
            lista.append(
                {"patrimonio": ps_no_db.ativo_pat, "data": 10101010101})
            retorno = {"patrimonio": str(
                ps_no_db.ativo_pat), "data": str(datetime.datetime.now())}
    return retorno


def get_lista_de_portas_no_db(db: Session, switch_mac: str):
    switch_no_db = db.query(models.switch).filter(
        models.switch.mac == switch_mac).first()
    dicionario = []
    if (switch_no_db):
        #print("encontrei switch no DB")
        ps_no_db = db.query(models.porta_switch).filter(
            models.porta_switch.switch_id == switch_no_db.id).all()
        if (ps_no_db):

            for ativo in ps_no_db:

                dici = ativo.as_dict()
                dicionario.append(dici)
    #print (dicionario)
    return dicionario


def get_placas_de_video(db):
    placas_no_db = db.query(models.biblioteca_hardware).filter(
        models.biblioteca_hardware.tipo == "monitor").all()
    for gpu in placas_no_db:
        print(gpu.nomeMonitoramento + " " + str(gpu.quantidade))

    return 0


def get_estatisticas(db: Session, skip: int = 0, limit: int = 100):
    data_ultima_verificacao = 0
    total_verificados = 0
    total_atualizados = 0
    total_cadastrado = 0
    total_descoberto = 0
    total_erro = 0
    total_ativos_monitorados = db.query(models.ativo_hardware).all()
    total_desktops = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.tipo == "desktop").all()
    total_notebooks = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.tipo == "notebook").all()
    lista_ativos_banco = get_lista_zabbixid_ativos_no_banco(db)
    dicionario_status_icmp = zabbix_api.busca_icmp_todos_hosts(
        lista_ativos_banco)
    memorias = db.query(models.biblioteca_hardware).filter(
        models.biblioteca_hardware.tipo == "memoria").all()
    processadores = db.query(models.biblioteca_hardware).filter(
        models.biblioteca_hardware.tipo == "processador").all()
    quantidade_de_pentes = 0
    for memoria in memorias:
        quantidade_de_pentes = quantidade_de_pentes + memoria.quantidade

    ultimo_log = db.query(models.log_sistema).order_by(
        models.log_sistema.id.desc()).limit(1)
    for log in ultimo_log:
        data_ultima_verificacao = log.data_execucao.strftime("%d/%m %H:%M")
        total_descoberto = log.total_ativos
        total_verificados = log.total_ativos_verificados
        total_atualizados = log.total_ativos_atualizados
        total_cadastrado = log.total_ativos_cadastrados
        total_erro = log.total_ativos_com_problema

    dicionario = {"total_monitorados": len(total_ativos_monitorados),
                  "total_online": dicionario_status_icmp['total_online'],
                  "total_offline": dicionario_status_icmp['total_offline'],
                  "total_manutencao": 0,
                  "total_desativados": 0,
                  "total_ociosos": 0,
                  "total_desktops": len(total_desktops),
                  "total_notebooks": len(total_notebooks),
                  "total_memorias": quantidade_de_pentes,
                  "total_modelos_de_processador": len(processadores),
                  "log_data_verificacao": data_ultima_verificacao,
                  "log_total_descoberto": total_descoberto,
                  "log_total_verificado": total_verificados,
                  "log_total_atualizado": total_atualizados,
                  "log_total_cadastrado": total_cadastrado,
                  "log_total_erro": total_erro


                  }

    jsonStr = json.dumps(dicionario)
    print(jsonStr)

    return jsonStr


def get_estatisticas_de_software(db: Session, skip: int = 0, limit: int = 100):

    total_de_softwares = db.query(models.biblioteca_de_software).all()
    total_de_desenvolvedores = db.query(models.fabricante).all()
    total_de_tipos = 0
    total_de_instalacoes = db.query(models.informacao_de_software).all()
    total_de_blacklisted = 0
    dicionario_de_ativos_blacklisted = {}
    dicionario_de_softwares_blacklisted = {}
    dicionario_de_tipos_de_software = {}
    dicionario_de_tipos_de_software_instalacoes = {}
    dicionario_contagem_de_instalacoes = {}
    dicionario_de_instalacoes = {}
    set_ativos_com_sw_blacklisted = set()
    lista_de_softwares_blacklisted = []

    for software in total_de_softwares:
        if (software.monitorado == True):
            if dicionario_de_tipos_de_software.get(software.tipo_de_software):
                dicionario_de_tipos_de_software[software.tipo_de_software] = dicionario_de_tipos_de_software[software.tipo_de_software] + 1
            else:
                dicionario_de_tipos_de_software[software.tipo_de_software] = 1

        if (software.blacklist == True):
            lista_de_softwares_blacklisted.append(software)
            identificadores_de_software = db.query(
                models.identificador_de_software).with_parent(software)
            for identificador in identificadores_de_software:
                info_no_db = db.query(models.informacao_de_software).with_parent(
                    identificador).all()
                for info in info_no_db:
                    ativo_no_db = db.query(
                        models.ativo_hardware).with_parent(info).first()
                    set_ativos_com_sw_blacklisted.add(ativo_no_db.hostname)
                    if dicionario_de_ativos_blacklisted.get(software.nome):
                        dicionario_de_ativos_blacklisted[software.nome].append(
                            ativo_no_db.hostname)
                    else:
                        dicionario_de_ativos_blacklisted[software.nome] = []
                        dicionario_de_ativos_blacklisted[software.nome].append(
                            ativo_no_db.hostname)
                    if dicionario_de_softwares_blacklisted.get(software.nome):
                        dicionario_de_softwares_blacklisted[
                            software.nome] = dicionario_de_softwares_blacklisted[software.nome] + 1
                    else:
                        dicionario_de_softwares_blacklisted[software.nome] = 1
        else:
            identificadores_de_software = db.query(
                models.identificador_de_software).with_parent(software)

            for identificador in identificadores_de_software:
                info_no_db = db.query(models.informacao_de_software).with_parent(
                    identificador).all()
                #print (len(info_no_db))
                # print(software.nome)
                if dicionario_contagem_de_instalacoes.get(software.nome):
                    lista_tipo_total = dicionario_de_tipos_de_software_instalacoes[software.nome]
                    lista_tipo_total[1] = lista_tipo_total[1] + 1
                    dicionario_de_tipos_de_software_instalacoes[software.nome] = lista_tipo_total
                    dicionario_contagem_de_instalacoes[software.nome] = dicionario_contagem_de_instalacoes[software.nome] + len(
                        info_no_db)
                else:
                    lista_tipo_total = []
                    lista_tipo_total.append(software.tipo_de_software)
                    lista_tipo_total.append(len(info_no_db))
                    dicionario_de_tipos_de_software_instalacoes[software.nome] = lista_tipo_total
                    dicionario_contagem_de_instalacoes[software.nome] = len(
                        info_no_db)

    total_de_blacklisted = len(lista_de_softwares_blacklisted)
    total_de_tipos = len(dicionario_de_tipos_de_software)
    dicionario_ordenado = dict(sorted(dicionario_contagem_de_instalacoes.items(
    ), key=lambda item: item[1], reverse=True))
    top50 = dict(itertools.islice(dicionario_ordenado.items(), 30))
    #print (dicionario_contagem_de_instalacoes)
    #print (top50)
    lista_softwares_lala = []
    categorias = ['engenharia', 'design', 'escritorio', 'geoespacial',
                  'programacao', 'banco de dados', 'estatistico', 'utilitario']

    for k, v in dicionario_de_tipos_de_software_instalacoes.items():
        novodici = {}
        novodici['name'] = k
        categoriasx = [0, 0, 0, 0, 0, 0, 0]
        if (v[0] == "engenharia"):
            categoriasx.insert(0, v[1])
            novodici['data'] = categoriasx
            lista_softwares_lala.append(novodici)
        if (v[0] == "design"):
            categoriasx.insert(1, v[1])
            novodici['data'] = categoriasx
            lista_softwares_lala.append(novodici)
        if (v[0] == "escritorio"):
            categoriasx.insert(2, v[1])
            novodici['data'] = categoriasx
            lista_softwares_lala.append(novodici)
        if (v[0] == "geoespacial"):
            categoriasx.insert(3, v[1])
            novodici['data'] = categoriasx
            lista_softwares_lala.append(novodici)
        if (v[0] == "programacao"):
            categoriasx.insert(4, v[1])
            novodici['data'] = categoriasx
            lista_softwares_lala.append(novodici)
        if (v[0] == "banco de dados"):
            categoriasx.insert(5, v[1])
            novodici['data'] = categoriasx
            lista_softwares_lala.append(novodici)
        if (v[0] == "estatistico"):
            categoriasx.insert(6, v[1])
            novodici['data'] = categoriasx
            lista_softwares_lala.append(novodici)
        if (v[0] == "utilitario"):
            categoriasx.insert(7, v[1])
            novodici['data'] = categoriasx
            lista_softwares_lala.append(novodici)

    #print(lista_softwares_lala)

    bar_tipo_instalacao = {"labels": [], "series": []}
    bar_tipo_instalacao["labels"] += categorias
    bar_tipo_instalacao["series"] += lista_softwares_lala

    donut_tipos_de_software = {"labels": [], "series": []}
    donut_tipos_de_software["labels"] += dicionario_de_tipos_de_software.keys()
    donut_tipos_de_software["series"] += dicionario_de_tipos_de_software.values()

    donut_blacklist = {"labels": [], "series": []}
    donut_blacklist["labels"] += dicionario_de_softwares_blacklisted.keys()
    donut_blacklist["series"] += dicionario_de_softwares_blacklisted.values()

    donut_instalacoes = {"labels": [], "series": []}
    donut_instalacoes["labels"] += top50.keys()
    donut_instalacoes["series"] += top50.values()

    dicionario = {"total_de_softwares": len(total_de_softwares),
                  "total_de_desenvolvedores": len(total_de_desenvolvedores),
                  "total_de_tipos": total_de_tipos,
                  "total_de_blacklisted": total_de_blacklisted,
                  "total_de_instalacoes": len(total_de_instalacoes),
                  "total_de_ativos_com_instalacao_blacklisted": len(set_ativos_com_sw_blacklisted),
                  "donut_blacklist": donut_blacklist,
                  "donut_instalacoes": donut_instalacoes,
                  "donut_tipos_de_software": donut_tipos_de_software,
                  "bar_tipo_instalacao": donut_tipos_de_software,
                  "instalacoes_de_software_blacklist": dicionario_de_ativos_blacklisted
                  }

    jsonStr = json.dumps(dicionario)
    # print(jsonStr)

    return jsonStr

def get_estatisticas_de_uso(db: Session):
    dicionario_de_retorno = {}
    estatisticas_de_uso = db.query(models.estatistica).filter(models.estatistica.tipo == "uso").first()
    json_resultante = estatisticas_de_uso.resultado
    dicionario = json.loads(json_resultante)
    
    
    dicionario_de_retorno['data_execucao'] = str(estatisticas_de_uso.data_execucao)
    dicionario_de_retorno['periodo_da_estatistica'] = str(estatisticas_de_uso.periodo_da_estatistica)
    dicionario_de_retorno['valor_do_kwh'] = "R$ " + str(dicionario['valor_do_kwh'])
    dicionario_de_retorno['gasto_total'] = "R$ " + str(dicionario['gasto_total'])
    dicionario_de_retorno['gasto_efetivo_total'] = "R$ " + str(dicionario['gasto_efetivo_total'])
    dicionario_de_retorno['desperdicio_total'] = "R$ " + str(dicionario['desperdicio_total'])
    dicionario_de_retorno['total_computadores_sem_uso'] = dicionario['total_computadores_sem_uso']
    dicionario_de_retorno['total_energia_gasto_computadores_sem_uso'] = "R$ " + str(dicionario['total_energia_gasto_computadores_sem_uso'])
    dicionario_de_retorno['lista_de_computadores_sem_uso'] = dicionario['lista_de_computadores_sem_uso']

    
    labels = ["DESPERDÍCIO", "EFETIVO"]
    dici_sala1 = {"labels": [], "series": []}
    dici_sala2 = {"labels": [], "series": []}
    dici_sala3 = {"labels": [], "series": []}
    dici_sala1["labels"] += labels
    dici_sala2["labels"] += labels
    dici_sala3["labels"] += labels

    series_sala1 = [dicionario['uso_sala_1']['total'],dicionario['uso_sala_1']['efetivo']]
    series_sala2 = [dicionario['uso_sala_2']['total'],dicionario['uso_sala_2']['efetivo']]
    series_sala3 = [dicionario['uso_sala_3']['total'],dicionario['uso_sala_3']['efetivo']]
    dici_sala1["series"] += series_sala1
    dici_sala2["series"] += series_sala2
    dici_sala3["series"] += series_sala3

    dicionario_de_retorno['donut_sala_1'] = dici_sala1
    dicionario_de_retorno['donut_sala_2'] = dici_sala2
    dicionario_de_retorno['donut_sala_3'] = dici_sala3

    json_retorno = json.dumps(dicionario_de_retorno)


    return json_retorno

def get_lista_de_ativos_estatisticas_de_uso(db: Session):
    dicionario_de_retorno = {}
    estatisticas_de_uso = db.query(models.estatistica).filter(models.estatistica.tipo == "uso").first()
    json_resultante = estatisticas_de_uso.resultado
    dicionario = json.loads(json_resultante)

    
    
    dic  = {"data": dicionario['lista_de_ativos']}
    json_def = json.dumps(dic)

    return json_def


def get_total_alertas_7_dias(db: Session, skip: int = 0, limit: int = 100):

    hoje = date.today() + timedelta(days=1)
    total_alertas_lista = []
    sete_dias = date.today() - timedelta(days=7)
    total_alertas = db.query(models.alerta_monitoramento).filter(models.alerta_monitoramento.data_ocorrencia <= hoje).filter(
        models.alerta_monitoramento.data_ocorrencia >= sete_dias).all()
    #print(total_alertas)
    total_alteracoes = db.query(models.documento_de_alteracao).filter(
        models.documento_de_alteracao.data_alteracao <= hoje).filter(models.documento_de_alteracao.data_alteracao >= sete_dias).all()
    alerta_HIN = db.query(models.alerta).filter(
        models.alerta.codigo == "HIN").first()
    alerta_HFP = db.query(models.alerta).filter(
        models.alerta.codigo == "HFP").first()

    total_alerta_padronizacao = 0
    total_alerta_dados_incompletos = 0
    total_alteracao_configuracao = 0
    total_alteracao_seguranca = 0
    total_alteracao_hardware = 0
    total_alteracao_software = 0
    for alerta in total_alertas:
        total_alertas_lista.append(alerta)

        if (alerta_HIN and alerta.alerta_id == alerta_HIN.id):
            total_alerta_dados_incompletos = total_alerta_dados_incompletos + 1
        if (alerta_HFP and alerta.alerta_id == alerta_HFP.id):
            total_alerta_padronizacao = total_alerta_padronizacao + 1
    for alt in total_alteracoes:
        if (alt.tipo == "configuracao"):
            total_alteracao_configuracao = total_alteracao_configuracao + 1
        if (alt.tipo == "hardware"):
            total_alteracao_hardware = total_alteracao_hardware + 1
        if (alt.tipo == "seguranca"):
            total_alteracao_seguranca = total_alteracao_seguranca + 1
        if (alt.tipo == "software"):
            total_alteracao_software = total_alteracao_software + 1    

    dicionario = {"total_alertas_e_alteracoes": len(total_alertas)+len(total_alteracoes),
                  "total_alertas_7_dias": len(total_alertas),
                  "total_alteracoes_7_dias": total_alteracao_configuracao + total_alteracao_hardware + total_alteracao_seguranca,
                  "total_alerta_padronizacao": total_alerta_padronizacao,
                  "total_alerta_dados_incompletos": total_alerta_dados_incompletos,
                  "total_alteracao_configuracao": total_alteracao_configuracao,
                  "total_alteracao_hardware": total_alteracao_hardware,
                  "total_alteracao_seguranca": total_alteracao_seguranca,
                  "total_alteracao_software": total_alteracao_software

                  }

    jsonStr = json.dumps(dicionario)
    print(jsonStr)

    return jsonStr


def get_donut_ativos_local(db: Session, skip: int = 0, limit: int = 100):
    labels = ["LOC", "FSE", "ECV", "SAN", "EAD", "MAX","DNT"]
    #labels = ["EAS", "EBS", "EBQ"]
    dici = {"labels": [], "series": []}
    dici["labels"] += labels
    ativos_fap = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.local == "LOC").all()
    ativos_fse = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.local == "FSE").all()
    ativos_ecv = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.local == "ECV").all()
    ativos_san = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.local == "SAN").all()
    ativos_ead = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.local == "EAD").all()
    ativos_max = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.local == "MAX").all()
    ativos_dnt = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.local == "DNT").all()
    series = [len(ativos_fap), len(ativos_fse), len(ativos_ecv), len(ativos_san), len(ativos_ead), len(ativos_max), len(ativos_dnt)]
    #series = [len(ativos_fap), len(ativos_fse), len(ativos_ecv)]
    dici["series"] += series

    jsonStr = json.dumps(dici)
    print(jsonStr)

    return jsonStr


def get_donut_ativos_equipe(db: Session, skip: int = 0, limit: int = 100):
    labels = ["TST", "STG", "PAS", "SUP", "NEA", "WEB", "ADM"]
    #labels = ["DEV", "ADM"]
    dici = {"labels": [], "series": []}
    dici["labels"] += labels
    ativos_gtl = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.equipe == "TST").all()
    ativos_stg = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.equipe == "STG").all()
    ativos_pas = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.equipe == "PAS").all()
    ativos_sup = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.equipe == "SUP").all()
    ativos_nea = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.equipe == "NEA").all()
    ativos_web = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.equipe == "WEB").all()
    ativos_adm = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.equipe == "ADM").all()

    #series = [len(ativos_gtl), len(ativos_stg)]
    series = [len(ativos_gtl), len(ativos_stg), len(ativos_pas), len(ativos_sup), len(ativos_nea), len(ativos_web), len(ativos_adm)]
    dici["series"] += series

    jsonStr = json.dumps(dici)
    print(jsonStr)

    return jsonStr


def get_donut_versoes_windows(db: Session, skip: int = 0, limit: int = 100):
    #GTL - PAS - NET - SUP - NEA - ADM - WEB - STG
    labels = []
    series = []
    dicionario_de_versoes = {}
    dici = {"labels": [], "series": []}

    dados_de_sistema = db.query(models.informacao_sistema).all()
    for info in dados_de_sistema:
        if (info.dados_de_versao in dicionario_de_versoes.keys()):
            dicionario_de_versoes[info.dados_de_versao] = dicionario_de_versoes[info.dados_de_versao] + 1
        else:
            dicionario_de_versoes[info.dados_de_versao] = 1

    series = []
    for key, value in dicionario_de_versoes.items():
        labels.append(key)
        series.append(value)
    dici["labels"] += labels
    dici["series"] += series
    jsonStr = json.dumps(dici)
    print(jsonStr)

    return jsonStr


def get_donut_ativos_tipo(db: Session, skip: int = 0, limit: int = 100):
    #GTL - PAS - NET - SUP - NEA - ADM - WEB - STG
    labels = ["Desktop", "Notebook"]
    dici = {"labels": [], "series": []}
    dici["labels"] += labels
    ativos_gtl = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.tipo == "desktop").all()
    ativos_stg = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.tipo == "notebook").all()

    series = [len(ativos_gtl), len(ativos_stg)]
    dici["series"] += series

    jsonStr = json.dumps(dici)
    print(jsonStr)

    return jsonStr


def teste_bar(db):

    dici = {"labels": [], "series": []}
    serie_total_ativos = []
    serie_total_verificados = []
    serie_total_atualizados = []
    serie_total_cadastrados = []
    serie_total_problema = []

    labels = []

    ultimos_5_logs = db.query(models.log_sistema).order_by(
        models.log_sistema.id.desc()).limit(5)
    for log in ultimos_5_logs:
        labels.append(log.data_execucao.strftime("%d/%m %Hh"))
        serie_total_ativos.append(log.total_ativos)
        serie_total_verificados.append(log.total_ativos_verificados)
        serie_total_atualizados.append(log.total_ativos_atualizados)
        serie_total_cadastrados.append(log.total_ativos_cadastrados)
        serie_total_problema.append(log.total_ativos_com_problema)

    lista_retorno = []

    dicionario_para_filtrar = {}
    dicionario_para_filtrar['name'] = "Cadastrados"
    dicionario_para_filtrar['data'] = serie_total_cadastrados
    lista_retorno.append(dicionario_para_filtrar)

    dicionario_para_filtrar = {}
    dicionario_para_filtrar['name'] = "Verificados"
    dicionario_para_filtrar['data'] = serie_total_verificados
    lista_retorno.append(dicionario_para_filtrar)

    dicionario_para_filtrar = {}
    dicionario_para_filtrar['name'] = "Total encontrado"
    dicionario_para_filtrar['data'] = serie_total_ativos
    lista_retorno.append(dicionario_para_filtrar)

    dicionario_para_filtrar = {}
    dicionario_para_filtrar['name'] = "Com problema"
    dicionario_para_filtrar['data'] = serie_total_problema
    lista_retorno.append(dicionario_para_filtrar)

    dicionario_para_filtrar = {}
    dicionario_para_filtrar['name'] = "Atualizados"
    dicionario_para_filtrar['data'] = serie_total_atualizados
    lista_retorno.append(dicionario_para_filtrar)

    dici["series"] += lista_retorno
    dici["labels"] += labels
    jsonStr = json.dumps(dici)

    return jsonStr





def get_donut_biblioteca_hardware(db: Session, tipo: str, skip: int = 0, limit: int = 100):
    #GTL - PAS - NET - SUP - NEA - ADM - WEB - STG
    labels = []
    series = []
    dici = {"labels": [], "series": []}

    todos_biblioteca = db.query(models.biblioteca_hardware).filter(
        models.biblioteca_hardware.tipo == tipo).all()
    for hardware in todos_biblioteca:
        labels.append(hardware.nomeMonitoramento)
        series.append(hardware.quantidade)
    #ativos_gtl = db.query(models.ativo_hardware).filter(models.ativo_hardware.tipo == "desktop").all()
    #ativos_stg = db.query(models.ativo_hardware).filter(models.ativo_hardware.tipo == "notebook").all()

    #series = [len(ativos_gtl),len(ativos_stg)]
    dici["labels"] += labels
    dici["series"] += series
    print(len(todos_biblioteca))
    jsonStr = json.dumps(dici)
    print(jsonStr)

    return jsonStr


def get_donut_monitores(db: Session, tipo: str, skip: int = 0, limit: int = 100):
    #GTL - PAS - NET - SUP - NEA - ADM - WEB - STG
    labels = []
    series = []
    dici = {"labels": [], "series": []}
    total_samsung = 0
    total_lg = 0
    total_philco = 0
    total_sony = 0
    total_benq = 0
    total_acer = 0
    total_acer = 0
    total_outros = 0
    todos_biblioteca = db.query(models.biblioteca_hardware).filter(
        models.biblioteca_hardware.tipo == "monitor").all()
    for monitor in todos_biblioteca:
        if ("sam" in monitor.nomeMonitoramento):
            if ("sam" not in labels):

                total_samsung = total_samsung + monitor.quantidade
    #ativos_gtl = db.query(models.ativo_hardware).filter(models.ativo_hardware.tipo == "desktop").all()
    #ativos_stg = db.query(models.ativo_hardware).filter(models.ativo_hardware.tipo == "notebook").all()

    #series = [len(ativos_gtl),len(ativos_stg)]
    dici["labels"] += labels
    dici["series"] += series
    print(len(todos_biblioteca))
    jsonStr = json.dumps(dici)
    print(jsonStr)

    return jsonStr


def get_donut_biblioteca_hardware_sem_elemento(db: Session, tipo: str, elemento: str, skip: int = 0, limit: int = 100):
    #GTL - PAS - NET - SUP - NEA - ADM - WEB - STG
    labels = []
    series = []
    dici = {"labels": [], "series": []}

    todos_biblioteca = db.query(models.biblioteca_hardware).filter(
        models.biblioteca_hardware.tipo == tipo).all()
    for hardware in todos_biblioteca:
        if (elemento not in str(hardware.detalhes)):
            labels.append(hardware.nomeMonitoramento)
            series.append(hardware.quantidade)
    #ativos_gtl = db.query(models.ativo_hardware).filter(models.ativo_hardware.tipo == "desktop").all()
    #ativos_stg = db.query(models.ativo_hardware).filter(models.ativo_hardware.tipo == "notebook").all()

    #series = [len(ativos_gtl),len(ativos_stg)]
    dici["labels"] += labels
    dici["series"] += series

    jsonStr = json.dumps(dici)
    print(jsonStr)

    return jsonStr


def get_donut_biblioteca_hardware_com_elemento(db: Session, tipo: str, elemento: str, skip: int = 0, limit: int = 100):
    #GTL - PAS - NET - SUP - NEA - ADM - WEB - STG
    labels = []
    series = []
    dici = {"labels": [], "series": []}

    todos_biblioteca = db.query(models.biblioteca_hardware).filter(
        models.biblioteca_hardware.tipo == tipo).all()
    for hardware in todos_biblioteca:
        if (elemento in str(hardware.detalhes)):
            labels.append(hardware.nomeMonitoramento)
            series.append(hardware.quantidade)
    #ativos_gtl = db.query(models.ativo_hardware).filter(models.ativo_hardware.tipo == "desktop").all()
    #ativos_stg = db.query(models.ativo_hardware).filter(models.ativo_hardware.tipo == "notebook").all()

    #series = [len(ativos_gtl),len(ativos_stg)]
    dici["labels"] += labels
    dici["series"] += series

    jsonStr = json.dumps(dici)
    #print(len(todos_biblioteca))
    print(jsonStr)

    return jsonStr


def get_donut_memoria_filtrada(db: Session, skip: int = 0, limit: int = 100):
    #GTL - PAS - NET - SUP - NEA - ADM - WEB - STG
    labels = ["2GB DDR3", "4GB DDR3", "8GB DDR3", "16GB DDR3",
              "4GB DDR4", "8GB DDR4"]
    series = []
    dici = {"labels": [], "series": []}
    total_2gb_ddr3 = 0
    total_4gb_ddr3 = 0
    total_4gb_ddr4 = 0
    total_8gb_ddr3 = 0
    total_8gb_ddr4 = 0
    total_16gb_ddr3 = 0
    total_16gb_ddr4 = 0
    total_32gb_ddr4 = 0
    total_outros = 0
    todos_biblioteca = db.query(models.biblioteca_hardware).filter(
        models.biblioteca_hardware.tipo == "memoria").all()
    #print(len(todos_biblioteca))
    for hardware in todos_biblioteca:
        if ("4GB ddr3" in str(hardware.nomeMonitoramento)):
            total_4gb_ddr3 = total_4gb_ddr3 + hardware.quantidade
        else:
            if ("8GB ddr3" in str(hardware.nomeMonitoramento)):
                total_8gb_ddr3 = total_8gb_ddr3 + hardware.quantidade
            else:
                if ("16GB ddr3" in str(hardware.nomeMonitoramento)):
                    total_16gb_ddr3 = total_16gb_ddr3 + hardware.quantidade
                else:
                    if ("4GB ddr4" in str(hardware.nomeMonitoramento)):
                        total_4gb_ddr4 = total_4gb_ddr4 + hardware.quantidade
                    else:
                        if ("8GB ddr4" in str(hardware.nomeMonitoramento)):
                            total_8gb_ddr4 = total_8gb_ddr4 + hardware.quantidade
                        else:
                            if ("16GB ddr4" in str(hardware.nomeMonitoramento)):
                                total_16gb_ddr4 = total_16gb_ddr4 + hardware.quantidade
                            else:
                                if ("32GB ddr4" in str(hardware.nomeMonitoramento)):
                                    total_32gb_ddr4 = total_32gb_ddr4 + hardware.quantidade
                                else:
                                    if ("2GB ddr3" in str(hardware.nomeMonitoramento)):
                                        total_2gb_ddr3 = total_2gb_ddr3 + hardware.quantidade
                                    else:
                                        total_outros = total_outros + hardware.quantidade

    #ativos_gtl = db.query(models.ativo_hardware).filter(models.ativo_hardware.tipo == "desktop").all()
    #ativos_stg = db.query(models.ativo_hardware).filter(models.ativo_hardware.tipo == "notebook").all()

    #series = [len(ativos_gtl),len(ativos_stg)]
    series = [total_2gb_ddr3, total_4gb_ddr3, total_8gb_ddr3, total_16gb_ddr3,
              total_4gb_ddr4, total_8gb_ddr4, total_16gb_ddr4, total_32gb_ddr4, total_outros]
    dici["labels"] += labels
    dici["series"] += series

    jsonStr = json.dumps(dici)
    print(jsonStr)

    return jsonStr


def get_donut_monitores_filtrados(db: Session, skip: int = 0, limit: int = 100):
    #GTL - PAS - NET - SUP - NEA - ADM - WEB - STG
    labels = ["SAMSUNG", "LG", "PHILIPS",
              "SONY", "BENQ", "ACER", "AOC", "OUTROS"]
    series = []

    total_samsung = 0
    total_lg = 0
    total_philips = 0
    total_sony = 0
    total_benq = 0
    total_acer = 0
    total_aoc = 0
    total_outros = 0
    dici = {"labels": [], "series": []}
    todos_biblioteca = db.query(models.biblioteca_hardware).filter(
        models.biblioteca_hardware.tipo == "monitor").all()
    #print(len(todos_biblioteca))
    for hardware in todos_biblioteca:
        #print(hardware.nomeMonitoramento)
        if ("sam" in str(hardware.nomeMonitoramento)):
            total_samsung = total_samsung + hardware.quantidade
        else:
            if ("gsm" in str(hardware.nomeMonitoramento)):
                total_lg = total_lg + hardware.quantidade
            else:
                if ("phl" in str(hardware.nomeMonitoramento)):
                    total_philips = total_philips + hardware.quantidade
                else:
                    if ("sny" in str(hardware.nomeMonitoramento)):
                        total_sony = total_sony + hardware.quantidade
                    else:
                        if ("bnq" in str(hardware.nomeMonitoramento)):
                            total_benq = total_benq + hardware.quantidade
                        else:
                            if ("acr" in str(hardware.nomeMonitoramento)):
                                total_acer = total_acer + hardware.quantidade
                            else:
                                if ("aoc" in str(hardware.nomeMonitoramento)):
                                    total_aoc = total_aoc + hardware.quantidade
                                else:
                                    total_outros = total_outros + hardware.quantidade

    #ativos_gtl = db.query(models.ativo_hardware).filter(models.ativo_hardware.tipo == "desktop").all()
    #ativos_stg = db.query(models.ativo_hardware).filter(models.ativo_hardware.tipo == "notebook").all()

    #series = [len(ativos_gtl),len(ativos_stg)]
    series = [total_samsung, total_lg, total_philips, total_sony,
              total_benq, total_acer, total_aoc, total_outros]
    dici["labels"] += labels
    dici["series"] += series

    jsonStr = json.dumps(dici)
    print(jsonStr)

    return jsonStr


def criar_ativo(db: Session, ativo: schemas.ativo_hardware_base):
    data_cadastro = date.today()
    db_ativo = models.ativo_hardware(zabbix_id=ativo.zabbix_id, cmdb_id=ativo.cmdb_id, tipo=ativo.tipo, ciclo_de_vida=ativo.ciclo_de_vida, status=ativo.status, endereco_mac=ativo.endereco_mac, patrimonio=ativo.patrimonio,
                                     hostname=ativo.hostname, equipe=ativo.equipe, local=ativo.local, data_cadastro=data_cadastro, endereco_ip=ativo.endereco_ip, quem_cadastrou=ativo.quem_cadastrou, monitorado=ativo.monitorado)
    db.add(db_ativo)
    db.commit()
    db.refresh(db_ativo)
    #print ("cadastrado no banco" + db_ativo.patrimonio)
    return db_ativo


def criar_switch(db: Session, switch: schemas.switch):
    #data_cadastro = date.today()
    db_switch = models.switch(regexporta=switch.regexporta, mac=switch.mac,
                              stack=switch.stack, local=switch.local, modelo=switch.modelo)
    db.add(db_switch)
    db.commit()
    db.refresh(db_switch)
    #print ("cadastrado no banco" + db_ativo.patrimonio)
    return db_switch


def criar_porta_switch(db: Session, switch: models.switch, patrimonio: str, info_do_switch: str, porta_do_switch: str, stack_do_switch: str):
    #data_cadastro = date.today()
    db_switch = switch
    db_ativo = get_ativo_por_patrimonio(db, patrimonio)
    db_porta = ""
    if (db_ativo):
        db_porta = models.porta_switch(
            porta_do_switch, stack_do_switch, info_do_switch, patrimonio, db_ativo.id, db_switch.id)
        db.add(db_porta)
        db.commit()
        db.refresh(db_porta)
    #print ("cadastrado no banco" + db_ativo.patrimonio)
    return db_porta


def atualize_porta(db: Session, switch: models.switch, patrimonio: str, porta_no_db: models.porta_switch):
    ativo_no_db = get_ativo_por_patrimonio(db, patrimonio)
    if (ativo_no_db):
        porta_no_db.ativo_pat = patrimonio
        porta_no_db.switch_id = switch.id
        db.commit()
        db.refresh(porta_no_db)
    return porta_no_db


def get_lista_localizacao_errada(db: Session):
    switches_no_db = db.query(models.switch).all()
    ativos_no_db = db.query(models.ativo_hardware).all()
    dici = {"series": []}
    for switch in switches_no_db:
        ps_no_db = db.query(models.porta_switch).filter(
            models.porta_switch.switch_id == switch.id).all()
        if (ps_no_db):

            for porta in ps_no_db:
                ativo = db.query(models.ativo_hardware).filter(models.ativo_hardware.id == porta.ativo_id).filter(
                    models.ativo_hardware.local != switch.local).first()
                if (ativo):
                    print(ativo.hostname + " Alterar Para -> " + switch.local)

    series = ["um", "dois"]
    dici["series"] += series

    jsonStr = json.dumps(dici)

    return jsonStr


def get_nomes_errados_em_alerta(db: Session):
    ativos_em_alerta = db.query(models.alerta_monitoramento).filter(
        models.alerta_monitoramento.alerta_id == 1).all()

    #for ativo in ativos_em_alerta:
     #   print(ativo.detalhes)

    dici = {"series": []}

    series = ["um", "dois"]
    dici["series"] += series

    jsonStr = json.dumps(dici)

    return jsonStr


def criar_log_erro_busca(db: Session, log_mensagem: str):
    data_acao = date.today()
    db_log = models.log_sistema(
        status="erro", tipo_acao="busca", mensagem=log_mensagem, data_acao=data_acao)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def criar_log_erro_cadastro(db: Session, log_mensagem: str):
    data_acao = date.today()
    db_log = models.log_sistema(
        status="erro", tipo_acao="cadastro", mensagem=log_mensagem, data_acao=data_acao)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def criar_log_erro_atualizacao(db: Session, log_mensagem: str):
    data_acao = date.today()
    db_log = models.log_sistema(
        status="erro", tipo_acao="atualizacao", mensagem=log_mensagem, data_acao=data_acao)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    return db_log


def criar_log_erro_verificacao(db: Session, log_mensagem: str):
    data_acao = date.today()
    db_log = models.log_sistema(
        status="erro", tipo_acao="verificacao", mensagem=log_mensagem, data_acao=data_acao)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    return db_log


def criar_log_sucesso_verificacao(db: Session, log_mensagem: str):
    data_acao = date.today()
    db_log = models.log_sistema(
        status="sucesso", tipo_acao="verificacao", mensagem=log_mensagem, data_acao=data_acao)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    return db_log


def criar_log_sucesso_cadastro(db: Session, log_mensagem: str):
    data_acao = date.today()
    db_log = models.log_sistema(
        status="sucesso", tipo_acao="cadastro", mensagem=log_mensagem, data_acao=data_acao)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    return db_log


def criar_log_sucesso_atualizacao(db: Session, log_mensagem: str):
    data_acao = date.today()
    db_log = models.log_sistema(
        status="sucesso", tipo_acao="atualizacao", mensagem=log_mensagem, data_acao=data_acao)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    return db_log


def criar_log_sistema(db: Session, total_ativos: str, total_ativos_verificados: str, total_ativos_atualizados: str, total_ativos_cadastrados: str, total_com_problema: str, tempo_execucao: int):
    data_acao = datetime.datetime.now()
    db_log = models.log_sistema(status="automatico", total_ativos=total_ativos, total_ativos_verificados=total_ativos_verificados, total_ativos_atualizados=total_ativos_atualizados,
                                total_ativos_cadastrados=total_ativos_cadastrados, total_ativos_com_problema=total_com_problema, data_execucao=data_acao, tempo_execucao_segundos=tempo_execucao)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    #print ("cadastrado no banco" + db_ativo.patrimonio)
    return db_log


def criar_alerta(db: Session, codigo: str, mensagem: str, tipo_acao: str, detalhes_acao: str):
    db_alerta = db.query(models.alerta).filter(
        models.alerta.codigo == codigo).first()
    if (db_alerta):
        return db_alerta
    else:
        db_alerta = models.alerta(
            codigo=codigo, mensagem=mensagem, tipo_acao=tipo_acao, detalhes_acao=detalhes_acao)
        db.add(db_alerta)
        db.commit()

    return db_alerta


def criar_documento_de_alteracao(db: Session, tipo: str, alteracao: str, detalhes: str, ativo: models.ativo_hardware):
    ativo_no_banco = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.patrimonio == ativo.patrimonio).first()
    data_alteracao = date.today()
    foi_verificado = False
    foi_autorizado = False
    quem_autorizou = ""
    id_autorizacao = ""
    db_alteracao_existe = db.query(models.documento_de_alteracao).filter(models.documento_de_alteracao.tipo == "configuracao").filter(
        models.documento_de_alteracao.detalhes_alteracao == detalhes).first()
    if (db_alteracao_existe):
        print("alteracao de configuracao ja existe")
        return db_alteracao_existe

    else:

        db_alteracao = models.documento_de_alteracao(ativo_id=ativo_no_banco.id, tipo=tipo, alteracao=alteracao, detalhes_alteracao=detalhes,
                                                     data_alteracao=data_alteracao, foi_autorizado=False, quem_autorizou=quem_autorizou, id_autorizacao=id_autorizacao, foi_verificado=False)
        db.add(db_alteracao)
        db.commit()

    return db_alteracao


def criar_alerta_monitoramento(db: Session, zabbix_id: int, hostname: str, codigo_alerta: str):

    alerta_id = db.query(models.alerta).filter(
        models.alerta.codigo == codigo_alerta).first()
    if (alerta_id):
        #print("alerta existe")
        detalhes = hostname
        verifica_ocorrencia_existe = db.query(models.alerta_monitoramento).filter(models.alerta_monitoramento.alerta_id == alerta_id.id).filter(models.alerta_monitoramento.detalhes == detalhes).first()
        if (verifica_ocorrencia_existe):
            print (verifica_ocorrencia_existe)
            db.delete(verifica_ocorrencia_existe)
            data_acao = date.today()
            db_alerta = models.alerta_monitoramento(zabbix_id=zabbix_id, data_ocorrencia=data_acao, corrigido=False,
                                                    data_correcao=None, quem_corrigiu="", detalhes=detalhes, alerta_id=alerta_id.id)
            db.add(db_alerta)
            db.commit()
        else:
            #print("ocorrencia nao existe")
            data_acao = date.today()
            db_alerta = models.alerta_monitoramento(zabbix_id=zabbix_id, data_ocorrencia=data_acao, corrigido=False,
                                                    data_correcao=None, quem_corrigiu="", detalhes=detalhes, alerta_id=alerta_id.id)
            db.add(db_alerta)
            db.commit()
    else:
        db_alerta = None

    return db_alerta


def criar_informacao_hardware_do_ativo(db: Session, info_hardware: schemas.informacao_hardware_base, ativo: models.ativo_hardware, componentes: List[models.biblioteca_hardware]):
    data_cadastro = date.today()
    db_informacao_hardware = models.informacao_hardware(dados_de_placamae=info_hardware.dados_de_placamae, dados_de_processador=info_hardware.dados_de_processador, dados_de_disco=info_hardware.dados_de_disco, dados_de_gpu=info_hardware.dados_de_gpu, dados_de_memoria=info_hardware.dados_de_memoria,
                                                        dados_de_memoria_total_em_gb=info_hardware.dados_de_memoria_total_em_gb, quantidade_de_discos=info_hardware.quantidade_de_discos, quantidade_de_memorias=info_hardware.quantidade_de_memorias, dados_completos=info_hardware.dados_completos, ativo=ativo)
    # print(len(componentes))
    db.add(db_informacao_hardware)
    db.commit()
    total_componentes = 0
    # db.refresh(db_informacao_hardware)
    for componente in componentes:
        total_componentes = total_componentes + 1
        # print(componente)
        db_informacao_hardware.componentes_hardware.append(componente)
        componente.quantidade = componente.quantidade + 1
        db.commit()
        db.refresh(db_informacao_hardware)

    print("total de componentes de hardware adicionados: " + str(total_componentes))
    return db_informacao_hardware


def criar_fabricante(db: Session, fabricante: schemas.fabricante_base, identificador: str):

    identificador_de_fabricante = db.query(models.identificador_de_fabricante).filter(
        models.identificador_de_fabricante.identificador == identificador).first()
    # print(identificador_de_fabricante)
    if (identificador_de_fabricante):
        fabricantedb = db.query(models.fabricante).with_parent(
            identificador_de_fabricante).first()
        #print ("entrei aqui")
        #print (fabricantedb)
        return identificador_de_fabricante
    else:
        fabricantedb = models.fabricante(
            nome_do_fabricante=fabricante.nome_do_fabricante)
        db.add(fabricantedb)
        db.commit()
        novo_identificador = models.identificador_de_fabricante(
            identificador, fabricantedb)
        db.add(novo_identificador)
        db.commit()
        #print ("entrei acola")
        return novo_identificador


def criar_informacao_sistema_do_ativo(db: Session, info_sistema: schemas.informacao_sistema_base, ativo: models.ativo_hardware):
    data_cadastro = date.today()
    db_informacao_sistema = models.informacao_sistema(sistema_operacional=info_sistema.sistema_operacional, dados_de_administradores=info_sistema.dados_de_administradores,
                                                      dados_de_antivirus=info_sistema.dados_de_antivirus, dados_de_versao=info_sistema.dados_de_versao, dados_de_update=info_sistema.dados_de_update, ativo=ativo)
    # print(len(componentes))
    db.add(db_informacao_sistema)
    db.commit()
    # db.refresh(db_informacao_hardware)

    #print ("hardware cadastrado no banco " + ativo.patrimonio)
    return db_informacao_sistema


def criar_informacao_de_software_do_ativo(db: Session, info_software: schemas.informacao_de_software_base, ativo: models.ativo_hardware, descoberta: bool):
    #print ("criando info de softw")
    data_cadastro = date.today()
    #print (info_software.identificador)
    esquema_de_fabricante = schemas.fabricante_base(
        nome_do_fabricante=info_software.publisher)
    identificador = db.query(models.identificador_de_software).filter(
        models.identificador_de_software.identificador == info_software.identificador).first()
    #print(" passou pela busca do identificador ")
    #print ("verificando id")
    if (identificador):
        #print ("id no banco")
        #print (identificador.identificador)
        # query software do identificador
        db_biblioteca_de_software = db.query(
            models.biblioteca_de_software).with_parent(identificador).first()
        if (db_biblioteca_de_software.monitorado == 1):
            #print("software na biblioteca")
            db_informacao_software = db.query(models.informacao_de_software).with_parent(
                identificador).filter(models.informacao_de_software.ativo_id == ativo.id).all()

            #query2 = db.query.join()
            #identificadores_do_ativo = db.query(models.identificador_de_software).filter(models.identificador_de_software.ativo_hardware.any).all()
            #teste = db.query(models.informacao_de_software).filter(models.informacao_de_software.componentes_software.any())
            # print(len(db_informacao_software))
            #print("informacao de software encontrada?")
            if (len(db_informacao_software) > 1):
                #print("deu xabu")
                return 0
            if (len(db_informacao_software) == 1):

                #print (info_software.nome_software)
                # atualizar info
                if (db_informacao_software[0].versao_instalada != info_software.versao_instalada):
                    db_informacao_software[0].versao_instalada = info_software.versao_instalada
                    db_informacao_software[0].data_instalacao = info_software.data_instalacao
                    db.commit()

            else:

                # criar nova info
                #print ("software novo que ja estava no banco detectado")
                if(descoberta == False):
                 criar_documento_de_alteracao(db, "software", "instalacao", "[SW INSTALADO] -> "+str(
                    info_software.nome_software)+" no computador [" + str(ativo.hostname) + "] [REGISTRO ATUALIZADO]", ativo)
                db_informacao_software = models.informacao_de_software(
                    nome_software=info_software.nome_software, versao_instalada=info_software.versao_instalada, data_instalacao=info_software.data_instalacao, ativo=ativo)
                db_informacao_software.componentes_software.append(
                    identificador)

                db.add(db_informacao_software)
                db.commit()

        else:
            return 0

    else:
        #print ("software novo que nao estava no banco detectado")

        identificador_de_fabricante = criar_fabricante(
            db, esquema_de_fabricante, info_software.publisher)
        #print (fabricante)
        novo_software = models.biblioteca_de_software(nome=info_software.nome_software, desenvolvedor=identificador_de_fabricante.id,
                                                      tipo_de_software="indefinido", proprietario=False, monitorado=True, blacklist=False)
        db.add(novo_software)
        db.commit()
        novo_identificador = models.identificador_de_software(
            info_software.identificador, biblioteca_de_software=novo_software)
        db.add(novo_identificador)
        db.commit()
        db_informacao_software = models.informacao_de_software(
            nome_software=info_software.nome_software, versao_instalada=info_software.versao_instalada, data_instalacao=info_software.data_instalacao, ativo=ativo)
        db_informacao_software.componentes_software.append(novo_identificador)
        db.add(db_informacao_software)
        db.commit()

    # db.refresh(db_informacao_hardware)

    #print ("hardware cadastrado no banco " + ativo.patrimonio)
    return db_informacao_software


def atualizar_softwares_do_ativo(db: Session, lista_do_monitoramento: List, ativo: models.ativo_hardware):
    informacoes_de_software_do_ativo = db.query(
        models.informacao_de_software).with_parent(ativo).all()
    lista_de_identificadores_no_db = []
    lista_de_identificadores_na_busca = []
    lista_desinstalados = []
    for software in lista_do_monitoramento:
        lista_de_identificadores_na_busca.append(software.identificador)
    #print("identificadores na busca")
    #print(lista_de_identificadores_na_busca)    
    if (len(lista_de_identificadores_na_busca) > 3): 
     for infosoft in informacoes_de_software_do_ativo:
        for componente in infosoft.componentes_software:
          identificador_de_software = db.query(models.identificador_de_software).with_parent(infosoft).first()
          software_no_db = db.query(models.biblioteca_de_software).with_parent(identificador_de_software).first()
          if (software_no_db.monitorado == True):
            if (componente.identificador in lista_de_identificadores_na_busca):
                lista_de_identificadores_no_db.append(componente.identificador)
            else:
                lista_de_identificadores_no_db.append(componente.identificador)
                #print("Software Desinstalado")
                #print(componente.identificador)
                criar_documento_de_alteracao(db, "software", "remocao", "[SW REMOVIDO] -> "+str(
                    infosoft.nome_software)+" no computador [" + str(ativo.hostname) + "] [REGISTRO ATUALIZADO]", ativo)
                
                if (software_no_db.proprietario):
                  #print("software é proprietario")
                  db_licenses_do_ativo_de_hw = db.query(models.license_de_software).filter_by(ativos_com_license_aplicada = ativo.id).all()
                  for license in db_licenses_do_ativo_de_hw:
                      db_ativo_de_software = db.query(models.ativo_de_software).with_parent(license).first()   
                      if (db_ativo_de_software.biblioteca_de_software_id == software_no_db.id):
                        print("license encontrada, liberando...")
                        criar_documento_de_alteracao(db, "software", "restauracao", "[LICENÇA DE SOFTWARE RESTAURADA] -> "+str(
                        infosoft.nome_software)+" do computador [" + str(ativo.hostname) + "] [REGISTRO ATUALIZADO]", ativo)
                        license.data_de_aplicacao = None
                        license.aplicado = False
                        license.reservado = False
                        license.disponivel = True
                        license.ativos_com_license_aplicada = None
                        db.commit()  
                db.delete(infosoft)
                db.commit()
                lista_desinstalados.append(componente.identificador)

     
     lista_instalados = set(lista_de_identificadores_na_busca).difference(
        lista_de_identificadores_no_db)
     

     for esquema in lista_do_monitoramento:
        if esquema.identificador in lista_instalados:
         if (len(lista_de_identificadores_no_db) > 3): 
          criar_informacao_de_software_do_ativo(db, esquema, ativo, False)
         else:
          criar_informacao_de_software_do_ativo(db, esquema, ativo, True)  

    # print(lista_desinstalados)
    # print("-----------------")
    # print(lista_instalados)

    return 0


def remover_todos_softwares_nao_monitorados(db: Session):
    #identificador = "7zip"
    softwares_desativados = db.query(models.biblioteca_de_software).filter(
        models.biblioteca_de_software.monitorado == 0).all()
    totaldeletados = 0
    for software_ds in softwares_desativados:
        # print(software_ds.nome)
        identificadores = db.query(
            models.identificador_de_software).with_parent(software_ds).all()
        for ident in identificadores:
            lista_informacao_de_software = db.query(
                models.informacao_de_software).with_parent(ident).all()
            for info in lista_informacao_de_software:
                informacao_de_software_no_db = db.query(models.informacao_de_software).filter(
                    models.informacao_de_software.id == info.id).first()
                # print(informacao_de_software_no_db.versao_instalada)
                db.delete(info)
                totaldeletados = totaldeletados + 1
    #print(totaldeletados)

    db.commit()

    return 0


def aplicar_license_em_ativo(db: Session, id: str, hostname: str):
    #print (id)
    #print (hostname)

    
    agora = datetime.datetime.now()
    data_de_aplicacao = agora.strftime("%d/%m/%Y")
    try:
     db_license = db.query(models.license_de_software).filter(models.license_de_software.id == int(id)).first()
     ativo_de_software = db.query(models.ativo_de_software).with_parent(db_license).first()
     ativo_para_aplicar = db.query(models.ativo_hardware).filter(models.ativo_hardware.hostname == hostname).first()
     #print("hostanme")
     #print(ativo_para_aplicar.hostname)
     #print("id da license")
     #print(db_license.id)
     db_license.aplicado = True
     db_license.disponivel = False
     db_license.ativos_com_license_aplicada = ativo_para_aplicar.id
     db_license.data_de_aplicacao = agora
     ativo_de_software.total_utilizado =  ativo_de_software.total_utilizado + 1
     db.commit()

    except:
     print ("Licença não aplicada - erro")

    return 0

def reservar_license(db: Session, id: str,observacao: str):
    #print (id)
    #print (hostname)
    
    
     agora = datetime.datetime.now()
     data_de_aplicacao = agora.strftime("%d/%m/%Y")
    #try:
     db_license = db.query(models.license_de_software).filter(models.license_de_software.id == int(id)).first()
     ativo_de_software = db.query(models.ativo_de_software).with_parent(db_license).first()
     db_license.reservado = True
     db_license.disponivel = False
     db_license.observacoes = observacao
     db_license.data_de_aplicacao = agora
     ativo_de_software.total_utilizado =  ativo_de_software.total_utilizado + 1
     db.commit()

    #except:
     #print ("erro")

     return 0

def atualize_softwares_descobertos(db: Session, json: str):
    #dicionario = json.loads(json)

    for software in json:
        db_biblioteca_de_software = db.query(models.biblioteca_de_software).filter(
            models.biblioteca_de_software.id == software['id']).first()
        db_biblioteca_de_software.tipo_de_software = software['tipo']
        db_biblioteca_de_software.nome = software['nome']
        db_biblioteca_de_software.monitorado = software['monitorado']
        db_biblioteca_de_software.proprietario = software['proprietario']
        db_biblioteca_de_software.blacklist = software['blacklist']
        db.commit()
    remover_todos_softwares_nao_monitorados(db)
    # print(type(json))
    return 0


def atualize_devs_descobertos(db: Session, jsone: str):
    sucesso = json.dumps(
        {"alerta": "sucesso", "msg": "Desenvolvedores agrupados com sucesso"})
    #lista_de_identificadores = []
    lista_de_desenvolvedores_para_remover = []
    lista_de_identificadores_para_agrupar = []
    desenvolvedor_principal = []
    for fabricante in jsone:

        if (fabricante['principal'] == True):
            desenvolvedor_no_db = db.query(models.fabricante).filter(
                models.fabricante.id == fabricante['id']).first()
            desenvolvedor_principal.append(desenvolvedor_no_db)
            if (fabricante['agrupar'] == True):
                json_def = json.dumps(
                    {"alerta": "ERRO", "msg": "Desenvolvedor principal nao deve ser marcado para agrupar"})
                return json_def
        if (fabricante['agrupar'] == True):
            desenvolvedor_no_db = db.query(models.fabricante).filter(
                models.fabricante.id == fabricante['id']).first()
            lista_de_desenvolvedores_para_remover.append(desenvolvedor_no_db)
            identificadores_no_db = db.query(
                models.identificador_de_fabricante).with_parent(desenvolvedor_no_db).all()
            for identificador in identificadores_no_db:
                lista_de_identificadores_para_agrupar.append(identificador)
            # db.delete(desenvolvedor_no_db)
            # db.commit()

    if (len(desenvolvedor_principal) == 0):
        json_def = json.dumps(
            {"alerta": "ERRO", "msg": "Selecione um desenvolvedor para manter"})
        return json_def

    if (len(desenvolvedor_principal) != 1):
        json_def = json.dumps(
            {"alerta": "ERRO", "msg": "Somente um desenvolvedor para manter deve ser selecionado"})
        return json_def

    fabricante_principal = desenvolvedor_principal[0]
    for fabricante in lista_de_desenvolvedores_para_remover:
        #print("deletando software")
        #print(fabricante.nome_do_fabricante)
        db.delete(fabricante)
        db.commit()

    for identificador in lista_de_identificadores_para_agrupar:
        identificador.fabricante_id = fabricante_principal.id
        db.commit()
    # print(desenvolvedor_no_db.nome_do_fabricante)
    # for devs in json:
        #  desenvolvedor_no_db = db.query(models.fabricante).filter(models.fabricante.id == devs['id'])
        # novo_desenvolvedor = db.query(models.fabricante).with_parent(desenvolvedor_no_db).all()
        #identificadores_no_db = db.query(models.identificador_de_fabricante).with_parent(desenvolvedor_no_db).all()
        #lista_de_softwares = db.query(models.biblioteca_de_software).with_parent(desenvolvedor_no_db).all()

    return sucesso


def agrupar_softwares_descobertos(db: Session, jsone: str):
    sucesso = json.dumps(
        {"alerta": "sucesso", "msg": "Softwares agrupados com sucesso"})
    lista_de_identificadores_de_software_para_agrupar = []
    lista_de_identificadores_de_fabricante = []
    lista_de_softwares_para_remover = []
    software_principal = []
    lista_de_ativos_com_identificador = []
    lista_de_identificadores_de_fabricante_do_software_principal = []
    for software in jsone:

        if (software['principal'] == True):
            if (software['agrupar'] == True):
                json_def = json.dumps(
                    {"alerta": "ERRO", "msg": "Software para manter não deve ser marcado para agrupar"})
                return json_def
            software_no_db = db.query(models.biblioteca_de_software).filter(
                models.biblioteca_de_software.id == software['id']).first()
            software_principal.append(software_no_db)
            identificador_de_fabricante_no_db = db.query(models.identificador_de_fabricante).filter(
                models.identificador_de_fabricante.id == software_no_db.desenvolvedor).first()
            fabricante_no_db = db.query(models.fabricante).with_parent(
                identificador_de_fabricante_no_db).first()
            lista_de_idenficadores_do_fabricante = db.query(
                models.identificador_de_fabricante).with_parent(fabricante_no_db).all()
            for identificador in lista_de_idenficadores_do_fabricante:
                lista_de_identificadores_de_fabricante_do_software_principal.append(
                    identificador)

        if (software['agrupar'] == True):
            #print(software['id'])
            software_no_db = db.query(models.biblioteca_de_software).filter(models.biblioteca_de_software.id == software['id']).first()
            #print(software_no_db.nome)
            lista_de_softwares_para_remover.append(software_no_db)
            identificadores_no_db = db.query(models.identificador_de_software).with_parent(software_no_db).all()
            identificador_de_fabricante_no_db = db.query(models.identificador_de_fabricante).filter(
                models.identificador_de_fabricante.id == software_no_db.desenvolvedor).first()
            lista_de_identificadores_de_fabricante.append(
                identificador_de_fabricante_no_db)
            for identificador in identificadores_no_db:
                lista_de_identificadores_de_software_para_agrupar.append(
                    identificador)

    if (len(software_principal) == 0):
        json_def = json.dumps(
            {"alerta": "ERRO", "msg": "Selecione um software principal"})
        return json_def

    if (len(software_principal) != 1):
        json_def = json.dumps(
            {"alerta": "ERRO", "msg": "Somente um software principal deve ser selecionado"})
        return json_def

    for fabricante in lista_de_identificadores_de_fabricante:
        if (fabricante not in lista_de_identificadores_de_fabricante_do_software_principal):

            json_def = json.dumps(
                {"alerta": "ERRO", "msg": "Softwares com desenvolvedores diferentes nao podem ser agrupados"})
            return json_def

    for software_no_db in lista_de_softwares_para_remover:
        db.delete(software_no_db)
        db.commit()
    software_principal_no_db = software_principal[0]
    #print (software_principal_no_db.id)

    for identificador in lista_de_identificadores_de_software_para_agrupar:
        identificador.biblioteca_de_software_id = software_principal_no_db.id
        db.commit()

    # print(lista_de_ativos_com_identificador)

    return sucesso


def atualize_informacao_hardware(db: Session, hardware_novo: schemas.informacao_hardware_base, ativo: models.ativo_hardware, componentes: List[models.biblioteca_hardware]):
        hardware_banco = get_informacao_de_hardware_do_ativo(db, ativo.patrimonio)
        
        # Verifica se existe realmente um novo dado para ser atualizado
        # Caso não exista, retorna None
        # Caso exista, atualiza o dado no banco de dados
        tipo_de_dados = ["dados_de_processador", "dados_de_disco",
                       "dados_de_placamae", "dados_de_memoria", "dados_de_gpu"]
        for atributo in tipo_de_dados:
            valor_do_atributo = getattr(hardware_novo, atributo)
            if (valor_do_atributo == "nodata"):
                print("Hardware não atualizado - Sem dados para atualizar")
                return False
            else:
              if len(valor_do_atributo) > 0:
                setattr(hardware_banco, atributo, valor_do_atributo)        
        
        if (hardware_novo.quantidade_de_memorias != 0):
            hardware_banco.quantidade_de_memorias = hardware_novo.quantidade_de_memorias
        if (hardware_novo.quantidade_de_discos != 0):
           hardware_banco.quantidade_de_discos = hardware_novo.quantidade_de_discos
        if (hardware_novo.dados_de_memoria_total_em_gb != 0):
           hardware_banco.dados_de_memoria_total_em_gb = hardware_novo.dados_de_memoria_total_em_gb   
            
        # Update the hardware_banco object with the new data
        #if (len(hardware_novo.dados_de_processador) > 0):
         #   hardware_banco.dados_de_processador = hardware_novo.dados_de_processador
        #if (len(hardware_novo.dados_de_disco) > 0):
         #   hardware_banco.dados_de_disco = hardware_novo.dados_de_disco
        #if (len(hardware_novo.dados_de_placamae) > 0):
         #   print(hardware_novo.dados_de_placamae)
          #  hardware_banco.dados_de_placamae = hardware_novo.dados_de_placamae
        #if (len(hardware_novo.dados_de_memoria) > 0):
         #   hardware_banco.dados_de_memoria = hardware_novo.dados_de_memoria
        #if (len(hardware_novo.dados_de_gpu) > 0):
         #   hardware_banco.dados_de_gpu = hardware_novo.dados_de_gpu
        #if (hardware_novo.dados_de_memoria_total_em_gb):
         #   hardware_banco.dados_de_memoria_total_em_gb = hardware_novo.dados_de_memoria_total_em_gb
        #if (hardware_novo.quantidade_de_memorias != 0):
         #   hardware_banco.quantidade_de_memorias = hardware_novo.quantidade_de_memorias
        #if (hardware_novo.quantidade_de_discos != 0):
         #   hardware_banco.quantidade_de_discos = hardware_novo.quantidade_de_discos
        
        # Commit the changes to the database and return the updated object
        db.commit()
        db.refresh(hardware_banco)
        return True




def atualize_informacao_sistema(db: Session, sistema_novo: schemas.informacao_sistema_base, ativo: models.ativo_hardware):
    sistema_banco = get_informacao_de_sistema_do_ativo(db, ativo.patrimonio)
    ativo_no_db = db.query(models.ativo_hardware).filter(
        models.ativo_hardware.patrimonio == ativo.patrimonio).first()
    #print (hardware_banco)
    if (sistema_banco.dados_de_administradores != sistema_novo.dados_de_administradores):
        criar_documento_de_alteracao(db, "seguranca", "alteracao", "[ADMINS] [" + ativo_no_db.hostname + "] " + str(
            sistema_banco.dados_de_administradores) + " ALTERADO PARA -> [" + sistema_novo.dados_de_administradores + "] [REGISTRO ATUALIZADO]", ativo_no_db)
    sistema_banco.sistema_operacional = sistema_novo.sistema_operacional
    sistema_banco.dados_de_antivirus = sistema_novo.dados_de_antivirus
    sistema_banco.dados_de_versao = sistema_novo.dados_de_versao
    sistema_banco.dados_de_update = sistema_novo.dados_de_update
    sistema_banco.dados_de_administradores = sistema_novo.dados_de_administradores

    db.commit()
    db.refresh(sistema_banco)
    return sistema_banco


def atualize_ativo(db: Session, ativo_atualizado: models.ativo_hardware):
    #ativo_no_banco = get_informacao_de_hardware_do_ativo(db,ativo_atualizado.patrimonio)
    #print (hardware_banco)

    db.commit()
    db.refresh(ativo_atualizado)
    return ativo_atualizado


def atualize_ativo_total(db: Session, ativo_no_banco: models.ativo_hardware, ativo_atualizado: schemas.ativo_hardware_base):
    #ativo_no_banco = get_informacao_de_hardware_do_ativo(db,ativo_no_banco.patrimonio)
    #print (hardware_banco)
    ativo_no_banco.zabbix_id = ativo_atualizado.zabbix_id
    ativo_no_banco.endereco_ip = ativo_atualizado.endereco_ip
    ativo_no_banco.cmdb_id = ativo_atualizado.cmdb_id
    ativo_no_banco.endereco_mac = ativo_atualizado.endereco_mac
    ativo_no_banco.equipe = ativo_atualizado.equipe
    ativo_no_banco.hostname = ativo_atualizado.hostname
    ativo_no_banco.local = ativo_atualizado.local
    ativo_no_banco.status = ativo_atualizado.status

    db.commit()
    db.refresh(ativo_no_banco)
    return ativo_no_banco


def crie_componente_biblioteca_hardware(db: Session, componente: schemas.criar_biblioteca_hardware):

    db_biblioteca_hardware = models.biblioteca_hardware(cmdb_id=componente.cmdb_id, cmdb_typeid=componente.cmdb_typeid,
                                                        tipo=componente.tipo, nomeMonitoramento=componente.nome_monitoramento, detalhes=componente.detalhes.strip(), quantidade=0)
    db.add(db_biblioteca_hardware)
    db.commit()
    db.refresh(db_biblioteca_hardware)
    #print ("hardware cadastrado no banco " + ativo.patrimonio)
    return db_biblioteca_hardware


def adicione_unidade_de_componente_biblioteca_hardware(db: Session, componente: models.biblioteca_hardware):
    #print("adicionando unidade no componente abaixo")
    #print(componente.detalhes)
    componente.quantidade = componente.quantidade + 1
    db.commit()
    return componente.quantidade


def adicione_componente_nos_dados_de_hardware(db: Session, componente: schemas.criar_biblioteca_hardware, hardware_banco: models.informacao_hardware):
    #hardware_banco = get_informacao_de_hardware_do_ativo(db,ativo.patrimonio)
    componente_no_banco = busque_componente_biblioteca_detalhes(
        db, componente.detalhes)

    if componente_no_banco:
        #print("componente existe")
        hardware_banco.componentes_hardware.append(componente_no_banco)
        componente_no_banco.quantidade = componente_no_banco.quantidade + 1
        #print(componente_no_banco.quantidade)
        db.commit()
        db.refresh(componente_no_banco)
        db.refresh(hardware_banco)
    else:
        #print("eh um novo componente")
        novo_componente = crie_componente_biblioteca_hardware(db, componente)
        hardware_banco.componentes_hardware.append(novo_componente)
        novo_componente.quantidade = novo_componente.quantidade + 1
        #print(novo_componente.quantidade)
        db.commit()
    return 0 


def adicione_ativo_de_software(db: Session, componente: json):

    # try:
    data_de_exp = componente['data_expiracao']
    retorno = "sucesso"
    formato = '%Y-%m-%d'
    data_de_aqui = datetime.datetime.strptime(
        componente['data_aquisicao'], formato)
    try:
        data_de_exp = datetime.datetime.strptime(data_de_exp, formato)
    except:
        data_de_exp = None
    software_no_db = db.query(models.biblioteca_de_software).filter(
        models.biblioteca_de_software.id == componente['id_do_software']).first()

    if (componente['tipo_de_software'] == "volume"):
        novo_ativo_de_software = models.ativo_de_software(nome=componente['nome_do_software'], versao_adquirida=componente['versao'], total_adquirido=componente['total_de_licenses'], total_utilizado=0,
                                                          tipo_de_license=componente['tipo_de_software'], tipo_de_contrato=componente['modalidade'], valida=True, data_de_expiracao=data_de_exp,
                                                          data_de_aquisicao=data_de_aqui, responsavel="indefinido", informacoes=componente['informacoes'], biblioteca_de_software_id=software_no_db.id)
        db.add(novo_ativo_de_software)
        db.commit()
        #print("add lic2")
        #print(novo_ativo_de_software.total_adquirido)
        for i in range(int(novo_ativo_de_software.total_adquirido)):
            #print("add lic")
            nova_license = models.license_de_software(tipo=novo_ativo_de_software.tipo_de_license, usuario=None, chave=componente['informacoes'],
                                                      observacoes=componente['informacoes'], data_de_aplicacao=None, aplicado=False, disponivel=True, reservado=False, ativo_de_software_id=novo_ativo_de_software.id)
            db.add(nova_license)
            db.commit()
    else:
        novo_ativo_de_software = models.ativo_de_software(nome=componente['nome_do_software'], versao_adquirida=componente['versao'], total_adquirido=componente['total_de_licenses'], total_utilizado=0,
                                                          tipo_de_license=componente['tipo_de_software'], tipo_de_contrato=componente['modalidade'], valida=True, data_de_expiracao=data_de_exp,
                                                          data_de_aquisicao=data_de_aqui, responsavel="indefinido", informacoes=componente['informacoes'], biblioteca_de_software_id=software_no_db.id)
        db.add(novo_ativo_de_software)
        db.commit()

    # except:

    #retorno = "erro"

    print(retorno)

    return retorno


def adicione_licenca_em_ativo_de_software(db: Session, dados_de_license: json):

    try:
        id_do_ativo_software = dados_de_license['id']
        tipo_do_software = dados_de_license['tipo']
        usuarios_de_software = []
        chaves_do_software = dados_de_license['chaves']
        lista_de_chaves = []
    except:
        return "erro"
    #print("passou um try")
    try:
        ativo_de_software = db.query(models.ativo_de_software).filter(
            models.ativo_de_software.id == id_do_ativo_software).first()
        software = db.query(models.biblioteca_de_software).filter(
            models.biblioteca_de_software.id == ativo_de_software.biblioteca_de_software_id).first()
        licensas_cadastradas = db.query(
            models.license_de_software.chave).with_parent(ativo_de_software).all()
        for license in licensas_cadastradas:
            lista_de_chaves.append(license.chave)

        total_para_cadastrar = ativo_de_software.total_adquirido - \
            len(licensas_cadastradas)
        #print(type(licensas_cadastradas))
    except:
        return "erro"
    #print("passou dois try")

    if (software.proprietario == True and len(chaves_do_software) <= total_para_cadastrar):
        #print(tipo_do_software)
        if (tipo_do_software == "dispositivo"):

            for chave in chaves_do_software:
                #print(chave)
                if (chave not in lista_de_chaves):
                    nova_license = models.license_de_software(tipo=ativo_de_software.tipo_de_license, usuario="", chave=chave, observacoes="",
                                                              data_de_aplicacao=None, aplicado=False, disponivel=True, reservado=False, ativo_de_software_id=ativo_de_software.id)
                    db.add(nova_license)
                    db.commit()
                else:
                    print("Software já cadastrado")
        if (tipo_do_software == "usuario"):
            usuarios_de_software = dados_de_license['user']
            quantidade_de_chaves = len(chaves_do_software)
            quantidade_de_usuarios = len(usuarios_de_software)
            if (quantidade_de_chaves == quantidade_de_usuarios):
                for i in range(quantidade_de_usuarios):
                    chavei = chaves_do_software[i]
                    useri = usuarios_de_software[i]
                    nova_license = models.license_de_software(tipo=ativo_de_software.tipo_de_license, usuario=useri, chave=chavei,
                                                              observacoes="", data_de_aplicacao=None, aplicado=False, disponivel=True, reservado=False, ativo_de_software_id=ativo_de_software.id)
                    db.add(nova_license)
                    db.commit()
            else:
                print("Quantidade incompativel")
                #print(quantidade_de_chaves)
                #print(quantidade_de_usuarios)

    else:
        return "erro de tamanho"

    return "sucesso"


                                                

def remove_componente_nos_dados_de_hardware(db: Session, componente: schemas.criar_biblioteca_hardware, hardware_banco: models.informacao_hardware):
    #hardware_banco = get_informacao_de_hardware_do_ativo(db,ativo.patrimonio)
    
    componente_no_banco = busque_componente_biblioteca_detalhes(
        db, componente.detalhes)

    if componente_no_banco:
        #print("Componente encontrado no banco")
        try:
            if componente_no_banco.quantidade > 0:
                hardware_banco.componentes_hardware.remove(componente_no_banco)
                componente_no_banco.quantidade = componente_no_banco.quantidade - 1
                #print(componente_no_banco.quantidade)
            else:
                print("Erro ao remover componente: quantidade menor ou igual a 0")
        except:
            print("Erro ao remover componente")
            componente_no_banco.quantidade = componente_no_banco.quantidade - 1
            #print(componente_no_banco.quantidade)
        db.commit()
        db.refresh(componente_no_banco)
        db.refresh(hardware_banco)
        print("atualizou no banco")
    else:
        print("erro, componente nao encontrado")
    return 0




def get_softwares_no_banco(db: Session):

    softwares = db.query(models.biblioteca_de_software).filter_by(
        monitorado=1).order_by(models.biblioteca_de_software.nome).all()
    dicionario_de_softwares = []
    for software in softwares:
        identificador = db.query(models.identificador_de_fabricante).filter(
            models.identificador_de_fabricante.id == software.desenvolvedor).first()
        desenvolvedor = db.query(models.fabricante).with_parent(
            identificador).first()
        dici = {
            'id': software.id,
            'nome': software.nome,
            'monitorado': software.monitorado,
            'blacklist': software.blacklist,
            'proprietario': software.proprietario,
            'tipo_de_software': software.tipo_de_software,
            'detalhes': software.detalhes,
            'desenvolvedor': desenvolvedor.nome_do_fabricante
        }
        dicionario_de_softwares.append(dici)
    print(dicionario_de_softwares)
    json_string = json.dumps(dicionario_de_softwares,
                             indent=4, sort_keys=True, default=str)

    return json_string


def get_fabricantes_no_banco(db: Session):

    softwares = db.query(models.fabricante).order_by(
        models.fabricante.nome_do_fabricante.asc()).all()
    #print(softwares[0].id)
    return softwares


def busque_componente_biblioteca_detalhes(db: Session, detalhes: str):

    db_componente = db.query(models.biblioteca_hardware).filter(
        models.biblioteca_hardware.detalhes == detalhes).first()
    #print ("hardware cadastrado no banco " + ativo.patrimonio)
    return db_componente


def busque_componente_biblioteca_nomemonitoramento(db: Session, nome_monitoramento: str):

    db_componente = db.query(models.biblioteca_hardware).filter(
        models.biblioteca_hardware.nomeMonitoramento == nome_monitoramento).first()
    #print ("hardware cadastrado no banco " + ativo.patrimonio)
    return db_componente


def get_softwares_no_banco_com_total_de_instalacoes(db: Session):

    softwares = db.query(models.biblioteca_de_software).filter(
        models.biblioteca_de_software.monitorado == True).order_by(models.biblioteca_de_software.nome).all()
    dicionario_de_softwares = []

    for software in softwares:
        contador_de_instalacoes = 0
        contador_de_licenses_aplicadas = 0
        lista_de_ativos_com_software = []
        identificadores_de_software = db.query(models.identificador_de_software).filter(
            models.identificador_de_software.biblioteca_de_software_id == software.id).all()
        identificador_de_fabricante = db.query(models.identificador_de_fabricante).filter(
            models.identificador_de_fabricante.id == software.desenvolvedor).first()
        desenvolvedor = db.query(models.fabricante).with_parent(
            identificador_de_fabricante).first()
        if (software.proprietario):
         ativos_de_software = db.query(models.ativo_de_software).filter_by(biblioteca_de_software_id = software.id).all()
         for ativo in ativos_de_software:
             licenses = db.query(models.license_de_software).filter_by(ativo_de_software_id = ativo.id).all()
             for license in licenses:
                if (license.aplicado):
                 contador_de_licenses_aplicadas = contador_de_licenses_aplicadas + 1

        for identificador in identificadores_de_software:
            info_no_db = db.query(models.informacao_de_software).with_parent(
                identificador).all()
            # for info in info_no_db:
            #   ativos_com_software = db.query(models.ativo_hardware).with_parent(info).all()
            #  for ativo in ativos_com_software:
            #     lista_de_ativos_com_software.append(ativo.hostname)

            contador_de_instalacoes = contador_de_instalacoes + len(info_no_db)

        software_dicionario = {
        'id': software.id,
        'nome': software.nome,
        'monitorado': software.monitorado,
        'blacklist': software.blacklist,
        'proprietario': software.proprietario,
        'tipo_de_software': software.tipo_de_software,
        'detalhes': software.detalhes,
        'desenvolvedor': desenvolvedor.nome_do_fabricante,
        'instalacoes': contador_de_instalacoes,
        'instalacoes_nao_licenciadas': contador_de_instalacoes - contador_de_licenses_aplicadas,
        'ativos_instalados': lista_de_ativos_com_software
        }
        dicionario_de_softwares.append(software_dicionario)
    print(dicionario_de_softwares)

    return dicionario_de_softwares


def get_licencas_adquiridasgpt(db: Session, softwareid: int):
    ativos_de_software = db.query(models.ativo_de_software).filter(
        models.ativo_de_software.biblioteca_de_software_id == softwareid).all()
    dicionario_de_aplicacoes = {}
    lista_de_licenses_disponiveis = []
    lista_de_licenses_aplicadas = []

    for ativo in ativos_de_software:
        licenses = db.query(
            models.license_de_software).with_parent(ativo).all()

        dicionario_de_licenses = {}
        dicionario_de_licenses['id'] = ativo.id
        dicionario_de_licenses['versao'] = ativo.versao_adquirida
        dicionario_de_licenses['data_de_aquisicao'] = ativo.data_de_aquisicao.strftime(
            "%d/%m/%Y")
        dicionario_de_licenses['adquiridos'] = ativo.total_adquirido
        dicionario_de_licenses['tipo'] = ativo.tipo_de_license

        total_disponivel = 0

        for license in licenses:
            data_de_expiracao = "Licenca perpetua" if not ativo.data_de_expiracao else ativo.data_de_expiracao.strftime(
                "%d/%m/%Y")
            license_como_dict = license.as_dict()
            license_como_dict['modalidade'] = ativo.tipo_de_contrato
            license_como_dict['data_de_expiracao'] = data_de_expiracao

            if license.disponivel:
                lista_de_licenses_disponiveis.append(license_como_dict)
                total_disponivel += 1
            else:
                ativo_com_license_aplicada = db.query(models.ativo_hardware).filter(
                    models.ativo_hardware.id == license.ativo_de_software_id).first()
                license_como_dict['hostname_aplicado'] = ativo_com_license_aplicada.hostname
                lista_de_licenses_aplicadas.append(license_como_dict)

        dicionario_de_licenses['disponiveis'] = total_disponivel
        lista_de_licenses = []
        lista_de_licenses.append(lista_de_licenses_disponiveis)
        lista_de_licenses.append(lista_de_licenses_aplicadas)
        dicionario_de_licenses['lista_de_licenses'] = lista_de_licenses
        dicionario_de_licenses['cadastrados'] = len(licenses)
    dicionario_de_aplicacoes['lista_disponiveis'] = lista_de_licenses_disponiveis
    dicionario_de_aplicacoes['lista_aplicadas'] = lista_de_licenses_aplicadas
    dicionario_de_aplicacoes['ativos_de_software'] = dicionario_de_licenses
    return dicionario_de_aplicacoes


def get_licencas_adquiridas(db: Session, softwareid: int):
    lista_de_todas_as_licenses = []
    dicionario_de_aplicacoes = {}
    lista_de_licenses_disponiveis = []
    lista_de_licenses_aplicadas = []
    lista_de_licenses_reservadas = []
    ativos_com_license_aplicada = []
    ativos_sem_license_aplicada = []
    ativos_de_software = db.query(models.ativo_de_software).filter(
        models.ativo_de_software.biblioteca_de_software_id == softwareid).all()
    for software in ativos_de_software:
        licenses = db.query(
            models.license_de_software).with_parent(software).all()
        dicionario_dados_de_license = {}
        dicionario_dados_de_license['id'] = software.id
        dicionario_dados_de_license['versao'] = software.versao_adquirida
        data_de_aquisicao = software.data_de_aquisicao.strftime(
            "%d/%m/%Y")
        try:
            data_de_expiracao = software.data_de_expiracao.strftime(
                "%d/%m/%Y")
        except:
            data_de_expiracao = "Licenca perpetua"
        dicionario_dados_de_license['data_de_aquisicao'] = data_de_aquisicao
        dicionario_dados_de_license['adquiridos'] = software.total_adquirido
        dicionario_dados_de_license['tipo'] = software.tipo_de_license
        dicionario_dados_de_license['cadastrados'] = len(licenses)
        total_disponivel = 0
        for license in licenses:
            license_como_dict = license.as_dict()
            license_como_dict['modalidade'] = software.tipo_de_contrato
            license_como_dict['data_de_expiracao'] = data_de_expiracao

            if license.disponivel:
                lista_de_licenses_disponiveis.append(license_como_dict)
                total_disponivel = total_disponivel + 1
            else:
                if(license.aplicado):
                 ativo_com_license_aplicada = db.query(models.ativo_hardware).filter(
                    models.ativo_hardware.id == license.ativos_com_license_aplicada).first()
                 license_como_dict['hostname_aplicado'] = ativo_com_license_aplicada.hostname
                 license_como_dict['ip_hostname_aplicado'] = ativo_com_license_aplicada.endereco_ip
                 lista_de_licenses_aplicadas.append(license_como_dict)
                 ativos_com_license_aplicada.append(ativo_com_license_aplicada.hostname) 
                else:
                 lista_de_licenses_reservadas.append(license_como_dict)
        dicionario_dados_de_license['disponiveis'] = total_disponivel
        lista_de_todas_as_licenses.append(dicionario_dados_de_license)
    
    instalacoes_de_software = get_instalacoes_do_software(db,softwareid) 
    for instalacao in instalacoes_de_software:
        if instalacao['hostname'] not in ativos_com_license_aplicada:
         ativo_sem_license_aplicada = db.query(models.ativo_hardware).filter(
                    models.ativo_hardware.hostname == instalacao['hostname']).first()
         dict_ativo_sem_license = {}
         dict_ativo_sem_license['hostname'] = ativo_sem_license_aplicada.hostname
         dict_ativo_sem_license['endereco_ip'] = ativo_sem_license_aplicada.endereco_ip
         ativos_sem_license_aplicada.append(dict_ativo_sem_license)
    dicionario_de_aplicacoes['lista_disponiveis'] = lista_de_licenses_disponiveis
    dicionario_de_aplicacoes['lista_aplicadas'] = lista_de_licenses_aplicadas
    dicionario_de_aplicacoes['lista_reservadas'] = lista_de_licenses_reservadas
    dicionario_de_aplicacoes['ativos_de_software'] = lista_de_todas_as_licenses
    dicionario_de_aplicacoes['ativos_nao_licenciados'] = ativos_sem_license_aplicada

    return dicionario_de_aplicacoes


def get_instalacoes_do_software(db: Session, softwareid: int):
    dicionario_de_dados = {}
    lista_de_ativos_com_software = []
    software = db.query(models.biblioteca_de_software).filter(
        models.biblioteca_de_software.id == softwareid).first()
    identificadores_de_software = db.query(models.identificador_de_software).filter(
        models.identificador_de_software.biblioteca_de_software_id == software.id).all()

    for identificador in identificadores_de_software:
        #print(lista_de_ativos_com_software)

        info_no_db = db.query(models.informacao_de_software).with_parent(
            identificador).all()
        #print(len(info_no_db))
        for info in info_no_db:
            dicionario_de_dados = {}
            ativo = db.query(models.ativo_hardware).with_parent(info).first()
            dicionario_de_dados['hostname'] = ativo.hostname
            #print(ativo.hostname)
            dicionario_de_dados['endereco_ip'] = ativo.endereco_ip
            dicionario_de_dados['versao_instalada'] = info.versao_instalada
            try:
                if (len(info.data_instalacao) == 8):
                    data = info.data_instalacao
                    newdate = "{}-{}-{}".format(data[6:], data[4:6], data[:4])
                    dicionario_de_dados['data_de_instalacao'] = newdate
                else:
                    dicionario_de_dados['data_de_instalacao'] = info.data_instalacao
            except:
                dicionario_de_dados['data_de_instalacao'] = info.data_instalacao
            lista_de_ativos_com_software.append(dicionario_de_dados)

    print(lista_de_ativos_com_software)

    return lista_de_ativos_com_software

def aplicar_license_de_volume_em_lista_de_ativos(db: Session, json_de_aplicacao: str):
    retorno = "sucesso"
    db_biblioteca_de_software = db.query(models.biblioteca_de_software).filter(
            models.biblioteca_de_software.id == json_de_aplicacao[0]['softwareid']).first()
    db_ativo_de_software = db.query(models.ativo_de_software).filter_by(biblioteca_de_software_id = db_biblioteca_de_software.id,tipo_de_license = "volume").all()
    total_de_licenses = []
    for ativo in db_ativo_de_software:
       db_license_de_software = db.query(models.license_de_software).filter_by(ativo_de_software_id = ativo.id,aplicado=False).all()
       for license in db_license_de_software:
           total_de_licenses.append(license)

    if (len(json_de_aplicacao) < len(total_de_licenses)):
      for dados_de_aplicacao in json_de_aplicacao:
        license_para_aplicar = total_de_licenses[0]
        #print("cadastrandando")
        #print(dados_de_aplicacao['hostname'])
        retorno = aplicar_license_em_ativo(db,license_para_aplicar.id,dados_de_aplicacao['hostname'])
        #print (retorno)
        total_de_licenses.pop(0)
    else: 
      return "erro de tamanho"      
        
    
    # print(type(json))
    return retorno
