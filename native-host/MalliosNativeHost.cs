using System;
using System.Diagnostics;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public static class MalliosNativeHost
{
    private static bool IsBackendAvailable()
    {
        try
        {
            using (var client = new TcpClient())
            {
                var connected = client.BeginConnect("127.0.0.1", 37491, null, null);
                return connected.AsyncWaitHandle.WaitOne(300) && client.Connected;
            }
        }
        catch
        {
            return false;
        }
    }

    private static void StartBackend()
    {
        var root = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, ".."));
        
        var pythonw = Path.Combine(root, "runtime", "python", "pythonw.exe");
        var python = Path.Combine(root, "runtime", "python", "python.exe");
        var appPy = Path.Combine(root, "backend", "app.py");
        var legacyAppExe = Path.Combine(root, "app", "app.exe");


        // Priority 1: pythonw.exe (runs silently with no console window popup)
        if (File.Exists(pythonw) && File.Exists(appPy))
        {
            var psi = new ProcessStartInfo
            {
                FileName = pythonw,
                Arguments = "\"" + appPy + "\"",
                WorkingDirectory = root,
                UseShellExecute = true,
                WindowStyle = ProcessWindowStyle.Hidden
            };
            Process.Start(psi);
            return;
        }

        // Priority 2: python.exe (fallback)
        if (File.Exists(python) && File.Exists(appPy))
        {
            var psi = new ProcessStartInfo
            {
                FileName = python,
                Arguments = "\"" + appPy + "\"",
                WorkingDirectory = root,
                UseShellExecute = true,
                WindowStyle = ProcessWindowStyle.Hidden
            };
            Process.Start(psi);
            return;
        }

        // Priority 3: app.exe
        if (File.Exists(legacyAppExe))
        {
            var psi = new ProcessStartInfo
            {
                FileName = legacyAppExe,
                WorkingDirectory = Path.GetDirectoryName(legacyAppExe),
                UseShellExecute = true,
                WindowStyle = ProcessWindowStyle.Hidden
            };
            Process.Start(psi);
            return;
        }

        throw new FileNotFoundException("Khong tim thay python runtime hoac app.exe de khoi dong backend.");
    }

    private static bool ReadMessage()
    {
        try
        {
            var stdin = Console.OpenStandardInput();
            var lengthBytes = new byte[4];
            var bytesRead = stdin.Read(lengthBytes, 0, 4);
            if (bytesRead == 0) return false;

            var length = BitConverter.ToInt32(lengthBytes, 0);
            if (length <= 0) return false;

            var buffer = new byte[length];
            var total = 0;
            while (total < length)
            {
                var chunk = stdin.Read(buffer, total, length - total);
                if (chunk <= 0) return false;
                total += chunk;
            }
            return true;
        }
        catch
        {
            return false;
        }
    }

    private static void WriteMessage(string json)
    {
        var bytes = Encoding.UTF8.GetBytes(json);
        var output = Console.OpenStandardOutput();
        output.WriteByte((byte)(bytes.Length & 0xff));
        output.WriteByte((byte)((bytes.Length >> 8) & 0xff));
        output.WriteByte((byte)((bytes.Length >> 16) & 0xff));
        output.WriteByte((byte)((bytes.Length >> 24) & 0xff));
        output.Write(bytes, 0, bytes.Length);
        output.Flush();
    }

    public static void Main()
    {
        while (true)
        {
            try
            {
                if (!ReadMessage()) break;

                if (!IsBackendAvailable())
                {
                    StartBackend();
                    // Wait briefly for server to bind to port 37491
                    for (int i = 0; i < 15; i++)
                    {
                        Thread.Sleep(200);
                        if (IsBackendAvailable()) break;
                    }
                }

                WriteMessage("{\"ok\":true}");
            }
            catch (Exception error)
            {
                var safeError = error.Message.Replace("\\", "\\\\").Replace("\"", "\\\"");
                WriteMessage("{\"ok\":false,\"error\":\"" + safeError + "\"}");
                break;
            }
        }
    }
}
