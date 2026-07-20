using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace TinyClipboardSync
{
    public class NetworkClient
    {
        private static readonly string ConfigPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "TinyClipboardSync",
            "config.txt");

        private static string serverIp = "";
        private static int serverPort = 5555;
        private static TcpClient client;
        private static NetworkStream stream;
        private static bool isRunning = true;
        private static Thread receiveThread;

        public static void Initialize()
        {
            LoadConfig();
        }

        public static void LoadConfig()
        {
            try
            {
                if (File.Exists(ConfigPath))
                {
                    serverIp = File.ReadAllText(ConfigPath).Trim();
                }
            }
            catch { }
        }

        public static void SaveConfig(string ip)
        {
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(ConfigPath));
                File.WriteAllText(ConfigPath, ip.Trim());
                serverIp = ip.Trim();
            }
            catch { }
        }

        public static bool Connect()
        {
            if (string.IsNullOrEmpty(serverIp))
                return false;

            try
            {
                Disconnect();
                client = new TcpClient();
                client.ConnectTimeout = 3000;
                IAsyncResult result = client.BeginConnect(serverIp, serverPort, null, null);
                if (result.AsyncWaitHandle.WaitOne(3000))
                {
                    client.EndConnect(result);
                    stream = client.GetStream();
                    StartReceiveThread();
                    return true;
                }
                else
                {
                    client.Close();
                    return false;
                }
            }
            catch
            {
                return false;
            }
        }

        public static void Disconnect()
        {
            try
            {
                if (stream != null)
                {
                    stream.Close();
                    stream = null;
                }
                if (client != null)
                {
                    client.Close();
                    client = null;
                }
            }
            catch { }
        }

        private static void StartReceiveThread()
        {
            if (receiveThread != null && receiveThread.IsAlive)
                return;

            receiveThread = new Thread(ReceiveLoop);
            receiveThread.IsBackground = true;
            receiveThread.Start();
        }

        private static void ReceiveLoop()
        {
            byte[] buffer = new byte[65536];
            while (isRunning && client != null && client.Connected)
            {
                try
                {
                    int bytesRead = stream.Read(buffer, 0, buffer.Length);
                    if (bytesRead > 0)
                    {
                        string json = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                        ProcessMessage(json);
                    }
                }
                catch
                {
                    Thread.Sleep(1000);
                    break;
                }
            }
        }

        private static void ProcessMessage(string json)
        {
            try
            {
                json = json.Trim();
                if (json.StartsWith("{") && json.EndsWith("}"))
                {
                    int typeStart = json.IndexOf("\"type\":") + 7;
                    if (typeStart > 6)
                    {
                        int typeEnd = json.IndexOf(",", typeStart);
                        if (typeEnd == -1) typeEnd = json.IndexOf("}", typeStart);
                        string type = json.Substring(typeStart, typeEnd - typeStart).Trim().Trim('"');

                        if (type == "clipboard")
                        {
                            int contentStart = json.IndexOf("\"content\":") + 10;
                            if (contentStart > 9)
                            {
                                int contentEnd = json.LastIndexOf("\"");
                                if (contentEnd > contentStart)
                                {
                                    string content = json.Substring(contentStart, contentEnd - contentStart);
                                    content = UnescapeJson(content);
                                    SetClipboard(content);
                                }
                            }
                        }
                    }
                }
            }
            catch { }
        }

        private static string UnescapeJson(string s)
        {
            return s.Replace("\\n", "\n")
                    .Replace("\\r", "\r")
                    .Replace("\\t", "\t")
                    .Replace("\\\"", "\"")
                    .Replace("\\\\", "\\");
        }

        private static void SetClipboard(string text)
        {
            try
            {
                Clipboard.SetText(text);
            }
            catch { }
        }

        public static void SendClipboard(string text)
        {
            if (stream == null || !client.Connected)
                return;

            try
            {
                string escaped = text.Replace("\\", "\\\\")
                                     .Replace("\"", "\\\"")
                                     .Replace("\n", "\\n")
                                     .Replace("\r", "\\r")
                                     .Replace("\t", "\\t");

                string json = "{\"type\":\"clipboard\",\"content\":\"" + escaped + "\"}";
                byte[] data = Encoding.UTF8.GetBytes(json);
                stream.Write(data, 0, data.Length);
                stream.Flush();
            }
            catch { }
        }

        public static void Stop()
        {
            isRunning = false;
            Disconnect();
        }

        public static bool IsConnected()
        {
            return client != null && client.Connected && stream != null;
        }
    }
}
