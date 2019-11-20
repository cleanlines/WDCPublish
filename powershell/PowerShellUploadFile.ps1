
<#
{'token': u'X6ZM2MyTjOReB_GXJ6C0a2ltPcBOHMTmajYmE7YVdVqEJRqNgUJG7RPa7hkp78Oj4LDtWpyXABQtX_8MHAM9okAvq3o-Y9Gxl_WA06toOv_0TFFJC47Ie402hZTY3X0a', 
'f': 'json', 
'typeKeywords': u'Data, Service, Service Definition', 
'itemType': 'file', 
'title': u'WDC_FWP_Service_Test', 
'async': 'false', 
'description': u'This item is to support the forward works plan.', 
'tags': u'WDC,FWP', 
'type': 'Service Definition', 
'filename': u'WDC_FWP_Service_Test.sd'}

u'https://wdc.maps.arcgis.com/sharing/rest/content/users/wdc_eagle/addItem'
{'file': (u'WDC_FWP_Service_Test.sd', <open file u'c:\\users\\fhand\\appdata\\local\\temp\\4\\WDC_FWP_Service_Test.sd', mode 'rb' at 0x08342E38>, 'application/octet-stream')}

title=WDC_FWP_Service_Test^type=Service Definition^filename=WDC_FWP_Service_Test.sd^tags=WDC,FWP^token=nt3Z0wwwLfSk8VwdvcK6huIa3wZ2aBtFNYzFUL1eklimIwC56t3SsbzCfRC3bcY0MtwuVMxqE0nRmo_ebOq8ONiCcj4RlWTuZPxQGewZGYsBxaBKwXhhXiZJOEQ5Crsz^itemType=file^f=json^typeKeywords=Data, Service, Service Definition^async=false^description=This item is to support the forward works plan.
#>

param(
    [string]$url,
    [string]$body,
    [string]$filePath
)


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

$ErrorActionPreference = 'Stop'
$fieldName = 'file'

<# 
$filePath = 'c:\\users\\fhand\\appdata\\local\\temp\\5\\WDC_FWP_Service_Test.sd'
$url = 'https://wdc.maps.arcgis.com/sharing/rest/content/users/wdc_eagle/addItem'
$body = 'title=WDC_FWP_Service_Test^type=Service Definition^filename=WDC_FWP_Service_Test.sd^tags=WDC,FWP^token=nt3Z0wwwLfSk8VwdvcK6huIa3wZ2aBtFNYzFUL1eklimIwC56t3SsbzCfRC3bcY0MtwuVMxqE0nRmo_ebOq8ONiCcj4RlWTuZPxQGewZGYsBxaBKwXhhXiZJOEQ5Crsz^itemType=file^f=json^typeKeywords=Data, Service, Service Definition^async=false^description=This item is to support the forward works plan.'
#>
#Write-Output $body
$dict = @{}
ForEach($v in $body.Split("^")){
    #Write-Output $v
    $b = $v.Split("=")
    $dict.Add($b[0],$b[1])
}

#Write-Output $dict
Try {
    Add-Type -AssemblyName 'System.Net.Http'
    $handler = New-Object  System.Net.Http.HttpClientHandler
    $handler.UseDefaultCredentials = $true
    $client = New-Object System.Net.Http.HttpClient($handler)
    #$client.DefaultRequestHeaders.Authorization = New-Object System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", "");
    $client.DefaultRequestHeaders.Add("Referer","http://wdc.govt.nz")
    $content = New-Object System.Net.Http.MultipartFormDataContent
    $fileStream = [System.IO.File]::OpenRead($filePath)
    $fileName = $dict['filename']#[System.IO.Path]::GetFileName($filePath)
    $fileContent = New-Object System.Net.Http.StreamContent($fileStream)
    $fileContent.Headers.ContentType = 'application/octet-stream'
    $content.Add($fileContent, $fieldName, $fileName)

    foreach($key in $dict.Keys){
         $content.Add((New-Object System.Net.Http.StringContent($dict[$key])),$key)
    }
    $task = $client.PostAsync($url, $content)
    $task.Wait()
    if ($task.IsCompleted) {
        Write-Output $task.Result.Content.ReadAsStringAsync().Result
    }
    #$result = $client.PostAsync($url, $content).Result
    #$result.EnsureSuccessStatusCode()
    #Write-Ouput $result.Content.ReadAsStringAsync()
     
}
Catch {
    $ErrorMessage = $_.Exception.Message
    Write-Output $ErrorMessage
    Write-Output "{}"
    exit 1
}
Finally {
    if ($client -ne $null) { $client.Dispose() }
    if ($content -ne $null) { $content.Dispose() }
    if ($fileStream -ne $null) { $fileStream.Dispose() }
    if ($fileContent -ne $null) { $fileContent.Dispose() }
}