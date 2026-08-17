using System;
using System.Diagnostics;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public static class MalliosNativeHost
{
    private static bool IsBackendAvailable(int timeoutMs = 300)
    {
        try
        {
            using (var client = new TcpClient())
            {
                var connected = client.BeginConnect("127.0.0.1", 37491, null, null);
                return connected.AsyncWaitHandle.WaitOne(timeoutMs) && client.Connected;
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
        var appPy = Path.Combine(root, "backend", "app.py");

        if (File.Exists(appPy))
        {
            var candidates = new[]
            {
                Path.Combine(root, "runtime", "python", "pythonw.exe"),
                Path.Combine(root, ".venv", "Scripts", "pythonw.exe"),
                Path.Combine(root, "runtime", "python", "python.exe"),
                Path.Combine(root, ".venv", "Scripts", "python.exe"),
                "pythonw.exe",
                "python.exe"
            };

            foreach (var py in candidates)
            {
                if (py.Contains(Path.DirectorySeparatorChar.ToString()) && !File.Exists(py))
                    continue;

                try
                {
                    var psi = new ProcessStartInfo
                    {
                        FileName = py,
                        Arguments = "\"" + appPy + "\"",
                        WorkingDirectory = root,
                        UseShellExecute = true,
                        WindowStyle = ProcessWindowStyle.Hidden
                    };
                    Process.Start(psi);
                    return;
                }
                catch
                {
                    // Thu candidate tiep theo
                }
            }
        }

        var legacyAppExe = Path.Combine(root, "app", "app.exe");
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

                if (!IsBackendAvailable(200))
                {
                    bool createdNew;
                    using (var mutex = new Mutex(false, "Local\\MalliosBackendStartMutex", out createdNew))
                    {
                        var hasHandle = false;
                        try
                        {
                            try
                            {
                                hasHandle = mutex.WaitOne(4000, false);
                            }
                            catch (AbandonedMutexException)
                            {
                                hasHandle = true;
                            }

                            if (!IsBackendAvailable(200))
                            {
                                StartBackend();
                            }
                        }
                        finally
                        {
                            if (hasHandle)
                            {
                                try { mutex.ReleaseMutex(); } catch { }
                            }
                        }
                    }

                    // Cho toi da 6 giay (30 x 200ms) de server Flask bind vao port 37491
                    for (int i = 0; i < 30; i++)
                    {
                        Thread.Sleep(200);
                        if (IsBackendAvailable(300)) break;
                    }
                }

                var isReady = IsBackendAvailable(300);
                WriteMessage("{\"ok\":" + (isReady ? "true" : "false") + ",\"status\":\"" + (isReady ? "online" : "starting") + "\"}");
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
