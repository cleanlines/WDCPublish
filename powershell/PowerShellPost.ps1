
param(
    [string]$url,
    [string]$body
)
<#
debug

$url = "https://wdc.maps.arcgis.com/sharing/generateToken?f=json"
$body = "request=gettoken&Referer=http://wdc.govt.nz&username=wdc_eagle&password=A5xg8k01"
#>

add-type @"
using System.Net;
using System.Security.Cryptography.X509Certificates;
public class TrustAllCertsPolicy : ICertificatePolicy {
    public bool CheckValidationResult(
        ServicePoint srvPoint, X509Certificate certificate,
        WebRequest request, int certificateProblem) {
        return true;
    }
}
"@
$AllProtocols = [System.Net.SecurityProtocolType]'Ssl3,Tls,Tls11,Tls12'
[System.Net.ServicePointManager]::SecurityProtocol = $AllProtocols
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy

$json = ConvertTo-Json -InputObject $payload
$content_type = 'application/x-www-form-urlencoded'
$Result = Invoke-RestMethod -Uri $url -Method Post -Headers @{'Referer' = 'http://wdc.govt.nz'} -ContentType $content_type -Body $body | ConvertTo-Json
#$resObj = ConvertFrom-Json -InputObject $Result
#Write-Output $resObj
Write-Output $Result
<#Write-Output "Result is"


Write-Output "--------------------------"

if($Result.Contains("token")){
    
}else{
    Write-Output ""
}
#>