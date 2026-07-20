using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace TinyClipboardSync
{
    public class ClipboardMonitor : NativeWindow, IDisposable
    {
        private static readonly int WM_CLIPBOARDUPDATE = 0x031D;
        private static IntPtr HWND_MESSAGE = new IntPtr(-3);

        private Action<string> onClipboardChanged;
        private string lastClipboardContent = "";

        [DllImport("user32.dll", SetLastError = true)]
        private static extern IntPtr SetParent(IntPtr hWndChild, IntPtr hWndNewParent);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool AddClipboardFormatListener(IntPtr hwnd);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool RemoveClipboardFormatListener(IntPtr hwnd);

        public ClipboardMonitor(Action<string> callback)
        {
            onClipboardChanged = callback;

            CreateHandle(new CreateParams());
            SetParent(this.Handle, HWND_MESSAGE);

            if (!AddClipboardFormatListener(this.Handle))
            {
                throw new InvalidOperationException("Failed to add clipboard format listener");
            }
        }

        protected override void WndProc(ref Message m)
        {
            if (m.Msg == WM_CLIPBOARDUPDATE)
            {
                try
                {
                    string content = Clipboard.GetText();
                    if (content != lastClipboardContent)
                    {
                        lastClipboardContent = content;
                        if (onClipboardChanged != null)
                        {
                            onClipboardChanged(content);
                        }
                    }
                }
                catch { }
            }
            base.WndProc(ref m);
        }

        public void Dispose()
        {
            try
            {
                RemoveClipboardFormatListener(this.Handle);
                DestroyHandle();
            }
            catch { }
        }
    }
}
