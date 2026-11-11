using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Text;

// Lo que hace el instalador por debajo de la ventana: buscar el archivo de causas,
// descomprimir el programa y correr instalar.ps1 leyendo su avance.
// Compilador de C# 5: sin interpolacion de cadenas, sin "?." y sin miembros con "=>".
namespace AsistenteLegal.Instalador
{
    class Hallazgo
    {
        public string Ruta;
        public DateTime Fecha;
        public long Tamano = -2;      // bytes de la carpeta datos; -2 = contando, -1 = no se pudo
        public int Documentos = -2;   // documentos distintos del indice; -2 = contando, -1 = no se pudo
        public Hallazgo(string ruta, DateTime fecha) { Ruta = ruta; Fecha = fecha; }
    }

    static class Motor
    {
        public static string Destino()
        {
            return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "AsistenteLegal");
        }

        public static string ArchivoClave(string datos)
        {
            return Path.Combine(datos, Path.Combine("indice", "fragmentos.json"));
        }

        // Una carpeta de datos valida del asistente es la que tiene indice\fragmentos.json.
        public static bool EsCarpetaDatos(string ruta)
        {
            try { return !string.IsNullOrEmpty(ruta) && File.Exists(ArchivoClave(ruta)); }
            catch (Exception) { return false; }
        }

        // Acepta la carpeta "datos" o la que la contiene (por ejemplo, "AsistenteLegal").
        public static string NormalizarDatos(string elegida)
        {
            if (string.IsNullOrEmpty(elegida)) return null;
            if (EsCarpetaDatos(elegida)) return elegida.TrimEnd('\\');
            string interna = Path.Combine(elegida, "datos");
            if (EsCarpetaDatos(interna)) return interna;
            return null;
        }

        static string Normal(string ruta)
        {
            try { return Path.GetFullPath(ruta).TrimEnd('\\').ToLowerInvariant(); }
            catch (Exception) { return ruta.TrimEnd('\\').ToLowerInvariant(); }
        }

        public static bool InstalacionExistente()
        {
            return File.Exists(Path.Combine(Destino(), Path.Combine("src", "app.py")));
        }

        public static bool TieneDatosInstalados()
        {
            return EsCarpetaDatos(Path.Combine(Destino(), "datos"));
        }

        // Busca al lado del instalador y en cada disco conectado. El mas reciente primero.
        public static List<Hallazgo> Buscar()
        {
            List<string> candidatos = new List<string>();
            try
            {
                string exe = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
                if (!string.IsNullOrEmpty(exe))
                {
                    candidatos.Add(Path.Combine(exe, "datos"));
                    candidatos.Add(Path.Combine(exe, Path.Combine("AsistenteLegal", "datos")));
                }
            }
            catch (Exception) { }
            try
            {
                foreach (DriveInfo d in DriveInfo.GetDrives())
                {
                    try
                    {
                        if (!d.IsReady || d.DriveType == DriveType.CDRom) continue;
                        string raiz = d.RootDirectory.FullName;
                        candidatos.Add(Path.Combine(raiz, Path.Combine("AsistenteLegal", "datos")));
                        candidatos.Add(Path.Combine(raiz, Path.Combine("Asistente Legal", "datos")));
                        candidatos.Add(Path.Combine(raiz, "datos"));
                    }
                    catch (Exception) { }
                }
            }
            catch (Exception) { }

            string propio = Normal(Path.Combine(Destino(), "datos"));
            HashSet<string> vistos = new HashSet<string>();
            List<Hallazgo> res = new List<Hallazgo>();
            foreach (string c in candidatos)
            {
                string n = Normal(c);
                if (n == propio || !vistos.Add(n)) continue;
                if (!EsCarpetaDatos(c)) continue;
                DateTime f = DateTime.MinValue;
                try { f = File.GetLastWriteTime(ArchivoClave(c)); } catch (Exception) { }
                res.Add(new Hallazgo(c.TrimEnd('\\'), f));
            }
            res.Sort(delegate(Hallazgo a, Hallazgo b) { return b.Fecha.CompareTo(a.Fecha); });
            return res;
        }

        // Suma de bytes de todos los archivos de la carpeta (sin fallar por una subcarpeta ilegible).
        public static long TamanoCarpeta(string ruta)
        {
            long total = 0;
            Stack<string> pila = new Stack<string>();
            pila.Push(ruta);
            while (pila.Count > 0)
            {
                string d = pila.Pop();
                try
                {
                    foreach (string f in Directory.GetFiles(d))
                    {
                        try { total += new FileInfo(f).Length; } catch (Exception) { }
                    }
                    foreach (string s in Directory.GetDirectories(d)) pila.Push(s);
                }
                catch (Exception) { }
            }
            return total;
        }

        class Lector
        {
            readonly TextReader r; readonly char[] b = new char[1 << 16]; int p, n;
            public Lector(TextReader lector) { r = lector; }
            public int Sig()
            {
                if (p >= n)
                {
                    n = r.Read(b, 0, b.Length); p = 0;
                    if (n <= 0) { n = 0; return -1; }
                }
                return b[p++];
            }
        }

        // Lee una cadena JSON ya abierta (despues de la comilla), respetando los escapes.
        // Solo guarda hasta "max" caracteres: lo demas se descarta sin ocupar memoria.
        static string LeerCadena(Lector l, int max)
        {
            StringBuilder sb = new StringBuilder();
            int c;
            while ((c = l.Sig()) != -1)
            {
                if (c == '"') break;
                if (c == '\\')
                {
                    int e = l.Sig();
                    if (e == -1) break;
                    if (e == 'u') { for (int i = 0; i < 4; i++) l.Sig(); c = '?'; }
                    else if (e == 'n' || e == 't' || e == 'r') c = ' ';
                    else c = e;
                }
                if (sb.Length < max) sb.Append((char)c);
            }
            return sb.ToString();
        }

        // Cuantos documentos distintos tiene el archivo: valores distintos de "ruta" en
        // indice\fragmentos.json (igual que resumen_indice de la app). El archivo puede pesar
        // cientos de MB y estar en una sola linea: se lee por bloques. -1 si algo falla.
        public static int ContarDocumentos(string datos)
        {
            try
            {
                HashSet<string> rutas = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                using (StreamReader sr = new StreamReader(ArchivoClave(datos), Encoding.UTF8, true, 1 << 16))
                {
                    Lector l = new Lector(sr);
                    bool esperaValor = false;
                    string ultima = null;
                    int c;
                    while ((c = l.Sig()) != -1)
                    {
                        if (c == '"')
                        {
                            string s = LeerCadena(l, esperaValor ? 4096 : 8);
                            if (esperaValor) { if (s.Length > 0) rutas.Add(s); esperaValor = false; ultima = null; }
                            else ultima = s;
                        }
                        else if (c == ':') { if (ultima == "ruta") esperaValor = true; ultima = null; }
                        else if (c == ' ' || c == '\t' || c == '\r' || c == '\n') { }
                        else { ultima = null; esperaValor = false; }
                    }
                }
                return rutas.Count;
            }
            catch (Exception) { return -1; }
        }

        // Completa tamano y cantidad de documentos de un hallazgo (en un hilo de fondo).
        public static void Medir(Hallazgo h)
        {
            h.Documentos = ContarDocumentos(h.Ruta);
            try { h.Tamano = TamanoCarpeta(h.Ruta); } catch (Exception) { h.Tamano = -1; }
        }

        // Paso 0: descomprime el programa (sin tocar la carpeta datos si ya existia).
        public static void Extraer(string destino)
        {
            Directory.CreateDirectory(destino);
            string raiz = Path.GetFullPath(destino) + Path.DirectorySeparatorChar;
            using (Stream s = Assembly.GetExecutingAssembly().GetManifestResourceStream("programa.zip"))
            {
                if (s == null) throw new InvalidOperationException("Este instalador no trae el programa adentro.");
                using (ZipArchive zip = new ZipArchive(s, ZipArchiveMode.Read))
                {
                    foreach (ZipArchiveEntry e in zip.Entries)
                    {
                        string ruta = Path.GetFullPath(Path.Combine(destino, e.FullName));
                        if (!ruta.StartsWith(raiz, StringComparison.OrdinalIgnoreCase)) continue;  // proteccion zip-slip
                        if (e.FullName.EndsWith("/") || e.Name.Length == 0)
                        {
                            Directory.CreateDirectory(ruta);
                            continue;
                        }
                        Directory.CreateDirectory(Path.GetDirectoryName(ruta));
                        e.ExtractToFile(ruta, true);
                    }
                }
            }
        }
    }

    // Corre instalar.ps1 sin ventana y entrega cada linea de su salida (UTF-8).
    class Ejecucion
    {
        Process proceso;
        public Action<string> AlLinea;
        public Action<int> AlTerminar;

        public bool Activa
        {
            get { try { return proceso != null && !proceso.HasExited; } catch (Exception) { return false; } }
        }

        public void Iniciar(string destino, bool celular, string datos, bool reemplazar)
        {
            StringBuilder args = new StringBuilder();
            args.Append("-NoProfile -ExecutionPolicy Bypass -File \"" + Path.Combine(destino, "instalar.ps1") + "\" -SinInteraccion");
            if (celular) args.Append(" -Celular");
            if (!string.IsNullOrEmpty(datos)) args.Append(" -Datos \"" + datos.TrimEnd('\\') + "\"");
            if (reemplazar) args.Append(" -ReemplazarDatos");

            ProcessStartInfo psi = new ProcessStartInfo("powershell.exe", args.ToString());
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;
            psi.WorkingDirectory = destino;
            psi.RedirectStandardOutput = true;
            psi.RedirectStandardError = true;
            psi.StandardOutputEncoding = Encoding.UTF8;
            psi.StandardErrorEncoding = Encoding.UTF8;

            proceso = new Process();
            proceso.StartInfo = psi;
            proceso.EnableRaisingEvents = true;
            proceso.OutputDataReceived += delegate(object o, DataReceivedEventArgs e) { if (e.Data != null && AlLinea != null) AlLinea(e.Data); };
            proceso.ErrorDataReceived += delegate(object o, DataReceivedEventArgs e) { if (e.Data != null && AlLinea != null) AlLinea(e.Data); };
            proceso.Exited += delegate(object o, EventArgs e)
            {
                // Se espera a que se vacien las lineas pendientes antes de avisar.
                try { proceso.WaitForExit(); } catch (Exception) { }
                int codigo = -1;
                try { codigo = proceso.ExitCode; } catch (Exception) { }
                if (AlTerminar != null) AlTerminar(codigo);
            };
            proceso.Start();
            proceso.BeginOutputReadLine();
            proceso.BeginErrorReadLine();
        }

        // Corta la instalacion y todo lo que lanzo (pip, winget...).
        public void Cancelar()
        {
            try
            {
                if (proceso == null || proceso.HasExited) return;
                ProcessStartInfo psi = new ProcessStartInfo("taskkill.exe", "/PID " + proceso.Id + " /T /F");
                psi.CreateNoWindow = true;
                psi.UseShellExecute = false;
                Process t = Process.Start(psi);
                if (t != null) t.WaitForExit(5000);
            }
            catch (Exception) { }
        }
    }
}
