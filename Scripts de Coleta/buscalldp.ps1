$PastaRaiz = $args[0]
$InterfaceID = $args[1]
$ArquivoDumpErro = $args[2]

$ErrFlag = 1

$Windump = "$PastaRaiz\WinDump.exe"

$ArquivoPCAP = "$PastaRaiz\capturas\captura-windump.pcap"
$MTUSize = "1522"
$Filtro = "(ether proto 0x88cc)"

<#
@ Argumentos:
    -w $ArquivoPCAP : escrever no arquivo $ArquivoPCAP    
    -i $InterfaceID : usar somente a interface de id $InterfaceID para captura
    -nn          : nao converte endereços em nomes
    -vvv         : verbose
    -s           : define o tamanho do MTU da frame
    -c 1         : define que apenas um pacote será capturado
    $Filtro
        ether proto : protocolo ethernet
        0x88cc      : Header do protocolo LLDP que queremos capturar
#>

$Argumentos = @("-w", "$ArquivoPCAP", '-i', "$InterfaceID", "-nn", "-vvv", "-s", "$MTUSize", "-c", "1", "$Filtro")

# Powershell encontra erros de sintaxe devido aos colchetes da interface, solução encontrada foi fazer o dump do erro em um arquivo
# para retornar somente o pacote, este arquivo é removido em seguida.
& $Windump $Argumentos 2> $ArquivoDumpErro
# Se o windump.exe falhar retorna uma flag de erro
if (!($LASTEXITCODE -eq 0)) {
    return $ErrFlag
}
Remove-Item $ArquivoDumpErro

$ArquivoPCAP


