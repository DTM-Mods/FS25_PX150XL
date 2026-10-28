. 'C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/Library/_FS25Knowledge/tools/ge10/ui.ps1'
Add-Type @"
using System;using System.Runtime.InteropServices;
public class FocusHD {
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h,IntPtr p);
[DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
[DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a,uint b,bool c);
[DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
}
"@
$p=Get-Process editor | Select-Object -First 1
$h=$p.MainWindowHandle
$a=[FocusHD]::GetCurrentThreadId(); $b=[FocusHD]::GetWindowThreadProcessId([U]::GetForegroundWindow(),[IntPtr]::Zero)
[void][FocusHD]::AttachThreadInput($a,$b,$true)
[void][U]::ShowWindow($h,5);[void][U]::ShowWindow($h,3)
[void][FocusHD]::BringWindowToTop($h);[void][U]::SetForegroundWindow($h)
[void][FocusHD]::AttachThreadInput($a,$b,$false)
Start-Sleep 2
Foreground-Title
Assert-Editor
Click 1000 1320; Send '^a'; Paste ('source("'+($pwd.Path.Replace('\','/'))+'/previews/hd50f_adapter_v1/before.lua")'); Send '+{ENTER}'
Start-Sleep 3
& 'C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/Library/_FS25Knowledge/tools/ge10/mockup/cap.ps1' (Join-Path $pwd 'previews/hd50f_adapter_v1/before.png')
