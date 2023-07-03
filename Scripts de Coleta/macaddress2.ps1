Try{
$ErrorActionPreference = "Stop";
Get-WmiObject win32_networkadapter | Where {$_.Name -Match "Ethernet" 
-and $_.Name -NotMatch "Virtual|vEthernet|Hyper-V|VPN|USB|Mobile"}  | ForEach-Object { ($_.MACADDRESS);}

}
Catch{
  Write-Host "erro"
}



