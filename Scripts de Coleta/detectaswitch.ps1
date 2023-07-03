$rootpath = 'C:\Program Files\Zabbix Agent2\conf\LLDP'
$global:HOST_NAME = & hostname
$global:ArquivoERRO = "C:\Program Files\Zabbix Agent2\conf\LLDP\log\stderr.tmp"
$global:PastaRaiz = 'C:\Program Files\Zabbix Agent2\conf'
$global:ArquivoSaida = "SWdata.txt"

#Verifica instalação WinPCAP
If (!(Test-Path 'C:\Windows\System32\drivers\npf.sys')) {

        Write-Host "Instale WinPcap"
		$null > "$PastaRaiz\$ArquivoSaida"
		Write-Output "ERRO: WinPCAP" | Out-File "$PastaRaiz\$ArquivoSaida" -Append
        #Salvar mensagem de falha no WinPCAP no txt

        exit
}

#$AdaptadorEthernet = Seleciona o adaptador ethernet ativo
$AdaptadorEthernet = Get-WmiObject win32_networkadapter | Where {$_.Name -Match "Ethernet|Local|Gigabit|GBE" -and $_.Name -NotMatch "Virtual|vEthernet|Hyper-V|VPN|USB|Mobile" -and $_.NetConnectionStatus -Match "2"}

If ($AdaptadorEthernet -eq $null) { #Caso nao exista adaptador ativo, verificar o motivo.
	    $AdaptadorEthernet = Get-WmiObject win32_networkadapter | Where {$_.Name -Match "Ethernet|Local|Gigabit|GBE" -and $_.Name -NotMatch "Virtual|vEthernet|Hyper-V|VPN|USB|Mobile"}
      	switch ($AdaptadorEthernet.NetConnectionStatus) {

            0  {$StatusAdaptador = "Desativado"}
            1  {$StatusAdaptador = "Conectando"}
            2  {$StatusAdaptador = "Conectado"}
            3  {$StatusAdaptador = "Desconectando"}
            4  {$StatusAdaptador = "Hardware Ausente"}
            5  {$StatusAdaptador = "Hardware Desabilitado"}
            6  {$StatusAdaptador = "Hardware Defeituoso"}
            7  {$StatusAdaptador = "Cabo Desconectado"}
            8  {$StatusAdaptador = "Autenticando"}
            9  {$StatusAdaptador = "Autenticado"}
            10 {$StatusAdaptador = "Falha na Autenticacao"}
            11 {$StatusAdaptador = "Endereco Invalido"}
            12 {$StatusAdaptador = "Erro de credenciais"}
}

        Write-Host "ERRO: Status: $StatusAdaptador ("$AdaptadorEthernet.NetConnectionStatus")"
		$null > "$PastaRaiz\$ArquivoSaida"
		Write-Output "ERRO: Status: Adaptador $StatusAdaptador" | Out-File "$PastaRaiz\$ArquivoSaida" -Append
        #Salvar mensagem de falha no Adaptador Ethernet no txt InfoSwitch
        exit
}

Else {  #Se o adaptador esta ativo inicia a busca pelo switch
        Write-Host "Adaptador ativo - Buscando Switch"
		
		$WDEthernet = Invoke-Command { C:\windows\system32\WinDump.exe -D | Select-String $AdaptadorEthernet.GUID }
		#Seleciona o GUID do adaptador, caso o resultado seja nulo apresenta um erro.
		If ($WDEthernet -eq $null) {
        Write-Host "ERRO - Adaptador nao encontrado"
        exit }
		#Extracao do ID de dispositivo do adaptador.
		$WDEthernet_S = $WDEthernet.ToString()
		$WDEthernet_CA = $WDEthernet_S.toCharArray()
		$WD_ID = $WDEthernet_CA[0]
		#Cria um job para captura do pacote broadcast do protocolo LLDP do switch.
		#job criado para aguardar o tempo de execução da busca de pacote, executando diretamente obtivemos alguns problemas de timeout.
		$WDJob = Start-Job -ArgumentList @("$PSScriptRoot","$WD_ID","$ArquivoERRO") -FilePath "$PSScriptRoot\buscalldp.ps1"
		
		
		#O Switch pode levar até 90 segundos para executar capturar o pacote LLDP.
		Wait-Job -Timeout 90 -Id $WDJob.Id | Out-Null
        $ArquivoPCAP = Receive-Job $WDJob.Id 
		
		If ($ArquivoPCAP -eq 1) {
			Write-Host "ERRO - WinPcap nao executou"
			Remove-Item $rootpath\log\*.tmp 
			exit} 
		ElseIf (Test-Path $ArquivoERRO) {
			Write-Host "INDETECTAVEL"
			
				$null > "$PastaRaiz\$ArquivoSaida"
				Write-Output "Switch: Indetectavel" | Out-File "$PastaRaiz\$ArquivoSaida" -Append
				Write-Output "Modelo: Indetectavel" | Out-File "$PastaRaiz\$ArquivoSaida" -Append
				Write-Output "MAC: Indetectavel" | Out-File "$PastaRaiz\$ArquivoSaida" -Append
				Write-Output "Porta ID: Indetectavel" | Out-File "$PastaRaiz\$ArquivoSaida" -Append
				Write-Output "Porta Desc: Indetectavel" | Out-File "$PastaRaiz\$ArquivoSaida" -Append
				
				Write-Host "Salvo em $PastaRaiz\$ArquivoSaida"

				$null > "$PastaRaiz\SWmac.txt"
				$null > "$PastaRaiz\SWnome.txt"
				$null > "$PastaRaiz\SWporta.txt"
				$null > "$PastaRaiz\SWportadesc.txt"
				$null > "$PastaRaiz\SWmodelo.txt"
				
				Write-Output "Indetectavel" | Out-File "$PastaRaiz\SWnome.txt" -Append
				Write-Output "Indetectavel"  | Out-File "$PastaRaiz\SWmodelo.txt" -Append
				Write-Output "Indetectavel"  | Out-File "$PastaRaiz\SWmac.txt" -Append
				Write-Output "Indetectavel"  | Out-File "$PastaRaiz\SWporta.txt" -Append
				Write-Output "Indetectavel"  | Out-File "$PastaRaiz\SWportadesc.txt" -Append	
			Stop-Process -Name WinDump -Force
			Start-Sleep -Seconds 5
			Remove-Item $rootpath\log\*.tmp
			exit}
		
		$PastaTSHARK = 'C:\Program Files\Wireshark\tshark.exe'
			
			If (Test-Path $PastaTSHARK) {
				#$MAC = $AdaptadorEthernet.MACAddress
				
				$SW_SYST_NAME = & $PastaTSHARK -T fields -e lldp.tlv.system.name -r $ArquivoPCAP
				$SW_SYST_DESC = & $PastaTSHARK -T fields -e lldp.tlv.system.desc -r $ArquivoPCAP
				$SW_IP_ADDRES = & $PastaTSHARK -T fields -e lldp.chassis.id.mac -r $ArquivoPCAP
				$SW_SHRT_PORT = & $PastaTSHARK -T fields -e lldp.port.id -r $ArquivoPCAP
				$SW_LONG_PORT = & $PastaTSHARK -T fields -e lldp.port.desc -r $ArquivoPCAP
				$SW_P_VLAN_ID = & $PastaTSHARK -T fields -e lldp.ieee.802_1.port_vlan.id -r $ArquivoPCAP
				Write-Host "Conectado ao Switch: $SW_SYST_NAME"
				Write-Host "Modelo do Switch: $SW_SYST_DESC"
				Write-Host "MAC do Switch: $SW_IP_ADDRES"
				Write-Host "Porta ID: $SW_SHRT_PORT"
				Write-Host "Porta Desc: $SW_LONG_PORT"

				$null > "$PastaRaiz\$ArquivoSaida"
				Write-Output "Switch: $SW_SYST_NAME" | Out-File "$PastaRaiz\$ArquivoSaida" -Append
				Write-Output "Modelo: $SW_SYST_DESC" | Out-File "$PastaRaiz\$ArquivoSaida" -Append
				Write-Output "MAC: $SW_IP_ADDRES" | Out-File "$PastaRaiz\$ArquivoSaida" -Append
				Write-Output "Porta ID: $SW_SHRT_PORT" | Out-File "$PastaRaiz\$ArquivoSaida" -Append
				Write-Output "Porta Desc: $SW_LONG_PORT" | Out-File "$PastaRaiz\$ArquivoSaida" -Append
				
				Write-Host "Salvo em $PastaRaiz\$ArquivoSaida"

				$null > "$PastaRaiz\SWmac.txt"
				$null > "$PastaRaiz\SWnome.txt"
				$null > "$PastaRaiz\SWporta.txt"
				$null > "$PastaRaiz\SWportadesc.txt"
				$null > "$PastaRaiz\SWmodelo.txt"
				
				Write-Output "$SW_SYST_NAME" | Out-File "$PastaRaiz\SWnome.txt" -Append
				Write-Output "$SW_SYST_DESC" | Out-File "$PastaRaiz\SWmodelo.txt" -Append
				Write-Output "$SW_IP_ADDRES" | Out-File "$PastaRaiz\SWmac.txt" -Append
				Write-Output "$SW_SHRT_PORT" | Out-File "$PastaRaiz\SWporta.txt" -Append
				Write-Output "$SW_LONG_PORT" | Out-File "$PastaRaiz\SWportadesc.txt" -Append
				
				$null > "$PastaRaiz\$ArquivoSaida"
				
				Write-Output "Nome: $SW_SYST_NAME - MAC: $SW_IP_ADDRES - Porta: $SW_SHRT_PORT - PortaDesc: $SW_LONG_PORT - Modelo: $SW_SYST_DESC" | Out-File "$PastaRaiz\$ArquivoSaida" -Append
				}
			
			Else {
				Write-Host "Instale Wireshark"  
				$null > "$PastaRaiz\$ArquivoSaida"
		        Write-Output "ERRO: Wireshark" | Out-File "$PastaRaiz\$ArquivoSaida" -Append}
			
			Remove-Item $rootpath\capturas\captura-windump.pcap -Force
       
}