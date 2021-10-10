from datetime import datetime, timedelta
from typing import Union
from src.params import MAX_DIAS_TRABAJO_JORNALERO
from ..entities import *
from ..sim import SimulationObject, event


class Lot(SimulationObject):
    def __init__(self,
                 name: str, grape_type: int, grape_qty: int, peak_day: int,
                 qlty_range: list[float], plant_distances: dict):
        """
        Represents a lot site.

        :param name: MUST be unique. Name of the lot, which will used by the simulator to both
                    display and reference.
        :param grape_type: Type of the grape grown in the lot (represented by a number from 1 to 8).
        :param grape_qty: Quantity of grape being grown in the lot (in kg).
        :param peak_day: Day that the grape will be at peak quality (represented by the number of
                        days from the initial simulated day).
        :param qlty_range: Range of quality while in the veraison.
        :param plant_distances: Dictionary of distances from the lot to the processing plants.
        """
        self.nombre = name
        self.tipo_uva = grape_type
        self.__cantidad_uva = grape_qty
        self.dia_optimo = SimulationObject.tiempo_actual + timedelta(days=peak_day-1)
        self.rango_calidad = qlty_range
        self.plant_distances = plant_distances

        # Lists of current entities at the lot.
        self.jornaleros: list[Laborer] = []
        self.cosechadoras: list[Harvester] = []
        self.bines: list[Bin] = []
        self.camiones: list[Truck] = []
        self.tolvas: list[Hopper] = []
        self.montacargas: list[LiftTruck] = []

        # Rain related vars
        self.penalizacion = 0  # Current quality level (Mu in math model)
        self.lloviendo = 0  # Binary var, 1 if it's raining

        # Time related vars
        self.tiempo_proximo_cajon: Union[datetime, None] = None
        self.tiempo_proximo_binlleno: Union[datetime, None] = None

        # Entities events related vars
        self.tolva_a_enganchar: Union[Hopper, None] = None
        self.bin_a_cargar: Union[Bin, None] = None
        self.working_lifttrucks: list[LiftTruck] = []
        self.flag_bin = True

    # -----------------------------------  General methods  ----------------------------------------
    @property
    def cantidad_uva(self) -> int:
        """
        :return: Current grape at the site (in kg)
        """
        return self.__cantidad_uva

    @cantidad_uva.setter
    def cantidad_uva(self, value: int):
        if value <= 0:
            value = 0
        self.__cantidad_uva = value

    @property
    def delta_optimo(self) -> int:
        """
        Returns the difference (in days) between the current date and the peak quality date.

        :return: Number of days (absolute)
        """
        delta = SimulationObject.tiempo_actual - self.dia_optimo
        return delta.days

    @property
    def calidad_actual(self) -> float:
        """
        Calculates the current quality of the grape at the site.

        :return: Quality of the grape, in point number percentage
        """
        a = (self.rango_calidad[0] + self.rango_calidad[1] - 2) / 98
        b = (self.rango_calidad[1] - self.rango_calidad[0]) / 14
        calidad = a * (self.delta_optimo**2) + b * self.delta_optimo + 1
        calidad = calidad * (1 - self.penalizacion)
        calidad = calidad if calidad <= 1 else 1
        return calidad

    # --------------------------------  Assignment methods  ----------------------------------------
    def asignar_jornalero(self, laborer: Laborer) -> None:
        # Todo: deberia retornar silo hizo e imprimir en el motor?
        """
        Assigns laborer to the lot, ONLY if the laborer wouldn't surpass the weekly work limit.

        :param laborer: Laborer to be assigned to the lot
        """
        if laborer.days_working < MAX_DIAS_TRABAJO_JORNALERO:
            self.jornaleros.append(laborer)
            print(f"El jornalero {laborer.id} fue asignado al lote {self.nombre}")
        else:
            print(f"El jornalero {laborer.id} no pudo ser asignado al lote {self.nombre}" +
                  "porque excede los dias maximos de trabajo")

    def assign_truck(self, truck) -> None:
        """
        Assigns truck to the lot.

        :param truck: Truck to be assigned to the lot
        """
        truck.current_lot = self
        self.camiones.append(truck)
        print(f"El camion {truck.id} fue asignado al lote {self.nombre}")

    # --------------------------------  Laborer/Crates  ----------------------------------------
    @property
    def proximo_bin_vacio(self) -> Bin:
        """
        Returns the bin which is currently being filled. If there is none, it creates a new one and
        returns it (said bin is stored in the lot bin list). This method is meant to be called when
        a crate is filled.

        :return: Next bin to be filled (or currently being filled).
        """
        if not self.bines:
            self.bines.append(Bin())  # TODO: agregar restriccion de bines(?)
        _bin = self.bines[-1]
        if _bin.full:
            print(
                f"{self.nombre} - Se empezó a auto_load un nuevo bin manualmente un bin a la hora {SimulationObject.tiempo_actual}")
            _bin = Bin()
            self.bines.append(_bin)
        return _bin

    @property
    def a_cargar(self): #-> Union[Bin, Hopper, None]:
        # TODO: this shit sucks
        """
        Devuelve si se va a cargar el cajon al bin o a un tolva
        """
        t_flag = False
        b_flag = False
        for camion in self.camiones:
            if camion.loading_bins:
                b_flag = True
            else:
                t_flag = True
            if t_flag and b_flag:
                break
        else:
            self.flag_bin = b_flag
        if not self.flag_bin and self.tolvas:
            for tolva in self.tolvas:
                if not tolva.full:
                    self.flag_bin = not self.flag_bin
                    return tolva
        self.flag_bin = not self.flag_bin
        return self.proximo_bin_vacio

    def generar_tiempo_cajon(self) -> None:
        """
        Calculates the time the next crate will be filled, given the current workers at the lot and
        their rate of harvest. The result is then stored for use.
        """
        if not self.jornaleros or not self.cantidad_uva:
            self.tiempo_proximo_cajon = SimulationObject.neverdate
            return
        rate = 0
        for laborer in self.jornaleros:
            rate += laborer.harvest_rate
        time = 60*24*18 / (rate - (rate * 0.3 * self.lloviendo))
        self.tiempo_proximo_cajon = SimulationObject.tiempo_actual + timedelta(minutes=time)

    @event('tiempo_proximo_cajon')
    def cajon_lleno(self) -> None:
        """
        [Event for when a crate is filled]. Generates a new filled crate, which is then loaded into
        either a hopper or bin, depending on what is currently being loaded.
        """
        SimulationObject.tiempo_actual = self.tiempo_proximo_cajon
        self.generar_tiempo_cajon()
        lugar_a_cargar = self.a_cargar
        cajon = Crate(self.tipo_uva, self.calidad_actual)
        lugar_a_cargar.load_crate(cajon)
        self.cantidad_uva -= 18

        print(f"{self.nombre} - Se full un nuevo cajon a la hora {SimulationObject.tiempo_actual}")

    # --------------------------------  Automatic Harvester  ---------------------------------------
    def generar_tiempo_bin(self) -> None:
        if not self.cosechadoras or not self.cantidad_uva:
            self.tiempo_proximo_binlleno = datetime(3000, 1, 1, hour=6, minute=0, second=0)
            return
        tasa = 0
        for cosechadore in self.cosechadoras:
            tasa += cosechadore.velocidad_cosecha
        tiempo = 60*486 / (tasa - (tasa * 0.6 * self.lloviendo))
        self.tiempo_proximo_binlleno = SimulationObject.tiempo_actual + timedelta(minutes=tiempo)

    def llenar_bin(self) -> None:
        """
        EVENTO COSECHADORA LLENA UN BIN
        """
        SimulationObject.tiempo_actual = self.tiempo_proximo_binlleno
        self.generar_tiempo_bin()
        _bin = Bin()
        _bin.auto_load(self.tipo_uva, self.calidad_actual)
        self.bines.insert(0, _bin)
        self.cantidad_uva -= 18*27
        print(f"{self.nombre} - Se llenó un bin automático a la hora {SimulationObject.tiempo_actual}")

    # --------------------------------------------------------------------------------------
    # Carga de bines a camiones
    @property
    def proximo_camion_vacio(self):# -> Union[Truck, None]:
        """
        Retorna el proximo camión que tiene espacio para un bin
        """
        for camion in self.camiones:
            if not camion.full and camion.loading_bins:
                return camion
        #print("No hay camiones con espacio disponible!")
        return None

    @property
    def tiempo_proximo_bin(self) -> datetime:
        """
        Retorna el tiempo en que se carga el próximo bin (fecha)
        """
        # Si es que hay bines y el último está full (si no, nada se va a unload)
        lifttruck = self.find_available_lifttruck()

        if lifttruck:
            if self.bines and self.bines[0].full:
                if not self.proximo_camion_vacio:
                    return SimulationObject.neverdate
                if not self.bin_a_cargar:
                    self.bin_a_cargar = self.bines[0]
                    self.bin_a_cargar.load_time = SimulationObject.tiempo_actual + timedelta(minutes=10)
                    self.working_lifttrucks.append(lifttruck)
                    lifttruck.working = True
                return self.bin_a_cargar.load_time

        return SimulationObject.neverdate

    def find_available_lifttruck(self):
        for m in self.montacargas:
            if m.available:
                return m
        return None

    def free_lifttruck(self):
        lifttruck = self.working_lifttrucks.pop(0)
        print(f'El montacargas {lifttruck._id} fue desocupado')

    def carga_bin(self) -> None:
        """
        Se carga el bin al camión y se elimina de la lista de bines. Se actualiza el tiempo.
        """
        SimulationObject.tiempo_actual = self.bin_a_cargar.load_time
        self.bines.pop(self.bines.index(self.bin_a_cargar))
        camion = self.proximo_camion_vacio
        camion.bins.append(self.bin_a_cargar)
        self.bin_a_cargar = None
        self.free_lifttruck()

        print(f"{self.nombre} -Se cargó un bin a la hora {SimulationObject.tiempo_actual}")
    # ------------------------------------------------------------------------------------------
    # Despacho de camiones
    @property
    def tiempo_proximo_camion(self) -> datetime:
        for camion in self.camiones:
            if camion.full or not self.cantidad_uva:
                return SimulationObject.tiempo_actual
        return datetime(3000, 1, 1, hour=6, minute=0, second=0)

    def salida_camion(self):# -> Truck:
        """
        Se despacha camión y se eliminca de la lista de camiones disp.
        """
        for i, camion in enumerate(self.camiones):
            if camion.full:
                print(
                    f"{self.nombre} - Se despachó un camión a la hora {SimulationObject.tiempo_actual}")
                return self.camiones.pop(i)


        print(f"{self.nombre} -Se llenó (automatico) un bin a la hora {SimulationObject.tiempo_actual}")

    # ---------------------------------------------------------------------------------------
    # Enganche de tolva
    @property
    def tiempo_proximo_tolva(self) -> datetime:
        for tolva in self.tolvas:
            if tolva.full:
                hora = tolva.transport_time
                self.tolva_a_enganchar = tolva
                if hora:
                    return hora
                tolva.transport_time = SimulationObject.tiempo_actual + timedelta(minutes=15)
                return tolva.transport_time
        return datetime(3000, 1, 1, hour=6, minute=0, second=0)

    def enganchar_tolva(self) -> None:
        SimulationObject.tiempo_actual = self.tolva_a_enganchar.transport_time
        for camion in self.camiones:
            if not camion.loading_bins and camion.can_attach:
                print(f"{self.nombre} - Se enganchó el tolva {self.tolva_a_enganchar._id} al camion {camion._id} a las {SimulationObject.tiempo_actual}")

                camion.hoppers.append(self.tolva_a_enganchar)
                self.tolvas.pop(self.tolvas.index(self.tolva_a_enganchar))
                self.tolva_a_enganchar = None
                break
        else:
            print(f"{self.nombre} - Hay un carro tolva que no se puede enganchar")
            self.tolva_a_enganchar.transport_time = None
    # ----------------------------------------------------------------------------------------
    # Manejo de eventos
    @property
    def proximo_evento(self) -> tuple[str, str, datetime]:
        """
        Retorna el proximo evento a ocurrir (segun fecha)
        """
        tiempos = [
            self.tiempo_proximo_cajon,
            self.tiempo_proximo_bin,
            self.tiempo_proximo_camion,
            self.tiempo_proximo_binlleno,
            self.tiempo_proximo_tolva
        ]
        tiempo_prox_evento = min(tiempos)
        eventos = ['llenar_cajon', 'cargar_bin', 'salida_camion', 'bin_lleno', 'enganchar_tolva']
        return self.nombre, eventos[tiempos.index(tiempo_prox_evento)], tiempo_prox_evento

    def resolver_evento(self, evento: str):# -> Union[Truck, None]:
        metodos = {
            'llenar_cajon': self.cajon_lleno,
            'cargar_bin': self.carga_bin,
            'salida_camion': self.salida_camion,
            'bin_lleno': self.llenar_bin,
            'enganchar_tolva': self.enganchar_tolva
        }
        return metodos[evento]()

    def llover(self, lluvia: int) -> None:
        self.lloviendo = lluvia
        if lluvia:
            self.penalizar()

    def penalizar(self) -> None:
        if 0.98 <= self.calidad_actual <= 1:
            self.penalizacion += 0.1
        elif 0.95 <= self.calidad_actual < 0.98:
            self.penalizacion += 0.07
        elif 0.90 <= self.calidad_actual < 0.95:
            self.penalizacion += 0.05
        else:
            self.penalizacion += 0.03

    def iniciar_dia(self) -> None:
        self.tiempo_proximo_cajon = None
        self.tiempo_proximo_binlleno = None
        self.tolva_a_enganchar = None
        self.bin_a_cargar = None
        self.flag_bin = True
        self.generar_tiempo_cajon()
        self.generar_tiempo_bin()

    def fin_dia(self) -> None:
        for jornalero in self.jornaleros:
            jornalero.days_working += 1

        self.jornaleros = []
        self.cosechadoras = []

    @property
    def estado(self) -> dict:
        ctd_jornaleros = len(self.jornaleros)
        tasa = 0
        for jornalere in self.jornaleros:
            tasa += jornalere.harvest_rate
        tasa_jornaleros = (tasa - (tasa * 0.3 * self.lloviendo)) / 60*24

        ctd_cosechadoras = len(self.cosechadoras)
        tasa = 0
        for cosechadere in self.cosechadoras:
            tasa += cosechadere.velocidad_cosecha
        tasa_cosechadoras = (tasa - (tasa * 0.6 * self.lloviendo)) / 60

        ctd_bines = len(self.bines)
        ctd_tolvas = len(self.tolvas)
        ctd_camiones = len(self.camiones)
        camiones = {}
        for camion in self.camiones:
            camiones[camion.id] = camion.state()

        data = {
            'nombre_lote': self.nombre,
            'ctd_jornaleros': ctd_jornaleros,
            'tasa_jornaleros': tasa_jornaleros,
            'ctd_cosechadoras': ctd_cosechadoras,
            'tasa_cosechadoras': tasa_cosechadoras,
            'ctd_bines': ctd_bines,
            'ctd_tolvas': ctd_tolvas,
            'ctd_camiones': ctd_camiones,
            'camiones': camiones
        }
        return data

    @property
    def estado_string(self) -> str:
        # De aca eliminar y cambiar por sacar el diccionario de state
        ctd_jornaleros = len(self.jornaleros)
        tasa = 0
        for jornalere in self.jornaleros:
            tasa += jornalere.harvest_rate
        tasa_jornaleros = (tasa - (tasa * 0.3 * self.lloviendo)) / 60*24

        ctd_cosechadoras = len(self.cosechadoras)
        tasa = 0
        for cosechadere in self.cosechadoras:
            tasa += cosechadere.velocidad_cosecha
        tasa_cosechadoras = (tasa - (tasa * 0.6 * self.lloviendo)) / 60

        ctd_bines = len(self.bines)
        ctd_tolvas = len(self.tolvas)
        ctd_camiones = len(self.camiones)
        camiones = ""
        for camion in self.camiones:
            estado = camion.state()
            string_camion = f"""
            * Camion {estado['id']} *
            Tipo:                 {estado['tipo']}
            Capacidad:            {estado['capacidad']}
            Nivel de ocupacion:   {estado['ocupacion']}
            """
            camiones += string_camion
        # Hasta aca
        string = f"""
        _____________________________________________
        //          Lote: {self.nombre}            //
        ---------------------------------------------
        ***************   General  ******************
        Jornaleros trabajando:       {ctd_jornaleros}
        Tasa de cosecha jornaleros: {tasa_jornaleros} kg/min
        
        Cosechadoras automáticas:     {ctd_cosechadoras}
        Tasa de cosecha cosechadoras : {tasa_cosechadoras} kg/min
        
        Bines en el sitio:             {ctd_bines}
        Tolvas en el sitio:            {ctd_tolvas}
        
        ***************   Camiones  ******************
        Camiones en sitio:              {ctd_camiones}
        {camiones}
        """
        return string






