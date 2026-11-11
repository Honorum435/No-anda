using System;
using System.IO;
using System.Windows.Forms;

// Instalador del Asistente Legal: ventana grafica con la identidad de la app.
// Uso normal: doble clic.  Modo de prueba visual:  Instalar.exe /capturas <carpeta>
// (guarda 6 imagenes de las pantallas con datos de ejemplo y sale, sin instalar nada).
namespace AsistenteLegal.Instalador
{
    static class Programa
    {
        [STAThread]
        static int Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            try
            {
                if (args.Length >= 2 && args[0].Equals("/capturas", StringComparison.OrdinalIgnoreCase))
                {
                    using (Ventana v = new Ventana()) v.GenerarCapturas(args[1]);
                    return 0;
                }
                Application.Run(new Ventana());
                return 0;
            }
            catch (Exception ex)
            {
                if (args.Length >= 2 && args[0].Equals("/capturas", StringComparison.OrdinalIgnoreCase))
                {
                    try { File.WriteAllText(Path.Combine(args[1], "error.txt"), ex.ToString()); } catch (Exception) { }
                    return 1;
                }
                MessageBox.Show("No se pudo abrir el instalador.\n\n" + ex.Message,
                                "Asistente Legal", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return 1;
            }
        }
    }
}
