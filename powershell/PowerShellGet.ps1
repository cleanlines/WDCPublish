
param(
    [string]$url,
    [string]$body
)
<#
$url = 'https://wdc.maps.arcgis.com/sharing/search'
$body ='f=json|token=5vYfw6pwCvxlX_TmUkRfSh1JcNalNX7kNT8nFRGxzSvL3jBJb9HVeGXywAjFHBkxuYmqKS0tI122Pmzqyi0O3oHelzAwGuex7Ff-FGy4h3B5pCdF79i2VqDg7g9GjzoJ|q=title:"WDC_FWP_Service" AND type:"Service Definition"'
# good $body ='f=json|token=NKhdseiypnjyHW76O2cgvWxyfx71Lg0KuEYN8va7aQo7zWnK1h1gcUukxcnIT1QmQIdgFAix18ebaCGvWZ8S4KBu54f2X0WIq-h5PNa_cJrB4Px8eitxjEmq_q8V1dyP|q=title:"WDC_FWP_Service" AND type:"Service Definition"'

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

$dict = @{}
ForEach($v in $body.Split("^")){
    $b = $v.Split("=")
    $dict.Add($b[0],$b[1])
}

$AllProtocols = [System.Net.SecurityProtocolType]'Ssl3,Tls,Tls11,Tls12'
[System.Net.ServicePointManager]::SecurityProtocol = $AllProtocols
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy

$content_type = 'application/json'
$Result = Invoke-RestMethod -Uri $url -ContentType $content_type -Body $dict -Headers @{'Referer' = 'http://wdc.govt.nz'} | ConvertTo-Json
Write-Output $Result
