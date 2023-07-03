Try{
$ErrorActionPreference = "Stop";
Get-wmiobject -Namespace "root/SecurityCenter2" -Class "AntivirusProduct" | ForEach-Object {($_.displayName); ($_.productState); -join "-----------------";}


}
Catch{
  Write-Host "erro"
}