
import numpy as np
class approx:
    def W_func(m, type):
        if type == "strike-slip":
            return 10**(-0.76+0.27*m)
        elif type == "reverse":
            return 10**(-1.61+0.41*m)
        elif type == "normal":
            return 10**(-1.14+0.35*m)
        else:
            return 10**(-1.01+0.32*m) 

    def Zhyp_func(m, type):
        if type == "strike-slip":
            return 5.63 + 0.68*m
        elif type == "reverse":
            return 11.24 - 0.2*m
        elif type == "normal":
            return 11.24 - 0.2*m
        else:
            return 7.08 + 0.61*m 
        
    def Ztor_func(m, type, θ=None):
        if θ is None:
            if type == "strike-slip":
                θ = np.radian(90)  # or whatever default you want
            elif type == "reverse":
                θ = np.radian(40)
            elif type == "normal":
                θ = np.radian(50)
        if type == "strike-slip":
            W = 10**(-0.76+0.27*m)
            return max((5.63 + 0.68*m)-0.6*W*np.sin(θ), 0)
        elif type == "reverse":
            W = 10**(-1.61+0.41*m)
            return max((11.24 - 0.2*m)-0.6*W*np.sin(θ), 0)
        elif type == "normal":
            W = 10**(-1.14+0.35*m)
            return max((11.24 - 0.2*m)-0.6*W*np.sin(θ), 0)
        else:
            W = 10**(-1.01+0.32*m) 
            return max((7.08 + 0.61*m)-0.6*W*np.sin(θ), 0) 
        
    def Rx_func(Rjb, m, θ_deg, type, Fhw):
        θ = np.radians(θ_deg)
        if Rjb == 0:
            if type == "strike-slip":
                W = 10**(-0.76+0.27*m)
                return 0.5*W*np.cos(θ)
            elif type == "reverse":
                W = 10**(-1.61+0.41*m)
                return 0.5*W*np.cos(θ)
            elif type == "normal":
                W = 10**(-1.14+0.35*m)
                return 0.5*W*np.cos(θ)
            else:
                W = 10**(-1.01+0.32*m) 
                return 0.5*W*np.cos(θ)
        else:
            if type == "strike-slip":
                return Rjb*np.sin(50)
            else:
                if Fhw == 1:
                    return Rjb*np.tan(50)
                else:
                    return Rjb*np.sin(-50)
                
    def Rrup_func(Rjb, Rx, W, Ztor, θ_rad, type):
        θ = np.radians(θ_rad)
        Ry = Rx*np.cot(θ)
        if type == "strike-slip":
            return np.sqrt(Rjb**2 + Ztor**2)
        else:
            if Rx < Ztor*np.tan(θ):
                R = np.sqrt(Rx**2 + Ztor**2)
                return np.sqrt(R**2 + Ry**2)
            elif Ztor*np.tan(θ) <= Rx <= Ztor*np.tan(θ) + W*np.sec(θ):
                R = Rx*np.sin(θ) + Ztor*np.cos(θ)
                return np.sqrt(R**2 + Ry**2)
            else:
                R = np.sqrt((Rx-W*np.cos(θ))**2 + (Ztor+W*np.sin(θ))**2)
                return np.sqrt(R**2 + Ry**2)

    def Z1_AS08(Vs30):
        if Vs30<180:
            return np.exp(6.745)
        elif 180 <= Vs30 < 500:
            return np.exp(6.745 - 1.35*np.log(Vs30/180))
        else:
            return np.exp(5.394 - 4.48*np.log(Vs30/500))
        
    def Z1_CY08(Vs30):
        return np.exp(28.5-3.82/8*np.log(Vs30**8+378.7**8))

    def Rjb_func(lat1, lon1, lat2, lon2, m):   
        R = 6371
        # Convert latitude and longitude from degrees to radians
        lat1 = np.radians(lat1)
        lon1 = np.radians(lon1)
        lat2 = np.radians(lat2)
        lon2 = np.radians(lon2)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        c = 2 * np.atan2(np.sqrt(a), np.sqrt(1 - a))

        # Calculate the distance
        distance = R * c

        K1 = 0.01015
        K2 = 1.04768

        # Step-by-step calculations
        Rrup = K1 * np.exp(K2 * m)
        theta = 2 * np.arcsin(Rrup/ 6371)
        TB = 0.5 * theta/ 2*np.pi * 40028
        dfault = distance - TB

        # Calculate delta
        delta = 0.00724 * (10 ** (0.507 * m))

        # Calculate Rboore
        return np.sqrt(dfault**2 + delta**2)