from typing import List, Optional
from pydantic import BaseModel
from datetime import date
class ativo_hardware_base(BaseModel):
    
    zabbix_id: str
    cmdb_id: Optional[str] = None
    quem_cadastrou: str
    monitorado: str
    tipo: str
    ciclo_de_vida: str
    status: str
    endereco_mac: str
    patrimonio: str
    hostname: str
    equipe: str
    local: str
    endereco_ip: str
    
def __eq__(self, other): 
        if not isinstance(other, ativo_hardware_base):
            return "Comparacao Invalida"

        return self.patrimonio == other.patrimonio and self.mac_address == other.mac_address 


class ativo_hardware(ativo_hardware_base):
    id: int

    class Config:
        orm_mode = True



class biblioteca_software_base(BaseModel):

    nome: str
    desenvolvedor: str
    tipo_de_software: str
    proprietario: bool
    monitorado: bool
    blacklist: bool



class biblioteca_software(biblioteca_software_base):
    id: int

    class Config:
        orm_mode = True




class biblioteca_hardware_base(BaseModel):

    cmdb_id: str
    cmdb_typeid: str
    tipo: str
    nome_monitoramento: str
    detalhes: str


class criar_biblioteca_hardware(biblioteca_hardware_base):
    quantidade: int

class biblioteca_hardware(criar_biblioteca_hardware):
    id: int

    class Config:
        orm_mode = True



class informacao_hardware_base(BaseModel):
    
    dados_de_processador: str
    dados_de_placamae: str
    dados_de_disco: str
    dados_de_gpu: str
    dados_de_memoria: str
    dados_de_memoria_total_em_gb: str
    quantidade_de_discos: str
    quantidade_de_memorias: str
    dados_completos: bool

    def __eq__(self, other): 
        if not isinstance(other, informacao_hardware):
            return "Comparacao Invalida"

        return self.dados_de_processador == other.dados_de_processador and self.dados_de_placamae == other.dados_de_placamae and self.dados_de_disco == other.dados_de_disco and self.dados_de_gpu == other.dados_de_gpu and self.dados_de_memoria == other.dados_de_memoria and self.dados_de_memoria_total_em_gb == other.dados_de_memoria_total_em_gb and self.quantidade_de_discos == other.quantidade_de_discos and self.quantidade_de_memorias == other.quantidade_de_memorias
    

class criar_informacao_hardware(informacao_hardware_base):
    ativo_id: ativo_hardware
    
class informacao_hardware(criar_informacao_hardware):
    id: int

    class Config:
        orm_mode = True


class informacao_sistema_base(BaseModel):
    sistema_operacional: str
    dados_de_administradores: str
    dados_de_antivirus: str
    dados_de_versao: str
    dados_de_update: str

    def __eq__(self, other): 
        if not isinstance(other, informacao_sistema):
            return "Comparacao Invalida"

        return self.sistema_operacional == other.sistema_operacional and self.dados_de_administradores == other.dados_de_administradores and self.dados_de_antivirus == other.dados_de_antivirus and self.dados_de_versao == other.dados_de_versao and self.dados_de_update == other.dados_de_update 
    

class criar_informacao_sistema(informacao_sistema_base):
    ativo_id: ativo_hardware
    
class informacao_sistema(criar_informacao_sistema):
    id: int

    class Config:
        orm_mode = True


class fabricante_base(BaseModel):
   
   
    nome_do_fabricante: str

    def __eq__(self, other): 
        if not isinstance(other, fabricante_base):
            return "Comparacao Invalida"

        return self.nome_do_fabricante == other.nome_do_fabricante 

class fabricante(fabricante_base):
    id: int

    class Config:
        orm_mode = True    

class informacao_de_software_base(BaseModel):
   
    identificador: str
    nome_software: str
    publisher: str
    versao_instalada: str
    data_instalacao: str

    def __eq__(self, other): 
        if not isinstance(other, informacao_sistema):
            return "Comparacao Invalida"

        return self.identificador == other.identificador and self.nome_software == other.publisher and self.publisher == other.nome_software and self.versao_instalada == other.versao_instalada and self.data_instalacao == other.data_instalacao 
    

class criar_informacao_de_software(informacao_de_software_base):
    ativo_id: ativo_hardware
    
class informacao_de_software(criar_informacao_de_software):
    id: int

    class Config:
        orm_mode = True


        

class log_sistema_base(BaseModel):

    status: str
    tipo_acao: str
    mensagem: str


class log_sistema(log_sistema_base):
    id: int

    class Config:
        orm_mode = True

class estatistica_base(BaseModel):

    tipo: str
    resultado: str
    total_ativos_verificados: str
    total_ativos_com_problema: str
    data_execucao: str
    periodo_da_estatistica: str
    tempo_execucao_segundos: str


class estatistica(estatistica_base):
    id: int

    class Config:
        orm_mode = True


class switch_base(BaseModel):

    local: str
    regexporta: str
    mac: str
    stack: str
    modelo: str


class switch(switch_base):
    id: int

    class Config:
        orm_mode = True

class monitor_descoberto_base(BaseModel):

    identificador: str
    serial: str
    fabricante: str
    modelo: str
    ativo_id: str

class monitor_descoberto(monitor_descoberto_base):
    id: int

    class Config:
        orm_mode = True