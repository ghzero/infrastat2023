itens_de_monitoramento_de_hardware = { 
     #chave_monitoramento_zabbix   #nome_banco_de_dados 
"[HW][CPU]-Detalhes-[JSN]" : "dados_de_processador"  , #Detalhes processador
"[HW][PLM]-Modelo-[TXT]"   : "dados_de_placamae" ,     #Detales PlacaMae
"[HW][DSK]-Detalhes-[JSN]" : "dados_de_disco",         #Detalhes Disco
"[HW][GPU]-Detalhes-[JSN]" : "dados_de_gpu" ,          #Detalhes GPU
"[HW][MEM]-Detalhes-[JSN]" : "dados_de_memoria" ,      #Detalhes Memoria
"[HW][MEM]-Total-[NUM]"    : "dados_de_memoria_total_em_gb",    #Memoria Total GB
"[MON][SW]-Lista-[JSN]"    : "dados_de_software",    #Memoria Total GB
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