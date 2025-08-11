import Albion_GLS.Albion_int as alb
import Albion_GLS.Wadiso as wadiso
import tsnet
import numpy as np
from tsnet.network.model import TransientModel

class TsnetInterface:
    
    # Constructor
    def __init__(self, iFileName: str = "default", iIsTimeSime: bool = True, wavespeed:float= 1200., dt:float=0.01, tf:int=25):
        self._filename = iFileName + '.inp'
        
        self._isTimeSim = iIsTimeSime
        
        self._WadisoModel = wadiso.WadisoModel()
        
        if self._isTimeSim:
            alb.RunWadisoCommand("ExportINPTimeSim|"+self._filename)
        else:
            alb.RunWadisoCommand("ExportINPSteadyState|"+self._filename)  
                                       
        self._tm = tsnet.network.TransientModel(self._filename) 
        
        # Set wavespeed
        self._tm.set_wavespeed(wavespeed) # m/s
        
        # Set time options
        self._tm.set_time(tf,dt)
        
        self._results_obj = ''
        
    def Event_Valve_Closure(self,valve_code: str, tc:int=0, ts:int=0,se:int=0,m:int=0, curve=None):
        """Set valve closure rule

        Parameters
        ----------
        name : str
            The name of the valve to close
        rule : list
            Contains paramters to define valve operation rule
            rule = [tc,ts,se,m]
            tc : the duration takes to close the valve [s]
            ts : closure start time [s]
            se : final open percentage [s]
            m  : closure constant [unitless]
        curve: list
            [(open_percentage[i], 1/kl[i]) for i ]
            List of open percentage and the corresponding
            inverse of valve coefficient
        """
        
        rule = [tc, ts, se, m]
        self._tm.valve_closure(valve_code,rule,curve)   
        
    def Event_Valve_Opening(self,valve_code: str, tc:int=0, ts:int=0,se:int=0,m:int=0, curve=None):
        """Set valve opening rule

        Parameters
        ----------
        name : str
            The name of the valve to close
        rule : list
            Contains paramters to define valve operation rule
            rule = [tc,ts,se,m]
            tc : the duration takes to open the valve [s]
            ts : opening start time [s]
            se : final open percentage [s]
            m  : closure constant [unitless]
        curve: list
            [(open_percentage[i], kl[i]) for i ]
            List of open percentage and the corresponding
            valve coefficient
        """
        rule = [tc, ts, se, m]
        self._tm.valve_opening(valve_code,rule,curve)     
        
    def Event_Pump_Shut_Off(self, name, tc:int=1, ts:int=1,se:int=0,m:int=1):
        """Set pump shut off rule

        Parameters
        ----------
        name : str
            The name of the pump to shut off
        rule : list
            Contains paramaters to define valve operation rule
            rule = [tc,ts,se,m]
            tc : the duration takes to close the pump [s]
            ts : closure start time [s]
            se : final open percentage [s]
            m  : closure constant [unitless]
        """
        rule = [tc, ts, se, m]
        self._tm.pump_shut_off(name,rule)  
        
    def Event_Pump_Start_Up(self, name, tc:int=1, ts:int=1,se:int=0,m:int=1):
        """Set pump start up rule

        Parameters
        ----------
        name : str
            The name of the pump to shut off
        rule : list
            Contains paramaters to define valve operation rule
            rule = [tc,ts,se,m]
            tc : the duration takes to close the valve [s]
            ts : closure start time [s]
            se : final open percentage [s]
            m  : closure constant [unitless]
        """
        rule = [tc, ts, se, m]
        self._tm.pump_start_up(name,rule)  
        
    def Event_Add_Demand_Pulse(self, name, tc:int=1, ts:int=1,se:int=0,m:int=1):
        """ Add demand pulse to junction

        Parameters
        ----------
        name : str or list
            The name of junctions to add demand pulse
                rule : list
            Contains paramters to define valve operation rule
        rule = [tc,ts,stay,dp,m]
            tc : total duration of the pulse [s]                                                                                                                                   
            ts : start time of demand [s]
            stay: duration of the demand to stay at peak level [s]
            dp : demand pulse multiplier [uniteless]
        """
        rule = [tc, ts, se, m]
        self._tm.add_demand_pulse(name,rule)
    
    def Event_Add_Open_Surge_Tank(self, name, As):
        """ Add surge tank

        Parameters
        ----------
        name : str
            the name of the node to add a surge tank
        shape : list
            if closed: [As, Ht, Hs]
                As : cross-sectional area of the surge tank
                Ht : tank height
                Hs : initial water height in the surge tank
            if open: [As]
        tank_type : int
            type of the surge tank, "closed" or "open",
            by default 'open'
        """
        shape = [As]
        self._tm.add_surge_tank(name, shape, 'open')
        
    def Event_Add_Closed_SurgeTank(self, name, As, Ht, Hs):
        """ Add surge tank

        Parameters
        ----------
        name : str
            the name of the node to add a surge tank
        shape : list
            if closed: [As, Ht, Hs]
                As : cross-sectional area of the surge tank
                Ht : tank height
                Hs : initial water height in the surge tank
            if open: [As]
        tank_type : int
            type of the surge tank, "closed" or "open",
            by default 'open'
        """
        shape = [As, Ht, Hs]
        self._tm.add_surge_tank(name, shape, 'closed')
        
    def Event_Add_Burst(self, name, ts=1, tc=1, final_burst_coeff=0.01):
        """Add leak to the transient model

        Parameters
        ----------
        name : str
            The name of the leak nodes, by default None
        ts : float
            Burst start time
        tc : float
            Time for burst to fully develop
        final_burst_coeff : list or float
            Final emitter coefficient at the burst nodes
        """
        self._tm.add_burst(name, ts, tc, final_burst_coeff)
        
    def Event_Add_Leak(self, name, coeff=0.01):
        """Add leak to the transient model

        Parameters
        ----------
        name : str, optional
            The name of the leak nodes, by default None
        coeff : list or float, optional
            Emitter coefficient at the leak nodes, by default None
        """
        self._tm.add_leak(name, coeff)
        
    def Event_Add_Blockage(self,name,percentage):
        """Add blockage to the transient model

        Parameters
        ----------
        name : str
            The name of the blockage nodes, by default None
        percentage : list or float
            The percentage of the blockage flow discharge
        """
        self._tm.add_blockage(name,percentage)
        
    
        
    def Initialize(self, t0:float=0.0, engine: str = 'PDD'): 
        # Initialize steady state simulation
        t0 = 0. # initialize the simulation at 0 [s]
        engine = 'PDD' # demand driven simulator
        self._tm = tsnet.simulation.Initializer(self._tm, t0, engine)
        
    def Transient_Simulation_Steady(self, results_obj:str='TnetSteady'): 
        # Transient simulation
        self._results_obj = results_obj # name of the object for saving simulation results
        result = tsnet.simulation.MOCSimulator(self._tm, self._results_obj, 'steady')
        return result
        
    def Transient_Simulation_Quasi(self, results_obj:str='TnetQuasi'): 
        # Transient simulation
        self._results_obj = results_obj # name of the object for saving simulation results
        result = tsnet.simulation.MOCSimulator(self._tm, self._results_obj, 'quasi-steady')
        return result
        
    def Transient_Simulation_Unsteady(self, results_obj:str='TnetUnsteady'): 
        # Transient simulation
        self._results_obj = results_obj # name of the object for saving simulation results
        result = tsnet.simulation.MOCSimulator(self._tm, self._results_obj, 'unsteady')
        return result
    
    def TransientModel(self) -> TransientModel:
        return self._tm
    
    def GetNode(self, iNodeCode):
        return self._tm.get_node(iNodeCode)
    
    def GetLink(self, iLinkCode):
        return self._tm.get_link(iLinkCode)
    
def CompareHeadResults_PDF(iTM1,iTM2, iLabel1, iLabel2, iNodeCode, iFileName):
    import matplotlib.pyplot as plt

    node = iNodeCode

    head1 = iTM1.get_node(node).head
    t1 = iTM1.simulation_timestamps
    
    head2 = iTM2.get_node(node).head
    t2 = iTM2.simulation_timestamps

    fig = plt.figure(figsize=(8,5), dpi=80, facecolor='w', edgecolor='k')
    plt.plot(t1, head1, 'k',label=iLabel1, linewidth=2.5)
    plt.plot(t2, head2, 'b', label=iLabel2,  linewidth=2.5)
    #plt.plot(t3, head3, 'r',label='unsteady', linewidth=2.5)
    plt.xlim([t1[0],t1[-1]])
    plt.xlabel("Time [s]")
    plt.ylabel("Pressure Head [m]")

    fig.savefig(iFileName + '.pdf', format='pdf',dpi=500)
