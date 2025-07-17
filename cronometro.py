import tkinter as tk

class cronocmetro:
    def __init__(self, parent, tiempo_inicial, interval_ms, on_tick, on_timeout):
        """
        parent         -> widget que provee .after y .after_cancel
        tiempo_inicial -> segundos iniciales del cronómetro
        interval_ms    -> intervalo en milisegundos entre ticks
        on_tick        -> callback(segundos_restantes)
        on_timeout     -> callback() al terminar
        """
        self.parent = parent
        self.segundos = tiempo_inicial
        self.interval = interval_ms
        self.on_tick = on_tick
        self.on_timeout = on_timeout
        self._after_id = None
        self.activo = False

    def iniciar(self):
        self.activo = True
        self._tick()

    def _tick(self):
        if not self.activo:
            return
        if self.segundos <= 0:
            self.activo = False
            self._after_id = None
            self.on_timeout()
            return
        self.on_tick(self.segundos)
        self.segundos -= 1
        self._after_id = self.parent.after(self.interval, self._tick)

    def detener(self):
        self.activo = False
        if self._after_id:
            self.parent.after_cancel(self._after_id)
            self._after_id = None