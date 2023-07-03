from xmlrpc.client import boolean
from sqlalchemy import *
from sqlalchemy.orm import relationship
from database import Base

class ativo_hardware(Base): #quem_cadastrou (sistema,manual), #monitorado. #ultima_alteracao
    __tablename__ = "ativos_hardware"
    id = Column(Integer, primary_key=True)
    zabbix_id = Column(Integer)
    cmdb_id = Column(Integer)
    patrimonio = Column(Text)
    tipo = Column(Text)
    ciclo_de_vida = Column(Text)
    status = Column(Text)
    endereco_mac = Column(Text)
    endereco_ip = Column(Text)
    hostname = Column(Text)
    equipe = Column(Text)
    local = Column(Text)
    informacao_hardware_id = Column(Integer, ForeignKey('informacao_hardware.id'))
    informacao_sistema_id = Column(Integer, ForeignKey('informacao_sistema.id'))
    informacao_software_id = relationship("informacao_de_software", backref="ativo_hardware", lazy=True, uselist=False )
    data_cadastro = Column(DateTime)
    ultima_alteracao = Column(DateTime)
    quem_cadastrou = Column(Text)
    monitorado = Column(Text)
    documento_de_incorporacao_id = Column(Integer, ForeignKey('documento_de_incorporacao.id'))
    

    
    def __init__(self, zabbix_id, cmdb_id, patrimonio, tipo, ciclo_de_vida, status, endereco_mac, endereco_ip, hostname, equipe, local, data_cadastro,quem_cadastrou,monitorado):
        self.zabbix_id = zabbix_id
        self.cmdb_id = cmdb_id
        self.patrimonio = patrimonio
        self.tipo = tipo
        self.ciclo_de_vida = ciclo_de_vida
        self.status = status
        self.endereco_mac = endereco_mac
        self.endereco_ip = endereco_ip 
        self.hostname = hostname
        self.equipe = equipe
        self.local = local
        self.data_cadastro = data_cadastro
        self.quem_cadastrou = quem_cadastrou
        self.monitorado = monitorado
        
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __eq__(self, other): 

        return self.patrimonio == other.patrimonio and self.endereco_mac == other.endereco_mac and self.hostname == other.hostname and self.zabbix_id == other.zabbix_id

    def alteracao(self, other):
        
        dicionario_alteracao = []
        if (self.hostname != other.hostname):
            dicionario_alteracao.append("hostname")
        if (self.local != other.local):
            dicionario_alteracao.append("local")    
        if (self.endereco_mac != other.endereco_mac):
            dicionario_alteracao.append("endereco_mac")
        if (self.status != other.status):
            dicionario_alteracao.append("status")
        if (self.zabbix_id != other.zabbix_id):
            dicionario_alteracao.append("zabbix_id")               

        return dicionario_alteracao 
    

class ativo_de_software(Base): #quem_cadastrou (sistema,manual), #monitorado. #ultima_alteracao
    __tablename__ = "ativo_de_software"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    versao_adquirida = Column(Text)
    total_adquirido = Column(Integer)
    total_utilizado = Column(Integer)
    tipo_de_license = Column(Text) 
    tipo_de_contrato = Column(Text) #servico / perpetuo
    valida = Column(Boolean)
    data_de_expiracao = Column(DateTime)
    data_de_aquisicao = Column(DateTime)
    responsavel = Column(Text)
    informacoes = Column(Text)
    biblioteca_de_software_id = Column(Integer, ForeignKey('biblioteca_de_software.id'))
    documento_de_aquisicao_id = Column(Integer, ForeignKey('documento_de_aquisicao.id'))
    lista_de_licenses_id = relationship("license_de_software", backref="ativo_de_software", lazy=True, uselist=False )
    

    
    def __init__(self, nome, versao_adquirida, total_adquirido, total_utilizado, tipo_de_license, tipo_de_contrato, valida, data_de_expiracao,data_de_aquisicao, responsavel,informacoes, biblioteca_de_software_id):
        self.nome = nome
        self.versao_adquirida = versao_adquirida
        self.total_adquirido = total_adquirido
        self.total_utilizado = total_utilizado
        self.tipo_de_license = tipo_de_license
        self.tipo_de_contrato = tipo_de_contrato
        self.valida = valida
        self.data_de_aquisicao = data_de_aquisicao 
        self.data_de_expiracao = data_de_expiracao 
        self.informacoes = informacoes
        self.responsavel = responsavel
        self.biblioteca_de_software_id = biblioteca_de_software_id
        
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __eq__(self, other): 

        return self.versao_adquirida == other.versao_adquirida and self.nome == other.nome and self.documento_de_aquisicao_id == other.documento_de_aquisicao_id

  
    
#tabela auxiliar n para n de detalhes de componentes na biblioteca
informacao_biblioteca_hardware = Table('informacao_biblioteca_hardware', Base.metadata,
    Column('biblioteca_hardware_id', Integer, ForeignKey('biblioteca_hardware.id'), primary_key=True),
    Column('informacao_hardware_id', Integer, ForeignKey('informacao_hardware.id'), primary_key=True)
)


informacao_biblioteca_software = Table('informacao_biblioteca_software', Base.metadata,
    Column('identificador_de_software_id', Integer, ForeignKey('identificador_de_software.id'), primary_key=True),
    Column('informacao_de_software_id', Integer, ForeignKey('informacao_de_software.id'), primary_key=True)
)



class license_de_software(Base):
    __tablename__ = "license_de_software"
    id = Column(Integer, primary_key=True)
    tipo = Column(Text)
    usuario = Column(Text)
    chave = Column(Text)
    observacoes = Column(Text)
    data_de_aplicacao = Column(DateTime)
    aplicado = Column(Boolean)
    disponivel = Column(Boolean)
    reservado = Column(Boolean)
    ativo_de_software_id = Column(Integer, ForeignKey('ativo_de_software.id'))
    ativos_com_license_aplicada = Column(Integer, ForeignKey('ativos_hardware.id')) 
    
    

    
    def __init__(self, tipo, usuario, chave, observacoes, data_de_aplicacao,aplicado,disponivel,reservado,ativo_de_software_id):
        self.tipo = tipo
        self.usuario = usuario
        self.chave = chave
        self.observacoes = observacoes
        self.data_de_aplicacao = data_de_aplicacao
        self.aplicado = aplicado
        self.disponivel = disponivel
        self.reservado = reservado
        self.ativo_de_software_id = ativo_de_software_id
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}  



class informacao_sistema(Base):
    __tablename__ = "informacao_sistema"
    id = Column(Integer, primary_key=True)
    sistema_operacional = Column(Text)
    dados_de_administradores = Column(Text)
    dados_de_antivirus = Column(Text)
    dados_de_versao = Column(Text)
    dados_de_update = Column(Text)
    ativo_id = relationship("ativo_hardware", backref="informacao_sistema", lazy=True, uselist=False )
    

    
    def __init__(self, sistema_operacional, dados_de_administradores, dados_de_antivirus, dados_de_versao, dados_de_update, ativo):
        self.sistema_operacional = sistema_operacional
        self.dados_de_administradores = dados_de_administradores
        self.dados_de_antivirus = dados_de_antivirus
        self.dados_de_versao = dados_de_versao
        self.dados_de_update = dados_de_update
        self.ativo_id = ativo
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __eq__(self, other): 

        return self.sistema_operacional == other.sistema_operacional and self.dados_de_administradores == other.dados_de_administradores and self.dados_de_antivirus == other.dados_de_antivirus and self.dados_de_versao == other.dados_de_versao and self.dados_de_update == other.dados_de_update 

    def alteracao(self, other):
        
        dicionario_alteracao = []
        if (self.sistema_operacional != other.sistema_operacional):
            dicionario_alteracao.append("sistema_operacional")
        if (self.dados_de_administradores != other.dados_de_administradores):
            dicionario_alteracao.append("dados_de_administradores")    
        if (self.dados_de_antivirus != other.dados_de_antivirus):
            dicionario_alteracao.append("dados_de_antivirus")
        if (self.dados_de_versao != other.dados_de_versao):
            dicionario_alteracao.append("dados_de_versao") 
        if (self.dados_de_update != other.dados_de_update):
            dicionario_alteracao.append("dados_de_update")
                   

        return dicionario_alteracao

class informacao_hardware(Base):
    __tablename__ = "informacao_hardware"
    id = Column(Integer, primary_key=True)
    dados_de_processador = Column(Text)
    dados_de_placamae = Column(Text)
    dados_de_disco = Column(Text)
    dados_de_gpu = Column(Text)
    dados_de_memoria = Column(Text)
    dados_de_memoria_total_em_gb = Column(Integer)
    quantidade_de_discos = Column(Integer)
    quantidade_de_memorias = Column(Integer)
    dados_completos = Column(Boolean)
    ativo_id = relationship("ativo_hardware", backref="informacao_hardware", lazy=True, uselist=False )
    componentes_hardware = relationship('biblioteca_hardware', secondary=informacao_biblioteca_hardware, lazy='subquery',
        backref='informacao_hardware_id')

    
    def __init__(self, dados_de_processador, dados_de_placamae, dados_de_disco, dados_de_gpu, dados_de_memoria, dados_de_memoria_total_em_gb, quantidade_de_discos, quantidade_de_memorias,dados_completos, ativo):
        self.dados_de_processador = dados_de_processador
        self.dados_de_placamae = dados_de_placamae
        self.dados_de_disco = dados_de_disco
        self.dados_de_gpu = dados_de_gpu
        self.dados_de_memoria = dados_de_memoria
        self.dados_de_memoria_total_em_gb = dados_de_memoria_total_em_gb
        self.quantidade_de_discos = quantidade_de_discos
        self.quantidade_de_memorias = quantidade_de_memorias
        self.dados_completos = dados_completos
        self.ativo_id = ativo
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def __eq__(self, other): 

        return self.dados_de_processador == other.dados_de_processador and self.dados_de_placamae == other.dados_de_placamae and self.dados_de_disco == other.dados_de_disco and self.dados_de_gpu == other.dados_de_gpu and self.dados_de_memoria == other.dados_de_memoria and self.dados_de_memoria_total_em_gb == other.dados_de_memoria_total_em_gb and self.quantidade_de_discos == other.quantidade_de_discos and self.quantidade_de_memorias == other.quantidade_de_memorias

    def alteracao(self, other):
        
        dicionario_alteracao = []
        if (self.dados_de_processador != other.dados_de_processador):
            dicionario_alteracao.append("dados_de_processador")
        if (self.dados_de_placamae != other.dados_de_placamae):
            dicionario_alteracao.append("dados_de_placamae")    
        if (self.dados_de_disco != other.dados_de_disco):
            dicionario_alteracao.append("dados_de_disco")
        if (self.dados_de_gpu != other.dados_de_gpu):
            dicionario_alteracao.append("dados_de_gpu") 
        if (self.dados_de_memoria != other.dados_de_memoria):
            dicionario_alteracao.append("dados_de_memoria")
        if (self.quantidade_de_discos != other.quantidade_de_discos):
            dicionario_alteracao.append("quantidade_de_discos")
        if (self.dados_de_memoria_total_em_gb != other.dados_de_memoria_total_em_gb):
            #print(self.dados_de_memoria_total_em_gb)
            #print(other.dados_de_memoria_total_em_gb)
            dicionario_alteracao.append("dados_de_memoria_total_em_gb")

            

        return dicionario_alteracao


class informacao_de_software(Base):
    __tablename__ = "informacao_de_software"
    id = Column(Integer, primary_key=True)
    nome_software = Column(Text)
    versao_instalada = Column(Text)
    data_instalacao = Column(Text)
    ativo_id = Column(Integer, ForeignKey('ativos_hardware.id'))
    componentes_software = relationship('identificador_de_software', secondary=informacao_biblioteca_software, lazy='subquery',
        backref='informacao_de_software_id')
     

    
    def __init__(self, nome_software, versao_instalada, data_instalacao, ativo):
        
        self.nome_software = nome_software
        self.versao_instalada = versao_instalada
        self.data_instalacao = data_instalacao
        self.ativo_id = ativo.id
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}  



class biblioteca_hardware(Base):
    __tablename__ = "biblioteca_hardware"
    id = Column(Integer, primary_key=True)
    cmdb_id = Column(Integer)
    cmdb_typeid = Column(Integer)
    tipo = Column(Text)
    nomeMonitoramento = Column(Text)
    detalhes = Column(Text)
    quantidade = Column(Integer) #Json
    #quantidade = quantidade de unidades deste tipo em uso
    #tamanho 
    #fabricante AOC
    #modelo AOC2050
    #nome_completo AOC AOC2050 50W
    #identificador_monitoramento AOC205
    #dados_monitoramento ["json"]
    #outras_informacoes ["json-adicionado-depois"] #[ Resolucao / Conexoes ]

    
    def __init__(self, cmdb_id, cmdb_typeid, tipo, nomeMonitoramento, detalhes, quantidade):
        self.cmdb_id = cmdb_id
        self.cmdb_typeid = cmdb_typeid
        self.tipo = tipo
        self.nomeMonitoramento = nomeMonitoramento
        self.detalhes = detalhes
        self.quantidade = quantidade
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}    

class identificador_de_software(Base):
    __tablename__ = "identificador_de_software"
    id = Column(Integer, primary_key=True)
    identificador = Column(Text)
    biblioteca_de_software_id = Column(Integer, ForeignKey('biblioteca_de_software.id'))
    
    def __init__(self, identificador,  biblioteca_de_software):
        self.identificador = identificador
        self.biblioteca_de_software_id = biblioteca_de_software.id
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}    

class fabricante(Base):
    __tablename__ = "fabricante"
    id = Column(Integer, primary_key=True)
    nome_do_fabricante = Column(Text)
    identificador_de_fabricante_id = relationship("identificador_de_fabricante", backref="fabricante", lazy=True, uselist=False )
    
    
    def __init__(self, nome_do_fabricante):
        self.nome_do_fabricante = nome_do_fabricante
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}  



class identificador_de_fabricante(Base):
    __tablename__ = "identificador_de_fabricante"
    id = Column(Integer, primary_key=True)
    identificador = Column(Text)
    fabricante_id = Column(Integer, ForeignKey('fabricante.id'))
    
    def __init__(self, identificador,  fabricante):
        self.identificador = identificador
        self.fabricante_id = fabricante.id
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}        



class biblioteca_de_software(Base):
    __tablename__ = "biblioteca_de_software"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    desenvolvedor = Column(Integer, ForeignKey('identificador_de_fabricante.id'))
    detalhes = Column(Text)
    tipo_de_software = Column(Text)
    proprietario = Column(Boolean)
    monitorado = Column(Boolean)
    blacklist = Column(Boolean) 
    identificador_de_software_id = relationship("identificador_de_software", backref="biblioteca_de_software", lazy=True, uselist=False )
    

    
    def __init__(self, nome, desenvolvedor,  tipo_de_software, proprietario, monitorado, blacklist,):
        self.nome = nome
        self.desenvolvedor = desenvolvedor
        self.tipo_de_software = tipo_de_software
        self.proprietario = proprietario
        self.monitorado = monitorado
        self.blacklist = blacklist
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}    



class log_sistema(Base):
    __tablename__ = "log_sistema"
    id = Column(Integer, primary_key=True)
    status = Column(Text)
    total_ativos = Column(Text)
    total_ativos_verificados = Column(Text)
    total_ativos_atualizados = Column(Text)
    total_ativos_cadastrados = Column(Text)
    total_ativos_com_problema = Column(Text)
    data_execucao = Column(DateTime)
    tempo_execucao_segundos = Column(Integer)
    
    def __init__(self, status,total_ativos,total_ativos_verificados,total_ativos_atualizados, total_ativos_cadastrados, total_ativos_com_problema, data_execucao,tempo_execucao_segundos):
        self.status = status
        self.total_ativos = total_ativos
        self.total_ativos_verificados = total_ativos_verificados
        self.total_ativos_atualizados = total_ativos_atualizados
        self.total_ativos_cadastrados = total_ativos_cadastrados
        self.total_ativos_com_problema = total_ativos_com_problema
        self.data_execucao = data_execucao
        self.tempo_execucao_segundos = tempo_execucao_segundos
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}   


class estatistica(Base):
    __tablename__ = "estatistica"
    id = Column(Integer, primary_key=True)
    tipo = Column(Text) #uso, hardware, software
    resultado = Column(Text) #json resultante
    total_ativos_verificados = Column(Integer)
    total_ativos_com_problema = Column(Integer)
    data_execucao = Column(Text)
    periodo_da_estatistica = Column(Text) 
    tempo_execucao_segundos = Column(Integer)
    
    def __init__(self, tipo,resultado,total_ativos_verificados,total_ativos_com_problema, data_execucao,periodo_da_estatistica,tempo_execucao_segundos):
        self.tipo = tipo
        self.resultado = resultado
        self.total_ativos_verificados = total_ativos_verificados
        self.total_ativos_com_problema = total_ativos_com_problema
        self.data_execucao = data_execucao
        self.periodo_da_estatistica = periodo_da_estatistica
        self.tempo_execucao_segundos = tempo_execucao_segundos
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}        

class monitor_descoberto(Base):
    __tablename__ = "monitor_descoberto"
    id = Column(Integer, primary_key=True)
    identificador = Column(Text)
    serial = Column(Text)
    fabricante = Column(Text)
    modelo = Column(Text)
    ativo_id = Column(Integer, ForeignKey('ativos_hardware.id'))
    
    
    def __init__(self, identificador, serial, fabricante, modelo, ativo_id):
        self.identificador = identificador
        self.serial = serial
        self.fabricante = fabricante
        self.modelo = modelo
        self.ativo_id = ativo_id
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}  

class switch(Base):
    __tablename__ = "switch"
    id = Column(Integer, primary_key=True)
    regexporta = Column(Text)
    mac = Column(Text)
    stack = Column(Text)
    local = Column(Text)
    modelo = Column(Text)
    portas = relationship("porta_switch")
    
    
    def __init__(self, local, regexporta, mac, stack, modelo):
        self.local = local
        self.regexporta = regexporta
        self.mac = mac
        self.stack = stack
        self.modelo = modelo
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}   

class porta_switch(Base):
    __tablename__ = "porta_switch"
    id = Column(Integer, primary_key=True)
    porta = Column(Text)
    stack = Column(Text)
    info = Column(Text)
    ativo_pat = Column(Text)
    ativo_id = Column(Integer, ForeignKey('ativos_hardware.id'))
    switch_id = Column(Integer, ForeignKey('switch.id'))
    
    def __init__(self, porta, stack, info, ativo_pat, ativo_id, switch_id):
        self.porta = porta
        self.stack = stack
        self.info = info
        self.ativo_pat = ativo_pat
        self.ativo_id = ativo_id
        self.switch_id = switch_id
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}     


class alerta(Base):
    __tablename__ = "alerta"
    id = Column(Integer, primary_key=True)
    codigo = Column(Text)
    mensagem = Column(Text)
    tipo_acao = Column(Text)
    detalhes_acao = Column(Text)
    
    
    def __init__(self, codigo, mensagem, tipo_acao, detalhes_acao):
        self.codigo = codigo
        self.mensagem = mensagem
        self.tipo_acao = tipo_acao
        self.detalhes_acao = detalhes_acao
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}  

class alerta_monitoramento(Base):
    __tablename__ = "alerta_monitoramento"
    id = Column(Integer, primary_key=True)
    zabbix_id = Column(Integer)
    data_ocorrencia = Column(DateTime)
    corrigido = Column(Boolean)
    quem_corrigiu = Column(Text)
    data_correcao = Column(DateTime)
    detalhes = Column(Text)
    alerta_id = Column(Integer, ForeignKey('alerta.id'))
    
    
    def __init__(self, zabbix_id, data_ocorrencia, corrigido, data_correcao,quem_corrigiu, detalhes, alerta_id):
        self.zabbix_id = zabbix_id
        self.data_ocorrencia = data_ocorrencia
        self.corrigido = corrigido
        self.quem_corrigiu = quem_corrigiu
        self.data_correcao = data_correcao
        self.detalhes = detalhes
        self.alerta_id = alerta_id
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}  


# class informacao_software(Model):
#     id = Column(Integer, primary_key=True)
#     ativo_id = relationship("ativo_hardware", backref="informacao_software", lazy=True, uselist=False )
#     lista_softwares_instalados = Column(Text)
#     total_softwares_instalados = Column(Integer)
#     licenca_software_id = Column(Text) #Many to Many

    
#     def __init__(self, lista_softwares, total_softwares, ativo):
#         self.ativo_id = ativo
#         self.lista_softwares_instalados = lista_softwares
#         self.total_softwares_instalados = total_softwares
#         self.licenca_software_id = "licenses"

#Documentos dos processos

class documento_de_aquisicao(Base):
    __tablename__ = "documento_de_aquisicao"
    id = Column(Integer, primary_key=True)
    identificador_externo = Column(Text)
    login_do_solicitante = Column(Text)
    solicitante = Column(Text)
    solicitacao = Column(Text)
    itens_adquiridos = Column(Text)
    valor_total = Column(Integer)
    detalhes_aquisicao = Column(Text)
    data_de_aquisicao = Column(DateTime)
    
    
    def __init__(self, identificador_externo, solicitante, solicitacao, itens_adquiridos,valor_total, detalhes_aquisicao, data_de_aquisicao):
        self.identificador_externo = identificador_externo
        self.solicitante = solicitante
        self.solicitacao = solicitacao
        self.itens_adquiridos = itens_adquiridos
        self.valor_total = valor_total
        self.detalhes_aquisicao = detalhes_aquisicao
        self.data_de_aquisicao = data_de_aquisicao
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}  


class documento_de_incorporacao(Base):
    __tablename__ = "documento_de_incorporacao"
    id = Column(Integer, primary_key=True)
    patrimonio = Column(Text)
    documento_de_aquisicao_id = Column(Integer, ForeignKey('documento_de_aquisicao.id'))
    local_de_destino = Column(Text)
    quem_incorporou = Column(Text)
    garantia_total_em_anos = Column(Text)
    
    
    def __init__(self, patrimonio, documento_de_aquisicao_id, local_de_destino, garantia_total):
        self.patrimonio = patrimonio
        self.documento_de_aquisicao_id = documento_de_aquisicao_id
        self.local_de_destino = local_de_destino
        self.garantia_total = garantia_total
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}  


class documento_de_alteracao(Base):
    __tablename__ = "documento_de_alteracao"
    id = Column(Integer, primary_key=True)
    ativo_id = Column(Integer, ForeignKey('ativos_hardware.id'))
    tipo = Column(Text)
    alteracao = Column(Text)
    detalhes_alteracao = Column(Text)
    data_alteracao = Column(DateTime)
    foi_autorizado = Column(Boolean)
    quem_autorizou = Column(Text)
    id_autorizacao = Column(Text)
    foi_verificado = Column(Boolean)
    
    
    def __init__(self, ativo_id, tipo, alteracao, detalhes_alteracao,data_alteracao,foi_autorizado,quem_autorizou,id_autorizacao,foi_verificado):
        self.ativo_id = ativo_id
        self.tipo = tipo
        self.alteracao = alteracao
        self.detalhes_alteracao = detalhes_alteracao
        self.data_alteracao = data_alteracao
        self.foi_autorizado = foi_autorizado
        self.quem_autorizou = quem_autorizou
        self.id_autorizacao = id_autorizacao
        self.foi_verificado = foi_verificado
        
    
    def as_dict(self):
    
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}  

#Tarefas_de_Processos

#Solicitacao
#Documento_de_Solicitacao#
 #ativo de ti eh solicitado para executar determinada funcao
  #solicitacao eh recebida e aprovada ou negada pelo departamento de ti
   #existe ativo ocioso que atende a demanda
    #departamento de ti solicita a realocacao de ativo junto ao setor administrativo 
   #nao existe ativo que atenda a demanda, departamento de ti envia solicitacao de aquisicao para setor administrativo
  #se solicitacao negada informar o motivo e reiniciar o processo caso adequacoes sejam necessarias


#Aquisicao
 #administrativo nega ou aprova a aquisicao do ativo solicitado
  #administrativo inicia o processo de aquisicao do bem criando um #Documento de aquisição#
 #se aquisicao negada informar o motivo e reiniciar o processo caso adequacoes sejam necessariasIM

#Recepcao e checagem
  #administrativo recebe os itens e cria um documento de incorporacao solicitando a instalacao do ativo junto ao departamento de ti
  #em um #Documento de Incorporacao#

#Incorporacao (configuracao, movimentacao, instalacao, teste, disponibilizacao)
  #departamento de ti de posse dos itens adquiridos inicia o processo de IMACD incorporando o ativo
   
#Operacao
  #apos a instalacao o ativo passa a ter status operacional e se encontra incorporado e operacional
   #processos de monitoramento de operação se iniciam

  #Para alteracoes se cria um #Documento de alteracao
  #Para manutencoes se cria um #Documento de manutencao







