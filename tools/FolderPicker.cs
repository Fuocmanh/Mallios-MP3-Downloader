using System;
using System.IO;
using System.Drawing;
using System.Windows.Forms;
using System.Runtime.InteropServices;

namespace Mallios
{
    class Program
    {
        [DllImport("shell32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern int SHCreateItemFromParsingName(
            [MarshalAs(UnmanagedType.LPWStr)] string pszPath,
            IntPtr pbc,
            ref Guid riid,
            [MarshalAs(UnmanagedType.Interface)] out IShellItem ppv);

        [DllImport("user32.dll")]
        private static extern bool SetForegroundWindow(IntPtr hWnd);

        [ComImport]
        [Guid("DC1C5A9C-E88A-4dde-A5A1-60F82A20AEF7")]
        [ClassInterface(ClassInterfaceType.None)]
        private class FileOpenDialogRCW { }

        [ComImport]
        [Guid("42f85136-db7e-439c-85f1-e4075d135fc8")]
        [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        private interface IFileDialog
        {
            [PreserveSig] int Show(IntPtr parent);
            void SetFileTypes(uint cFileTypes, IntPtr rgFilterSpec);
            void SetFileTypeIndex(uint iFileType);
            void GetFileTypeIndex(out uint piFileType);
            void Advise(IntPtr pfde, out uint pdwCookie);
            void Unadvise(uint dwCookie);
            void SetOptions(uint fos);
            void GetOptions(out uint pfos);
            void SetDefaultFolder(IShellItem psi);
            void SetFolder(IShellItem psi);
            void GetFolder(out IShellItem ppsi);
            void GetCurrentSelection(out IShellItem ppsi);
            void SetFileName([MarshalAs(UnmanagedType.LPWStr)] string pszName);
            void GetFileName([MarshalAs(UnmanagedType.LPWStr)] out string pszName);
            void SetTitle([MarshalAs(UnmanagedType.LPWStr)] string pszTitle);
            void SetOkButtonLabel([MarshalAs(UnmanagedType.LPWStr)] string pszText);
            void SetFileNameLabel([MarshalAs(UnmanagedType.LPWStr)] string pszLabel);
            void GetResult(out IShellItem ppsi);
            void AddPlace(IShellItem psi, int fdap);
            void SetDefaultExtension([MarshalAs(UnmanagedType.LPWStr)] string pszDefaultExtension);
            void Close(int hr);
            void SetClientGuid(ref Guid guid);
            void ClearClientData();
            void SetFilter(IntPtr pFilter);
        }

        [ComImport]
        [Guid("43826D1E-E718-42EE-BC55-A1E261C37BFE")]
        [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        private interface IShellItem
        {
            void BindToHandler(IntPtr pbc, ref Guid bhid, ref Guid riid, out IntPtr ppv);
            void GetParent(out IShellItem ppsi);
            void GetDisplayName(uint sigdnName, [MarshalAs(UnmanagedType.LPWStr)] out string ppszName);
            void GetAttributes(uint sfgaoMask, out uint psfgaoAttribs);
            void Compare(IShellItem psi, uint hint, out int piOrder);
        }

        [STAThread]
        static int Main(string[] args)
        {
            try { Console.OutputEncoding = System.Text.Encoding.UTF8; } catch {}
            string title = args.Length > 0 ? args[0] : "Chọn thư mục lưu nhạc MP3";
            string initialDir = args.Length > 1 ? args[1] : "";

            try
            {
                Application.EnableVisualStyles();
                Application.SetCompatibleTextRenderingDefault(false);

                var dialog = (IFileDialog)new FileOpenDialogRCW();
                // FOS_PICKFOLDERS (0x20) | FOS_FORCEFILESYSTEM (0x40) | FOS_NOCHANGEDIR (0x8)
                dialog.SetOptions(0x00000020 | 0x00000040 | 0x00000008);
                if (!string.IsNullOrEmpty(title))
                    dialog.SetTitle(title);

                if (!string.IsNullOrEmpty(initialDir) && Directory.Exists(initialDir))
                {
                    var iid = new Guid("43826D1E-E718-42EE-BC55-A1E261C37BFE");
                    IShellItem folderItem;
                    if (SHCreateItemFromParsingName(initialDir, IntPtr.Zero, ref iid, out folderItem) == 0 && folderItem != null)
                    {
                        dialog.SetFolder(folderItem);
                    }
                }

                // Cua so an dung giua man hinh chinh de dialog hien dung giua man hinh va TopMost
                using (var ownerForm = new Form())
                {
                    ownerForm.StartPosition = FormStartPosition.CenterScreen;
                    ownerForm.Size = new Size(1, 1);
                    ownerForm.Opacity = 0;
                    ownerForm.ShowInTaskbar = false;
                    ownerForm.TopMost = true;
                    ownerForm.Show();
                    ownerForm.BringToFront();
                    ownerForm.Activate();
                    SetForegroundWindow(ownerForm.Handle);

                    int hr = dialog.Show(ownerForm.Handle);
                    ownerForm.Close();

                    if (hr == 0) // S_OK
                    {
                        IShellItem resultItem;
                        dialog.GetResult(out resultItem);
                        if (resultItem != null)
                        {
                            string path;
                            resultItem.GetDisplayName(0x80058000 /* SIGDN_FILESYSPATH */, out path);
                            if (!string.IsNullOrEmpty(path))
                            {
                                WriteOutput(path);
                                return 0;
                            }
                        }
                    }
                    else if (hr == unchecked((int)0x800704C7)) // HRESULT for ERROR_CANCELLED (User clicked Cancel)
                    {
                        return 2; // Nguoi dung bam huy
                    }
                }
                return 1;
            }
            catch (Exception ex)
            {
                // Fallback qua FolderBrowserDialog neu IFileDialog gap su co
                try
                {
                    using (var fbd = new FolderBrowserDialog())
                    {
                        fbd.Description = title;
                        fbd.ShowNewFolderButton = true;
                        if (!string.IsNullOrEmpty(initialDir) && Directory.Exists(initialDir))
                        {
                            fbd.SelectedPath = initialDir;
                        }
                        using (var ownerForm = new Form())
                        {
                            ownerForm.StartPosition = FormStartPosition.CenterScreen;
                            ownerForm.Size = new Size(1, 1);
                            ownerForm.Opacity = 0;
                            ownerForm.ShowInTaskbar = false;
                            ownerForm.TopMost = true;
                            ownerForm.Show();
                            ownerForm.BringToFront();
                            ownerForm.Activate();
                            SetForegroundWindow(ownerForm.Handle);

                            if (fbd.ShowDialog(ownerForm) == DialogResult.OK && !string.IsNullOrEmpty(fbd.SelectedPath))
                            {
                                WriteOutput(fbd.SelectedPath);
                                return 0;
                            }
                        }
                    }
                    return 2;
                }
                catch (Exception fallbackEx)
                {
                    try { Console.Error.WriteLine("Error: " + ex.Message + " | Fallback: " + fallbackEx.Message); } catch {}
                    return 1;
                }
            }
        }

        static void WriteOutput(string text)
        {
            try
            {
                using (var stdout = new StreamWriter(Console.OpenStandardOutput(), new System.Text.UTF8Encoding(false)))
                {
                    stdout.WriteLine(text);
                    stdout.Flush();
                }
            }
            catch
            {
                try { Console.WriteLine(text); } catch {}
            }
        }
    }
}
