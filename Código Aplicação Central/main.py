import datetime
from typing import List
from typing_extensions import Annotated
from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks, Request, Body, Form
from pydantic import Json
from sqlalchemy.orm import Session
from enum import Enum
import zabbix_api
import redmine_api
import sistema
import json
import crud
import models
import schemas
from database import SessionLocal, engine
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=engine)


def sensor():
    sistema.executar_analise(SessionLocal())
    print("Executando verificacao")

tempo_de_execucao_em_segundos = 18000 
#define o tempo de execucao em segundos do sistema em background
sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor, 'interval', seconds=tempo_de_execucao_em_segundos)
sched.start()

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/ativos/", response_model=schemas.ativo_hardware)
def create_ativo(ativo: schemas.ativo_hardware_base, db: Session = Depends(get_db)):
    db_user = crud.get_ativo_por_patrimonio(db, patrimonio=ativo.patrimonio)
    if db_user:
        raise HTTPException(status_code=400, detail="Patrimonio nao existe")
    return crud.criar_ativo(db=db, ativo=ativo)


@app.get("/api/ativos/", response_model=List[schemas.ativo_hardware])
def ler_ativos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ativos = crud.get_ativos(db, skip=skip, limit=limit)
    return ativos


@app.get("/api/ativos2/", response_model=Json)
def ler_ativos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ativos = crud.get_ativos2(db, skip=skip, limit=limit)
    json_string = json.dumps(ativos, indent=4, sort_keys=True, default=str)
    json_object = json.loads(json_string)
    dic = {"data": json_object}
    json_def = json.dumps(dic)
    return json_def


@app.get("/api/alteracoes/{tipo}", response_model=Json)
def ler_ativos(tipo: str, db: Session = Depends(get_db)):
    ativos = crud.get_alteracoes_por_tipo(
        db, tipo)
    json_string = json.dumps(ativos, indent=4, sort_keys=True, default=str)
    json_object = json.loads(json_string)
    dic = {"data": json_object}
    json_def = json.dumps(dic)
    return json_def

@app.get("/api/alteracoes_de_configuracao/", response_model=Json)
def ler_ativos(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    ativos = crud.get_alteracoes_por_tipo(
        db, "configuracao", skip=skip, limit=limit)
    json_string = json.dumps(ativos, indent=4, sort_keys=True, default=str)
    json_object = json.loads(json_string)
    dic = {"data": json_object}
    json_def = json.dumps(dic)
    return json_def


@app.get("/api/alteracoes_de_hardware/", response_model=Json)
def ler_ativos(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    ativos = crud.get_alteracoes_por_tipo(
        db, "hardware", skip=skip, limit=limit)
    json_string = json.dumps(ativos, indent=4, sort_keys=True, default=str)
    json_object = json.loads(json_string)
    dic = {"data": json_object}
    json_def = json.dumps(dic)
    return json_def


@app.get("/api/alteracoes_de_seguranca/", response_model=Json)
def ler_ativos(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    ativos = crud.get_alteracoes_por_tipo(db, "s", skip=skip, limit=limit)
    json_string = json.dumps(ativos, indent=4, sort_keys=True, default=str)
    json_object = json.loads(json_string)
    dic = {"data": json_object}
    json_def = json.dumps(dic)
    return json_def


@app.get("/api/alertas_de_padrao/", response_model=Json)
def ler_ativos(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    ativos = crud.get_alertas_por_tipo(db, "HFP", skip=skip, limit=limit)
    json_string = json.dumps(ativos, indent=4, sort_keys=True, default=str)
    json_object = json.loads(json_string)
    dic = {"data": json_object}
    json_def = json.dumps(dic)
    return json_def


@app.get("/api/alertas_de_hin/", response_model=Json)
def ler_ativos(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    ativos = crud.get_alertas_por_tipo(db, "HIN", skip=skip, limit=limit)
    json_string = json.dumps(ativos, indent=4, sort_keys=True, default=str)
    json_object = json.loads(json_string)
    dic = {"data": json_object}
    json_def = json.dumps(dic)
    print(type(json_def))
    return json_def


@app.get("/api/estatisticas/", response_model=Json)
def ler_estatisticas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ativos = crud.get_estatisticas(db)
    return ativos


@app.get("/api/total_de_alertas_7_dias/", response_model=Json)
def ler_estatisticas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ativos = crud.get_total_alertas_7_dias(db)
    return ativos


@app.get("/api/seguranca/", response_model=Json)
def ler_seg(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ativos = sistema.verificar_seguranca(db)
    return ativos


@app.get("/api/donut_ativos_local/", response_model=Json)
def ler_get_donut_ativos_local(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    ativos = crud.get_donut_ativos_local(db)
    return ativos


@app.get("/api/donut_ativos_equipe/", response_model=Json)
def ler_get_donut_ativos_equipe(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    ativos = crud.get_donut_ativos_equipe(db)
    return ativos


@app.get("/api/get_donut_versoes_windows/", response_model=Json)
def fget_donut_versoes_windows(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    ativos = crud.get_donut_versoes_windows(db)
    return ativos


@app.get("/api/donut_ativos_tipo/", response_model=Json)
def ler_get_donut_ativos_tipo(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    ativos = crud.get_donut_ativos_tipo(db)
    return ativos


@app.get("/api/testebar/", response_model=Json)
def ler_get_donut_ativos_tipo(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    ativos = crud.teste_bar(db)
    return ativos


@app.get("/api/donut_ativos_processador/", response_model=Json)
def ler_get_donut_processadores(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    ativos = crud.get_donut_biblioteca_hardware(db, "processador")
    return ativos


@app.get("/api/donut_ativos_memoria/", response_model=Json)
def ler_get_donut_processadores(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    ativos = crud.get_donut_biblioteca_hardware(db, "memoria")
    return ativos


@app.get("/api/donut_ativos_gpu/", response_model=Json)
def ler_get_donut_processadores(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    ativos = crud.get_donut_biblioteca_hardware(db, "gpu")
    return ativos


@app.get("/api/get_donut_memoria_filtrada/", response_model=Json)
def ler_get_donut_processadores(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    ativos = crud.get_donut_memoria_filtrada(db)
    return ativos


@app.get("/api/donut_ativos_gpu_offboard/", response_model=Json)
def ler_get_donut_processadores(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    ativos = crud.get_donut_biblioteca_hardware_sem_elemento(
        db, "gpu", "intel")
    return ativos


@app.get("/api/donut_ativos_mobo_gigabyte/", response_model=Json)
def ler_get_donut_processadores(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    ativos = crud.get_donut_biblioteca_hardware_com_elemento(
        db, "placamae", "dell")
    return ativos


@app.get("/api/donut_ativos_discos/", response_model=Json)
def ler_get_donut_processadores(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    ativos = crud.get_donut_biblioteca_hardware(db, "disco")
    return ativos


@app.get("/api/donut_ativos_mobo/", response_model=Json)
def ler_get_donut_processadores(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    ativos = crud.get_donut_biblioteca_hardware(db, "placamae")
    return ativos


@app.get("/api/donut_monitores/", response_model=Json)
def ler_get_donut_monitores(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    ativos = crud.get_donut_monitores_filtrados(db, "monitor")
    return ativos


@app.get("/api/ativo/{patrimonio}", response_model=schemas.ativo_hardware)
def read_user(patrimonio: str, db: Session = Depends(get_db)):
    db_user = crud.get_ativo_por_patrimonio(db, patrimonio)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Inexistente")
    return db_user


@app.get("/api/estatisticas_de_uso2/", response_model=Json)
def read_user(db: Session = Depends(get_db)):
    db_user = crud.get_estatisticas_de_uso(db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Inexistente")
    return db_user

@app.get("/api/swinfo/{patrimonio}", response_model=Json)
def read_user(patrimonio: str, db: Session = Depends(get_db)):
    db_software_do_ativo = crud.get_informacao_de_software_do_ativo(
        db, patrimonio)

    if db_software_do_ativo is None:
        raise HTTPException(status_code=404, detail="Inexistente")
    print(db_software_do_ativo)
    jsoni = json.dumps(db_software_do_ativo)
    return jsoni



@app.get("/api/hwinfo/{patrimonio}", response_model=Json)
def read_user(patrimonio: str, db: Session = Depends(get_db)):
    db_hardware_do_ativo = crud.get_informacao_de_hardware_do_ativo(
        db, patrimonio)

    if db_hardware_do_ativo is None:
        raise HTTPException(status_code=404, detail="Inexistente")
    json_hw_ativo = sistema.get_json_dados_hardware_ativo(db_hardware_do_ativo)
    return json_hw_ativo


@app.get("/api/usohw/{patrimonio}", response_model=Json)
def read_user(patrimonio: str, db: Session = Depends(get_db)):
    ativo_no_banco = crud.get_ativo_por_patrimonio(db, patrimonio)
    dados_de_hardware = crud.get_informacao_de_hardware_do_ativo(db,patrimonio)
    if ativo_no_banco is None:
        raise HTTPException(status_code=404, detail="Inexistente")
    json_hw_ativo = zabbix_api.busque_estatisticas_de_uso_de_ativo_trinta_dias(ativo_no_banco,dados_de_hardware)
    return json_hw_ativo

@app.get("/api/usohw3/", response_model=Json)
def read_user(db: Session = Depends(get_db)):
    lista_de_ativos_no_db = crud.get_ativos(db)
    json_hw_ativo = zabbix_api.busque_estatisticas_de_uso_de_ativo_trinta_dias2(lista_de_ativos_no_db,db)
    return json_hw_ativo



@app.get("/api/usohw2/{patrimonio}", response_model=Json)
def read_user(patrimonio: str, db: Session = Depends(get_db)):
    db_user = crud.get_ativo_por_patrimonio(db, patrimonio)
    dados_de_hardware = crud.get_informacao_de_hardware_do_ativo(db,patrimonio)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Inexistente")
    json_hw_ativo = zabbix_api.busque_usuarios_logados_trinta_dias(db_user.patrimonio,dados_de_hardware)
    jsond = json.dumps(json_hw_ativo[0])
    return jsond


@app.get("/api/switch/{mac}/{porta}", response_model=Json)
def read_user(mac: str, porta: str, db: Session = Depends(get_db)):
    db_switch = crud.get_dados_porta_no_db(db, mac, porta)
    if db_switch is None:
        json_def = json.dumps(
            {"patrimonio": "none", "data": str(datetime.datetime.now())})
        return json_def
    json_def = json.dumps(db_switch)
    return json_def


@app.get("/api/get_ativos_no_switch/{mac}", response_model=Json)
def read_user(mac: str, db: Session = Depends(get_db)):
    db_switch = crud.get_lista_de_portas_no_db(db, mac)
    if db_switch is None:
        json_def = json.dumps(
            {"patrimonio": "none", "data": str(datetime.datetime.now())})
        return json_def
    json_def = json.dumps(db_switch)
    return json_def


@app.get("/api/statusinfo/{patrimonio}", response_model=Json)
def read_user(patrimonio: str, db: Session = Depends(get_db)):
    #db_user = crud.get_informacao_de_hardware_do_ativo(db, patrimonio)
    db_ativo = crud.get_ativo_por_patrimonio(db, patrimonio)
    # print(db_ativo.patrimonio)
    if db_ativo is None:
        raise HTTPException(status_code=404, detail="Inexistente")
    json_hw_ativo = sistema.get_json_status_ativo(db, db_ativo)
    return json_hw_ativo


@app.get("/api/icmpgeral/", response_model=Json)
def ler_icmp_geral(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    json_icmp = sistema.get_json_status_icmp_todos_ativos(db)

    return json_icmp


@app.get("/api/switch/", response_model=Json)
def ler_icmp_geral(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    json_icmp = sistema.teste_json_switch()

    return json_icmp


@app.get("/api/errados/", response_model=Json)
def ler_icmp_geral(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    json_icmp = crud.get_lista_localizacao_errada(db)

    return json_icmp


@app.get("/api/errados_em_alerta/", response_model=Json)
def ler_icmp_geral(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)):
    json_icmp = crud.get_nomes_errados_em_alerta(db)

    return json_icmp


# posts

@app.get("/api/softwares_descobertos/", response_model=Json)
def ler_ativos(db: Session = Depends(get_db)):
    softwares = crud.get_softwares_no_banco(db)

    return softwares

@app.get("/api/softwares_descobertos2/", response_model=Json)
def ler_ativos(db: Session = Depends(get_db)):
    softwares = crud.get_softwares_no_banco_com_total_de_instalacoes(db)
    json_string = json.dumps(softwares, indent=4, sort_keys=True, default=str)
    json_object = json.loads(json_string)
    dic = {"data": json_object}
    json_def = json.dumps(dic)
    return json_def


@app.get("/api/desenvolvedores_descobertos/", response_model=List[schemas.fabricante])
def ler_ativos(db: Session = Depends(get_db)):
    softwares = crud.get_fabricantes_no_banco(db)

    return softwares


@app.post("/api/atualize_softwares/")
async def read_user(mac: Request, db: Session = Depends(get_db)):
    req_info = await mac.json()
    print(req_info)
    crud.atualize_softwares_descobertos(db, req_info)
    # print(req_info)
    return 0


@app.post("/api/agrupar_softwares")
async def read_user(mac: Request, db: Session = Depends(get_db)):
    req_info = await mac.json()
    print (req_info)
    retorno = crud.agrupar_softwares_descobertos(db, req_info)
    print(retorno)
    return retorno


@app.post("/api/agrupar_devs")
async def read_user(mac: Request, db: Session = Depends(get_db)):
    req_info = await mac.json()
    print(req_info)
    retorno = crud.atualize_devs_descobertos(db, req_info)
    # print(req_info)
    return retorno

@app.get("/api/api/estatisticas_de_software/", response_model=Json)
def ler_estatisticas(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    ativos = crud.get_estatisticas_de_software(db)
    return ativos

@app.get("/api/estatisticas_de_uso/", response_model=Json)
def ler_estatisticas(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    ativos = crud.get_estatisticas_de_uso(db)
    return ativos

@app.get("/api/lista_ativos_estatisticas_de_uso/", response_model=Json)
def ler_estatisticas(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    ativos = crud.get_lista_de_ativos_estatisticas_de_uso(db)
    return ativos



@app.get("/api/instalacoes_sw/{id}", response_model=Json)
def read_user(id: int, db: Session = Depends(get_db)):
    #db_user = crud.get_informacao_de_hardware_do_ativo(db, patrimonio)
    ativos_com_sw = crud.get_instalacoes_do_software(db, id)
    # print(db_ativo.patrimonio)
    if ativos_com_sw is None:
        raise HTTPException(status_code=404, detail="Inexistente")
    json_string = json.dumps(ativos_com_sw, indent=4, sort_keys=True, default=str)
    
    return json_string

@app.get("/api/dados_de_software/{id}", response_model=Json)
#dados de software + ativos_de_software do software
def read_user(id: int, db: Session = Depends(get_db)):
    #db_user = crud.get_informacao_de_hardware_do_ativo(db, patrimonio)
    ativos_com_sw = crud.get_instalacoes_do_software(db, id)
    # print(db_ativo.patrimonio)
    if ativos_com_sw is None:
        raise HTTPException(status_code=404, detail="Inexistente")
    json_string = json.dumps(ativos_com_sw, indent=4, sort_keys=True, default=str)
    
    return json_string

@app.get("/api/get_licencas_adquiridas/{id}", response_model=Json)
#licenses de software vinculados ao id do ativo
def read_user(id: int, db: Session = Depends(get_db)):
    #db_user = crud.get_informacao_de_hardware_do_ativo(db, patrimonio)
    ativos_com_sw = crud.get_licencas_adquiridas(db, id)
    # print(db_ativo.patrimonio)
    if ativos_com_sw is None:
        raise HTTPException(status_code=404, detail="Inexistente")
    json_string = json.dumps(ativos_com_sw, indent=4, sort_keys=True, default=str)
    
    return json_string


@app.post('/api/adicionar_nova_licenca_adquirida/')
async def main(dados: Request, db: Session = Depends(get_db)): 
    req_info = await dados.json()
    print(req_info)
    retorno = crud.adicione_ativo_de_software(db,req_info)
    return retorno


@app.post('/api/adicionar_nova_licenca_adquirida2/')
async def main(dados: Request, db: Session = Depends(get_db)): 
    #req_info = await dados.json()
    print(dados)
    return dados

@app.post("/api/items_via_request_body")
async def read_item_via_request_body(request: Request, db: Session = Depends(get_db)):
    req_info = await request.form()
    lista_de_ids = []
    lista_de_chaves = []
    lista_de_users = []
    tipo_da_license = ""
    dicionario = {}
    print(req_info)
    for form in req_info:
     print (form)
     if ("id" in form):
         lista_de_ids.append(req_info[form])
     if ("tipo" in form):
         tipo_da_license = req_info[form]
     if ("chave" in form):
         lista_de_chaves.append(req_info[form])
     if ("user" in form):
         lista_de_users.append(req_info[form])       
    dicionario['id'] = lista_de_ids[0]
    dicionario['tipo'] = tipo_da_license
    dicionario['chaves'] = lista_de_chaves
    dicionario['users'] = lista_de_users
    print(json.dumps(dicionario))
    retorno = crud.adicione_licenca_em_ativo_de_software(db,dicionario)         
    print(retorno)
    
    
    return 0


@app.post('/api/adicionar_dados_de_licenca_em_licenca_adquirida/')
async def main(dados: Request, db: Session = Depends(get_db)): 
    
    #try:
     req_info = await dados.form()
     print (req_info)
     #for form in req_info:
     #print (req_info['json_enviado'])
     dicionaro = json.loads(req_info['json_enviado'])
     
     #print(dicionaro['tipo'])
     retorno = crud.adicione_licenca_em_ativo_de_software(db,dicionaro) 
     #retorno = "sucesso"
    #except:    
     #retorno = "erro 1"
    
     return retorno


@app.post('/api/aplicar_license/')
async def main(dados: Request, db: Session = Depends(get_db)): 
    
    #try:
     
     req_info = await dados.form()
     tipo_de_license =  req_info['tipo']
     ativo_para_aplicar = req_info['ativo']
     id_de_license = req_info['license_id']
     #for form in req_info:
     #print (req_info['json_enviado'])
     #dicionaro = json.loads(req_info['ativo'])
     print (type(req_info['license_id']))
     #print(dicionaro['tipo'])
     retorno = crud.aplicar_license_em_ativo(db,id_de_license,ativo_para_aplicar) 
     #retorno = "sucesso"
    #except:    
     #retorno = "erro 1"
    
     return "well"


@app.post('/api/reservar_license/')
async def main(dados: Request, db: Session = Depends(get_db)): 
    
    #try:
     
     req_info = await dados.form()
     tipo_de_license =  req_info['tipo']
     observacao = req_info['observacao_reservar']
     id_de_license = req_info['license_id']
     #for form in req_info:
     #print (req_info['json_enviado'])
     #dicionaro = json.loads(req_info['ativo'])
     print (type(req_info['license_id']))
     #print(dicionaro['tipo'])
     retorno = crud.reservar_license(db,id_de_license,observacao) 
     #retorno = "sucesso"
    #except:    
     #retorno = "erro 1"
    
     return "well"


@app.post("/api/aplicar_volume_em_lista_de_ativos")
async def read_user(mac: Request, db: Session = Depends(get_db)):
    req_info = await mac.json()
    print(req_info)
    crud.aplicar_license_de_volume_em_lista_de_ativos(db, req_info)
    # print(req_info)
    return 0



#   grupoDesktop = 43

#     hosts_coletados = zabbix_api.busca_lista_todos_ativos_zabbix(grupoDesktop)

#     for host in hosts_coletados:

#      dados_zabbix = zabbix_api.busca_ativo_monitorado_zabbix("hostid", host["hostid"])
#      ativo = dados_zabbix[0]
#      # print(ativo)
#      hardware = dados_zabbix[1]
