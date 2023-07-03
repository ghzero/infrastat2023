Try{
$ErrorActionPreference = "Stop";
$object =  gwmi WmiMonitorID -Namespace root\wmi | ForEach-Object { -join "   [{""InstanceName"":"" "; ($_.InstanceName); -join " "","" UserFriendlyName"":"" "  ;   ($_.UserFriendlyName -notmatch 0 | foreach {[char]$_}) -join "";    -join " "","" Fabricante"":"" "  ; ($_.ManufacturerName -notmatch 0 | foreach {[char]$_}) -join ""; -join " "","" SerialNumber"":"" "  ; ($_.SerialNumberID -notmatch 0 | foreach {[char]$_}) -join "";  -join " ""}]"; }

$array = $object -join '';
$final = $array -replace '\s', ''
$final -replace '\\', '\\'
}
Catch{
  Write-Host "Nenhum"
}