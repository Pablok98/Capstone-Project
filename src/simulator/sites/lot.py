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
        self.name = name
        self.grape = grape_type
        self.__grape_quantity = grape_qty
        self.optimal_day = SimulationObject.current_time + timedelta(days=peak_day - 1)
        self.quality_range = qlty_range
        self.plant_distances = plant_distances

        # Lists of current entities at the lot.
        self.laborers: list[Laborer] = []
        self.harvesters: list[Harvester] = []
        self.bins: list[Bin] = []
        self.trucks: list[Truck] = []
        self.hoppers: list[Hopper] = []
        self.lift_trucks: list[LiftTruck] = []

        # Rain related vars
        self.penalty = 0  # Current quality level (Mu in math model)
        self.is_raining = 0  # Binary var, 1 if it's raining, 0 otherwise

        # Time related vars (t_ suffix)
        self.t_next_crate: Union[datetime, None] = None
        self.t_next_autobin: Union[datetime, None] = None

        # Entity event related vars
        self.attaching_hopper: Union[Hopper, None] = None  # Stores hopper being attached, if any.
        self.loading_bin: Union[Bin, None] = None  # Stores bing being loaded, if any.
        self.working_lift_trucks: list[LiftTruck] = []  # Todo: what it does
        self.flag_bin = True

    # -----------------------------------  General methods  ----------------------------------------

    @property
    def grape_quantity(self) -> int:
        """
        :return: Current grape at the site (in kg)
        """
        return self.__grape_quantity

    @grape_quantity.setter
    def grape_quantity(self, value: int) -> None:
        if value <= 0:
            value = 0
        self.__grape_quantity = value

    @property
    def current_optimal_delta(self) -> int:
        """
        Returns the difference (in days) between the current date and the peak quality date.

        :return: Number of days (absolute)
        """
        delta = SimulationObject.current_time - self.optimal_day
        return delta.days

    @property
    def current_quality(self) -> float:
        """
        Calculates the current quality of the grape at the site.

        :return: Quality of the grape, in point number percentage
        """
        # TODO: clean? Move?
        a = (self.quality_range[0] + self.quality_range[1] - 2) / 98
        b = (self.quality_range[1] - self.quality_range[0]) / 14
        quality = a * (self.current_optimal_delta ** 2) + b * self.current_optimal_delta + 1
        quality = quality * (1 - self.penalty)
        quality = quality if quality <= 1 else 1
        return quality

    # --------------------------------  Assignment methods  ----------------------------------------

    def assign_laborer(self, laborer: Laborer) -> None:
        # Todo: deberia retornar si lo hizo e imprimir en el motor?
        """
        Assigns laborer to the lot, ONLY if the laborer wouldn't surpass the weekly work limit.

        :param laborer: Laborer to be assigned to the lot
        """
        if laborer.days_working < MAX_DIAS_TRABAJO_JORNALERO:
            self.laborers.append(laborer)
            print(f"El jornalero {laborer.id} fue asignado al lote {self.name}")
        else:
            print(f"El jornalero {laborer.id} no pudo ser asignado al lote {self.name}" +
                  "porque excede los dias maximos de trabajo")

    def assign_truck(self, truck) -> None:
        """
        Assigns truck to the lot.

        :param truck: Truck to be assigned to the lot
        """
        truck.current_lot = self
        self.trucks.append(truck)
        print(f"El camion {truck.id} fue asignado al lote {self.name}")

    # --------------------------------  Laborer/Crates  ----------------------------------------
    @property
    def proximo_bin_vacio(self) -> Bin:
        """
        Returns the bin which is currently being filled. If there is none, it creates a new one and
        returns it (said bin is stored in the lot bin list). This method is meant to be called when
        a crate is filled.

        :return: Next bin to be filled (or currently being filled).
        """
        if not self.bins:
            self.bins.append(Bin())  # TODO: agregar restriccion de bines(?)
        _bin = self.bins[-1]
        if _bin.full:
            print(
                f"{self.name} - Se empezó a auto_load un nuevo bin manualmente un bin a la hora {SimulationObject.current_time}")
            _bin = Bin()
            self.bins.append(_bin)
        return _bin

    @property
    def to_load(self) -> Union[Bin, 'Hopper', None]:
        # TODO: this shit sucks
        """
        Devuelve si se va a cargar el cajon al bin o a un tolva
        """
        t_flag = False
        b_flag = False
        for truck in self.trucks:
            if truck.loading_bins:
                b_flag = True
            else:
                t_flag = True
            if t_flag and b_flag:
                break
        else:
            self.flag_bin = b_flag
        if not self.flag_bin and self.hoppers:
            for hopper in self.hoppers:
                if not hopper.full:
                    self.flag_bin = not self.flag_bin
                    return hopper
        self.flag_bin = not self.flag_bin
        return self.proximo_bin_vacio

    def timegen_crate(self) -> None:
        """
        Calculates the time the next crate will be filled, given the current workers at the lot and
        their rate of harvest. The result is then stored for use.
        """
        if not self.laborers or not self.grape_quantity:
            self.t_next_crate = SimulationObject.never_date
            return
        rate = 0
        for laborer in self.laborers:
            rate += laborer.harvest_rate
        time = 60*24*18 / (rate - (rate * 0.3 * self.is_raining))
        self.t_next_crate = SimulationObject.current_time + timedelta(minutes=time)

    @event('t_next_crate', 'timegen_crate')
    def crate_full_event(self) -> None:
        """
        [Event for when a crate is filled]. Generates a new filled crate, which is then loaded into
        either a hopper or bin, depending on what is currently being loaded.
        """
        container = self.to_load
        crate = Crate(self.grape, self.current_quality)
        container.load_crate(crate)
        self.grape_quantity -= 18

        print(f"{self.name} - Se llenó un nuevo cajon a la hora {SimulationObject.current_time}")

    # --------------------------------  Automatic Harvester  ---------------------------------------
    def timegen_bin_fill(self) -> None:
        """
        Calculates the time the next bin will be auto filled, given the current harvester at the lot
        and their rate of harvest. The result is then stored for use.
        """
        if not self.harvesters or not self.grape_quantity:
            self.t_next_autobin = datetime(3000, 1, 1, hour=6, minute=0, second=0)
            return
        rate = 0
        for harvester in self.harvesters:
            rate += harvester.velocidad_cosecha
        time = 60*486 / (rate - (rate * 0.6 * self.is_raining))
        self.t_next_autobin = SimulationObject.current_time + timedelta(minutes=time)

    @event('t_next_autobin', 'timegen_bin_fill')
    def autofill_bin_event(self) -> None:
        """
        [Event for when a bin is filled by a harvester]. Generates a new filled bin, which is added
        to the lot's bins
        """
        _bin = Bin()
        _bin.auto_load(self.grape, self.current_quality)
        self.bins.insert(0, _bin)
        self.grape_quantity -= 18 * 27
        print(f"{self.name} - Se llenó un bin automático a la hora {SimulationObject.current_time}")

    # ---------------------------      Bin Loading      -------------------------------------------
    @property
    def current_loading_truck(self) -> Union[Truck, None]:
        """
        Returns the next truck which has space to load a bin.

        :return: Truck which has to be loaded.
        """
        for truck in self.trucks:
            if not truck.full and truck.loading_bins:
                return truck
        # We return None if no trucks at the site can be loaded.
        return None

    @property
    def t_next_binload(self) -> datetime:
        """
        :return: Time which the next bin would be loaded to a truck.
        """
        # We need to check if there's a lift truck to load the bin
        lift_truck = self.available_lift_truck()
        if not lift_truck:
            return SimulationObject.never_date

        if self.bins and self.bins[0].full:
            if not self.current_loading_truck:
                return SimulationObject.never_date
            if not self.loading_bin:
                self.loading_bin = self.bins[0]
                self.loading_bin.load_time = SimulationObject.current_time + timedelta(minutes=10)
                self.working_lift_trucks.append(lift_truck)
                lift_truck.working = True
            return self.loading_bin.load_time

    def available_lift_truck(self) -> Union['LiftTruck', None]:
        for truck in self.lift_trucks:
            if truck.available:
                return truck
        return None

    def free_lift_truck(self):
        lift_truck = self.working_lift_trucks.pop(0)
        print(f'El montacargas {lift_truck._id} fue desocupado')

    def load_bin_event(self) -> None:
        """
        Se carga el bin al camión y se elimina de la lista de bines. Se actualiza el tiempo.
        """
        SimulationObject.current_time = self.loading_bin.load_time
        self.bins.pop(self.bins.index(self.loading_bin))
        camion = self.current_loading_truck
        camion.bins.append(self.loading_bin)
        self.loading_bin = None
        self.free_lift_truck()

        print(f"{self.name} -Se cargó un bin a la hora {SimulationObject.current_time}")

    # ----------------------------    Truck dispatch      -----------------------------------------
    @property
    def tiempo_proximo_camion(self) -> datetime:
        for camion in self.trucks:
            if camion.full or not self.grape_quantity:
                return SimulationObject.current_time
        return datetime(3000, 1, 1, hour=6, minute=0, second=0)

    def salida_camion(self) -> Truck:
        """
        Se despacha camión y se eliminca de la lista de camiones disp.
        """
        for i, camion in enumerate(self.trucks):
            if camion.full:
                print(
                    f"{self.name} - Se despachó un camión a la hora {SimulationObject.current_time}")
                return self.trucks.pop(i)


        print(f"{self.name} -Se llenó (automatico) un bin a la hora {SimulationObject.current_time}")

    # ---------------------------------------------------------------------------------------
    # Enganche de tolva
    @property
    def tiempo_proximo_tolva(self) -> datetime:
        for tolva in self.hoppers:
            if tolva.full:
                hora = tolva.transport_time
                self.attaching_hopper = tolva
                if hora:
                    return hora
                tolva.transport_time = SimulationObject.current_time + timedelta(minutes=15)
                return tolva.transport_time
        return datetime(3000, 1, 1, hour=6, minute=0, second=0)

    def enganchar_tolva(self) -> None:
        SimulationObject.current_time = self.attaching_hopper.transport_time
        for camion in self.trucks:
            if not camion.loading_bins and camion.can_attach:
                print(f"{self.name} - Se enganchó el tolva {self.attaching_hopper._id} al camion {camion._id} a las {SimulationObject.current_time}")

                camion.hoppers.append(self.attaching_hopper)
                self.hoppers.pop(self.hoppers.index(self.attaching_hopper))
                self.attaching_hopper = None
                break
        else:
            print(f"{self.name} - Hay un carro tolva que no se puede enganchar")
            self.attaching_hopper.transport_time = None
    # ----------------------------------------------------------------------------------------
    # Manejo de eventos
    @property
    def proximo_evento(self) -> tuple[str, str, datetime]:
        """
        Retorna el proximo evento a ocurrir (segun fecha)
        """
        tiempos = [
            self.t_next_crate,
            self.t_next_binload,
            self.tiempo_proximo_camion,
            self.t_next_autobin,
            self.tiempo_proximo_tolva
        ]
        tiempo_prox_evento = min(tiempos)
        eventos = ['llenar_cajon', 'cargar_bin', 'salida_camion', 'bin_lleno', 'enganchar_tolva']
        return self.name, eventos[tiempos.index(tiempo_prox_evento)], tiempo_prox_evento

    def resolver_evento(self, evento: str):# -> Union[Truck, None]:
        metodos = {
            'llenar_cajon': self.crate_full_event,
            'cargar_bin': self.load_bin_event,
            'salida_camion': self.salida_camion,
            'bin_lleno': self.autofill_bin_event,
            'enganchar_tolva': self.enganchar_tolva
        }
        return metodos[evento]()

    def llover(self, lluvia: int) -> None:
        self.is_raining = lluvia
        if lluvia:
            self.penalizar()

    def penalizar(self) -> None:
        if 0.98 <= self.current_quality <= 1:
            self.penalty += 0.1
        elif 0.95 <= self.current_quality < 0.98:
            self.penalty += 0.07
        elif 0.90 <= self.current_quality < 0.95:
            self.penalty += 0.05
        else:
            self.penalty += 0.03

    def iniciar_dia(self) -> None:
        self.t_next_crate = None
        self.t_next_autobin = None
        self.attaching_hopper = None
        self.loading_bin = None
        self.flag_bin = True
        self.timegen_crate()
        self.timegen_bin_fill()

    def fin_dia(self) -> None:
        for jornalero in self.laborers:
            jornalero.days_working += 1

        self.laborers = []
        self.harvesters = []

    @property
    def estado(self) -> dict:
        ctd_jornaleros = len(self.laborers)
        tasa = 0
        for jornalere in self.laborers:
            tasa += jornalere.harvest_rate
        tasa_jornaleros = (tasa - (tasa * 0.3 * self.is_raining)) / 60 * 24

        ctd_cosechadoras = len(self.harvesters)
        tasa = 0
        for cosechadere in self.harvesters:
            tasa += cosechadere.velocidad_cosecha
        tasa_cosechadoras = (tasa - (tasa * 0.6 * self.is_raining)) / 60

        ctd_bines = len(self.bins)
        ctd_tolvas = len(self.hoppers)
        ctd_camiones = len(self.trucks)
        camiones = {}
        for camion in self.trucks:
            camiones[camion.id] = camion.state()

        data = {
            'nombre_lote': self.name,
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
        ctd_jornaleros = len(self.laborers)
        tasa = 0
        for jornalere in self.laborers:
            tasa += jornalere.harvest_rate
        tasa_jornaleros = (tasa - (tasa * 0.3 * self.is_raining)) / 60 * 24

        ctd_cosechadoras = len(self.harvesters)
        tasa = 0
        for cosechadere in self.harvesters:
            tasa += cosechadere.velocidad_cosecha
        tasa_cosechadoras = (tasa - (tasa * 0.6 * self.is_raining)) / 60

        ctd_bines = len(self.bins)
        ctd_tolvas = len(self.hoppers)
        ctd_camiones = len(self.trucks)
        camiones = ""
        for camion in self.trucks:
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
        //          Lote: {self.name}            //
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






