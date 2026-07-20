using System;
using Microsoft.Win32;

namespace TinyClipboardSync
{
    public class RegistryHelper
    {
        private static readonly string RunKey = @"SOFTWARE\Microsoft\Windows\CurrentVersion\Run";
        private static readonly string AppName = "TinyClipboardSync";
        private static readonly string ExecutablePath = System.Windows.Forms.Application.ExecutablePath;

        public static bool IsAutoStartEnabled()
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.OpenSubKey(RunKey, false))
                {
                    if (key != null)
                    {
                        object value = key.GetValue(AppName);
                        return value != null && value.ToString() == ExecutablePath;
                    }
                }
            }
            catch { }
            return false;
        }

        public static void EnableAutoStart()
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.CreateSubKey(RunKey))
                {
                    if (key != null)
                    {
                        key.SetValue(AppName, ExecutablePath);
                    }
                }
            }
            catch { }
        }

        public static void DisableAutoStart()
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.OpenSubKey(RunKey, true))
                {
                    if (key != null)
                    {
                        key.DeleteValue(AppName, false);
                    }
                }
            }
            catch { }
        }
    }
}
