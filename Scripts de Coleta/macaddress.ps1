Try{
$ErrorActionPreference = "Stop";
Get-WmiObject win32_networkadapterconfiguration | Where{$_.DefaultIPGateway -Match "150.162.177.254"} | ForEach-Object { ($_.macaddress);}


}
Catch{
  Write-Host "erro"
}
