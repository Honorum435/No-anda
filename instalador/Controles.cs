using System;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Text;
using System.Windows.Forms;

// Controles propios del instalador del Asistente Legal: todo se dibuja con GDI+ para que
// la ventana tenga la identidad de la app (marino, dorado, marfil) y no el gris de Windows.
// Compilador de C# 5: sin interpolacion de cadenas, sin "?." y sin miembros con "=>".
namespace AsistenteLegal.Instalador
{
    static class Paleta
    {
        public static readonly Color Marino = ColorTranslator.FromHtml("#1E3A8A");
        public static readonly Color MarinoHover = ColorTranslator.FromHtml("#172F72");
        public static readonly Color MarinoPresionado = ColorTranslator.FromHtml("#11265C");
        public static readonly Color MarinoSuave = ColorTranslator.FromHtml("#E9EEF9");
        public static readonly Color MarinoLinea = ColorTranslator.FromHtml("#C9D5EE");
        public static readonly Color Crema = ColorTranslator.FromHtml("#FAF8F3");
        public static readonly Color DoradoPunto = ColorTranslator.FromHtml("#D08A2E");
        public static readonly Color Dorado = ColorTranslator.FromHtml("#B45309");
        public static readonly Color Linea = ColorTranslator.FromHtml("#E4DFD3");
        public static readonly Color Tinta = ColorTranslator.FromHtml("#0F172A");
        public static readonly Color Apagado = ColorTranslator.FromHtml("#475569");
        public static readonly Color Control = ColorTranslator.FromHtml("#7D8591");
        public static readonly Color Pendiente = ColorTranslator.FromHtml("#9AA3B2");
        public static readonly Color Verde = ColorTranslator.FromHtml("#166534");
        public static readonly Color Rojo = ColorTranslator.FromHtml("#B91C1C");
    }

    static class Ui
    {
        static float k;

        // Escala de la pantalla (1,0 a 96 dpi). La ventana se arma en pixeles de dispositivo
        // multiplicando por esta escala, asi se ve igual de grande en cualquier pantalla.
        public static float K
        {
            get
            {
                if (k <= 0)
                {
                    using (Graphics g = Graphics.FromHwnd(IntPtr.Zero)) { k = g.DpiX / 96f; }
                    if (k < 1f) k = 1f;
                }
                return k;
            }
        }

        public static int S(int v) { return (int)Math.Round(v * K); }

        public static readonly Font Texto = new Font("Segoe UI", 11f);
        public static readonly Font TextoChico = new Font("Segoe UI", 10f);
        public static readonly Font Subrayado = new Font("Segoe UI", 11f, FontStyle.Underline);
        public static readonly Font Seminegrita = new Font("Segoe UI Semibold", 11f);
        public static readonly Font Negrita = new Font("Segoe UI", 11f, FontStyle.Bold);
        public static readonly Font Serif20 = new Font("Georgia", 20f, FontStyle.Bold);
        public static readonly Font Serif19 = new Font("Georgia", 19f, FontStyle.Bold);
        public static readonly Font Registro = new Font("Consolas", 9f);

        public const TextFormatFlags Flujo = TextFormatFlags.WordBreak | TextFormatFlags.NoPrefix |
            TextFormatFlags.Left | TextFormatFlags.Top | TextFormatFlags.NoPadding;

        public static void Suave(Graphics g)
        {
            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.PixelOffsetMode = PixelOffsetMode.HighQuality;
            g.CompositingQuality = CompositingQuality.HighQuality;
        }

        public static GraphicsPath Redondo(RectangleF r, float radio)
        {
            GraphicsPath p = new GraphicsPath();
            float d = radio * 2;
            p.AddArc(r.X, r.Y, d, d, 180, 90);
            p.AddArc(r.Right - d, r.Y, d, d, 270, 90);
            p.AddArc(r.Right - d, r.Bottom - d, d, d, 0, 90);
            p.AddArc(r.X, r.Bottom - d, d, d, 90, 90);
            p.CloseFigure();
            return p;
        }

        public static int AltoTexto(string texto, Font fuente, int ancho)
        {
            Size m = TextRenderer.MeasureText(texto, fuente, new Size(ancho, 100000), Flujo);
            return m.Height + S(2);
        }

        public static Label Etiqueta(string texto, Font fuente, Color color)
        {
            Label l = new Label();
            l.AutoSize = false;
            l.UseMnemonic = false;
            l.UseCompatibleTextRendering = false;
            l.BackColor = Color.Transparent;
            l.ForeColor = color;
            l.Font = fuente;
            l.Text = texto;
            l.Padding = Padding.Empty;
            l.Margin = Padding.Empty;
            return l;
        }
    }

    // La balanza de la marca, igual que en src/generar_icono.py, dibujada en vectores.
    // El brazo (con los dos platillos colgados) oscila; el poste, la base y el punto dorado no.
    static class Balanza
    {
        static PointF Rotar(float x, float y, double grados)
        {
            double a = grados * Math.PI / 180.0, c = Math.Cos(a), s = Math.Sin(a);
            double dx = x - 512, dy = y - 300;
            return new PointF((float)(512 + dx * c - dy * s), (float)(300 + dx * s + dy * c));
        }

        static Pen Trazo(Color color, float ancho)
        {
            Pen p = new Pen(color, ancho);
            p.StartCap = LineCap.Round;
            p.EndCap = LineCap.Round;
            p.LineJoin = LineJoin.Round;
            return p;
        }

        public static void Dibujar(Graphics g, RectangleF caja, double grados)
        {
            // El dibujo ocupa x 160..864 e y 190..810 de un cuadro de 1024.
            float s = Math.Min(caja.Width / 704f, caja.Height / 620f);
            float ox = caja.X + (caja.Width - 704f * s) / 2f - 160f * s;
            float oy = caja.Y + (caja.Height - 620f * s) / 2f - 190f * s;
            Func<PointF, PointF> P = delegate(PointF q) { return new PointF(ox + q.X * s, oy + q.Y * s); };
            Color crema = Paleta.Crema;

            using (Pen grueso = Trazo(crema, 48f * s))
            using (Pen fino = Trazo(crema, 36f * s))
            using (SolidBrush relleno = new SolidBrush(crema))
            {
                g.DrawLine(grueso, P(new PointF(512, 262)), P(new PointF(512, 772)));       // poste
                g.DrawLine(grueso, P(new PointF(372, 772)), P(new PointF(652, 772)));       // base
                PointF a = Rotar(236, 352, grados), b = Rotar(512, 300, grados), c = Rotar(788, 352, grados);
                g.DrawLines(grueso, new PointF[] { P(a), P(b), P(c) });                      // brazo
                // Los platillos cuelgan de dos puntos del brazo y siempre quedan derechos.
                PointF izq = Rotar(300, 340, grados), der = Rotar(724, 340, grados);
                Platillo(g, fino, relleno, P, izq.X, izq.Y + 20, s);
                Platillo(g, fino, relleno, P, der.X, der.Y + 20, s);
            }
            using (SolidBrush oro = new SolidBrush(Paleta.DoradoPunto))
            {
                PointF c0 = P(new PointF(512, 232));
                float r = 44f * s;
                g.FillEllipse(oro, c0.X - r, c0.Y - r, r * 2, r * 2);
            }
        }

        static void Platillo(Graphics g, Pen pen, Brush relleno, Func<PointF, PointF> P,
                             float x, float y0, float s)
        {
            float medio = 118f, y1 = y0 + 230f;
            g.DrawLines(pen, new PointF[] { P(new PointF(x - medio, y1)), P(new PointF(x, y0)),
                                            P(new PointF(x + medio, y1)) });
            PointF esq = P(new PointF(x - medio - 18f, y1 - 65f));
            using (GraphicsPath cuenco = new GraphicsPath())
            {
                cuenco.AddArc(esq.X, esq.Y, (medio + 18f) * 2f * s, 130f * s, 0, 180);
                cuenco.CloseFigure();
                g.FillPath(relleno, cuenco);
            }
        }
    }

    // Banda superior: marino con la balanza, el titulo serif y el filete dorado.
    class Encabezado : Control
    {
        double angulo;

        public Encabezado()
        {
            SetStyle(ControlStyles.UserPaint | ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.OptimizedDoubleBuffer | ControlStyles.ResizeRedraw, true);
            TabStop = false;
            AccessibleRole = AccessibleRole.Grouping;
            AccessibleName = "Asistente Legal";
        }

        public double Angulo
        {
            get { return angulo; }
            set { if (Math.Abs(value - angulo) > 0.001) { angulo = value; Invalidate(); } }
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            Graphics g = e.Graphics;
            Ui.Suave(g);
            int filete = Ui.S(3);
            using (SolidBrush b = new SolidBrush(Paleta.Marino))
                g.FillRectangle(b, 0, 0, Width, Height - filete);
            using (SolidBrush b = new SolidBrush(Paleta.Dorado))
                g.FillRectangle(b, 0, Height - filete, Width, filete);

            Balanza.Dibujar(g, new RectangleF(Ui.S(34), Ui.S(12), Ui.S(72), Ui.S(68)), angulo);

            int x = Ui.S(124);
            Size t1 = TextRenderer.MeasureText("Asistente Legal", Ui.Serif20);
            Size t2 = TextRenderer.MeasureText("Instalador", Ui.TextoChico);
            int alto = t1.Height + t2.Height - Ui.S(2);
            int y = (Height - filete - alto) / 2;
            TextRenderer.DrawText(g, "Asistente Legal", Ui.Serif20, new Point(x, y), Color.White,
                                  TextFormatFlags.NoPadding | TextFormatFlags.NoPrefix);
            TextRenderer.DrawText(g, "Archivo del estudio · consultas, fichas y escritos",
                                  Ui.TextoChico, new Point(x + Ui.S(1), y + t1.Height - Ui.S(2)),
                                  Paleta.MarinoLinea, TextFormatFlags.NoPadding | TextFormatFlags.NoPrefix);
        }
    }

    // Boton redondeado de 44 px: primario (marino) o secundario (blanco con borde).
    // Foco del teclado: anillo dorado de 2 px.
    class Boton : Control, IButtonControl
    {
        bool hover, presionado, esPredeterminado;
        DialogResult resultado = DialogResult.None;
        public bool Primario;
        public bool Enlace;   // sin borde ni relleno: texto subrayado (pero con objetivo de 44 px y foco dorado)

        public Boton(string texto, bool primario)
        {
            Primario = primario;
            Text = texto;
            Font = Ui.Seminegrita;
            SetStyle(ControlStyles.UserPaint | ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.OptimizedDoubleBuffer | ControlStyles.ResizeRedraw |
                     ControlStyles.Selectable | ControlStyles.SupportsTransparentBackColor, true);
            BackColor = Color.Transparent;
            TabStop = true;
            Cursor = Cursors.Hand;
            AccessibleRole = AccessibleRole.PushButton;
        }

        // Margen interior para el anillo de foco: el boton "real" es el rectangulo menos este margen.
        public static int Margen { get { return Ui.S(4); } }

        public void Colocar(int x, int y, int ancho)
        {
            SetBounds(x - Margen, y - Margen, ancho + Margen * 2, Ui.S(44) + Margen * 2);
        }

        public DialogResult DialogResult
        {
            get { return resultado; }
            set { resultado = value; }
        }

        public void NotifyDefault(bool valor) { esPredeterminado = valor; Invalidate(); }

        public void PerformClick() { if (Enabled && Visible) OnClick(EventArgs.Empty); }

        protected override void OnClick(EventArgs e)
        {
            Form f = FindForm();
            if (f != null && resultado != DialogResult.None) f.DialogResult = resultado;
            base.OnClick(e);
        }

        protected override void OnMouseEnter(EventArgs e) { hover = true; Invalidate(); base.OnMouseEnter(e); }
        protected override void OnMouseLeave(EventArgs e) { hover = false; presionado = false; Invalidate(); base.OnMouseLeave(e); }
        protected override void OnMouseDown(MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left) { presionado = true; Focus(); Invalidate(); }
            base.OnMouseDown(e);
        }
        protected override void OnMouseUp(MouseEventArgs e) { presionado = false; Invalidate(); base.OnMouseUp(e); }
        protected override void OnGotFocus(EventArgs e) { Invalidate(); base.OnGotFocus(e); }
        protected override void OnLostFocus(EventArgs e) { Invalidate(); base.OnLostFocus(e); }
        protected override void OnEnabledChanged(EventArgs e) { Invalidate(); base.OnEnabledChanged(e); }
        protected override void OnTextChanged(EventArgs e) { Invalidate(); base.OnTextChanged(e); }

        protected override bool IsInputKey(Keys tecla) { return tecla == Keys.Space || base.IsInputKey(tecla); }
        protected override void OnKeyDown(KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Space) { presionado = true; Invalidate(); e.Handled = true; }
            base.OnKeyDown(e);
        }
        protected override void OnKeyUp(KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Space && presionado) { presionado = false; Invalidate(); PerformClick(); e.Handled = true; }
            base.OnKeyUp(e);
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            Graphics g = e.Graphics;
            Ui.Suave(g);
            int m = Margen;
            RectangleF r = new RectangleF(m, m, Width - m * 2 - 1, Height - m * 2 - 1);
            if (Enlace)
            {
                Color cl = hover || presionado ? Paleta.MarinoHover : Paleta.Marino;
                Rectangle zona = new Rectangle(m + Ui.S(6), m, Width - m * 2 - Ui.S(6), Height - m * 2);
                if (Focused && ShowFocusCues)
                {
                    RectangleF ro = new RectangleF(m / 2f, m / 2f, Width - m - 1, Height - m - 1);
                    using (GraphicsPath p = Ui.Redondo(ro, Ui.S(10)))
                    using (Pen pen = new Pen(Paleta.Dorado, 2f)) g.DrawPath(pen, p);
                }
                TextRenderer.DrawText(g, Text, Ui.Subrayado, zona, cl,
                    TextFormatFlags.Left | TextFormatFlags.VerticalCenter | TextFormatFlags.SingleLine | TextFormatFlags.NoPrefix);
                return;
            }
            Color relleno, texto, borde = Color.Empty;
            if (!Enabled)
            {
                relleno = Primario ? Color.FromArgb(168, 180, 210) : Color.FromArgb(243, 241, 236);
                texto = Primario ? Color.White : Paleta.Pendiente;
                if (!Primario) borde = Paleta.Linea;
            }
            else if (Primario)
            {
                relleno = presionado ? Paleta.MarinoPresionado : (hover ? Paleta.MarinoHover : Paleta.Marino);
                texto = Color.White;
            }
            else
            {
                relleno = presionado ? Paleta.MarinoLinea : (hover ? Paleta.MarinoSuave : Color.White);
                texto = Paleta.Marino;
                borde = hover ? Paleta.Marino : Paleta.Control;
            }
            using (GraphicsPath p = Ui.Redondo(r, Ui.S(8)))
            {
                using (SolidBrush b = new SolidBrush(relleno)) g.FillPath(b, p);
                if (borde != Color.Empty)
                    using (Pen pen = new Pen(borde, 1.5f)) g.DrawPath(pen, p);
            }
            if (Focused && ShowFocusCues)
            {
                RectangleF ro = new RectangleF(m / 2f, m / 2f, Width - m - 1, Height - m - 1);
                using (GraphicsPath p = Ui.Redondo(ro, Ui.S(10)))
                using (Pen pen = new Pen(Paleta.Dorado, 2f)) g.DrawPath(pen, p);
            }
            Rectangle cuerpo = new Rectangle(m, m, Width - m * 2, Height - m * 2);
            TextRenderer.DrawText(g, Text, Font, cuerpo, texto,
                TextFormatFlags.HorizontalCenter | TextFormatFlags.VerticalCenter |
                TextFormatFlags.SingleLine | TextFormatFlags.NoPrefix | TextFormatFlags.EndEllipsis);
        }
    }

    class BotonPrimario : Boton
    {
        public BotonPrimario(string texto) : base(texto, true) { }
    }

    class BotonEnlace : Boton
    {
        public BotonEnlace(string texto) : base(texto, false) { Enlace = true; }
    }

    class BotonSecundario : Boton
    {
        public BotonSecundario(string texto) : base(texto, false) { }
    }

    // Tarjeta blanca con borde de 1 px, esquinas redondeadas y una sombra suave hacia abajo.
    class Tarjeta : Panel
    {
        public Tarjeta()
        {
            SetStyle(ControlStyles.UserPaint | ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.OptimizedDoubleBuffer | ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor, true);
            BackColor = Color.Transparent;
        }

        public static int Sombra { get { return Ui.S(6); } }

        protected override void OnPaint(PaintEventArgs e)
        {
            Graphics g = e.Graphics;
            Ui.Suave(g);
            RectangleF r = new RectangleF(0.5f, 0.5f, Width - 2, Height - Sombra - 1);
            for (int i = 4; i >= 1; i--)
            {
                RectangleF s = new RectangleF(r.X - i * 0.6f, r.Y + i * 0.9f, r.Width + i * 1.2f, r.Height + i * 0.4f);
                using (GraphicsPath p = Ui.Redondo(s, Ui.S(10) + i * 0.5f))
                using (SolidBrush b = new SolidBrush(Color.FromArgb(9, 15, 23, 42))) g.FillPath(b, p);
            }
            using (GraphicsPath p = Ui.Redondo(r, Ui.S(10)))
            {
                g.FillPath(Brushes.White, p);
                using (Pen pen = new Pen(Paleta.Linea, 1f)) g.DrawPath(pen, p);
            }
        }
    }

    enum Estado { Pendiente, EnCurso, Listo, Aviso, Error, Info }

    // Icono de estado dibujado: circulo hueco, arco que gira, tilde, "!", "x" o "i".
    class IconoEstado : Control
    {
        Estado estado = Estado.Pendiente;
        public static float Fase;

        public IconoEstado()
        {
            SetStyle(ControlStyles.UserPaint | ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.OptimizedDoubleBuffer | ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor, true);
            BackColor = Color.Transparent;
            TabStop = false;
            AccessibleRole = AccessibleRole.Graphic;
            AccessibleName = "Pendiente";
        }

        public Estado Estado
        {
            get { return estado; }
            set
            {
                if (value == estado) return;
                estado = value;
                switch (value)
                {
                    case Estado.EnCurso: AccessibleName = "En curso"; break;
                    case Estado.Listo: AccessibleName = "Listo"; break;
                    case Estado.Aviso: AccessibleName = "Con aviso"; break;
                    case Estado.Error: AccessibleName = "Error"; break;
                    case Estado.Info: AccessibleName = "Informacion"; break;
                    default: AccessibleName = "Pendiente"; break;
                }
                Invalidate();
            }
        }

        static Pen Trazo(Color c, float ancho)
        {
            Pen p = new Pen(c, ancho);
            p.StartCap = LineCap.Round;
            p.EndCap = LineCap.Round;
            p.LineJoin = LineJoin.Round;
            return p;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            Graphics g = e.Graphics;
            Ui.Suave(g);
            float d = Math.Min(Width, Height);
            float m = Math.Max(1.5f, d * 0.07f);
            float tr = Math.Max(2f, d * 0.085f);
            RectangleF r = new RectangleF((Width - d) / 2f + m, (Height - d) / 2f + m, d - 2 * m, d - 2 * m);
            Func<float, float, PointF> Q = delegate(float u, float v)
            { return new PointF(r.X + r.Width * u, r.Y + r.Height * v); };

            switch (estado)
            {
                case Estado.Pendiente:
                    using (Pen p = new Pen(Paleta.Pendiente, tr)) g.DrawEllipse(p, r.X + tr / 2, r.Y + tr / 2, r.Width - tr, r.Height - tr);
                    break;
                case Estado.EnCurso:
                    using (Pen p = new Pen(Paleta.MarinoLinea, tr)) g.DrawEllipse(p, r.X + tr / 2, r.Y + tr / 2, r.Width - tr, r.Height - tr);
                    using (Pen p = Trazo(Paleta.Marino, tr)) g.DrawArc(p, r.X + tr / 2, r.Y + tr / 2, r.Width - tr, r.Height - tr, Fase, 120);
                    break;
                case Estado.Listo:
                    Disco(g, r, Paleta.Verde);
                    using (Pen p = Trazo(Color.White, tr * 1.15f))
                        g.DrawLines(p, new PointF[] { Q(0.27f, 0.53f), Q(0.44f, 0.69f), Q(0.75f, 0.33f) });
                    break;
                case Estado.Aviso:
                    Disco(g, r, Paleta.Dorado);
                    using (Pen p = Trazo(Color.White, tr * 1.25f)) g.DrawLine(p, Q(0.5f, 0.26f), Q(0.5f, 0.58f));
                    PuntoBlanco(g, Q(0.5f, 0.76f), tr * 0.72f);
                    break;
                case Estado.Error:
                    Disco(g, r, Paleta.Rojo);
                    using (Pen p = Trazo(Color.White, tr * 1.2f))
                    {
                        g.DrawLine(p, Q(0.33f, 0.33f), Q(0.67f, 0.67f));
                        g.DrawLine(p, Q(0.67f, 0.33f), Q(0.33f, 0.67f));
                    }
                    break;
                case Estado.Info:
                    Disco(g, r, Paleta.Marino);
                    PuntoBlanco(g, Q(0.5f, 0.27f), tr * 0.72f);
                    using (Pen p = Trazo(Color.White, tr * 1.25f)) g.DrawLine(p, Q(0.5f, 0.45f), Q(0.5f, 0.75f));
                    break;
            }
        }

        static void Disco(Graphics g, RectangleF r, Color c)
        {
            using (SolidBrush b = new SolidBrush(c)) g.FillEllipse(b, r);
        }

        static void PuntoBlanco(Graphics g, PointF c, float radio)
        {
            g.FillEllipse(Brushes.White, c.X - radio, c.Y - radio, radio * 2, radio * 2);
        }
    }

    // Barra de avance general: pista clara, relleno marino, redondeada; avanza con ease-out.
    class Barra : Control
    {
        float actual, objetivo;

        public Barra()
        {
            SetStyle(ControlStyles.UserPaint | ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.OptimizedDoubleBuffer | ControlStyles.ResizeRedraw |
                     ControlStyles.SupportsTransparentBackColor, true);
            BackColor = Color.Transparent;
            TabStop = false;
            AccessibleRole = AccessibleRole.ProgressBar;
            AccessibleName = "Avance de la instalacion";
        }

        public float Objetivo
        {
            get { return objetivo; }
            set { objetivo = Math.Max(0f, Math.Min(1f, value)); }
        }

        public void Fijar(float valor) { objetivo = actual = Math.Max(0f, Math.Min(1f, valor)); Invalidate(); }

        // Un paso de la animacion (cada ~33 ms): se acerca al objetivo y frena al llegar.
        public void Avanzar()
        {
            if (Math.Abs(objetivo - actual) < 0.0005f) { if (actual != objetivo) { actual = objetivo; Invalidate(); } return; }
            actual += (objetivo - actual) * 0.2f;
            Invalidate();
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            Graphics g = e.Graphics;
            Ui.Suave(g);
            RectangleF pista = new RectangleF(0, 0, Width - 1, Height - 1);
            float radio = pista.Height / 2f;
            using (GraphicsPath p = Ui.Redondo(pista, radio))
            using (SolidBrush b = new SolidBrush(Paleta.Linea)) g.FillPath(b, p);
            float ancho = Math.Max(pista.Height, pista.Width * actual);
            if (actual > 0.001f)
            {
                RectangleF lleno = new RectangleF(0, 0, ancho, pista.Height);
                using (GraphicsPath p = Ui.Redondo(lleno, radio))
                using (SolidBrush b = new SolidBrush(Paleta.Marino)) g.FillPath(b, p);
            }
        }
    }

    // Casilla de verificacion grande, con foco dorado. Se marca con clic o con la barra espaciadora.
    class Casilla : Control
    {
        bool marcada, hover;
        public event EventHandler MarcadaCambio;

        public Casilla(string texto)
        {
            Text = texto;
            Font = Ui.Texto;
            ForeColor = Paleta.Tinta;
            SetStyle(ControlStyles.UserPaint | ControlStyles.AllPaintingInWmPaint |
                     ControlStyles.OptimizedDoubleBuffer | ControlStyles.ResizeRedraw |
                     ControlStyles.Selectable | ControlStyles.SupportsTransparentBackColor, true);
            BackColor = Color.Transparent;
            TabStop = true;
            Cursor = Cursors.Hand;
            AccessibleRole = AccessibleRole.CheckButton;
        }

        public bool Marcada
        {
            get { return marcada; }
            set
            {
                if (marcada == value) return;
                marcada = value;
                Invalidate();
                if (MarcadaCambio != null) MarcadaCambio(this, EventArgs.Empty);
            }
        }

        public void Alternar() { Marcada = !marcada; }

        public static int Lado { get { return Ui.S(26); } }

        public int AltoPara(int ancho)
        {
            int texto = Ui.AltoTexto(Text, Font, ancho - Lado - Ui.S(22));
            return Math.Max(Ui.S(44), texto + Ui.S(24));
        }

        protected override void OnClick(EventArgs e) { Focus(); Alternar(); base.OnClick(e); }
        protected override void OnMouseEnter(EventArgs e) { hover = true; Invalidate(); base.OnMouseEnter(e); }
        protected override void OnMouseLeave(EventArgs e) { hover = false; Invalidate(); base.OnMouseLeave(e); }
        protected override void OnGotFocus(EventArgs e) { Invalidate(); base.OnGotFocus(e); }
        protected override void OnLostFocus(EventArgs e) { Invalidate(); base.OnLostFocus(e); }
        protected override bool IsInputKey(Keys tecla) { return tecla == Keys.Space || base.IsInputKey(tecla); }
        protected override void OnKeyUp(KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Space) { Alternar(); e.Handled = true; }
            base.OnKeyUp(e);
        }

        protected override AccessibleObject CreateAccessibilityInstance() { return new CasillaAccesible(this); }

        protected override void OnPaint(PaintEventArgs e)
        {
            Graphics g = e.Graphics;
            Ui.Suave(g);
            int lado = Lado, x0 = Ui.S(4), y0 = Math.Max(Ui.S(4), (Math.Min(Height, Ui.S(44)) - Lado) / 2);
            RectangleF caja = new RectangleF(x0 + 0.75f, y0 + 0.75f, lado - 1.5f, lado - 1.5f);
            using (GraphicsPath p = Ui.Redondo(caja, Ui.S(5)))
            {
                using (SolidBrush b = new SolidBrush(marcada ? Paleta.Marino : Color.White)) g.FillPath(b, p);
                using (Pen pen = new Pen(marcada ? Paleta.Marino : (hover ? Paleta.Marino : Paleta.Control), 1.5f)) g.DrawPath(pen, p);
            }
            if (marcada)
            {
                using (Pen p = new Pen(Color.White, Math.Max(2.2f, lado * 0.12f)))
                {
                    p.StartCap = LineCap.Round; p.EndCap = LineCap.Round; p.LineJoin = LineJoin.Round;
                    g.DrawLines(p, new PointF[] {
                        new PointF(caja.X + caja.Width * 0.24f, caja.Y + caja.Height * 0.53f),
                        new PointF(caja.X + caja.Width * 0.43f, caja.Y + caja.Height * 0.71f),
                        new PointF(caja.X + caja.Width * 0.77f, caja.Y + caja.Height * 0.31f) });
                }
            }
            if (Focused && ShowFocusCues)
            {
                RectangleF ro = RectangleF.Inflate(caja, Ui.S(3), Ui.S(3));
                using (GraphicsPath p = Ui.Redondo(ro, Ui.S(7)))
                using (Pen pen = new Pen(Paleta.Dorado, 2f)) g.DrawPath(pen, p);
            }
            int xt = x0 + lado + Ui.S(12);
            Rectangle zona = new Rectangle(xt, y0 + (lado - Ui.S(20)) / 2, Width - xt - Ui.S(2), Height - y0);
            TextRenderer.DrawText(g, Text, Font, zona, ForeColor, Ui.Flujo);
        }
    }

    class CasillaAccesible : Control.ControlAccessibleObject
    {
        readonly Casilla casilla;
        public CasillaAccesible(Casilla c) : base(c) { casilla = c; }
        public override AccessibleStates State
        {
            get
            {
                AccessibleStates s = base.State;
                if (casilla.Marcada) s |= AccessibleStates.Checked;
                return s;
            }
        }
        public override string DefaultAction { get { return "Marcar o desmarcar"; } }
        public override void DoDefaultAction() { casilla.Alternar(); }
    }
}
