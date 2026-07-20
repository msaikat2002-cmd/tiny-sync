using System;
using System.Threading;
using System.Windows.Forms;

namespace TinyClipboardSync
{
    static class Program
    {
        private static Mutex mutex;
        private static ClipboardMonitor clipboardMonitor;
        private static Timer reconnectTimer;
        private const string AppName = "TinyClipboardSync";

        [STAThread]
        static void Main()
        {
            bool createdNew;
            mutex = new Mutex(true, AppName, out createdNew);

            if (!createdNew)
            {
                return;
            }

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            NetworkClient.Initialize();
            RegistryHelper.EnableAutoStart();

            SetupClipboardMonitoring();
            SetupReconnectTimer();

            NetworkClient.Connect();

            Application.Run();
        }

        private static void SetupClipboardMonitoring()
        {
            try
            {
                clipboardMonitor = new ClipboardMonitor((content) =>
                {
                    Thread.Sleep(50);
                    NetworkClient.SendClipboard(content);
                });
            }
            catch { }
        }

        private static void SetupReconnectTimer()
        {
            reconnectTimer = new Timer();
            reconnectTimer.Interval = 5000;
            reconnectTimer.Tick += (sender, e) =>
            {
                try
                {
                    if (!NetworkClient.IsConnected())
                    {
                        NetworkClient.Connect();
                    }
                }
                catch { }
            };
            reconnectTimer.Start();
        }

        public static void ExitApplication()
        {
            try
            {
                if (reconnectTimer != null)
                {
                    reconnectTimer.Stop();
                    reconnectTimer.Dispose();
                }
                if (clipboardMonitor != null)
                {
                    clipboardMonitor.Dispose();
                }
                NetworkClient.Stop();
                if (mutex != null)
                {
                    mutex.ReleaseMutex();
                    mutex.Dispose();
                }
            }
            finally
            {
                Application.Exit();
            }
        }
    }
}
