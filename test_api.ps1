$headers = @{
    "Content-Type" = "application/json"
}

$registerBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

$loginBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

Write-Host "Testing user registration..."
try {
    $registerResponse = Invoke-RestMethod -Uri "https://mmdb-f1b3.onrender.com/api/auth/register" -Method POST -Headers $headers -Body $registerBody
    Write-Host "Registration successful:" $registerResponse
} catch {
    Write-Host "Registration failed:" $_.Exception.Message
}

Write-Host "`nTesting user login..."
try {
    $loginResponse = Invoke-RestMethod -Uri "https://mmdb-f1b3.onrender.com/api/auth/login" -Method POST -Headers $headers -Body $loginBody
    Write-Host "Login successful"
    $token = $loginResponse.access_token
    Write-Host "Token: $token"
    
    # Test protected API with token
    $authHeaders = @{
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $token"
    }
    
    Write-Host "`nTesting protected API - get likes..."
    $likesResponse = Invoke-RestMethod -Uri "https://mmdb-f1b3.onrender.com/api/user/likes" -Method GET -Headers $authHeaders
    Write-Host "Likes response:" $likesResponse
    
} catch {
    Write-Host "Login failed:" $_.Exception.Message
}
