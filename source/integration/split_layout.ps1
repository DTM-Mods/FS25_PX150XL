Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type @"
using System;using System.Runtime.InteropServices;public class SplitPX{[DllImport("user32.dll")]public static extern bool MoveWindow(IntPtr h,int x,int y,int w,int z,bool r);[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int n);[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);[DllImport("user32.dll")]public static extern bool SetProcessDPIAware();}
"@
[void][SplitPX]::SetProcessDPIAware();$a=[System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea;$half=[int]($a.Width/2)
$ge=Get-Process -Id 3284
[void][SplitPX]::ShowWindow($ge.MainWindowHandle,9);[void][SplitPX]::MoveWindow($ge.MainWindowHandle,0,0,$half,$a.Height,$true)
[void][SplitPX]::ShowWindow([IntPtr]131568,9);[void][SplitPX]::MoveWindow([IntPtr]131568,$half,0,$a.Width-$half,$a.Height,$true)
[void][SplitPX]::SetForegroundWindow($ge.MainWindowHandle);Start-Sleep 1
$b=New-Object System.Drawing.Bitmap $a.Width,$a.Height;$g=[System.Drawing.Graphics]::FromImage($b);$g.CopyFromScreen(0,0,0,0,$b.Size);$b.Save((Join-Path $pwd 'source/integration/split_screen.png'));$g.Dispose();$b.Dispose()
Write-Output ('GE_HANDLE='+$ge.MainWindowHandle+' HALF='+$half+' HEIGHT='+$a.Height)
