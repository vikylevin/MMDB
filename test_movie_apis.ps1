$headers = @{
    "Content-Type" = "application/json"
}

$loginBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

# Login to get token
$loginResponse = Invoke-RestMethod -Uri "https://mmdb-f1b3.onrender.com/api/auth/login" -Method POST -Headers $headers -Body $loginBody
$token = $loginResponse.access_token

$authHeaders = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $token"
}

Write-Host "Token obtained: $($token.Substring(0, 50))..."

# Test rating a movie
Write-Host "`nTesting movie rating..."
$ratingBody = @{
    rating = 5
} | ConvertTo-Json

try {
    $ratingResponse = Invoke-RestMethod -Uri "https://mmdb-f1b3.onrender.com/api/movie/550/rate" -Method POST -Headers $authHeaders -Body $ratingBody
    Write-Host "Rating successful:" $ratingResponse
} catch {
    Write-Host "Rating failed:" $_.Exception.Message
    Write-Host "Response:" $_.Exception.Response.StatusCode
}

# Test toggling like
Write-Host "`nTesting toggle like..."
$likeBody = @{
    movie_id = 550
} | ConvertTo-Json

try {
    $likeResponse = Invoke-RestMethod -Uri "https://mmdb-f1b3.onrender.com/api/user/likes" -Method POST -Headers $authHeaders -Body $likeBody
    Write-Host "Like toggle successful:" $likeResponse
} catch {
    Write-Host "Like toggle failed:" $_.Exception.Message
}

# Test toggling watched
Write-Host "`nTesting toggle watched..."
$watchedBody = @{
    movie_id = 550
} | ConvertTo-Json

try {
    $watchedResponse = Invoke-RestMethod -Uri "https://mmdb-f1b3.onrender.com/api/user/watched" -Method POST -Headers $authHeaders -Body $watchedBody
    Write-Host "Watched toggle successful:" $watchedResponse
} catch {
    Write-Host "Watched toggle failed:" $_.Exception.Message
}
