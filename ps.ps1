# 앱 목록
$apps = @(
    "Microsoft.Microsoft3DViewer",         # 3DViewer
    "Microsoft.Copilot",       # Copilot
    "Microsoft.549981C3F5F10",    # 일반 앱
    "Microsoft.HEIFImageExtension", # HEIF 이미지 확장
    "Microsoft.M365Copilot",      # M365Copilot
    "Microsoft.OneDrive",         # OneDrive
    "Microsoft.Office.OneNote",   # OneNote
    "Microsoft.SkypeApp",         # Skype
    "Microsoft.MicrosoftSolitaireCollection", # 솔리테어
    "Microsoft.WebpImageExtension", # WebP 이미지 확장
    "Microsoft.WindowsAlarms",    # 알람
    "Microsoft.XboxApp",          # Xbox Live
    "Microsoft.XboxCompanion",    # Xbox Companion
    "Microsoft.WindowsCalculator",# 계산기
    "Microsoft.MSPaint",          # 그림판
    "Microsoft.Paint3D",          # Paint3D
    "Microsoft.BingWeather",      # 날씨
    "microsoft.windowscommunicationsapps", # 메일
    "Microsoft.ZuneMusic",        # Zune 음악
    "Microsoft.Windows.Photos",   # 사진
    "Microsoft.MicrosoftStickyNotes", # 스티커 메모
    "Microsoft.ZuneVideo",        # Zune 비디오
    "Microsoft.RemoteDesktop",    # 원격 데스크톱
    "Microsoft.WebMediaExtension",# 웹 미디어 확장
    "Microsoft.WindowsSoundRecorder", # 음성 기록기
    "Microsoft.WindowsMaps",      # 지도
    "Microsoft.WindowsCamera",    # 카메라
    "Microsoft.ScreenSketch",     # 캡쳐 도구
    "Microsoft.CapturePicker",    # 캡쳐 도구
    "Microsoft.WindowsFeedbackHub", # 피드백 허브
    "Microsoft.People",           # 사람
    "Microsoft.GetHelp",          # 도움말
    "Microsoft.GetStarted",       # 시작
    "Microsoft.YourPhone",        # Your Phone
    "Microsoft.OutlookForWindows",    # Outlook
    "Microsoft.MixedReality.Portal",
    "Microsoft.XboxGamingOverlay",
    "Microsoft.WindowsStore",
    "Microsoft.BingSearch",
    "Microsoft.Wallet",
    "Microsoft.Windows.DevHome",
    "Microsoft.Xbox.TCUI",
    "Microsoft.XboxSpeechToTextOverlay",
    "Microsoft.XboxIdentityProvider",
    "Microsoft.Paint",
    "Microsoft.RemoteDesktop",
    "Microsoft.ScreenSketch",
    "Microsoft.WebMediaExtensions",
    "Microsoft.DesktopAppInstaller"
)

# 각 앱 제거
foreach ($app in $apps) {
    Write-Host "Attempting to remove $app..."
    
    try {
        # 사용자 앱 제거
        Get-AppxPackage -Name $app | Remove-AppxPackage -ErrorAction Stop
        Write-Host "$app removed successfully."
    } catch {
        Write-Host "Failed to remove ${app}: $_"
    }

    try {
        # 시스템에 프로비저닝된 앱 제거
        Get-AppxProvisionedPackage -Online | Where-Object { $_.PackageName -like "*${app}*" } | Remove-AppxProvisionedPackage -Online -ErrorAction Stop
        Write-Host "${app} provisioned package removed successfully."
    } catch {
        Write-Host "Failed to remove provisioned package for ${app}: $_"
    }
}

$regKey = "HKCU:\Software\Policies\Microsoft\Windows\Explorer"
if (-not (Test-Path $regKey)) {
    New-Item -Path $regKey -Force
}
Set-ItemProperty -Path $regKey -Name "DisableSearchBoxSuggestions" -Value 1

taskkill /f /im OneDrive.exe

if ([Environment]::Is64BitOperatingSystem) {
    Start-Process "$env:SystemRoot\SysWOW64\OneDriveSetup.exe" -ArgumentList "/uninstall" -Wait
} else {
    Start-Process "$env:SystemRoot\System32\OneDriveSetup.exe" -ArgumentList "/uninstall" -Wait
}

# 잔여 파일 제거
Remove-Item "$env:USERPROFILE\OneDrive" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\Microsoft\OneDrive" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:PROGRAMDATA\Microsoft OneDrive" -Recurse -Force -ErrorAction SilentlyContinue

Remove-WindowsPackage -Online -PackageName Microsoft-Windows-UserExperience-Desktop-Package~31bf3856ad364e35~amd64~~10.0.19041.3758

Write-Host "All apps removal completed."
pause