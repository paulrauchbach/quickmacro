Param(
    [switch]$Clean,
    [switch]$OneDir,
    [string]$Name = "QuickMacro",
    [switch]$Slim,
    [switch]$UseUPX,
    [string]$UPXDir = "",
    [switch]$KeepSpec
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Section($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Resolve-Path (Join-Path $ScriptDir '..')
Set-Location $Root

Write-Section "Project root: $Root"

# Default Slim to true if not explicitly provided
if (-not $PSBoundParameters.ContainsKey('Slim')) { $Slim = $true }

$buildDir = Join-Path $Root 'build'
$distDir = Join-Path $Root 'dist'
$VenvDir = Join-Path $Root '.venv'
$VenvPython = Join-Path $VenvDir 'Scripts\python.exe'

# Absolute resource paths to avoid specpath-relative resolution
$assetsPath = Join-Path $Root 'assets'
$iconPath = Join-Path $assetsPath 'icon.ico'
$defaultConfigPath = Join-Path (Join-Path $Root 'src') (Join-Path 'config' 'default_config.json')

function Ensure-BuildDir {
    if (-not (Test-Path $buildDir)) { New-Item -ItemType Directory -Path $buildDir | Out-Null }
}

function Ensure-Venv {
    if (-not (Test-Path $VenvPython)) {
        Write-Section "Creating virtual environment (.venv)"
        if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 -m venv $VenvDir } else { & python -m venv $VenvDir }
    }
    else { Write-Host "Virtual environment already exists: $VenvDir" }
}

function Install-Dependencies {
    Write-Section "Installing/upgrading pip and project requirements"
    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -r (Join-Path $Root 'requirements.txt')
}

function Clean-Outputs {
    Write-Section "Cleaning build artifacts"
    $specRoot = Join-Path $Root ("$Name.spec")
    $specBuild = Join-Path $buildDir ("$Name.spec")
    if (Test-Path $distDir) { Remove-Item $distDir -Recurse -Force }
    if (Test-Path $buildDir) { Remove-Item $buildDir -Recurse -Force }
    if (Test-Path $specRoot) { Remove-Item $specRoot -Force }
    if (Test-Path $specBuild) { Remove-Item $specBuild -Force }
}

function Invoke-Build {
    Write-Section "Running PyInstaller"

    Ensure-BuildDir

    $oneFlag = if ($OneDir) { '--onedir' } else { '--onefile' }

    $args = @(
        'PyInstaller',
        '--noconfirm',
        '--clean',
        '--name', $Name,
        $oneFlag,
        '--windowed',
        '--paths', 'src',
        '--specpath', $buildDir,
        '--icon', $iconPath,
        '--add-data', ("$assetsPath;assets"),
        '--add-data', ("$defaultConfigPath;config"),
        '--hidden-import', 'config.settings',
        '--hidden-import', 'tray_manager',
        '--hidden-import', 'hotkey_manager',
        '--hidden-import', 'action_manager',
        '--hidden-import', 'gui.main_window',
        '--hidden-import', 'actions.lock_screen',
        '--hidden-import', 'actions.mute_app',
        '--hidden-import', 'actions.set_app_volume',
        '--hidden-import', 'actions.toggle_active_app_mute',
        '--hidden-import', 'actions.toggle_main_window',
        '--hidden-import', 'actions.toggle_system_mute',
        '--collect-submodules', 'comtypes',
        '--collect-submodules', 'pycaw'
    )

    if ($Slim) {
        Write-Section "Slim mode: excluding unused Qt and tkinter modules"
        $qtExcludes = @(
            'PyQt6.QAxContainer', 'PyQt6.QtBluetooth', 'PyQt6.QtDBus', 'PyQt6.QtDesigner', 'PyQt6.QtHelp',
            'PyQt6.QtMultimedia', 'PyQt6.QtMultimediaWidgets', 'PyQt6.QtNetwork', 'PyQt6.QtNfc', 'PyQt6.QtOpenGL',
            'PyQt6.QtOpenGLWidgets', 'PyQt6.QtPdf', 'PyQt6.QtPdfWidgets', 'PyQt6.QtPositioning', 'PyQt6.QtPrintSupport',
            'PyQt6.QtQml', 'PyQt6.QtQuick', 'PyQt6.QtQuick3D', 'PyQt6.QtQuickWidgets', 'PyQt6.QtRemoteObjects',
            'PyQt6.QtSensors', 'PyQt6.QtSerialPort', 'PyQt6.QtSpatialAudio', 'PyQt6.QtSql', 'PyQt6.QtStateMachine',
            'PyQt6.QtSvg', 'PyQt6.QtSvgWidgets', 'PyQt6.QtTest', 'PyQt6.QtTextToSpeech', 'PyQt6.QtWebChannel',
            'PyQt6.QtWebSockets', 'PyQt6.QtXml', 'tkinter', '_tkinter'
        )
        foreach ($m in $qtExcludes) { $args += @('--exclude-module', $m) }
    }
    else {
        $args += @('--collect-all', 'PyQt6')
    }

    if ($UseUPX -and $UPXDir -ne '') {
        Write-Section "Using UPX from $UPXDir"
        $args += @('--upx-dir', $UPXDir)
    }

    $args += 'src\\main.py'
    & $VenvPython -m @args

    if (-not $KeepSpec) {
        $specBuild = Join-Path $buildDir ("$Name.spec")
        $specRoot = Join-Path $Root ("$Name.spec")
        if (Test-Path $specBuild) { Remove-Item $specBuild -Force }
        if (Test-Path $specRoot) { Remove-Item $specRoot -Force }
    }
}

if ($Clean) { Clean-Outputs }

Ensure-Venv
Install-Dependencies
Invoke-Build

Write-Section "Build output"
$exePath = Join-Path $Root ("dist\\$Name.exe")
if (Test-Path $exePath) {
    $fi = Get-Item $exePath
    $mb = [Math]::Round($fi.Length / 1MB, 1)
    Write-Host ("Executable: {0} ({1} MB)" -f $fi.FullName, $mb) -ForegroundColor Green
}
elseif (Test-Path $distDir) {
    Get-ChildItem -Force -Recurse -File $distDir | Select-Object FullName, Length | Format-Table -AutoSize
}
else {
    Write-Host "No dist folder found." -ForegroundColor Red
}

Write-Host "`nDone." -ForegroundColor Cyan


