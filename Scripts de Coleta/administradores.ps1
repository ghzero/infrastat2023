Try{
$ErrorActionPreference = "Stop";
$contador = 0
$object = Get-LocalGroupMember administradores | ForEach-Object { -join "{""Tipo"":"" "; ($_.ObjectClass); -join " "","" Name"":"" "  ; ($_.Name) -join "";  -join " ""},"; $contador++; }

$quantidade = $object.count

function Remove-StringLatinCharacters
{
    PARAM ([string]$String)
    [Text.Encoding]::ASCII.GetString([Text.Encoding]::GetEncoding("Cyrillic").GetBytes($String))
}


$array = $object -join ''
$final = $array -replace '\s', ''
$final = $final -replace '\\', '\\'

$json = "[$final]"

$json | % { Remove-StringLatinCharacters $_ }
}
Catch{
Try{
$ErrorActionPreference = "Stop";
$contador = 0
$object = Get-LocalGroupMember administrators | ForEach-Object { -join "{""Tipo"":"" "; ($_.ObjectClass); -join " "","" Name"":"" "  ; ($_.Name) -join "";  -join " ""},"; $contador++; }

$quantidade = $object.count

function Remove-StringLatinCharacters
{
    PARAM ([string]$String)
    [Text.Encoding]::ASCII.GetString([Text.Encoding]::GetEncoding("Cyrillic").GetBytes($String))
}


$array = $object -join ''
$final = $array -replace '\s', ''
$final = $final -replace '\\', '\\'

$json = "[$final]"

$json | % { Remove-StringLatinCharacters $_ }
}
Catch{
	
	
	
  Write-Host "Erro"
}	
	
}











