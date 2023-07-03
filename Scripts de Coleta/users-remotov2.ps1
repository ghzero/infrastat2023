function Get-TSSessions
{
    qwinsta | ForEach-Object {$_ -replace "\s{2,18}","," } | ConvertFrom-Csv
}

$usuariosativos = Get-TSSessions | Where-Object { ($_.State -eq 'Active') -or ($_.State -eq 'Ativo') -or ($_.Type -eq 'Ativo') -or ($_.Type -eq 'Active') -or ($_.Device -eq 'Ativo') -or ($_.Device -eq 'Active') } | Format-Table UserName -HideTableHeaders | Out-String

if  ($usuariosativos) {
$comandoquser = quser | ForEach-Object {$_ -replace "\s{2,18}","," } | ConvertFrom-Csv
} else { $comandoquser = '' }


$consolelogonui = $false


$objremoto = $comandoquser | Where-Object { ($_.State -eq 'Active') -or ($_.State -eq 'Ativo') -or ($_.Type -eq 'Ativo') -or ($_.Type -eq 'Active') -or ($_.Device -eq 'Ativo') -or ($_.Device -eq 'Active') -and ($_.Sessionname -ne 'console') -and ($_.'IDLE TIME'.Length -le 1) } | Format-Table UserName -HideTableHeaders | Out-String 
#$objtempoteste = Get-TSSessions | Where-Object { ($_.'IDLE TIME' -eq 'nenhum') -or ($_.'IDLE TIME' -lt 10)   } | Format-Table UserName -HideTableHeaders | Out-String 
#write-output $objremoto
#$objremotodisc = Get-TSSessions | Where-Object { ($_.State -eq 'Disc') -or ($_.State -eq 'Disco') -or ($_.Type -eq 'Disco') -or ($_.Type -eq 'Disc') -or ($_.Device -eq 'Disco') -or ($_.Device -eq 'Disc') -and ($_.Sessionname -ne 'console') } | Format-Table ID -HideTableHeaders | Out-String 
$objconsole = $comandoquser | Where-Object { ($_.State -eq 'Active') -or ($_.State -eq 'Ativo') -or ($_.Type -eq 'Ativo') -or ($_.Type -eq 'Active') -or ($_.Device -eq 'Ativo') -or ($_.Device -eq 'Active') -and ($_.Sessionname -eq 'console') } | Format-Table UserName -HideTableHeaders | Out-String 

$jsonremoto = $objremoto -replace '\s', ' '
$jsonremoto = $jsonremoto -replace '>', ''
$trim = $jsonremoto.trim()
$jsonremoto = $trim -replace "\s{2,18}",","
$jsonremoto = $jsonremoto -replace ",",'","'


$jsonconsole = $objconsole -replace '\s', ' '
$trim = $jsonconsole.trim()
$jsonconsole = $trim -replace "\s{2,18}",","
$jsonconsole = $jsonconsole -replace ",",'","'


$usuariosconsole = '"'+$jsonconsole+'"'
$usuariosremoto = '"'+$jsonremoto+'"'

Try
{
$obj3 = Get-Process logonui -ErrorAction Stop
$verificausersemlogon = tasklist /FI "ImageName eq logonui.exe" /FI "Sessionname eq console"

if ($verificausersemlogon -Match "INFO") {
	$consolelogonui = $false
	#write-output 'Logon UI nao eh do console'
} else { 
$consolelogonui = $true
#write-output 'Logon UI eh do Console'
}

}
Catch
{
$consolelogonui = $false
}


$usuariosremoto = $usuariosremoto.trim()
$usuariosremoto = $usuariosremoto -replace '\s', ''
$usuariosconsole = $usuariosconsole.trim()
$usuariosconsole = $usuariosconsole -replace '\s', ''
if ($consolelogonui) {
	  $todosusers = $usuariosremoto.trim()  	

} else {
	if($jsonconsole) { 
	
	$todosusers = $usuariosconsole.trim()
	    if($jsonremoto) { 
		
	    $todosusers = $todosusers+','+$usuariosremoto.trim() 
    
	     }
	
    }else { $todosusers = $usuariosremoto.trim() } 
	
	
}


$json = '['+$todosusers+']'	

Write-Host ($json) 


