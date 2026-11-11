using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using System.Threading;
using System.Windows.Forms;

// Ventana del instalador: Bienvenida, Progreso y Final. Compilador de C# 5: sin
// interpolacion de cadenas, sin "?." y sin miembros con "=>".
namespace AsistenteLegal.Instalador
{
    class Ventana : Form
    {
        // Pasos que ve el usuario: el 0 lo hace el instalador (copiar el programa) y del 1
        // al 9 son los del motor (instalar.ps1). Los nombres son llanos, sin jerga.
        static readonly string[] NombresPaso = {
            "Copiar el programa", "Componentes básicos", "Preparar el programa", "Herramientas del programa",
            "Lector de documentos escaneados", "Microsoft Word", "Inteligencia artificial",
            "Archivo de causas", "Iconos de acceso", "Uso desde el celular" };
        // Cuanto pesa cada paso en la barra general (los de descarga tardan mucho mas).
        static readonly int[] PesoPaso = { 3, 2, 2, 30, 5, 2, 40, 5, 2, 3 };
        const string AyudaFinal = " Si vuelve a pasar, copie el detalle y envíeselo a quien le instaló el programa.";

        // Numeros al estilo argentino: miles con punto y decimales con coma.
        static readonly NumberFormatInfo Fmt = CrearFormato();
        static NumberFormatInfo CrearFormato()
        {
            NumberFormatInfo f = new NumberFormatInfo();
            f.NumberDecimalSeparator = ",";
            f.NumberGroupSeparator = ".";
            f.NumberGroupSizes = new int[] { 3 };
            return f;
        }

        static string Tam(long b)
        {
            if (b >= 1073741824L) return (b / 1073741824.0).ToString("0.0", Fmt) + " GB";
            if (b >= 1048576L) return Math.Round(b / 1048576.0).ToString("N0", Fmt) + " MB";
            return "menos de 1 MB";
        }

        static string Docs(int n)
        {
            return n.ToString("N0", Fmt) + (n == 1 ? " documento" : " documentos");
        }

        // "924 documentos · 1,2 GB · actualizado el 19/08/2026" (solo lo que se sabe).
        static string Resumen(Hallazgo h)
        {
            List<string> partes = new List<string>();
            if (h == null) return "";
            if (h.Documentos >= 0) partes.Add(Docs(h.Documentos));
            else if (h.Documentos == -2) partes.Add("contando documentos…");
            if (h.Tamano >= 0) partes.Add(Tam(h.Tamano));
            if (h.Fecha != DateTime.MinValue) partes.Add("actualizado el " + h.Fecha.ToString("dd/MM/yyyy"));
            return string.Join(" · ", partes.ToArray());
        }

        readonly string destino = Motor.Destino();
        bool actualizando;
        bool hayDatosInstalados;
        readonly Stopwatch cron = Stopwatch.StartNew();
        readonly System.Windows.Forms.Timer reloj = new System.Windows.Forms.Timer();
        readonly System.Windows.Forms.Timer relojCopia = new System.Windows.Forms.Timer();

        // Estado de la bienvenida
        List<Hallazgo> encontrados = new List<Hallazgo>();
        string datosElegido;
        bool sinArchivo;
        bool buscando = true;
        string errorDatos;
        bool cambiandoCombo;

        // Estado de la instalacion
        bool instalando, terminado, finRecibido, cancelando;
        int pasoActual = -1, pasoFallo;
        DateTime inicioPaso, inicioTotal;
        readonly bool[] pasoConAviso = new bool[10];
        readonly List<string> avisos = new List<string>();
        string motivoError;
        string datosUsado; bool reemplazoUsado, celularUsado;
        readonly StringBuilder registro = new StringBuilder();
        Ejecucion ejecucion;

        // Movimiento de la balanza
        bool oscilando, nivelando;
        double anguloNivel; double inicioNivel;

        Panel raiz, pBienvenida, pProgreso, pFinal;
        Encabezado enc;

        // Bienvenida
        Label lblTitulo, lblIntro, lblDatosTit, lblDatosMain, lblDatosSub, lblInstalado;
        Tarjeta tarjDatos; IconoEstado icoDatos; Boton btnOtra, btnSin, btnCancelar, btnInstalar;
        ComboBox cmbDatos; Casilla chkReemplazar, chkCelular;

        // Progreso
        Label lblTituloP, lblPaso, lblActividad, lblTiempo, lblNota;
        Tarjeta tarjPasos; IconoEstado[] iconosPaso = new IconoEstado[10]; Label[] etiquetasPaso = new Label[10];
        Barra barra; Boton lnkDetalleP; TextBox txtLogP;

        // Final
        IconoEstado icoFinal; Label lblTituloF, lblSubF, lblFallo; Tarjeta tarjAvisos; Boton lnkDetalleF;
        TextBox txtLogF; Boton btnCerrarF, btnAbrirF, btnReintentar, btnCopiar;
        readonly List<Control> filasFinal = new List<Control>();
        bool detalleVisibleP, detalleVisibleF;

        public Ventana()
        {
            actualizando = Motor.InstalacionExistente();
            hayDatosInstalados = Motor.TieneDatosInstalados();

            AutoScaleMode = AutoScaleMode.None;
            FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox = false;
            StartPosition = FormStartPosition.CenterScreen;
            Text = actualizando ? "Actualizar Asistente Legal" : "Instalar Asistente Legal";
            Font = Ui.Texto;
            BackColor = Paleta.Crema;
            ClientSize = new Size(Ui.S(760), Ui.S(520));
            try
            {
                using (Stream s = Assembly.GetExecutingAssembly().GetManifestResourceStream("icono.ico"))
                    if (s != null) Icon = new Icon(s);
            }
            catch (Exception) { }

            raiz = new Panel();
            raiz.SetBounds(0, 0, Ui.S(760), Ui.S(520));
            raiz.BackColor = Paleta.Crema;
            Controls.Add(raiz);

            enc = new Encabezado();
            enc.SetBounds(0, 0, Ui.S(760), Ui.S(95));
            raiz.Controls.Add(enc);

            ConstruirBienvenida();
            ConstruirProgreso();
            ConstruirFinal();

            reloj.Interval = 33;
            reloj.Tick += AlTic;
            relojCopia.Interval = 2000;
            relojCopia.Tick += delegate { relojCopia.Stop(); btnCopiar.Text = "Copiar el detalle"; };
            Mostrar(pBienvenida);
            AcomodarBienvenida();
        }

        protected override void OnShown(EventArgs e)
        {
            base.OnShown(e);
            if (!capturando) IniciarBusqueda();
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            if (instalando && !terminado && !cancelando && !capturando)
            {
                using (DialogoConfirmar d = new DialogoConfirmar(
                    "¿Cancelar la instalación?",
                    "La instalación todavía no terminó. Si la cancela ahora, el programa puede quedar a medias. Podrá volver a abrir este instalador cuando quiera.",
                    "Seguir instalando", "Cancelar la instalación"))
                {
                    if (d.ShowDialog(this) != DialogResult.Yes) { e.Cancel = true; return; }
                }
                cancelando = true;
                if (ejecucion != null) ejecucion.Cancelar();
            }
            base.OnFormClosing(e);
        }

        // ------------------------------------------------------------ construccion

        Label Et(Control padre, string texto, Font f, Color c)
        {
            Label l = Ui.Etiqueta(texto, f, c);
            padre.Controls.Add(l);
            return l;
        }

        Panel NuevaPantalla()
        {
            Panel p = new Panel();
            p.SetBounds(0, Ui.S(95), Ui.S(760), Ui.S(425));
            p.BackColor = Paleta.Crema;
            p.Visible = false;
            raiz.Controls.Add(p);
            return p;
        }

        void ConstruirBienvenida()
        {
            pBienvenida = NuevaPantalla();
            lblTitulo = Et(pBienvenida, actualizando ? "Actualizar Asistente Legal" : "Instalar Asistente Legal", Ui.Serif19, Paleta.Marino);
            lblIntro = Et(pBienvenida, "", Ui.Texto, Paleta.Tinta);

            tarjDatos = new Tarjeta();
            pBienvenida.Controls.Add(tarjDatos);
            tarjDatos.AccessibleName = "Su archivo de causas";
            lblDatosTit = Et(tarjDatos, "Su archivo de causas", Ui.Seminegrita, Paleta.Tinta);
            icoDatos = new IconoEstado(); tarjDatos.Controls.Add(icoDatos);
            lblDatosMain = Et(tarjDatos, "", Ui.Texto, Paleta.Tinta);
            lblDatosSub = Et(tarjDatos, "", Ui.TextoChico, Paleta.Apagado);
            btnOtra = new BotonSecundario("Elegir carpeta...");
            btnOtra.AccessibleName = "Elegir la carpeta del archivo de causas";
            btnOtra.Click += AlElegirCarpeta;
            tarjDatos.Controls.Add(btnOtra);
            btnSin = new BotonSecundario("Seguir sin el archivo");
            btnSin.Visible = false;
            btnSin.Click += AlSeguirSin;
            tarjDatos.Controls.Add(btnSin);

            cmbDatos = new ComboBox();
            cmbDatos.DropDownStyle = ComboBoxStyle.DropDownList;
            cmbDatos.DrawMode = DrawMode.OwnerDrawFixed;
            cmbDatos.ItemHeight = Ui.S(40);
            cmbDatos.FlatStyle = FlatStyle.Flat;
            cmbDatos.BackColor = Color.White;
            cmbDatos.Font = Ui.Texto;
            cmbDatos.Visible = false;
            cmbDatos.AccessibleName = "Archivo de causas encontrado";
            cmbDatos.DrawItem += AlDibujarItem;
            cmbDatos.SelectedIndexChanged += AlCambiarCombo;
            tarjDatos.Controls.Add(cmbDatos);

            lblInstalado = Et(tarjDatos, "Ya tiene un archivo de causas instalado y se va a conservar.", Ui.Texto, Paleta.Tinta);
            lblInstalado.Visible = false;
            chkReemplazar = new Casilla("Reemplazarlo por el del disco");
            chkReemplazar.Visible = false;
            tarjDatos.Controls.Add(chkReemplazar);

            chkCelular = new Casilla("Usarlo también desde el celular (pide permiso de administrador)");
            pBienvenida.Controls.Add(chkCelular);

            btnCancelar = new BotonSecundario("Cancelar");
            btnCancelar.Click += delegate { Close(); };
            btnInstalar = new BotonPrimario(actualizando ? "Actualizar" : "Instalar");
            btnInstalar.Click += AlInstalar;
            pBienvenida.Controls.Add(btnCancelar);
            pBienvenida.Controls.Add(btnInstalar);
        }

        void ConstruirProgreso()
        {
            pProgreso = NuevaPantalla();
            lblTituloP = Et(pProgreso, "Instalando...", Ui.Serif19, Paleta.Marino);
            lblPaso = Et(pProgreso, "Paso 1 de 10", Ui.Texto, Paleta.Apagado);
            lblPaso.TextAlign = ContentAlignment.TopRight;

            tarjPasos = new Tarjeta();
            tarjPasos.AccessibleName = "Pasos de la instalación";
            pProgreso.Controls.Add(tarjPasos);
            for (int i = 0; i < 10; i++)
            {
                iconosPaso[i] = new IconoEstado();
                tarjPasos.Controls.Add(iconosPaso[i]);
                etiquetasPaso[i] = Et(tarjPasos, NombresPaso[i], Ui.Texto, Paleta.Tinta);
            }
            barra = new Barra();
            pProgreso.Controls.Add(barra);
            lblActividad = Et(pProgreso, "", Ui.Texto, Paleta.Tinta);
            lblActividad.AutoEllipsis = true;
            lblActividad.AccessibleName = "Lo que se está haciendo ahora";
            lblTiempo = Et(pProgreso, "Recién empieza", Ui.TextoChico, Paleta.Apagado);

            lnkDetalleP = new BotonEnlace("Ver detalle");
            lnkDetalleP.Click += delegate { AlternarDetalleP(); };
            pProgreso.Controls.Add(lnkDetalleP);
            txtLogP = NuevoRegistro();
            pProgreso.Controls.Add(txtLogP);
            lblNota = Et(pProgreso, "Puede seguir usando la computadora mientras tanto.", Ui.TextoChico, Paleta.Apagado);
            lblNota.TextAlign = ContentAlignment.TopRight;
        }

        void ConstruirFinal()
        {
            pFinal = NuevaPantalla();
            icoFinal = new IconoEstado(); pFinal.Controls.Add(icoFinal);
            lblTituloF = Et(pFinal, "", Ui.Serif20, Paleta.Marino);
            lblSubF = Et(pFinal, "", Ui.Texto, Paleta.Tinta);
            lblFallo = Et(pFinal, "", Ui.Seminegrita, Paleta.Rojo);
            tarjAvisos = new Tarjeta();
            tarjAvisos.AccessibleName = "Resumen de la instalación";
            pFinal.Controls.Add(tarjAvisos);
            lnkDetalleF = new BotonEnlace("Ver detalle");
            lnkDetalleF.Click += delegate { AlternarDetalleF(); };
            pFinal.Controls.Add(lnkDetalleF);
            txtLogF = NuevoRegistro();
            pFinal.Controls.Add(txtLogF);
            btnCerrarF = new BotonSecundario("Cerrar");
            btnCerrarF.Click += delegate { Close(); };
            btnAbrirF = new BotonPrimario("Abrir Asistente Legal");
            btnAbrirF.Click += AlAbrir;
            btnReintentar = new BotonPrimario("Volver a intentar");
            btnReintentar.Click += AlReintentar;
            btnCopiar = new BotonSecundario("Copiar el detalle");
            btnCopiar.Click += AlCopiar;
            pFinal.Controls.Add(btnCerrarF);
            pFinal.Controls.Add(btnAbrirF);
            pFinal.Controls.Add(btnReintentar);
            pFinal.Controls.Add(btnCopiar);
        }

        TextBox NuevoRegistro()
        {
            TextBox t = new TextBox();
            t.Multiline = true;
            t.ReadOnly = true;
            t.ScrollBars = ScrollBars.Vertical;
            t.Font = Ui.Registro;
            t.BackColor = Color.White;
            t.ForeColor = Paleta.Tinta;
            t.BorderStyle = BorderStyle.FixedSingle;
            t.WordWrap = true;
            t.Visible = false;
            t.AccessibleName = "Detalle técnico de la instalación";
            return t;
        }

        // ------------------------------------------------------------ navegacion

        void Mostrar(Panel p)
        {
            pBienvenida.Visible = (p == pBienvenida);
            pProgreso.Visible = (p == pProgreso);
            pFinal.Visible = (p == pFinal);
            if (p == pBienvenida) { AcceptButton = btnInstalar; CancelButton = btnCancelar; }
            else if (p == pFinal) { AcceptButton = btnAbrirF.Visible ? btnAbrirF : btnReintentar; CancelButton = btnCerrarF; }
            else { AcceptButton = null; CancelButton = null; }
        }

        // ------------------------------------------------------------ bienvenida

        void IniciarBusqueda()
        {
            buscando = true;
            ActualizarDatos();
            reloj.Start();
            ThreadPool.QueueUserWorkItem(delegate
            {
                List<Hallazgo> r;
                try { r = Motor.Buscar(); } catch (Exception) { r = new List<Hallazgo>(); }
                try
                {
                    BeginInvoke(new Action(delegate
                    {
                        encontrados = r;
                        datosElegido = r.Count > 0 ? r[0].Ruta : null;
                        buscando = false;
                        if (!instalando) reloj.Stop();
                        ActualizarDatos();
                        if (!instalando && !capturando) btnInstalar.Focus();   // Enter instala
                        MedirEnFondo(new List<Hallazgo>(r));
                    }));
                }
                catch (Exception) { }
            });
        }

        // Cuenta documentos y tamano sin frenar la ventana. Solo se muestran los numeros.
        void MedirEnFondo(List<Hallazgo> lista)
        {
            if (lista.Count == 0) return;
            ThreadPool.QueueUserWorkItem(delegate
            {
                foreach (Hallazgo h in lista)
                {
                    try { Motor.Medir(h); } catch (Exception) { h.Documentos = -1; h.Tamano = -1; }
                    Marshal(delegate { if (!instalando && !cmbDatos.DroppedDown) ActualizarDatos(); });
                }
            });
        }

        Hallazgo Actual()
        {
            foreach (Hallazgo h in encontrados)
                if (string.Equals(h.Ruta, datosElegido, StringComparison.OrdinalIgnoreCase)) return h;
            return null;
        }

        // Pone en la tarjeta lo que corresponde segun lo encontrado.
        void ActualizarDatos()
        {
            lblIntro.Text = actualizando
                ? string.Format("Se actualizará el programa en {0}. Sus causas y su historial se conservan. Puede tardar varios minutos y necesita conexión a internet.", destino)
                : string.Format("Se instalará en {0}. La primera vez tarda entre 15 y 30 minutos y descarga unos 2 GB: necesita conexión a internet.", destino);

            Hallazgo h = Actual();
            btnSin.Visible = false;
            if (buscando)
            {
                icoDatos.Estado = Estado.EnCurso;
                lblDatosMain.Text = "Buscando su archivo de causas en los discos conectados…";
                lblDatosSub.Text = "Puede tardar unos segundos.";
                btnOtra.Text = "Elegir carpeta...";
            }
            else if (datosElegido != null)
            {
                icoDatos.Estado = Estado.Listo;
                lblDatosMain.Text = "Encontramos su archivo de causas en " + datosElegido;
                lblDatosSub.Text = Resumen(h);
                btnOtra.Text = "Elegir otra carpeta...";
                btnSin.Text = "Seguir sin el archivo";
                btnSin.Visible = true;
            }
            else if (sinArchivo)
            {
                icoDatos.Estado = Estado.Info;
                lblDatosMain.Text = "Va a seguir sin copiar un archivo de causas.";
                lblDatosSub.Text = "Podrá agregarlo después desde la pestaña Archivo.";
                btnOtra.Text = "Elegir carpeta...";
                if (encontrados.Count > 0) { btnSin.Text = "Usar el encontrado"; btnSin.Visible = true; }
            }
            else
            {
                icoDatos.Estado = Estado.Info;
                lblDatosMain.Text = "No encontramos un archivo de causas en los discos conectados.";
                lblDatosSub.Text = "Puede continuar sin el archivo y agregarlo después desde la pestaña Archivo.";
                btnOtra.Text = "Elegir carpeta...";
            }
            lblDatosSub.ForeColor = Paleta.Apagado;
            if (!string.IsNullOrEmpty(errorDatos))
            {
                lblDatosSub.Text = errorDatos;
                lblDatosSub.ForeColor = Paleta.Rojo;
            }
            lblDatosMain.AccessibleName = lblDatosMain.Text;
            lblDatosSub.AccessibleName = lblDatosSub.Text;

            cambiandoCombo = true;
            cmbDatos.Items.Clear();
            if (!buscando && encontrados.Count > 1)
            {
                int sel = -1;
                for (int i = 0; i < encontrados.Count; i++)
                {
                    string r = Resumen(encontrados[i]);
                    cmbDatos.Items.Add(encontrados[i].Ruta + (r.Length > 0 ? "   (" + r + ")" : ""));
                    if (string.Equals(encontrados[i].Ruta, datosElegido, StringComparison.OrdinalIgnoreCase)) sel = i;
                }
                cmbDatos.SelectedIndex = sel;
                cmbDatos.Visible = true;
            }
            else cmbDatos.Visible = false;
            cambiandoCombo = false;

            bool hayElegido = datosElegido != null && !buscando;
            lblInstalado.Visible = hayDatosInstalados && hayElegido;
            chkReemplazar.Visible = hayDatosInstalados && hayElegido;
            if (chkReemplazar.Visible)
            {
                string detalle = datosElegido;
                if (h != null && h.Documentos >= 0) detalle += ", " + Docs(h.Documentos);
                chkReemplazar.Text = "Reemplazarlo por el del disco (" + detalle + ")";
                chkReemplazar.Invalidate();
            }
            btnInstalar.Enabled = !buscando;
            AcomodarBienvenida();
        }

        void AcomodarBienvenida()
        {
            int ancho = Ui.S(688), x0 = Ui.S(36);
            lblTitulo.SetBounds(x0, Ui.S(12), ancho, Ui.S(38));
            lblIntro.SetBounds(x0, Ui.S(52), ancho, Ui.AltoTexto(lblIntro.Text, Ui.Texto, ancho));
            int yTarj = lblIntro.Bottom + Ui.S(12);

            int pad = Ui.S(20), anchoBtn = Ui.S(200);
            lblDatosTit.SetBounds(pad, Ui.S(12), ancho - pad * 2, Ui.S(26));
            int filaY = Ui.S(44);
            icoDatos.SetBounds(pad, filaY + Ui.S(2), Ui.S(28), Ui.S(28));
            int xt = pad + Ui.S(28) + Ui.S(14);
            int anchoT = ancho - xt - pad - anchoBtn - Ui.S(16);
            int hMain = Ui.AltoTexto(lblDatosMain.Text, Ui.Texto, anchoT);
            int hSub = Ui.AltoTexto(lblDatosSub.Text, Ui.TextoChico, anchoT);
            lblDatosMain.SetBounds(xt, filaY, anchoT, hMain);
            lblDatosSub.SetBounds(xt, filaY + hMain + Ui.S(2), anchoT, hSub);
            int izquierda = hMain + hSub + Ui.S(2);
            if (cmbDatos.Visible)
            {
                cmbDatos.SetBounds(xt, filaY + izquierda + Ui.S(8), anchoT, Ui.S(40));
                izquierda += Ui.S(8) + cmbDatos.Height;
            }
            int derecha = btnSin.Visible ? Ui.S(44) * 2 + Ui.S(8) : Ui.S(44);
            int hFila = Math.Max(Ui.S(48), Math.Max(izquierda, derecha));
            int xb = ancho - pad - anchoBtn;
            if (btnSin.Visible)
            {
                btnOtra.Colocar(xb, filaY, anchoBtn);
                btnSin.Colocar(xb, filaY + Ui.S(52), anchoBtn);
            }
            else btnOtra.Colocar(xb, filaY + (hFila - Ui.S(44)) / 2, anchoBtn);
            int y = filaY + hFila;
            if (lblInstalado.Visible)
            {
                int w = ancho - pad * 2;
                lblInstalado.SetBounds(pad, y + Ui.S(8), w, Ui.AltoTexto(lblInstalado.Text, Ui.Texto, w));
                y = lblInstalado.Bottom;
            }
            if (chkReemplazar.Visible)
            {
                int w = ancho - pad * 2;
                chkReemplazar.SetBounds(pad, y + Ui.S(2), w, chkReemplazar.AltoPara(w));
                y = chkReemplazar.Bottom;
            }
            tarjDatos.SetBounds(x0, yTarj, ancho, y + Ui.S(12) + Tarjeta.Sombra);

            // Pie: la casilla del celular a la izquierda y los botones a la derecha, en la misma fila.
            int yBot = Ui.S(425) - Ui.S(20) - Ui.S(44);
            int xInst = Ui.S(760) - Ui.S(36) - Ui.S(150);
            int xCan = xInst - Ui.S(12) - Ui.S(110);
            btnInstalar.Colocar(xInst, yBot, Ui.S(150));
            btnCancelar.Colocar(xCan, yBot, Ui.S(110));
            int wc = xCan - Ui.S(16) - x0;
            int hc = chkCelular.AltoPara(wc);
            chkCelular.SetBounds(x0, yBot + (Ui.S(44) - hc) / 2, wc, hc);
        }

        void AlDibujarItem(object o, DrawItemEventArgs e)
        {
            if (e.Index < 0) return;
            bool sel = (e.State & DrawItemState.Selected) != 0 && (e.State & DrawItemState.ComboBoxEdit) == 0;
            using (SolidBrush b = new SolidBrush(sel ? Paleta.MarinoSuave : Color.White)) e.Graphics.FillRectangle(b, e.Bounds);
            using (Pen p = new Pen(Paleta.Linea)) e.Graphics.DrawLine(p, e.Bounds.Left, e.Bounds.Bottom - 1, e.Bounds.Right, e.Bounds.Bottom - 1);
            Rectangle r = new Rectangle(e.Bounds.Left + Ui.S(10), e.Bounds.Top, e.Bounds.Width - Ui.S(14), e.Bounds.Height);
            TextRenderer.DrawText(e.Graphics, cmbDatos.Items[e.Index].ToString(), Ui.Texto, r,
                sel ? Paleta.Marino : Paleta.Tinta,
                TextFormatFlags.Left | TextFormatFlags.VerticalCenter | TextFormatFlags.EndEllipsis | TextFormatFlags.NoPrefix | TextFormatFlags.SingleLine);
        }

        void AlSeguirSin(object o, EventArgs e)
        {
            if (datosElegido != null) { sinArchivo = true; datosElegido = null; }
            else if (sinArchivo && encontrados.Count > 0) { sinArchivo = false; datosElegido = encontrados[0].Ruta; }
            errorDatos = null;
            chkReemplazar.Marcada = false;
            ActualizarDatos();
        }

        void AlElegirCarpeta(object o, EventArgs e)
        {
            using (FolderBrowserDialog d = new FolderBrowserDialog())
            {
                d.Description = "Elija la carpeta \"datos\" del Asistente Legal, o la carpeta que la contiene.";
                d.ShowNewFolderButton = false;
                if (d.ShowDialog(this) != DialogResult.OK) return;
                string datos = Motor.NormalizarDatos(d.SelectedPath);
                if (datos == null)
                {
                    errorDatos = "Esa carpeta no tiene un archivo de causas del Asistente Legal.";
                    ActualizarDatos();
                    return;
                }
                errorDatos = null;
                sinArchivo = false;
                chkReemplazar.Marcada = false;
                Hallazgo nuevo = null;
                foreach (Hallazgo h in encontrados)
                    if (string.Equals(h.Ruta, datos, StringComparison.OrdinalIgnoreCase)) nuevo = h;
                if (nuevo == null)
                {
                    DateTime f = DateTime.MinValue;
                    try { f = File.GetLastWriteTime(Motor.ArchivoClave(datos)); } catch (Exception) { }
                    nuevo = new Hallazgo(datos, f);
                    encontrados.Add(nuevo);
                    List<Hallazgo> uno = new List<Hallazgo>();
                    uno.Add(nuevo);
                    MedirEnFondo(uno);
                }
                datosElegido = datos;
                ActualizarDatos();
            }
        }

        void AlCambiarCombo(object o, EventArgs e)
        {
            if (cambiandoCombo) return;
            int i = cmbDatos.SelectedIndex;
            if (i < 0 || i >= encontrados.Count) return;
            datosElegido = encontrados[i].Ruta;
            errorDatos = null;
            sinArchivo = false;
            chkReemplazar.Marcada = false;
            Marshal(ActualizarDatos);
        }

        // ------------------------------------------------------------ instalacion

        void AlInstalar(object o, EventArgs e)
        {
            if (instalando) return;
            instalando = true;
            terminado = false; finRecibido = false; cancelando = false;
            inicioTotal = DateTime.Now;
            Text = actualizando ? "Actualizando Asistente Legal" : "Instalando Asistente Legal";
            lblTituloP.Text = actualizando ? "Actualizando..." : "Instalando...";
            lblTiempo.Text = "Recién empieza";
            Mostrar(pProgreso);
            AcomodarProgreso();
            for (int i = 0; i < 10; i++) { iconosPaso[i].Estado = Estado.Pendiente; etiquetasPaso[i].Font = Ui.Texto; }
            barra.Fijar(0);
            oscilando = SystemInformation.UIEffectsEnabled;
            nivelando = false;
            reloj.Start();
            IniciarPaso(0);

            bool celular = chkCelular.Marcada;
            string datos = datosElegido;
            bool reemplazar = chkReemplazar.Visible && chkReemplazar.Marcada;
            celularUsado = celular; datosUsado = datos; reemplazoUsado = reemplazar;
            ThreadPool.QueueUserWorkItem(delegate
            {
                string fallo = null; string detalle = null;
                try { Motor.Extraer(destino); }
                catch (Exception ex)
                {
                    detalle = ex.ToString();
                    fallo = "No se pudo copiar el programa. Si el Asistente Legal está abierto, ciérrelo y toque Volver a intentar." + AyudaFinal;
                }
                try
                {
                    BeginInvoke(new Action(delegate
                    {
                        if (cancelando) return;
                        if (fallo != null) { AgregarRegistro(detalle); Fallar(fallo); return; }
                        ArrancarMotor(celular, datos, reemplazar);
                    }));
                }
                catch (Exception) { }
            });
        }

        // "Volver a intentar": limpia todo lo de la corrida anterior y empieza de nuevo.
        void AlReintentar(object o, EventArgs e)
        {
            // Lo que quede vivo del intento anterior se corta y sus avisos se ignoran.
            if (ejecucion != null) { ejecucion.Cancelar(); ejecucion = null; }
            terminado = false; finRecibido = false; instalando = false; cancelando = false;
            avisos.Clear();
            Array.Clear(pasoConAviso, 0, pasoConAviso.Length);
            motivoError = null;
            registro.Length = 0;
            txtLogP.Clear(); txtLogF.Clear();
            pasoActual = -1; pasoFallo = 0;
            detalleVisibleP = false; txtLogP.Visible = false; tarjPasos.Visible = true;
            lnkDetalleP.Text = "Ver detalle";
            lblFallo.Text = "";
            AlInstalar(null, EventArgs.Empty);
        }

        void AlCopiar(object o, EventArgs e)
        {
            try
            {
                string t = (motivoError ?? "") + Environment.NewLine + "Paso: " + NombresPaso[Math.Max(0, Math.Min(9, pasoFallo))] +
                           Environment.NewLine + Environment.NewLine + registro.ToString();
                Clipboard.SetText(t);
                btnCopiar.Text = "Copiado";
                relojCopia.Stop(); relojCopia.Start();
            }
            catch (Exception)
            {
                btnCopiar.Text = "No se pudo copiar";
                relojCopia.Stop(); relojCopia.Start();
            }
        }

        void ArrancarMotor(bool celular, string datos, bool reemplazar)
        {
            Ejecucion esta = new Ejecucion();
            ejecucion = esta;
            // Solo cuenta lo que llega de la corrida actual (no de un intento anterior).
            esta.AlLinea = delegate(string l) { Marshal(delegate { if (ejecucion == esta) ProcesarLinea(l); }); };
            esta.AlTerminar = delegate(int codigo) { Marshal(delegate { if (ejecucion == esta) AlTerminarMotor(codigo); }); };
            try { esta.Iniciar(destino, celular, datos, reemplazar); }
            catch (Exception ex)
            {
                AgregarRegistro(ex.ToString());
                Fallar("No se pudo poner en marcha la instalación. Toque Volver a intentar." + AyudaFinal);
            }
        }

        void Marshal(Action a)
        {
            try { if (IsHandleCreated && !IsDisposed) BeginInvoke(a); } catch (Exception) { }
        }

        void AgregarRegistro(string l)
        {
            registro.AppendLine(l);
            if (registro.Length > 400000) registro.Remove(0, registro.Length - 300000);
            if (txtLogP.Visible) { txtLogP.AppendText(l + Environment.NewLine); }
            if (txtLogF.Visible) { txtLogF.AppendText(l + Environment.NewLine); }
        }

        static string Resto(string l)
        {
            int i = l.IndexOf('|');
            return i < 0 ? "" : l.Substring(i + 1).Trim();
        }

        void ProcesarLinea(string l)
        {
            AgregarRegistro(l);
            if (!l.StartsWith("@@")) return;
            string[] p = l.Substring(2).Split('|');
            switch (p[0])
            {
                case "PASO":
                    int n;
                    if (p.Length >= 2 && int.TryParse(p[1], out n)) IniciarPaso(n);
                    break;
                case "INFO":
                case "OK":
                    string t = Resto(l);
                    if (t.Length > 0) lblActividad.Text = t;
                    break;
                case "AVISO":
                    string a = Resto(l);
                    if (a.Length > 0)
                    {
                        avisos.Add(a);
                        if (pasoActual >= 0 && pasoActual < 10) pasoConAviso[pasoActual] = true;
                        lblActividad.Text = a;
                    }
                    break;
                case "ERROR":
                    motivoError = Resto(l);
                    break;
                case "FIN":
                    finRecibido = true;
                    if (p.Length >= 2 && p[1] == "ok") Terminar();
                    else
                    {
                        string porque = p.Length >= 3 ? string.Join("|", p, 2, p.Length - 2).Trim() : "";
                        Fallar(porque.Length > 0 ? porque : (motivoError ?? "La instalación se interrumpió. Toque Volver a intentar." + AyudaFinal));
                    }
                    break;
            }
        }

        void CompletarPasosHasta(int n)
        {
            for (int i = 0; i < n && i < 10; i++)
                if (iconosPaso[i].Estado == Estado.Pendiente || iconosPaso[i].Estado == Estado.EnCurso)
                    iconosPaso[i].Estado = pasoConAviso[i] ? Estado.Aviso : Estado.Listo;
        }

        void IniciarPaso(int n)
        {
            if (n < 0 || n > 9) return;
            CompletarPasosHasta(n);
            pasoActual = n;
            inicioPaso = DateTime.Now;
            iconosPaso[n].Estado = Estado.EnCurso;
            for (int i = 0; i < 10; i++) etiquetasPaso[i].Font = (i == n) ? Ui.Negrita : Ui.Texto;
            lblPaso.Text = string.Format("Paso {0} de 10", n + 1);
            lblActividad.Text = NombresPaso[n] + "...";
        }

        void AlTerminarMotor(int codigo)
        {
            if (finRecibido || cancelando || terminado) return;
            AgregarRegistro("El proceso terminó con el código " + codigo);
            Fallar((motivoError ?? "La instalación se interrumpió antes de terminar. Toque Volver a intentar.") + AyudaFinal);
        }

        void Terminar()
        {
            if (terminado) return;
            terminado = true; instalando = false;
            CompletarPasosHasta(10);
            barra.Objetivo = 1f;
            Nivelar();
            MostrarFinal(avisos.Count > 0 ? "avisos" : "ok");
        }

        void Fallar(string motivo)
        {
            if (terminado) return;
            terminado = true; instalando = false;
            motivoError = motivo;
            pasoFallo = Math.Max(0, Math.Min(9, pasoActual));
            iconosPaso[pasoFallo].Estado = Estado.Error;
            Nivelar();
            MostrarFinal("error");
        }

        void Nivelar()
        {
            if (!oscilando) { enc.Angulo = 0; return; }
            oscilando = false;
            nivelando = true;
            anguloNivel = enc.Angulo;
            inicioNivel = cron.Elapsed.TotalMilliseconds;
        }

        // ------------------------------------------------------------ reloj

        void AlTic(object o, EventArgs e)
        {
            double t = cron.Elapsed.TotalSeconds;
            IconoEstado.Fase = (float)((cron.Elapsed.TotalMilliseconds * 0.36) % 360.0);
            if (oscilando) enc.Angulo = 4.0 * Math.Sin(2.0 * Math.PI * t / 2.4);
            else if (nivelando)
            {
                double p = Math.Min(1.0, (cron.Elapsed.TotalMilliseconds - inicioNivel) / 700.0);
                double facil = 1.0 - Math.Pow(1.0 - p, 3.0);
                enc.Angulo = anguloNivel * (1.0 - facil);
                if (p >= 1.0) { nivelando = false; enc.Angulo = 0; }
            }
            if (buscando) icoDatos.Invalidate();
            if (instalando)
            {
                for (int i = 0; i < 10; i++)
                    if (iconosPaso[i].Estado == Estado.EnCurso) iconosPaso[i].Invalidate();
                if (pasoActual >= 0 && pasoActual < 10 && !capturando)
                {
                    int hecho = 0;
                    for (int i = 0; i < pasoActual; i++) hecho += PesoPaso[i];
                    double seg = (DateTime.Now - inicioPaso).TotalSeconds;
                    double w = PesoPaso[pasoActual];
                    // Sube rapido al principio del paso y despues muy despacio, sin llegar nunca al final del paso.
                    double avance = 0.80 * (1.0 - Math.Exp(-seg / (w * 5.0))) + 0.19 * (1.0 - Math.Exp(-seg / (w * 60.0)));
                    int total = 0; foreach (int x in PesoPaso) total += x;
                    barra.Objetivo = (float)((hecho + w * avance) / total);
                }
                if (!capturando) ActualizarTiempo();
            }
            barra.Avanzar();
            if (!instalando && !buscando && !nivelando && !oscilando && !capturando) reloj.Stop();
        }

        void ActualizarTiempo()
        {
            int min = (int)(DateTime.Now - inicioTotal).TotalMinutes;
            string s = min < 1 ? "Recién empieza" : (min == 1 ? "Lleva 1 minuto" : "Lleva " + min + " minutos");
            if (pasoActual == 3 || pasoActual == 6) s += " · Este paso es el más largo: puede tardar unos 10 minutos.";
            if (lblTiempo.Text != s) lblTiempo.Text = s;
        }

        // ------------------------------------------------------------ progreso

        void AcomodarProgreso()
        {
            int ancho = Ui.S(688), x0 = Ui.S(36);
            lblTituloP.SetBounds(x0, Ui.S(16), Ui.S(430), Ui.S(38));
            lblPaso.SetBounds(x0 + ancho - Ui.S(240), Ui.S(26), Ui.S(240), Ui.S(26));
            int fila = Ui.S(34), pad = Ui.S(20), col2 = Ui.S(350);
            for (int i = 0; i < 10; i++)
            {
                int c = i / 5, r = i % 5;
                int x = pad + (c == 0 ? 0 : col2 - pad), y = Ui.S(12) + r * fila;
                iconosPaso[i].SetBounds(x, y + Ui.S(4), Ui.S(24), Ui.S(24));
                etiquetasPaso[i].SetBounds(x + Ui.S(36), y + Ui.S(5), (c == 0 ? col2 - pad : ancho - col2) - Ui.S(52), Ui.S(26));
            }
            tarjPasos.SetBounds(x0, Ui.S(62), ancho, Ui.S(12) * 2 + fila * 5 - Ui.S(4) + Tarjeta.Sombra);
            txtLogP.SetBounds(x0, Ui.S(62), ancho, tarjPasos.Height - Tarjeta.Sombra);
            barra.SetBounds(x0, tarjPasos.Bottom + Ui.S(14), ancho, Ui.S(10));
            lblActividad.SetBounds(x0, barra.Bottom + Ui.S(12), ancho, Ui.S(26));
            lblTiempo.SetBounds(x0, lblActividad.Bottom + Ui.S(2), ancho, Ui.S(22));
            int yLnk = lblTiempo.Bottom + Ui.S(6);
            lnkDetalleP.Colocar(x0, yLnk, Ui.S(130));
            lblNota.SetBounds(x0 + ancho - Ui.S(420), yLnk + Ui.S(12), Ui.S(420), Ui.S(24));
        }

        void AlternarDetalleP()
        {
            detalleVisibleP = !detalleVisibleP;
            txtLogP.Visible = detalleVisibleP;
            tarjPasos.Visible = !detalleVisibleP;
            lnkDetalleP.Text = detalleVisibleP ? "Ocultar detalle" : "Ver detalle";
            if (detalleVisibleP) { txtLogP.Text = registro.ToString(); txtLogP.SelectionStart = txtLogP.TextLength; txtLogP.ScrollToCaret(); }
        }

        // ------------------------------------------------------------ final

        void MostrarFinal(string modo)
        {
            Mostrar(pFinal);
            Text = "Asistente Legal";
            detalleVisibleF = false;
            txtLogF.Visible = false;
            tarjAvisos.Visible = true;
            lnkDetalleF.Text = "Ver detalle";
            foreach (Control c in filasFinal) { tarjAvisos.Controls.Remove(c); c.Dispose(); }
            filasFinal.Clear();

            bool sinDatos = datosElegido == null && !hayDatosInstalados && datosUsado == null;
            List<KeyValuePair<Estado, string>> filas = new List<KeyValuePair<Estado, string>>();
            lblFallo.Text = "";
            if (modo == "ok")
            {
                icoFinal.Estado = Estado.Listo;
                lblTituloF.Text = "Asistente Legal está listo";
                lblTituloF.ForeColor = Paleta.Marino;
                lblSubF.Text = "Ya puede abrirlo con el icono de la balanza que quedó en el escritorio.";
                // Resumen de lo que se hizo.
                if (datosUsado != null && (!hayDatosInstalados || reemplazoUsado))
                    filas.Add(new KeyValuePair<Estado, string>(Estado.Listo, "Su archivo de causas quedó copiado desde " + datosUsado));
                else if (hayDatosInstalados)
                    filas.Add(new KeyValuePair<Estado, string>(Estado.Listo, "Se conservó su archivo de causas."));
                filas.Add(new KeyValuePair<Estado, string>(Estado.Listo, "Iconos en el escritorio y en el menú Inicio."));
                if (celularUsado)
                    filas.Add(new KeyValuePair<Estado, string>(Estado.Listo, "Celular habilitado: en el programa, Ajustes, Usar en el celular."));
            }
            else if (modo == "avisos")
            {
                icoFinal.Estado = Estado.Aviso;
                lblTituloF.Text = "Instalado con avisos";
                lblTituloF.ForeColor = Paleta.Marino;
                lblSubF.Text = "El programa quedó instalado y se puede abrir. Hay cosas para revisar:";
                int max = 5;
                for (int i = 0; i < avisos.Count && i < max; i++) filas.Add(new KeyValuePair<Estado, string>(Estado.Aviso, avisos[i]));
                if (avisos.Count > max)
                    filas.Add(new KeyValuePair<Estado, string>(Estado.Aviso, "Y " + (avisos.Count - max) + " avisos más: puede verlos en el detalle."));
            }
            else
            {
                icoFinal.Estado = Estado.Error;
                lblTituloF.Text = "No se pudo completar la instalación";
                lblTituloF.ForeColor = Paleta.Rojo;
                lblSubF.Text = motivoError ?? "La instalación se interrumpió. Toque Volver a intentar." + AyudaFinal;
                lblFallo.Text = "Falló en el paso: " + NombresPaso[Math.Max(0, Math.Min(9, pasoFallo))];
            }
            if (modo != "error" && sinDatos)
                filas.Add(new KeyValuePair<Estado, string>(Estado.Info, "Todavía no tiene un archivo de causas. Agréguelo desde la pestaña Archivo del programa."));
            lblTituloF.AccessibleName = lblTituloF.Text;

            int x0 = Ui.S(36), ancho = Ui.S(688);
            icoFinal.SetBounds(x0, Ui.S(24), Ui.S(72), Ui.S(72));
            int xt = x0 + Ui.S(72) + Ui.S(20), wt = Ui.S(760) - xt - x0;
            int hSub = Ui.AltoTexto(lblSubF.Text, Ui.Texto, wt);
            int hFallo = lblFallo.Text.Length > 0 ? Ui.S(30) : 0;
            int bloque = Ui.S(38) + Ui.S(6) + hSub + hFallo;
            int yTit = Math.Max(Ui.S(14), Ui.S(24) + (Ui.S(72) - bloque) / 2);
            lblTituloF.SetBounds(xt, yTit, wt, Ui.S(38));
            lblSubF.SetBounds(xt, yTit + Ui.S(44), wt, hSub);
            lblFallo.SetBounds(xt, lblSubF.Bottom + Ui.S(6), wt, Ui.S(26));

            int yTarj = Math.Max(Math.Max(lblSubF.Bottom, lblFallo.Text.Length > 0 ? lblFallo.Bottom : 0), icoFinal.Bottom) + Ui.S(16);
            int pad = Ui.S(20), y = Ui.S(14);
            foreach (KeyValuePair<Estado, string> f in filas)
            {
                IconoEstado ic = new IconoEstado(); ic.Estado = f.Key;
                ic.SetBounds(pad, y + Ui.S(2), Ui.S(24), Ui.S(24));
                Label l = Ui.Etiqueta(f.Value, Ui.Texto, Paleta.Tinta);
                int wl = ancho - pad * 2 - Ui.S(38);
                int hl = Ui.AltoTexto(f.Value, Ui.Texto, wl);
                l.SetBounds(pad + Ui.S(38), y + Ui.S(3), wl, hl);
                tarjAvisos.Controls.Add(ic); tarjAvisos.Controls.Add(l);
                filasFinal.Add(ic); filasFinal.Add(l);
                y += Math.Max(Ui.S(28), hl + Ui.S(6)) + Ui.S(6);
            }
            tarjAvisos.Visible = filas.Count > 0;
            tarjAvisos.SetBounds(x0, yTarj, ancho, y + Ui.S(8) + Tarjeta.Sombra);
            int yBot = Ui.S(425) - Ui.S(20) - Ui.S(44);
            txtLogF.SetBounds(x0, yTarj, ancho, Math.Max(Ui.S(100), yBot - Ui.S(14) - yTarj));

            bool error = (modo == "error");
            btnAbrirF.Visible = !error;
            btnReintentar.Visible = error;
            btnCopiar.Visible = error;
            btnCerrarF.Primario = false;
            btnCerrarF.Invalidate();
            int derecha = Ui.S(760) - Ui.S(36);
            if (error)
            {
                int xR = derecha - Ui.S(210);
                btnReintentar.Colocar(xR, yBot, Ui.S(210));
                int xC = xR - Ui.S(12) - Ui.S(190);
                btnCopiar.Colocar(xC, yBot, Ui.S(190));
                btnCerrarF.Colocar(xC - Ui.S(12) - Ui.S(110), yBot, Ui.S(110));
            }
            else
            {
                int xAbrir = derecha - Ui.S(260);
                btnAbrirF.Colocar(xAbrir, yBot, Ui.S(260));
                btnCerrarF.Colocar(xAbrir - Ui.S(12) - Ui.S(130), yBot, Ui.S(130));
            }
            btnCopiar.Text = "Copiar el detalle";
            lnkDetalleF.Visible = (modo != "ok");
            lnkDetalleF.Colocar(x0, yBot, Ui.S(120));
            AcceptButton = error ? (IButtonControl)btnReintentar : (IButtonControl)btnAbrirF;
            CancelButton = btnCerrarF;
            if (!capturando) (error ? (Control)btnReintentar : (Control)btnAbrirF).Focus();
        }

        void AlternarDetalleF()
        {
            detalleVisibleF = !detalleVisibleF;
            txtLogF.Visible = detalleVisibleF;
            tarjAvisos.Visible = !detalleVisibleF && filasFinal.Count > 0;
            lnkDetalleF.Text = detalleVisibleF ? "Ocultar detalle" : "Ver detalle";
            if (detalleVisibleF) { txtLogF.Text = registro.ToString(); txtLogF.SelectionStart = txtLogF.TextLength; txtLogF.ScrollToCaret(); }
        }

        void AlAbrir(object o, EventArgs e)
        {
            try
            {
                ProcessStartInfo psi = new ProcessStartInfo("wscript.exe", "\"" + Path.Combine(destino, "abrir.vbs") + "\"");
                psi.UseShellExecute = false;
                psi.WorkingDirectory = destino;
                Process.Start(psi);
                Close();
            }
            catch (Exception)
            {
                MessageBox.Show(this, "No se pudo abrir el programa. Búsquelo con el icono \"Asistente Legal\" del escritorio.",
                                "Asistente Legal", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        // ------------------------------------------------------------ capturas (modo /capturas)

        bool capturando;

        void Guardar(string carpeta, string nombre)
        {
            Application.DoEvents();
            Application.DoEvents();
            using (Bitmap bmp = new Bitmap(raiz.Width, raiz.Height))
            {
                raiz.DrawToBitmap(bmp, new Rectangle(Point.Empty, raiz.Size));
                bmp.Save(Path.Combine(carpeta, nombre), ImageFormat.Png);
            }
        }

        static Hallazgo Ejemplo(string ruta, int docs, long bytes, DateTime f)
        {
            Hallazgo h = new Hallazgo(ruta, f);
            h.Documentos = docs; h.Tamano = bytes;
            return h;
        }

        // Genera las 7 imagenes con datos de ejemplo (inventados), sin instalar nada.
        public void GenerarCapturas(string carpeta)
        {
            capturando = true;
            Directory.CreateDirectory(carpeta);
            Opacity = 0;
            ShowInTaskbar = false;
            Show();
            Application.DoEvents();

            // 1. Bienvenida con el archivo de causas encontrado
            buscando = false;
            hayDatosInstalados = false; actualizando = false;
            encontrados = new List<Hallazgo>();
            encontrados.Add(Ejemplo("E:\\AsistenteLegal\\datos", 924, 1288490189L, new DateTime(2026, 8, 19)));
            datosElegido = encontrados[0].Ruta;
            ActualizarDatos();
            Guardar(carpeta, "1-bienvenida-encontrado.png");

            // 2. Bienvenida sin datos
            encontrados = new List<Hallazgo>();
            datosElegido = null;
            ActualizarDatos();
            Guardar(carpeta, "2-bienvenida-sin-datos.png");

            // 3. Progreso: un paso largo en curso, un aviso, 45 %
            Mostrar(pProgreso);
            AcomodarProgreso();
            instalando = true;
            for (int i = 0; i < 10; i++) etiquetasPaso[i].Font = Ui.Texto;
            for (int i = 0; i < 3; i++) iconosPaso[i].Estado = Estado.Listo;
            iconosPaso[2].Estado = Estado.Aviso;
            iconosPaso[3].Estado = Estado.EnCurso;
            etiquetasPaso[3].Font = Ui.Negrita;
            pasoActual = 3;
            lblPaso.Text = "Paso 4 de 10";
            lblActividad.Text = "Instalando las herramientas del programa (varios minutos la primera vez).";
            lblTiempo.Text = "Lleva 7 minutos · Este paso es el más largo: puede tardar unos 10 minutos.";
            barra.Fijar(0.45f);
            IconoEstado.Fase = 40f;
            enc.Angulo = 3.2;
            Guardar(carpeta, "3-progreso.png");
            enc.Angulo = 0;
            instalando = false;

            // 4. Final correcto
            datosElegido = "E:\\AsistenteLegal\\datos";
            datosUsado = datosElegido; celularUsado = false;
            avisos.Clear();
            MostrarFinal("ok");
            Guardar(carpeta, "4-final-ok.png");

            // 5. Final con avisos
            avisos.Add("No se dio el permiso de administrador, así que el celular no quedó habilitado. Puede hacerlo después con 'Permitir el celular' del menú Inicio.");
            avisos.Add("No se encontró Word: los documentos .doc viejos no se van a poder leer.");
            datosElegido = null; datosUsado = null;
            MostrarFinal("avisos");
            Guardar(carpeta, "5-final-avisos.png");

            // 6. Error
            motivoError = "No se pudo instalar un componente que el programa necesita. Revise que la computadora tenga internet y toque Volver a intentar." + AyudaFinal;
            pasoFallo = 1;
            MostrarFinal("error");
            Guardar(carpeta, "6-error.png");

            // 7. Bienvenida con una instalacion que ya tiene archivo de causas (actualizar)
            actualizando = true; hayDatosInstalados = true;
            lblTitulo.Text = "Actualizar Asistente Legal";
            btnInstalar.Text = "Actualizar";
            Mostrar(pBienvenida);
            encontrados = new List<Hallazgo>();
            encontrados.Add(Ejemplo("E:\\AsistenteLegal\\datos", 924, 1288490189L, new DateTime(2026, 8, 19)));
            datosElegido = encontrados[0].Ruta;
            ActualizarDatos();
            Guardar(carpeta, "7-bienvenida-ya-instalado.png");

            terminado = true;
            Close();
        }
    }

    // Pregunta de confirmacion con el mismo estilo (reemplaza al MessageBox gris de Windows).
    class DialogoConfirmar : Form
    {
        public DialogoConfirmar(string titulo, string texto, string textoSi, string textoNo)
        {
            AutoScaleMode = AutoScaleMode.None;
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false; MinimizeBox = false; ShowInTaskbar = false;
            StartPosition = FormStartPosition.CenterParent;
            Text = "Asistente Legal";
            BackColor = Paleta.Crema;
            Font = Ui.Texto;
            ClientSize = new Size(Ui.S(540), Ui.S(250));

            Label t = Ui.Etiqueta(titulo, Ui.Serif19, Paleta.Marino);
            t.SetBounds(Ui.S(28), Ui.S(24), Ui.S(484), Ui.S(38));
            Label c = Ui.Etiqueta(texto, Ui.Texto, Paleta.Tinta);
            c.SetBounds(Ui.S(28), Ui.S(72), Ui.S(484), Ui.AltoTexto(texto, Ui.Texto, Ui.S(484)));
            Controls.Add(t); Controls.Add(c);

            int y = Ui.S(250) - Ui.S(24) - Ui.S(44);
            Boton si = new BotonPrimario(textoSi);
            si.DialogResult = DialogResult.No;           // seguir instalando = no cerrar
            si.Colocar(Ui.S(540) - Ui.S(28) - Ui.S(190), y, Ui.S(190));
            Boton no = new BotonSecundario(textoNo);
            no.DialogResult = DialogResult.Yes;          // cancelar la instalacion = cerrar
            no.Colocar(si.Left + Boton.Margen - Ui.S(12) - Ui.S(230), y, Ui.S(230));
            Controls.Add(si); Controls.Add(no);
            AcceptButton = si;
            CancelButton = si;
        }
    }
}
