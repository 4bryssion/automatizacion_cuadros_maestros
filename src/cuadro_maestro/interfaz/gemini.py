"""Asistente con Gemini (mockups 08 y 09) y Confirmar sugerencias del programa (mockup 29)."""
from __future__ import annotations

import tkinter as tk
import webbrowser
from pathlib import Path

from .. import sugerencias as S
from ..cruce import cruzar
from ..lectura import leer_carpeta
from . import dialogos as D
from . import tema as T
from .modelo import vigencia

ESTADO_RESPUESTA = {S.POR_CONFIRMAR: ("Por confirmar", "aviso"), S.NO_COINCIDE: ("No coincide", "error"),
                    S.NO_ESTA: ("No está en la lista", "error"), S.SIN_RESPUESTA: ("Sin respuesta", "gris")}
TIPO = {S.INSTITUCION: ("Institución", "gris"), S.PROGRAMA: ("Programa", "aviso"), S.COLUMNA: ("Columna", "gris")}


def contexto_principal(app):
    """Carpeta, programa y vigencia de la ventana principal (desde Configuración)."""
    v = app.ventana
    desde, hasta = v.anios_elegidos()
    return v.v_carpeta.get(), v.programa_id(), desde, hasta


def contexto_ultimo(app):
    """Los del último cuadro (desde Ver revisión)."""
    u = app.estado.ultima
    return u.carpeta, u.programa_id, u.anio_inicio, u.anio_fin


def que_falta(contexto) -> str | None:
    carpeta, programa_id, desde, hasta = contexto
    if not carpeta or not Path(carpeta).is_dir():
        return "Elige en la ventana principal la carpeta con los Excel."
    if not programa_id:
        return "Elige el programa en la ventana principal."
    if desde is None or hasta is None or desde > hasta:
        return "Elige una vigencia válida en la ventana principal."
    return None


def _ilustracion(padre, n):
    """Dibujos de los 4 pasos (mockup 08), suavizados con Pillow."""
    from . import graficos as G
    W, H = 380, 120

    def dibujar(d, w, h):
        k = G.SS
        gris, verde, osc, blanco = G.rgb("#CFCFCF"), G.rgb(T.VERDE_CTA), G.rgb(T.GRIS_OSC), G.rgb(T.BLANCO)

        def caja_(x0, y0, x1, y1, r=8, fill=blanco, outline=gris, ancho=1):
            d.rounded_rectangle((x0 * k, y0 * k, x1 * k, y1 * k), r * k, fill=fill, outline=outline, width=ancho * k)

        def texto(x, y, t, px=13, color=osc, negrita=True, centro=False):
            f = G.fuente(px, negrita)
            if centro:
                G.texto_centrado(d, x * k, y * k, t, px, color, negrita)
            else:
                b = d.textbbox((0, 0), t, font=f)
                d.text((x * k, y * k - (b[1] + b[3]) / 2), t, font=f, fill=color)

        def flecha_(x0, y0, x1, y1):
            d.line((x0 * k, y0 * k, x1 * k, y1 * k), fill=G.rgb(T.GRIS), width=2 * k)
            if y0 == y1:
                d.polygon([(x1 * k, (y1 - 5) * k), ((x1 + 8) * k, y1 * k), (x1 * k, (y1 + 5) * k)], fill=G.rgb(T.GRIS))
            else:
                d.polygon([((x1 - 5) * k, y1 * k), (x1 * k, (y1 + 8) * k), ((x1 + 5) * k, y1 * k)], fill=verde)
        if n == 1:
            caja_(22, 14, 200, 106)
            texto(34, 30, "Mensaje para Gemini")
            for i, ancho in enumerate((150, 128, 140, 96)):
                d.rounded_rectangle((34 * k, (46 + i * 13) * k, (34 + ancho) * k, (52 + i * 13) * k), 3 * k, fill=gris)
            flecha_(210, 60, 226, 60)
            caja_(242, 40, 358, 80, 8, blanco, verde, 2)
            texto(300, 60, "Copiar", 14, verde, centro=True)
        elif n == 2:
            caja_(40, 12, 340, 108, 10)
            d.rounded_rectangle((41 * k, 13 * k, 339 * k, 34 * k), 9 * k, fill=G.rgb("#EDEDED"),
                                corners=(True, True, False, False))
            for i in range(3):
                d.ellipse(((52 + i * 12) * k, 20 * k, (59 + i * 12) * k, 27 * k), fill=G.rgb("#BDBDBD"))
            caja_(100, 17, 300, 30, 6)
            texto(200, 24, "gemini.google.com", 11, G.rgb(T.GRIS), False, centro=True)
            texto(190, 58, "Gemini", 17, osc, centro=True)
            caja_(95, 76, 285, 96, 10)
        elif n == 3:
            for x, t in ((150, "Ctrl"), (220, "V")):
                caja_(x - 28, 10, x + 28, 38, 6, blanco, osc, 2)
                texto(x, 24, t, 14, osc, centro=True)
            flecha_(185, 42, 185, 60)
            caja_(40, 72, 340, 106, 17, blanco, osc, 2)
            texto(58, 89, "Ayúdame a emparejar estos nombres…", 12, osc, False)
            d.ellipse((310 * k, 76 * k, 336 * k, 102 * k), fill=verde)
            d.line((323 * k, 95 * k, 323 * k, 83 * k), fill=blanco, width=2 * k)
            d.polygon([(317 * k, 88 * k), (323 * k, 81 * k), (329 * k, 88 * k)], fill=blanco)
        else:
            caja_(22, 14, 170, 106)
            texto(34, 30, "Respuesta")
            for i, ancho in enumerate((118, 100, 110, 86)):
                d.rounded_rectangle((34 * k, (46 + i * 13) * k, (34 + ancho) * k, (52 + i * 13) * k), 3 * k, fill=gris)
            flecha_(180, 60, 196, 60)
            caja_(212, 14, 358, 106, 8, blanco, verde, 2)
            texto(224, 30, "Pegar respuesta")
            caja_(224, 44, 346, 66, 5)
            d.rounded_rectangle((224 * k, 76 * k, 346 * k, 94 * k), 5 * k, fill=verde)
            texto(285, 85, "Revisar sugerencias", 10, blanco, centro=True)
    caja_ill = T.Caja(padre, fondo=T.FONDO, borde=None, grosor=0, radio=T.RADIO + 2, padx=8, pady=8)
    tk.Label(caja_ill, image=G.imagen(padre, ("ilustracion", n), W, H, dibujar), bg=T.FONDO, bd=0).pack()
    return caja_ill


class ModalGemini(D.Modal):
    """Paso 1 a 3: cómo usarlo y copiar el mensaje. Paso 4: pegar la respuesta y marcar lo que se guarda.
    Devuelve la lista de lo guardado (vacía si no se guardó nada)."""

    def __init__(self, app, duena=None, contexto=None):
        super().__init__(duena or app.raiz, "Asistente con Gemini", ancho=1000)
        self.app = app
        self.contexto = contexto or contexto_principal(app)
        self.falta = que_falta(self.contexto)
        self.preguntas, self.respuestas, self.marcadas = [], None, {}
        self.paso = "pasos"
        self.ver_mensaje = False
        self.quitadas: set[str] = set()
        self.v_respuesta = None
        self.texto_respuesta = ""
        if not self.falta:
            carpeta, pid, desde, hasta = self.contexto
            config = app.config

            def trabajo():
                lectura = leer_carpeta(Path(carpeta), config, desde, hasta)
                return S.preguntas_para_gemini(lectura, cruzar(lectura, config, pid), config)
            self.preguntas = D.en_espera(duena or app.raiz, trabajo)
        self.contenido = tk.Frame(self.cuerpo, bg=T.BLANCO)
        self.contenido.pack(fill="both", expand=True)
        self.resultado = []
        self.pintar()

    @property
    def enviadas(self):
        """Las preguntas que van en el mensaje: la persona puede quitar las que no sean nombres de instituciones
        (en los reportes, la columna de institución a veces trae un cargo o una descripción)."""
        return [p for p in self.preguntas if p.id not in self.quitadas]

    @property
    def mensaje(self) -> str:
        return S.mensaje(self.enviadas)

    def pintar(self):
        for w in self.contenido.winfo_children():
            w.destroy()
        (self._pasos if self.paso == "pasos" else self._respuesta)(self.contenido)

    # pasos 1 a 3
    def _pasos(self, c):
        cab = tk.Frame(c, bg=T.BLANCO)
        cab.pack(fill="x")
        tk.Label(cab, text="Asistente con Gemini", font=T.F["modal_titulo"], bg=T.BLANCO).pack(side="left")
        T.chip(cab, "Opcional", "gris").pack(side="left", padx=12)
        T.Ayuda(cab, "gemini").pack(side="left")
        n_inst = sum(p.tipo == S.INSTITUCION for p in self.preguntas)
        n_col = len(self.preguntas) - n_inst
        tk.Label(c, text="Gemini te ayuda a emparejar columnas y nombres de instituciones que el programa no reconoció. "
                         "Son 4 pasos y no necesitas instalar nada.", font=T.F["cuerpo"], bg=T.BLANCO, anchor="w",
                 justify="left", wraplength=self.ancho - 80).pack(fill="x", pady=(8, 10))
        if self.falta:
            T.Franja(c, "aviso", self.falta).pack(fill="x", pady=(0, 10))
        elif not self.preguntas:
            T.Franja(c, "info", "No hay nada que preguntar: todas las instituciones y columnas de estos archivos se "
                     "reconocieron.").pack(fill="x", pady=(0, 10))
        else:
            partes = [x for x in (f"{n_inst} institución" + ("es" if n_inst != 1 else "") if n_inst else "",
                                  f"{n_col} columna" + ("s" if n_col != 1 else "") if n_col else "") if x]
            fila = tk.Frame(c, bg=T.BLANCO)
            fila.pack(fill="x", pady=(0, 10))
            tk.Label(fila, text="El mensaje pregunta por " + " y ".join(partes) + " de " +
                     f"{self._programa()} · {vigencia(self.contexto[2], self.contexto[3])}.", font=T.F["cuerpo_b"],
                     bg=T.BLANCO).pack(side="left")
            T.Enlace(fila, "Ocultar" if self.ver_mensaje else "Revisar qué se envía ›",
                     lambda: (setattr(self, "ver_mensaje", not self.ver_mensaje), self.pintar()),
                     fuente="pequena_b").pack(side="right")
            if self.ver_mensaje:
                tk.Label(c, text="Quita lo que no sea el nombre de una institución o el título de una columna (por "
                                 "ejemplo, un cargo o la descripción de una persona). Solo se copia lo marcado.",
                         font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w", justify="left",
                         wraplength=self.ancho - 80).pack(fill="x")
                lista = T.desplazable(c, min(170, 34 * len(self.preguntas)), bg=T.FONDO)
                lista.pack(fill="x", pady=(4, 10))
                for p in self.preguntas:
                    texto = p.como_aparece if p.tipo == S.INSTITUCION else f"Columna para «{p.como_aparece}» " \
                        f"({len(p.opciones)} títulos de columnas)"
                    T.Casilla(lista.interior, texto, p.id not in self.quitadas,
                              lambda v, k=p.id: (self.quitadas.discard(k) if v else self.quitadas.add(k), self.pintar()),
                              wraplength=self.ancho - 160).pack(fill="x", padx=10, pady=3)
        rejilla = tk.Frame(c, bg=T.BLANCO)
        rejilla.pack(fill="x")
        pasos = [("Copia el mensaje", "El programa lo prepara por ti con títulos de columnas y nombres de "
                                      "instituciones. Pulsa Copiar."),
                 ("Abre Gemini", "Se abre en tu navegador. Inicia sesión con tu cuenta y abre un chat nuevo."),
                 ("Pega y envía", "Pega el mensaje con Ctrl + V y envíalo. Gemini responde con una lista de "
                                  "coincidencias."),
                 ("Vuelve y pega la respuesta", "Copia la respuesta de Gemini, vuelve aquí, pégala y pulsa Revisar "
                                                "sugerencias.")]
        for i, (titulo, texto) in enumerate(pasos):
            t = T.Caja(rejilla, fondo=T.BLANCO, borde=T.LINEA, radio=T.RADIO_GRANDE, padx=12, pady=12)
            t.grid(row=i // 2, column=i % 2, sticky="nsew", padx=(0, 8) if i % 2 == 0 else (8, 0), pady=(0, 12))
            rejilla.grid_columnconfigure(i % 2, weight=1, uniform="g")
            _ilustracion(t, i + 1).pack(fill="x")
            f = tk.Frame(t, bg=T.BLANCO)
            f.pack(fill="x", pady=(10, 4))
            T.numero(f, i + 1, 30).pack(side="left")
            tk.Label(f, text=titulo, font=T.F["seccion"], bg=T.BLANCO).pack(side="left", padx=10)
            tk.Label(t, text=texto, font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w", justify="left",
                     wraplength=420).pack(fill="x")
        d = T.Caja(c, fondo=T.AVISO_BG, borde=T.NARANJA, radio=T.RADIO + 2, padx=16, pady=12)
        d.pack(fill="x")
        T.icono(d, "aviso", 24, bg=T.AVISO_BG).pack(side="left")          # centrado con las dos líneas
        tx = tk.Frame(d, bg=T.AVISO_BG)
        tx.pack(side="left", fill="x", padx=12)
        tk.Label(tx, text="Gemini solo sugiere: nada se aplica sin tu confirmación.", font=T.F["cuerpo_b"],
                 bg=T.AVISO_BG, anchor="w").pack(fill="x")
        tk.Label(tx, text="No pegues nombres, documentos ni correos de personas. El mensaje que prepara el programa ya no "
                          "los incluye.", font=T.F["cuerpo"], bg=T.AVISO_BG, anchor="w").pack(fill="x")
        pie = tk.Frame(c, bg=T.BLANCO)
        pie.pack(fill="x", pady=(16, 0))
        T.Boton(pie, "Cerrar", lambda: self.cerrar(self.resultado), tipo="secundario", ancho=140).pack(side="left")
        ya = T.Enlace(pie, "Ya tengo la respuesta", lambda: self.ir_a_respuesta())
        ya.pack(side="left", padx=20)
        copiar = T.Boton(pie, "Copiar mensaje y abrir Gemini", lambda: self.copiar_y_abrir(), ancho=340)
        copiar.pack(side="right")
        hay = bool(self.enviadas) and not self.falta
        copiar.activar(hay)
        ya.activar(hay)

    def _programa(self):
        return next((p["nombre"] for p in self.app.config["programas"] if p["id"] == self.contexto[1]), "—")

    def copiar_y_abrir(self, abrir_navegador=True):
        self.clipboard_clear()
        self.clipboard_append(self.mensaje)
        self.update()
        if abrir_navegador:
            try:
                webbrowser.open(S.URL_GEMINI)
            except Exception:   # noqa: BLE001 — si no abre, la persona puede ir a la dirección a mano
                pass
        self.ir_a_respuesta()

    def ir_a_respuesta(self):
        self.paso = "respuesta"
        self.pintar()

    # paso 4
    def _respuesta(self, c):
        cab = tk.Frame(c, bg=T.BLANCO)
        cab.pack(fill="x")
        tk.Label(cab, text="Pega la respuesta de Gemini", font=T.F["modal_titulo"], bg=T.BLANCO).pack(side="left")
        T.chip(cab, "Paso 4 de 4", "ok").pack(side="right")
        tk.Label(c, text="El mensaje ya está copiado. Si Gemini no se abrió, ve a gemini.google.com en tu navegador.",
                 font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w").pack(fill="x", pady=(6, 8))
        borde = T.Caja(c, fondo=T.BLANCO, borde=T.VERDE_CTA, grosor=2, radio=T.RADIO + 2, padx=8, pady=6)
        borde.pack(fill="x")
        self.caja_respuesta = tk.Text(borde, height=6, wrap="word", font=T.F["cuerpo"], bd=0, padx=6, pady=4,
                                      highlightthickness=0)
        self.caja_respuesta.insert("1.0", self.texto_respuesta)
        self.caja_respuesta.pack(fill="x")
        self.caja_respuesta.bind("<KeyRelease>", lambda e: self._contar())
        self.caja_respuesta.bind("<<Paste>>", lambda e: self.after(10, self._contar))
        self.caja_respuesta.focus_set()
        fila = tk.Frame(c, bg=T.BLANCO)
        fila.pack(fill="x", pady=(10, 0))
        self.lbl_pegado = tk.Label(fila, font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS)
        self.lbl_pegado.pack(side="left")
        T.Enlace(fila, "‹ Volver a los pasos", lambda: (self._guardar_texto(), setattr(self, "paso", "pasos"),
                                                       self.pintar()), fuente="pequena_b").pack(side="left", padx=16)
        T.Boton(fila, "Revisar sugerencias", lambda: self.revisar(), ancho=240).pack(side="right")
        self._contar()
        if self.respuestas is not None:
            self._tabla(c)
        pie = tk.Frame(c, bg=T.BLANCO)
        pie.pack(fill="x", pady=(14, 0))
        n = sum(self.marcadas.values())
        total = len(self.respuestas or [])
        tk.Label(pie, text=f"{n} de {total} seleccionadas" if self.respuestas is not None else "", font=T.F["cuerpo_b"],
                 bg=T.BLANCO).pack(side="left")
        cuantas = "equivalencia" if all(r.pregunta.tipo == S.INSTITUCION for r in self.respuestas or []
                                        if self.marcadas.get(r.pregunta.id)) else "sugerencia"
        guardar = T.Boton(pie, f"Guardar {n} {cuantas}{'s' if n != 1 else ''}", lambda: self.guardar(),
                          ancho=300)
        guardar.pack(side="right")
        guardar.activar(n > 0)
        T.Boton(pie, "Cancelar", lambda: self.cerrar(self.resultado), tipo="secundario", ancho=140).pack(side="right",
                                                                                                    padx=10)

    def _guardar_texto(self):
        if getattr(self, "caja_respuesta", None) and self.caja_respuesta.winfo_exists():
            self.texto_respuesta = self.caja_respuesta.get("1.0", "end")

    def _contar(self):
        self._guardar_texto()
        self.lbl_pegado.configure(text=f"Pegado: {S.lineas_pegadas(self.texto_respuesta)} líneas")

    def revisar(self, texto=None):
        if texto is not None:
            self.texto_respuesta = texto
        else:
            self._guardar_texto()
        self.respuestas = S.interpretar(self.texto_respuesta, self.enviadas)
        self.marcadas = {r.pregunta.id: r.se_puede_guardar for r in self.respuestas}
        self.pintar()

    def _tabla(self, c):
        cab = tk.Frame(c, bg=T.BLANCO)
        cab.pack(fill="x", pady=(14, 6))
        tk.Label(cab, text=f"Sugerencias ({len(self.respuestas)})", font=T.F["seccion"], bg=T.BLANCO).pack(side="left")
        tk.Label(cab, text="Marca las que quieres guardar", font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS).pack(side="right")
        caja = T.tabla(c, pie=True)
        caja.pack(fill="x")
        anchos = (40, 330, 340, 170)
        h = T.cabecera(caja, padx=12, pady=8)
        h.pack(fill="x")
        for j, (texto, w) in enumerate(zip(("", "El Excel dice", "Gemini propone", "Estado"), anchos)):
            h.grid_columnconfigure(j, minsize=w)
            tk.Label(h, text=texto, font=T.F["pequena_b"], bg=T.GRIS_OSC, fg=T.BLANCO).grid(row=0, column=j, sticky="w")
        lista = T.desplazable(caja, min(300, 52 * len(self.respuestas) + 4))
        lista.pack(fill="x")
        if not self.respuestas:
            tk.Label(lista.interior, text="No se encontró ninguna línea con el formato esperado («I1 → …»). Revisa que "
                                          "pegaste la respuesta completa.", font=T.F["cuerpo"], bg=T.BLANCO,
                     fg=T.GRIS, pady=12).pack()
        for i, r in enumerate(self.respuestas):
            fondo = T.BLANCO if i % 2 == 0 else T.FONDO
            f = tk.Frame(lista.interior, bg=fondo, padx=12, pady=7)
            f.pack(fill="x")
            for j, w in enumerate(anchos):
                f.grid_columnconfigure(j, minsize=w)
            p = r.pregunta
            if r.se_puede_guardar:
                T.Casilla(f, "", self.marcadas.get(p.id, False),
                          lambda v, k=p.id: (self.marcadas.__setitem__(k, v), self.pintar())).grid(row=0, column=0,
                                                                                                    sticky="w")
            dice = p.como_aparece if p.tipo == S.INSTITUCION else f"Columna para «{p.como_aparece}»"
            tk.Label(f, text=dice, font=T.F["cuerpo"], bg=fondo, anchor="w", justify="left",
                     wraplength=anchos[1] - 16).grid(row=0, column=1, sticky="w")
            tk.Label(f, text=r.propuesta or "—", font=T.F["cuerpo"], bg=fondo, anchor="w", justify="left",
                     wraplength=anchos[2] - 16).grid(row=0, column=2, sticky="w")
            texto, tipo = ESTADO_RESPUESTA[r.estado]
            T.chip(f, texto, tipo).grid(row=0, column=3, sticky="w")
        tk.Label(c, text="Las equivalencias que guardes aparecen en Equivalencias de instituciones (origen Gemini) y las "
                         "columnas en Fuentes de datos. «No está en la lista»: Gemini propuso un nombre que no existe en "
                         "la matriz o en el Excel, así que no se puede guardar. Lo que no guardes sigue en Ver revisión.",
                 font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w", justify="left",
                 wraplength=self.ancho - 80).pack(fill="x", pady=(8, 0))

    def guardar(self):
        elegidas = [r for r in self.respuestas if self.marcadas.get(r.pregunta.id)]
        self.resultado = S.guardar_respuestas(self.app.config, elegidas)
        self.app.guardar_config()
        self.cerrar(self.resultado)


# ---------------------------------------------------------------- Confirmar sugerencias del programa (29)
class ModalSugerencias(D.Modal):
    """Devuelve lo que se guardó (lista de frases) o [] si no se guardó nada."""

    def __init__(self, app, duena, avisos, programa, desde, hasta, carpeta=None):
        super().__init__(duena or app.raiz, "Confirmar sugerencias del programa", ancho=1060)
        self.app, self.carpeta = app, carpeta
        self.lista = S.sugerencias_del_programa(avisos, app.config)
        self.instituciones = None
        self.resultado = []
        cab = tk.Frame(self.cuerpo, bg=T.BLANCO)
        cab.pack(fill="x")
        tk.Label(cab, text="Confirmar sugerencias del programa", font=T.F["modal_titulo"], bg=T.BLANCO).pack(side="left")
        T.Ayuda(cab, "sugerencias").pack(side="left", padx=10)
        T.chip(cab, "Solo se guarda lo que marques", "gris").pack(side="right")
        chips = tk.Frame(self.cuerpo, bg=T.BLANCO)
        chips.pack(fill="x", pady=(10, 10))
        for texto in (f"Programa: {programa}", f"Vigencia: {vigencia(desde, hasta)}"):
            T.chip_contexto(chips, texto).pack(side="left", padx=(0, 8))
        T.Franja(self.cuerpo, "info", "Estos nombres no coinciden exactamente, pero se parecen. El programa los propone "
                 "y tú decides: ninguno viene marcado. Lo que no marques sigue como aviso en Ver revisión.").pack(
            fill="x", pady=(0, 12))
        self.contenido = tk.Frame(self.cuerpo, bg=T.BLANCO)
        self.contenido.pack(fill="both", expand=True)
        self.pintar()

    def pintar(self):
        c = self.contenido
        for w in c.winfo_children():
            w.destroy()
        n = sum(s.marcada for s in self.lista)
        cab = tk.Frame(c, bg=T.BLANCO)
        cab.pack(fill="x", pady=(0, 8))
        tk.Label(cab, text=f"{len(self.lista)} sugerencia{'s' if len(self.lista) != 1 else ''}", font=T.F["seccion"],
                 bg=T.BLANCO).pack(side="left")
        tk.Label(cab, text=f"{n} marcada{'s' if n != 1 else ''}", font=T.F["pequena_b"], bg=T.BLANCO,
                 fg=T.VERDE_CTA).pack(side="right")
        muy = T.Enlace(cab, f"Marcar las muy parecidas ({S.MUY_PARECIDA_PCT} % o más)",
                       lambda: (S.marcar_muy_parecidas(self.lista), self.pintar()), fuente="pequena_b")
        muy.pack(side="right", padx=20)
        muy.activar(any(s.muy_parecida and not s.marcada for s in self.lista))
        caja = T.tabla(c, pie=True)
        caja.pack(fill="x")
        anchos = (36, 110, 310, 280, 140)
        h = T.cabecera(caja, padx=12, pady=8)
        h.pack(fill="x")
        for j, (texto, w) in enumerate(zip(("", "Tipo", "Así aparece en el Excel", "El programa propone", "Parecido"),
                                           anchos)):
            h.grid_columnconfigure(j, minsize=w)
            tk.Label(h, text=texto, font=T.F["pequena_b"], bg=T.GRIS_OSC, fg=T.BLANCO).grid(row=0, column=j, sticky="w")
        lista = T.desplazable(caja, min(380, 66 * max(1, len(self.lista))))
        lista.pack(fill="x")
        if not self.lista:
            tk.Label(lista.interior, text="No hay sugerencias pendientes.", font=T.F["cuerpo"], bg=T.BLANCO, fg=T.GRIS,
                     pady=14).pack()
        for i, s in enumerate(self.lista):
            fondo = T.TINTE_VERDE if s.marcada else T.BLANCO
            f = tk.Frame(lista.interior, bg=fondo, padx=12, pady=8)
            f.pack(fill="x")
            for j, w in enumerate(anchos):
                f.grid_columnconfigure(j, minsize=w)
            f.grid_columnconfigure(5, weight=1)
            T.Casilla(f, "", s.marcada, lambda v, x=s: (setattr(x, "marcada", v), self.pintar())).grid(row=0, column=0,
                                                                                                      sticky="w")
            texto, tipo = TIPO[s.tipo]
            T.chip(f, texto, tipo).grid(row=0, column=1, sticky="w")
            a = tk.Frame(f, bg=fondo)
            a.grid(row=0, column=2, sticky="w")
            tk.Label(a, text=f"«{s.como_aparece}»", font=T.F["cuerpo_b"], bg=fondo, anchor="w", justify="left",
                     wraplength=anchos[2] - 16).pack(fill="x")
            tk.Label(a, text=s.donde, font=T.F["pequena"], bg=fondo, fg=T.GRIS, anchor="w", justify="left",
                     wraplength=anchos[2] - 16).pack(fill="x")
            b = tk.Frame(f, bg=fondo)
            b.grid(row=0, column=3, sticky="w")
            tk.Label(b, text=s.propone or "—", font=T.F["cuerpo_b"], bg=fondo, anchor="w", justify="left",
                     wraplength=anchos[3] - 16).pack(fill="x")
            tk.Label(b, text=s.guarda_en, font=T.F["pequena"], bg=fondo, fg=T.GRIS, anchor="w").pack(fill="x")
            T.chip(f, f"{s.parecido} % · {'Muy parecida' if s.muy_parecida else 'Revisa'}",
                   "ok" if s.muy_parecida else "aviso").grid(row=0, column=4, sticky="w")
            T.Enlace(f, "Cambiar ›", lambda x=s: self.cambiar(x), fuente="pequena_b").grid(row=0, column=5, sticky="e")
        tk.Label(c, text="«Cambiar ›» abre la lista para elegir otra opción. Lo que guardes se puede editar o eliminar "
                         "después en Configuración.", font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS,
                 anchor="w").pack(fill="x", pady=(8, 0))
        pie = tk.Frame(c, bg=T.BLANCO)
        pie.pack(fill="x", pady=(14, 0))
        tk.Frame(pie, bg=T.LINEA, height=1).pack(fill="x", pady=(0, 14))
        tk.Label(pie, text=f"Con {n} marcada{'s' if n != 1 else ''}, {n} aviso{'s' if n != 1 else ''} se resuelve"
                           f"{'n' if n != 1 else ''}. Luego pulsa Recargar archivos." if n else
                 "Marca las que sean la misma institución, programa o columna.", font=T.F["pequena"], bg=T.BLANCO,
                 fg=T.GRIS).pack(side="left")
        confirmar = T.Boton(pie, f"Confirmar las {n} marcadas" if n != 1 else "Confirmar la marcada",
                            lambda: self.confirmar(), ancho=280)
        confirmar.pack(side="right")
        confirmar.activar(n > 0)
        T.Boton(pie, "Cancelar", lambda: self.cerrar([]), tipo="secundario", ancho=140).pack(side="right", padx=10)

    def cambiar(self, s):
        if s.tipo == S.INSTITUCION:
            from ..revision import instituciones_de_la_matriz
            from .revision import ElegirInstitucion
            if self.instituciones is None:
                self.instituciones = instituciones_de_la_matriz(self.carpeta, self.app.config) if self.carpeta else []
            eleccion = ElegirInstitucion(self, s.aviso, self.instituciones).mostrar()
        elif s.tipo == S.PROGRAMA:
            eleccion = ElegirDeLista(self, "Elegir programa", s.como_aparece,
                                     [p["nombre"] for p in self.app.config["programas"]], s.propone).mostrar()
        else:
            self.app.abrir_modal("fuentes", self, fuente_id=s.aviso.detalle.get("fuente"), dato=s.aviso.detalle.get("dato"))
            col = next((f["columnas"].get(s.aviso.detalle.get("dato")) for f in self.app.config["fuentes"]
                        if f["id"] == s.aviso.detalle.get("fuente")), None) or {}
            if col.get("elegida"):
                self.lista.remove(s)                  # ya se resolvió en Fuentes de datos
                self.resultado.append(f"«{col['elegida']}» se eligió en Fuentes de datos")
            self.pintar()
            return
        if eleccion:
            s.propone, s.marcada = eleccion, True
            s.parecido = max(s.parecido, 0)
        self.pintar()

    def confirmar(self):
        self.resultado += S.confirmar_marcadas(self.app.config, self.lista)
        self.app.guardar_config()
        self.cerrar(self.resultado)


class ElegirDeLista(D.Modal):
    def __init__(self, duena, titulo, como_aparece, opciones, actual=None):
        super().__init__(duena, titulo, ancho=620)
        tk.Label(self.cuerpo, text=titulo, font=T.F["modal_titulo"], bg=T.BLANCO, anchor="w").pack(fill="x")
        caja = T.Caja(self.cuerpo, fondo=T.FONDO, borde=None, grosor=0, radio=T.RADIO + 2, padx=16, pady=10)
        caja.pack(fill="x", pady=(10, 10))
        tk.Label(caja, text="Así aparece en el Excel", font=T.F["pequena"], bg=T.FONDO, fg=T.GRIS, anchor="w").pack(fill="x")
        tk.Label(caja, text=f"«{como_aparece}»", font=T.F["seccion"], bg=T.FONDO, anchor="w").pack(fill="x")
        self.opciones = T.Opciones(self.cuerpo, [(o, o) for o in opciones], actual)
        self.opciones.pack(fill="x")
        pie = self.botones()
        T.Boton(pie, "Usar este", lambda: self.cerrar(self.opciones.valor()), ancho=150).pack(side="right")
        T.Boton(pie, "Cancelar", lambda: self.cerrar(None), tipo="secundario", ancho=130).pack(side="right", padx=10)
