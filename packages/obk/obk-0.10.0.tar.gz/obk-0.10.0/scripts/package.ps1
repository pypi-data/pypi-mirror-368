<# scripts/package.ps1
    Orchestrates: build/vendor organization + offline helpers -> zip.
    Passes -IncludeLinuxWheels through to build-and-vendor.ps1.
#>

[CmdletBinding()]
param(
  [string] $Ref = "",
  [string] $ZipName = "",
  [string] $RuntimeRequirements = "",   # optional: requirements file to download wheels
  [switch] $IncludeLinuxWheels         # also fetch manylinux wheels when downloading
)

$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (git rev-parse --show-toplevel)

# Organize + verify + (optional) download + write helpers
$bvArgs = @("-WriteOfflineScripts")
if ($RuntimeRequirements) { $bvArgs += @("-RuntimeRequirements", $RuntimeRequirements) }
if ($IncludeLinuxWheels)  { $bvArgs += "-IncludeLinuxWheels" }

pwsh -File "$here/build-and-vendor.ps1" @bvArgs

# Zip (reuse your existing make-zip.ps1)
$zipArgs = @()
if ($Ref)     { $zipArgs += @("-Ref", $Ref) }
if ($ZipName) { $zipArgs += @("-ZipName", $ZipName) }
pwsh -File "$here/make-zip.ps1" @zipArgs
