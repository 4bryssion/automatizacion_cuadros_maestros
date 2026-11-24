"""Reglas de cruce (mockup 19). Vienen confirmadas por la jefatura; lo que se cambie queda marcado «Cambiada» y se
puede restablecer regla por regla o todas. Solo se ofrecen opciones que el motor de cruce sabe aplicar; lo que no se
puede cambiar se muestra con candado."""
from __future__ import annotations

import tkinter as tk

from .. import ajustes as A
from ..configuracion.valores_iniciales import REGLAS_CONFIRMADAS
from . import dialogos as D
from . import tema as T
from .configuracion import reglas_cambiadas

ENTRAN = [("con_o_sin_resultados", "Entran con o sin resultados"), ("solo_con_resultados", "Solo si tienen resultados")]
PREFERIDO = [("especifico", "Específico"), ("marco", "Marco"), ("ninguno", "Ninguno (cualquiera)")]
DESEMPATE = [("inicio_mas_reciente", "El de inicio más reciente"), ("inicio_mas_antiguo", "El de inicio más antiguo")]
FECHA_FIN = [("inicio_mas_vigencia", "Año de inicio + vigencia en años"), ("revision", "Enviar a Ver revisión")]

REGLAS = [
    ("r1_convenios_que_entran", "Qué convenios entran al cuadro",
     "Un convenio entra si la columna de su programa en la matriz dice que aplica."),
    ("r2_asignacion", "A qué convenio va cada registro",
     "El cruce se hace por el nombre de la institución. Cada registro se asigna a un solo convenio."),
    ("r3_conteo", "Qué se cuenta", "Cuántas unidades suma cada fuente al resultado de un convenio."),
    ("r4_fecha_fin", "Vigencia y fecha de fin", "De dónde sale la vigencia cuando la fecha de fin no es una fecha usable."),
    ("r5_activo", "Activo o No activo", "Cómo se decide la columna Activo del cuadro."),
]


class ModalReglas(D.Modal):
    def __init__(self, app, duena=None):
        super().__init__(duena or app.raiz, "Reglas de cruce", ancho=1000)
        self.app = app
        self.contenido = tk.Frame(self.cuerpo, bg=T.BLANCO)
        self.contenido.pack(fill="both", expand=True)
        self.controles = {}
        self.pintar()

    @property
    def reglas(self):
        return self.app.config["reglas"]

    def cambio(self):
        self.app.guardar_config()
        posicion = self.marco.lienzo.yview()[0] if hasattr(self, "marco") else 0
        self.pintar()
        self.update_idletasks()
        self.marco.lienzo.yview_moveto(posicion)

    def poner(self, clave, campo, valor):
        self.reglas[clave][campo] = valor
        self.cambio()

    def pintar(self):
        c = self.contenido
        for w in c.winfo_children():
            w.destroy()
        n = reglas_cambiadas(self.app.config)
        cab = tk.Frame(c, bg=T.BLANCO)
        cab.pack(fill="x")
        tk.Label(cab, text="Reglas de cruce", font=T.F["modal_titulo"], bg=T.BLANCO).pack(side="left")
        T.Ayuda(cab, "reglas").pack(side="left", padx=10)
        T.chip(cab, f"5 reglas · {n} cambiada{'s' if n != 1 else ''}" if n else "5 reglas · confirmadas",
               "aviso" if n else "ok").pack(side="right")
        tk.Label(c, text="Definen qué convenios entran al cuadro, a cuál se asigna cada registro y qué se cuenta. Vienen "
                         "confirmadas por la jefatura. Cámbialas solo si la regla cambió; lo que cambies queda marcado.",
                 font=T.F["cuerpo"], bg=T.BLANCO, anchor="w", justify="left",
                 wraplength=self.ancho - 80).pack(fill="x", pady=(8, 12))
        self.marco = T.desplazable(c, 560)
        self.marco.pack(fill="both", expand=True)
        for i, (clave, titulo, texto) in enumerate(REGLAS, start=1):
            self._tarjeta(self.marco.interior, i, clave, titulo, texto)
        pie = tk.Frame(c, bg=T.BLANCO)
        pie.pack(fill="x", pady=(14, 0))
        tk.Frame(pie, bg=T.LINEA, height=1).pack(fill="x", pady=(0, 14))
        todas = T.Boton(pie, "Restablecer todas a lo confirmado", self.restablecer_todas, tipo="secundario", ancho=330)
        todas.pack(side="left")
        todas.activar(bool(n))
        ver = T.Boton(pie, "Ver cómo se aplican", None, tipo="secundario", ancho=220)
        ver.pack(side="left", padx=12)
        ver.activar(False)
        T.Boton(pie, "Listo", lambda: self.cerrar(True), ancho=160).pack(side="right")
        tk.Label(c, text="Los cambios se guardan al instante. «Ver cómo se aplican» llega en la próxima versión; mientras "
                         "tanto, usa Previsualizar cuadro.", font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS,
                 anchor="w").pack(fill="x", pady=(8, 0))

    def restablecer(self, clave=None):
        A.restablecer_reglas(self.app.config, clave)
        self.cambio()

    def restablecer_todas(self):
        if D.aviso(self, "Restablecer las reglas", "aviso", "Las cinco reglas vuelven a como las confirmó la jefatura. "
                   "Lo que cambiaste se pierde (queda en las copias de seguridad).",
                   [("Restablecer todas", "ok", "primario"), ("Cancelar", "cancelar", "secundario")]) == "ok":
            self.restablecer()

    def _tarjeta(self, padre, n, clave, titulo, texto):
        cambiada = A.regla_cambiada(self.app.config, clave)
        borde = tk.Frame(padre, bg=T.NARANJA if cambiada else T.LINEA, padx=2 if cambiada else 1,
                         pady=2 if cambiada else 1)
        borde.pack(fill="x", pady=(0, 12), padx=(0, 8))
        t = tk.Frame(borde, bg=T.BLANCO, padx=22, pady=14)
        t.pack(fill="both")
        cab = tk.Frame(t, bg=T.BLANCO)
        cab.pack(fill="x")
        num = tk.Canvas(cab, width=32, height=32, bg=T.BLANCO, highlightthickness=0)
        num.create_oval(1, 1, 31, 31, fill=T.VERDE_CTA, outline=T.VERDE_CTA)
        num.create_text(16, 16, text=str(n), fill=T.BLANCO, font=T.F["cuerpo_b"])
        num.pack(side="left")
        tk.Label(cab, text=titulo, font=T.F["seccion"], bg=T.BLANCO).pack(side="left", padx=12)
        if cambiada:
            T.chip(cab, "Cambiada", "aviso").pack(side="right")
            T.Enlace(cab, "Restablecer a lo confirmado", lambda: self.restablecer(clave),
                     fuente="pequena_b").pack(side="right", padx=12)
        else:
            T.chip(cab, f"Confirmada · {A.fecha_confirmada(self.app.config)}", "ok").pack(side="right")
        tk.Label(t, text=texto, font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w").pack(fill="x", pady=(4, 6))
        getattr(self, f"_{clave[:2]}")(t, clave)

    def _fila(self, t, texto, primera=False):
        if not primera:
            tk.Frame(t, bg="#EBEBEB", height=1).pack(fill="x")
        f = tk.Frame(t, bg=T.BLANCO, pady=8)
        f.pack(fill="x")
        tk.Label(f, text=texto, font=T.F["cuerpo"], bg=T.BLANCO, anchor="w", justify="left",
                 wraplength=470).pack(side="left")
        der = tk.Frame(f, bg=T.BLANCO, width=440, height=42)
        der.pack(side="right")
        der.pack_propagate(False)
        return der, f

    def _opciones(self, t, texto, clave, campo, pares, editable=False, primera=False):
        der, _ = self._fila(t, texto, primera)
        valor = self.reglas[clave].get(campo)
        confirmado = REGLAS_CONFIRMADAS[clave].get(campo)
        o = T.Opciones(der, pares, valor, lambda v: self.poner(clave, campo, v), editable=editable)
        if valor != confirmado:
            o.configure(style="Cambiada.CM.TCombobox")
        o.pack(fill="both", expand=True)
        self.controles[(clave, campo)] = o
        return o

    def _interruptor(self, t, texto, clave, campo):
        _, f = self._fila(t, texto)
        f.winfo_children()[-1].destroy()
        i = T.Interruptor(f, self.reglas[clave].get(campo, True), lambda v: self.poner(clave, campo, v))
        i.pack(side="right")
        self.controles[(clave, campo)] = i

    def _bloqueado(self, t, texto, valor):
        der, _ = self._fila(t, texto)
        T.campo_bloqueado(der, valor).pack(fill="both", expand=True)

    def _r1(self, t, clave):
        valores = ["APLICA"] + [x for x in [self.reglas[clave]["valor_aplica"]] if x != "APLICA"]
        self._opciones(t, "Valor que significa que aplica", clave, "valor_aplica", [(v, v) for v in valores],
                       editable=True, primera=True)
        self._opciones(t, "Convenios vigentes", clave, "vigentes", ENTRAN)
        self._opciones(t, "Convenios vencidos", clave, "vencidos", ENTRAN)

    def _r2(self, t, clave):
        primera = tk.Frame(t, bg=T.BLANCO)
        primera.pack(fill="x")
        f = tk.Frame(primera, bg=T.BLANCO, pady=8)
        f.pack(fill="x")
        tk.Label(f, text="Solo cuenta dentro de los años de vigencia del convenio (inicio y fin incluidos)",
                 font=T.F["cuerpo"], bg=T.BLANCO, anchor="w", justify="left", wraplength=560).pack(side="left")
        i = T.Interruptor(f, self.reglas[clave]["solo_dentro_de_vigencia"],
                          lambda v: self.poner(clave, "solo_dentro_de_vigencia", v))
        i.pack(side="right")
        self.controles[(clave, "solo_dentro_de_vigencia")] = i
        self._opciones(t, "Movilidad prefiere el convenio", clave, "preferido_movilidad", PREFERIDO)
        self._opciones(t, "Internacionalización en casa prefiere el convenio", clave, "preferido_internacionalizacion",
                       PREFERIDO)
        self._opciones(t, "Si sigue habiendo empate, gana", clave, "desempate", DESEMPATE)
        nota = tk.Frame(t, bg=T.FONDO, padx=12, pady=8)
        nota.pack(fill="x", pady=(6, 0))
        T.icono(nota, "gris", 18, bg=T.FONDO).pack(side="left", anchor="n")
        tk.Label(nota, text="Si la institución no tiene ningún convenio que cubra el año del registro, se omite y se "
                            "lista en Ver revisión. Esta parte no se puede cambiar.", font=T.F["pequena"], bg=T.FONDO,
                 anchor="w", justify="left", wraplength=820).pack(side="left", padx=8)

    def _r3(self, t, clave):
        der, _ = self._fila(t, "Movilidad cuenta", primera=True)
        T.campo_bloqueado(der, "Movilidades (una por fila)").pack(fill="both", expand=True)
        self._bloqueado(t, "Internacionalización en casa cuenta", "Actividades (una por fila)")
        self._interruptor(t, "Una fila con varios programas cuenta para cada uno de ellos", clave,
                          "varios_programas_cuentan_para_cada_uno")
        tk.Label(t, text="Si se apaga, la fila cuenta solo para el primer programa que lista.", font=T.F["pequena"],
                 bg=T.BLANCO, fg=T.GRIS, anchor="w").pack(fill="x")

    def _r4(self, t, clave):
        self._opciones(t, "Si la fecha de fin es texto (INDEFINIDO), está vacía o es solo un año", clave, "si_no_es_fecha",
                       FECHA_FIN, primera=True)
        self._bloqueado(t, "Si no hay una fecha de inicio válida", "Enviar a Ver revisión")

    def _r5(self, t, clave):
        der, _ = self._fila(t, "Se decide según", primera=True)
        T.campo_bloqueado(der, "El estado de la matriz el día de generar").pack(fill="both", expand=True)
        r5 = self.reglas[clave]
        self._bloqueado(t, f"«{', '.join(r5['valores_activo'])}» en la matriz se escribe", r5["etiqueta_activo"])
        self._bloqueado(t, f"«{', '.join(r5['valores_no_activo'])}» se escribe", r5["etiqueta_no_activo"])
