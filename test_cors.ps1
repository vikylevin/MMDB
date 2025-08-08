# Test CORS preflight request
$headers = @{
    "Origin" = "https://mmdb-web.onrender.com"
    "Access-Control-Request-Method" = "GET"
    "Access-Control-Request-Headers" = "authorization"
}

Write-Host "Testing CORS preflight request..."
try {
    $response = Invoke-WebRequest -Uri "https://mmdb-f1b3.onrender.com/api/user/likes" -Method OPTIONS -Headers $headers -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)"
    Write-Host "Headers:"
    foreach ($header in $response.Headers.GetEnumerator()) {
        Write-Host "  $($header.Key): $($header.Value)"
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}

# Test actual authenticated request
Write-Host "`nTesting authenticated request..."
$loginHeaders = @{
    "Content-Type" = "application/json"
}

$loginBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "https://mmdb-f1b3.onrender.com/api/auth/login" -Method POST -Headers $loginHeaders -Body $loginBody
    $token = $loginResponse.access_token
    
    $authHeaders = @{
        "Authorization" = "Bearer $token"
        "Origin" = "https://mmdb-web.onrender.com"
    }
    
    $likesResponse = Invoke-WebRequest -Uri "https://mmdb-f1b3.onrender.com/api/user/likes" -Method GET -Headers $authHeaders -UseBasicParsing
    Write-Host "Likes request successful: $($likesResponse.StatusCode)"
    Write-Host "Response headers:"
    foreach ($header in $likesResponse.Headers.GetEnumerator()) {
        if ($header.Key -like "*cors*" -or $header.Key -like "*origin*") {
            Write-Host "  $($header.Key): $($header.Value)"
        }
    }
} catch {
    Write-Host "Auth request failed: $($_.Exception.Message)"
}
