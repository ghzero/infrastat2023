 Try{
 $ErrorActionPreference = "Stop";
 $soft32 = 0
 $soft64 = 0 
 $soft32 = (gci "hklm:\software\microsoft\windows\currentversion\uninstall" | foreach {if ($($_.GetValue("Displayname") -notmatch "Update" -and $($_.GetValue("Displayname") -notmatch "plug-in" ) -and $($_.GetValue("Displayname") -notmatch "plugin" ) -and $($_.GetValue("Displayname") -notmatch "atualizacao" ) -and $($_.GetValue("Displayname") -notmatch "redistributable" ) -and $($_.GetValue("Displayname") -notmatch "idioma" ) -and $($_.GetValue("Displayname") -notmatch "pack" ) -and $($_.GetValue("Displayname") -notmatch "library" )  -and $($_.GetValue("Displayname") -notmatch "runtime" ) -and $($_.GetValue("InstallSource") -notmatch "programdata\\coreldraw" ) -and $($_.GetValue("InstallSource") -notmatch "C:\\ProgramData\\Microsoft\\VisualStudio\\Packages" ) -and $($_.GetValue("InstallSource") -notmatch "MSOCache" ) -and $($_.GetValue("InstallSource") -notmatch "ProgramData\\Package" ) -and $($_.GetValue("InstallLocation") -notmatch "Common" ) -and ![string]::IsNullOrEmpty($($_.GetValue("Displayname")))  )  -and ![string]::IsNullOrEmpty($($_.GetValue("UninstallString")))    ) {   "{""Displayname"":""$($_.GetValue("Displayname"))"",""Displayversion"":""$($_.GetValue("Displayversion"))"",""Publisher"":""$($_.GetValue("Publisher"))"" ,""InstallDate"":""$($_.GetValue("InstallDate"))""}," } }).Trim() -ne ""
 $soft64 = (gci "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"| foreach {if ($($_.GetValue("Displayname") -notmatch "Update" -and $($_.GetValue("Displayname") -notmatch "plug-in" ) -and $($_.GetValue("Displayname") -notmatch "plugin" ) -and $($_.GetValue("Displayname") -notmatch "atualizacao" ) -and $($_.GetValue("Displayname") -notmatch "redistributable" ) -and $($_.GetValue("Displayname") -notmatch "idioma" ) -and $($_.GetValue("Displayname") -notmatch "pack" ) -and $($_.GetValue("Displayname") -notmatch "library" )  -and $($_.GetValue("UninstallString") -notmatch "ProgramData\\Package" )  -and $($_.GetValue("Displayname") -notmatch "Microsoft_V" ) -and $($_.GetValue("InstallSource") -notmatch "MSOCache" ) -and $($_.GetValue("InstallSource") -notmatch "ProgramData\\Package" )  -and $($_.GetValue("InstallSource") -notmatch "C:\\ProgramData\\Microsoft" ) -and ![string]::IsNullOrEmpty($($_.GetValue("Displayname")))) -and ![string]::IsNullOrEmpty($($_.GetValue("UninstallString"))) ) {    "{""Displayname"":""$($_.GetValue("Displayname"))"",""Displayversion"":""$($_.GetValue("Displayversion"))"",""Publisher"":""$($_.GetValue("Publisher"))"" ,""InstallDate"":""$($_.GetValue("InstallDate"))""}," } }).Trim() -ne ""

$quantidade = $soft32.count + $soft64.count
$todos = $soft32 + $soft64 | sort-object

function Remove-StringLatinCharacters
{
    PARAM ([string]$String)
    [Text.Encoding]::ASCII.GetString([Text.Encoding]::GetEncoding("Cyrillic").GetBytes($String))
}

$json = "[$todos]"

$nice = $json -replace ' ', '#'
$json = $nice -replace '\s', ''
$ota = $json -replace '#', ' ' 

$ota | % { Remove-StringLatinCharacters $_ }


}
Catch{
  Write-Host "erro"
}
 
 


