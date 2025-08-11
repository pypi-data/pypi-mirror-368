import numpy as np
import pandas as pd

class BCHydro:
    def __init__(self):
        # Load coefficients
        self.coeff_df = pd.DataFrame({
            "T": [0, 0.02, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.75, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7.5, 10],
            "Vlin": [865.1, 865.1, 1053.5, 1085.7, 1032.5, 877.6, 748.2, 654.3, 587.1, 503, 456.6, 430.3, 410.5, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400],
            "b": [-1.186, -1.186, -1.346, -1.471, -1.624, -1.931, -2.188, -2.381, -2.518, -2.657, -2.669, -2.599, -2.401, -1.955, -1.025, -0.299, 0, 0, 0, 0, 0, 0, 0],
            "θ1": [4.2203, 4.2203, 4.5371, 5.0733, 5.2892, 5.4563, 5.2684, 5.0594, 4.7945, 4.4644, 4.0181, 3.6055, 3.2174, 2.7981, 2.0123, 1.4128, 0.9976, 0.6443, 0.0657, -0.4624, -0.9809, -1.6017, -2.2937],
            "θ2": [-1.35, -1.35, -1.4, -1.45, -1.45, -1.45, -1.4, -1.35, -1.28, -1.18, -1.08, -0.99, -0.91, -0.85, -0.77, -0.71, -0.67, -0.64, -0.58, -0.54, -0.5, -0.46, -0.4],
            "θ6": [-0.0012, -0.0012, -0.0012, -0.0012, -0.0012, -0.0014, -0.0018, -0.0023, -0.0027, -0.0035, -0.0044, -0.005, -0.0058, -0.0062, -0.0064, -0.0064, -0.0064, -0.0064, -0.0064, -0.0064, -0.0064, -0.0064, -0.0064],
            "θ7": [1.0988, 1.0988, 1.2536, 1.4175, 1.3997, 1.3582, 1.1648, 0.994, 0.8821, 0.7046, 0.5799, 0.5021, 0.3687, 0.1746, -0.082, -0.2821, -0.4108, -0.4466, -0.4344, -0.4368, -0.4586, -0.4433, -0.4828],
            "θ8": [-1.42, -1.42, -1.65, -1.8, -1.8, -1.69, -1.49, -1.3, -1.18, -0.98, -0.82, -0.7, -0.54, -0.34, -0.05, 0.12, 0.25, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
            "θ10": [3.12, 3.12, 3.37, 3.37, 3.33, 3.25, 3.03, 2.8, 2.59, 2.2, 1.92, 1.7, 1.42, 1.1, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
            "θ11": [0.013, 0.013, 0.013, 0.013, 0.013, 0.013, 0.0129, 0.0129, 0.0128, 0.0127, 0.0125, 0.0124, 0.012, 0.0114, 0.01, 0.0085, 0.0069, 0.0054, 0.0027, 0.0005, -0.0013, -0.0033, -0.006],
            "θ12": [0.98, 0.98, 1.288, 1.483, 1.613, 1.882, 2.076, 2.248, 2.348, 2.427, 2.399, 2.273, 1.993, 1.47, 0.408, -0.401, -0.723, -0.673, -0.627, -0.596, -0.566, -0.528, -0.504],
            "θ13": [-0.0135, -0.0135, -0.0138, -0.0142, -0.0145, -0.0153, -0.0162, -0.0172, -0.0183, -0.0206, -0.0231, -0.0256, -0.0296, -0.0363, -0.0493, -0.061, -0.0711, -0.0798, -0.0935, -0.098, -0.098, -0.098, -0.098],
            "θ14": [-0.4, -0.4, -0.4, -0.4, -0.4, -0.4, -0.35, -0.31, -0.28, -0.23, -0.19, -0.16, -0.12, -0.07, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "θ15": [0.9996, 0.9996, 1.103, 1.2732, 1.3042, 1.26, 1.223, 1.16, 1.05, 0.8, 0.662, 0.58, 0.48, 0.33, 0.31, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
            "θ16": [-1, -1, -1.18, -1.36, -1.36, -1.3, -1.25, -1.17, -1.06, -0.78, -0.62, -0.5, -0.34, -0.14, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        })

        # Period-independent coefficients
        self.C1 = 7.8
        self.C4 = 10
        self.θ3 = 0.1
        self.θ4 = 0.9
        self.θ5 = 0
        self.θ9 = 0.4
        self.C = 1.88
        self.n = 1.18

    def _get_coeffs(self, T):
        coeff = self.coeff_df[self.coeff_df['T'] == T].iloc[0]
        coeff_0 = self.coeff_df[self.coeff_df['T'] == 0].iloc[0]
        return coeff, coeff_0

    def _source(self, Fevent, θ1, θ2, θ3, θ4, ΔC1, m, Rrup, C4, θ9, θ14, Rhypo):
        if Fevent == 0:
            return θ1 + θ4*ΔC1 + (θ2 + θ3*(m - 7.8)) * np.log(Rrup + C4*np.exp(θ9*(m - 6)))
        else:
            return θ1 + θ4*ΔC1 + (θ2 + θ14*Fevent + θ3*(m - 7.8)) * np.log(Rhypo + C4*np.exp(θ9*(m - 6)))

    def _path(self, Fevent, Rrup, Rhypo, θ6):
        return θ6 * (Rrup if Fevent == 0 else Rhypo)

    def _fFevent(self, Fevent, θ10):
        return θ10 * Fevent if Fevent == 1 else 0

    def _depth(self, θ11, Zh, Fevent):
        return θ11 * (min(Zh, 120) - 60) * Fevent

    def _mag(self, θ4, θ5, m, C1, deltaC1, θ13):
        if m <= (C1 - deltaC1):
            return (θ4 * (m - (C1 + deltaC1))) - θ13*((10 - m)**2)
        else:
            return (θ5 * (m - (C1 + deltaC1))) - θ13*((10 - m)**2)

    def _FABA(self, θ7, θ8, θ15, θ16, Rhypo, Rrup, Ffaba, Fevent):
        if Fevent == 1:
            return θ7 + θ8 * np.log(max(Rhypo, 85)/40) * Ffaba
        else:
            return θ15 + θ16 * np.log(max(Rrup, 100)/40) * Ffaba

    def _site(self, PGA1000, Vs30, Vlin, θ12, b, C, n):
        Vs30 = min(Vs30, 1000)
        if Vs30 < Vlin:
            return θ12*np.log(Vs30/Vlin) - b*np.log(PGA1000+C) + b*np.log(PGA1000 + C*(Vs30/Vlin)**n)
        else:
            return θ12*np.log(Vs30/Vlin) - b*n*np.log(PGA1000+C)
        
    def get_source(self, event, forearc, m, Rrup, Rhypo, Vs30, Zh, T):
        coeff, coeff_0 = self._get_coeffs(T)
        # Region/event flags
        Fevent = 0 if event == 'Interface' else 1
        Ffaba = 1 if forearc == 'Forearc' else 0
        ΔC1 = max(0.19 - 0.138 * T, -0.2)
        return self._source(Fevent, coeff_0['θ1'], coeff_0['θ2'], self.θ3, self.θ4, ΔC1, m, Rrup, self.C4, self.θ9, coeff_0['θ14'], Rhypo)
    
    def get_path(self, event, forearc, m, Rrup, Rhypo, Vs30, Zh, T):
        coeff, coeff_0 = self._get_coeffs(T)
        # Region/event flags
        Fevent = 0 if event == 'Interface' else 1
        return self._path(Fevent, Rrup, Rhypo, coeff_0['θ6'])
    
    def get_mag(self, event, forearc, m, Rrup, Rhypo, Vs30, Zh, T):
        coeff, coeff_0 = self._get_coeffs(T)
        # Region/event flags
        Fevent = 0 if event == 'Interface' else 1
        ΔC1 = max(0.19 - 0.138 * T, -0.2)
        return self._mag(self.θ4, self.θ5, m, self.C1, ΔC1, coeff_0['θ13'])
    
    def get_faba(self, event, forearc, m, Rrup, Rhypo, Vs30, Zh, T):
        coeff, coeff_0 = self._get_coeffs(T)
        # Region/event flags
        Fevent = 0 if event == 'Interface' else 1
        Ffaba = 1 if forearc == 'Forearc' else 0
        return self._FABA(coeff_0['θ7'], coeff_0['θ8'], coeff_0['θ15'], coeff_0['θ16'], Rhypo, Rrup, Ffaba, Fevent)
    
    def get_depth(self, event, forearc, m, Rrup, Rhypo, Vs30, Zh, T):   
        coeff, coeff_0 = self._get_coeffs(T)
        # Region/event flags
        Fevent = 0 if event == 'Interface' else 1
        return self._depth(coeff_0['θ11'], Zh, Fevent)
    
    def get_fFevent(self, event, forearc, m, Rrup, Rhypo, Vs30, Zh, T):
        coeff, coeff_0 = self._get_coeffs(T)
        # Region/event flags
        Fevent = 0 if event == 'Interface' else 1
        return self._fFevent(Fevent, coeff_0['θ10'])
    
    def get_site(self, event, forearc, m, Rrup, Rhypo, Vs30, Zh, T):
        coeff, coeff_0 = self._get_coeffs(T)
        # Region/event flags
        Fevent = 0 if event == 'Interface' else 1
        ΔC1 = max(0.19 - 0.138 * T, -0.2)

        # PGA1000 for site term
        PGA_source = self._source(Fevent, coeff_0['θ1'], coeff_0['θ2'], self.θ3, self.θ4, ΔC1, m, Rrup, self.C4, self.θ9, coeff_0['θ14'], Rhypo)
        Yref = np.exp(PGA_source + self._path(Fevent, Rrup, Rhypo, coeff_0['θ6']))
        
        return self._site(Yref, Vs30, coeff['Vlin'], coeff['θ12'], coeff['b'], self.C, self.n)

    def calculate(self, event, forearc, m, Rrup, Rhypo, Vs30, Zh, T):
        coeff, coeff_0 = self._get_coeffs(T)

        # Region/event flags
        Fevent = 0 if event == 'Interface' else 1
        Ffaba = 1 if forearc == 'Forearc' else 0
        ΔC1 = max(0.19 - 0.138 * T, -0.2)

        # PGA1000 for site term
        PGA_source = self._source(Fevent, coeff_0['θ1'], coeff_0['θ2'], self.θ3, self.θ4, 0.2, m, Rrup, self.C4, self.θ9, coeff_0['θ14'], Rhypo)
        PGA_path = self._path(Fevent, Rrup, Rhypo, coeff_0['θ6'])
        PGA_mag = self._mag(self.θ4, self.θ5, m, self.C1, 0.2, coeff_0['θ13'])
        PGA_faba = self._FABA(coeff_0['θ7'], coeff_0['θ8'], coeff_0['θ15'], coeff_0['θ16'], Rhypo, Rrup, Ffaba, Fevent)
        PGA_depth = self._depth(coeff_0['θ11'], Zh, Fevent)
        PGA_fevent = self._fFevent(Fevent, coeff_0['θ10'])
        Yref = np.exp(PGA_source + PGA_path + PGA_mag + PGA_faba + PGA_depth + PGA_fevent)

        # Full SA computation
        source = self._source(Fevent, coeff['θ1'], coeff['θ2'], self.θ3, self.θ4, ΔC1, m, Rrup, self.C4, self.θ9, coeff['θ14'], Rhypo)
        path = self._path(Fevent, Rrup, Rhypo, coeff['θ6'])
        mag = self._mag(self.θ4, self.θ5, m, self.C1, ΔC1, coeff['θ13'])
        faba = self._FABA(coeff['θ7'], coeff['θ8'], coeff['θ15'], coeff['θ16'], Rhypo, Rrup, Ffaba, Fevent)
        depth = self._depth(coeff['θ11'], Zh, Fevent)
        fevent = self._fFevent(Fevent, coeff['θ10'])
        site = self._site(Yref, Vs30, coeff['Vlin'], coeff['θ12'], coeff['b'], self.C, self.n)

        lnY = source + path + mag + faba + depth + fevent + site
        return np.exp(lnY)

class Boore:
    def __init__(self):
        # Load coefficients
        self.coeff_df = pd.DataFrame({
            "T": [0.01, 0.02, 0.03, 0.05, 0.08, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.75, 1, 1.5, 2, 3, 4, 5, 7.5, 10, 0, -1],
            "e0": [0.4534,0.48598,0.56916,0.75436,0.96447,1.1268,1.3095,1.3255,1.2766,1.2217,1.1046,0.96991,0.66903,0.3932,-0.14954,-0.58669,-1.1898,-1.6388,-1.966,-2.5865,-3.0702,0.4473,5.037],
            "e1": [0.4916, 0.52359, 0.6092, 0.79905, 1.0077, 1.1669, 1.3481, 1.359, 1.3017, 1.2401, 1.1214, 0.99106, 0.69737, 0.4218, -0.11866, -0.55003, -1.142, -1.5748, -1.8882, -2.4874, -2.9537, 0.4856, 5.078],
            "e2": [0.2519, 0.29707, 0.40391, 0.60652, 0.77678, 0.8871, 1.0648, 1.122, 1.0828, 1.0246, 0.89765, 0.7615, 0.47523, 0.207, -0.3138, -0.71466, -1.23, -1.6673, -2.0245, -2.8176, -3.3776, 0.2459, 4.849],
            "e3": [0.4599, 0.48875, 0.55783, 0.72726, 0.9563, 1.1454, 1.3324, 1.3414, 1.3052, 1.2653, 1.1552, 1.012, 0.69173, 0.4124, -0.1437, -0.60658, -1.2664, -1.7516, -2.0928, -2.6854, -3.1726, 0.4539, 5.033],
            "e4": [1.421, 1.4331, 1.4261, 1.3974, 1.4174, 1.4293, 1.2844, 1.1349, 1.0166, 0.95676, 0.96766, 1.0384, 1.2871, 1.5004, 1.7622, 1.9152, 2.1323, 2.204, 2.2299, 2.1187, 1.8837, 1.431, 1.073],
            "e5": [0.04932, 0.053388, 0.061444, 0.067357, 0.073549, 0.055231, -0.04207, -0.11096, -0.16213, -0.1959, -0.22608, -0.23522, -0.21591, -0.18983, -0.1467, -0.11237, -0.04332, -0.01464, -0.01486, -0.08161, -0.15096, 0.05053, -0.1536],
            "e6": [-0.1659, -0.16561, -0.1669, -0.18082, -0.19665, -0.19838, -0.18234, -0.15852, -0.12784, -0.09286, -0.02319, 0.029119, 0.10829, 0.17895, 0.33896, 0.44788, 0.62694, 0.76303, 0.87314, 1.0121, 1.0651, -0.1662, 0.2252],
            "C1": [-1.134, -1.1394, -1.1421, -1.1159, -1.0831, -1.0652, -1.0532, -1.0607, -1.0773, -1.0948, -1.1243, -1.1459, -1.1777, -1.193, -1.2063, -1.2159, -1.2179, -1.2162, -1.2189, -1.2543, -1.3253, -1.134, -1.243],
            "C2": [0.1916, 0.18962, 0.18842, 0.18709, 0.18225, 0.17203, 0.15401, 0.14489, 0.13925, 0.13388, 0.12512, 0.12015, 0.11054, 0.10248, 0.09645, 0.09636, 0.09764, 0.10218, 0.10353, 0.12507, 0.15183, 0.1917, 0.1489],
            "C3": [-0.00809, -0.00807, -0.00834, -0.00982, -0.01058, -0.0102, -0.00898, -0.00772, -0.00652, -0.00548, -0.00405, -0.00322, -0.00193, -0.00121, -0.00037, 0, 0, -0.00005, 0, 0, 0, -0.00809, -0.00344],
            "h": [4.5, 4.5, 4.49, 4.2, 4.04, 4.13, 4.39, 4.61, 4.78, 4.93, 5.16, 5.34, 5.6, 5.74, 6.18, 6.5, 6.93, 7.32, 7.78, 9.48, 9.66, 4.5, 5.3],
            "C3 Global": [0]*23,
            "C3 China": [0.00282, 0.00278, 0.00276, 0.00296, 0.00296, 0.00288, 0.00279, 0.00261, 0.00244, 0.0022, 0.00211, 0.00235, 0.00269, 0.00292, 0.00304, 0.00292, 0.00262, 0.00261, 0.0026, 0.0026, 0.00303, 0.00286, 0.00435],
            "C3 Japan": [-0.00244, -0.00234, -0.00217, -0.00199, -0.00216, -0.00244, -0.00271, -0.00297, -0.00314, -0.0033, -0.00321, -0.00291, -0.00253, -0.00209, -0.00152, -0.00117, -0.00119, -0.00108, -0.00057, 0.00038, 0.00149, -0.00255, -0.00033],
            "C": [-0.6037, -0.5739, -0.5341, -0.458, -0.4441, -0.4872, -0.5796, -0.6876, -0.7718, -0.8417, -0.9109, -0.9693, -1.0154, -1.05, -1.0454, -1.0392, -1.0112, -0.9694, -0.9195, -0.7766, -0.6558, -0.6, -0.84],
            "Vc": [1500.2, 1500.36, 1502.95, 1501.42, 1494, 1479.12, 1442.85, 1392.61, 1356.21, 1308.47, 1252.66, 1203.91, 1147.59, 1109.95, 1072.39, 1009.49, 922.43, 844.48, 793.13, 771.01, 775, 1500, 1300],
            "Vref": [760]*23,
            "f1": [0]*23,
            "f3": [0.1]*23,
            "f4": [-0.15,-0.15,-0.15,-0.19,-0.24,-0.25,-0.26,-0.25,-0.24,-0.22,-0.2,-0.18,-0.14,-0.11,-0.06,-0.04,-0.01,0,0,0,0,-0.15,-0.1],
            "f5": [-0.01,-0.01,-0.01,-0.01,-0.01,-0.01,-0.01,-0.01,-0.01,-0.01,-0.01,-0.01,-0.01,-0.01,-0.01,0,0,0,0,0,0,-0.01,-0.01]
        })

    def _get_coeffs(self, T):
        coeff = self.coeff_df[self.coeff_df['T'] == T].iloc[0]
        coeff_0 = self.coeff_df[self.coeff_df['T'] == 0].iloc[0]
        return coeff, coeff_0
    
    def _source(self, m, mh, e0, e1, e2, e3, e4, e5, e6, U, SS, NS, RS):
        if m <= mh:
            return e0*U + e1*SS + e2*NS + e3*RS + e4*(m - mh) + e5*((m - mh)**2)
        else:
            return e0*U + e1*SS + e2*NS + e3*RS + e6*(m - mh)

    def _path(self, C1, C2, m, h, R, C3, deltaC3):
        return (C1 + C2*(m - 4.5)) * np.log(np.sqrt(R**2 + h**2)) + (C3 + deltaC3)*(R - 1)

    def _site_linear(self, C, V30, Vc, Vref):
        if V30 <= Vc:
            return C * np.log(V30 / Vref)
        else:
            return C * np.log(Vc / Vref)

    def _f2_calc(self, f4, f5, V30):
        if V30 < 760:
            return f4 * (np.exp(f5*(min(V30,760)-360)) - np.exp(f5*400))
        else:
            return f4

    def _site_nonlinear(self, f1, f2_val, PGAR, f3):
        return f1 + f2_val * np.log((PGAR + f3) / f3)
    
    def get_source(self, M, Mech, R, Vs30, Region, T):
        coeff, coeff_0 = self._get_coeffs(T)

        # Mechanism flag
        U = 1 if Mech == 'U' else 0
        SS = 1 if Mech == 'SS' else 0
        RS = 1 if Mech == 'RS' else 0
        NS = 1 if Mech == 'NS' else 0
        return self._source(M, coeff_0['h'], coeff_0['e0'], coeff_0['e1'], coeff_0['e2'], coeff_0['e3'], coeff_0['e4'], coeff_0['e5'], coeff_0['e6'], U, SS, NS, RS)
        
    def get_path(self, M, Mech, R, Vs30, Region, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._path(coeff_0['C1'], coeff_0['C2'], M, coeff_0['h'], R, coeff_0['C3 Global'] if Region == 'Global' else coeff_0['C3 China'], 0)
    
    def get_site(self, M, Mech, R, Vs30, Region, T):
        coeff, coeff_0 = self._get_coeffs(T)

    def get_site_linear(self, M, Mech, R, Vs30, Region, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._site_linear(coeff['C'], Vs30, coeff['Vc'], coeff['Vref'])
    
    def get_f2(self, M, Mech, R, Vs30, Region, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._f2_calc(coeff['f4'], coeff['f5'], Vs30)

    def calculate(self, M, Mech, R, Vs30, Region, T):
        coeff, coeff_0 = self._get_coeffs(T)

        # Mechanism flag
        U = 1 if Mech == 'U' else 0
        SS = 1 if Mech == 'SS' else 0
        RS = 1 if Mech == 'RS' else 0
        NS = 1 if Mech == 'NS' else 0

        PGA_source = self._source(M, coeff_0['h'], coeff_0['e0'], coeff_0['e1'], coeff_0['e2'], coeff_0['e3'], coeff_0['e4'], coeff_0['e5'], coeff_0['e6'], U, SS, NS, RS)
        PGA_path = self._path(coeff_0['C1'], coeff_0['C2'], M, coeff_0['h'], R, coeff_0['C3 Global'] if Region == 'Global' else coeff_0['C3 China'], 0)
        PGAR = np.exp(PGA_source + PGA_path)

        source = self._source(M, coeff['h'], coeff['e0'], coeff['e1'], coeff['e2'], coeff['e3'], coeff['e4'], coeff['e5'], coeff['e6'], U, SS, NS, RS)
        path = self._path(coeff['C1'], coeff['C2'], M, coeff['h'], R, coeff['C3 Global'] if Region == 'Global' else coeff['C3 China'], 0)
        site_linear = self._site_linear(coeff['C'], Vs30, coeff['Vc'], coeff['Vref'])
        f2_val = self._f2_calc(coeff['f4'], coeff['f5'], Vs30)
        site_nonlinear = self._site_nonlinear(coeff['f1'], f2_val, PGAR, coeff['f3'])

        lnY = source + path + site_linear + site_nonlinear
        return np.exp(lnY)

class Campbell:
    def __init__(self):
        # Load coefficients
        self.coeff_df = pd.DataFrame({
            "T": [0, 0.02, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.75, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7.5, 10],
            "Vlin": [865.1, 865.1, 1053.5, 1085.7, 1032.5, 877.6, 748.2, 654.3, 587.1, 503, 456.6, 430.3, 410.5, 400, 400, 400, 400, 400, 400, 400, 400, 400, 400],
            "b": [-1.186, -1.186, -1.346, -1.471, -1.624, -1.931, -2.188, -2.381, -2.518, -2.657, -2.669, -2.599, -2.401, -1.955, -1.025, -0.299, 0, 0, 0, 0, 0, 0, 0],
            "θ1": [4.2203, 4.2203, 4.5371, 5.0733, 5.2892, 5.4563, 5.2684, 5.0594, 4.7945, 4.4644, 4.0181, 3.6055, 3.2174, 2.7981, 2.0123, 1.4128, 0.9976, 0.6443, 0.0657, -0.4624, -0.9809, -1.6017, -2.2937],
            "θ2": [-1.35, -1.35, -1.4, -1.45, -1.45, -1.45, -1.4, -1.35, -1.28, -1.18, -1.08, -0.99, -0.91, -0.85, -0.77, -0.71, -0.67, -0.64, -0.58, -0.54, -0.5, -0.46, -0.4],
            "θ6": [-0.0012, -0.0012, -0.0012, -0.0012, -0.0012, -0.0014, -0.0018, -0.0023, -0.0027, -0.0035, -0.0044, -0.005, -0.0058, -0.0062, -0.0064, -0.0064, -0.0064, -0.0064, -0.0064, -0.0064, -0.0064, -0.0064, -0.0064],
            "θ7": [1.0988, 1.0988, 1.2536, 1.4175, 1.3997, 1.3582, 1.1648, 0.994, 0.8821, 0.7046, 0.5799, 0.5021, 0.3687, 0.1746, -0.082, -0.2821, -0.4108, -0.4466, -0.4344, -0.4368, -0.4586, -0.4433, -0.4828],
            "θ8": [-1.42, -1.42, -1.65, -1.8, -1.8, -1.69, -1.49, -1.3, -1.18, -0.98, -0.82, -0.7, -0.54, -0.34, -0.05, 0.12, 0.25, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
            "θ10": [3.12, 3.12, 3.37, 3.37, 3.33, 3.25, 3.03, 2.8, 2.59, 2.2, 1.92, 1.7, 1.42, 1.1, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
            "θ11": [0.013, 0.013, 0.013, 0.013, 0.013, 0.013, 0.0129, 0.0129, 0.0128, 0.0127, 0.0125, 0.0124, 0.012, 0.0114, 0.01, 0.0085, 0.0069, 0.0054, 0.0027, 0.0005, -0.0013, -0.0033, -0.006],
            "θ12": [0.98, 0.98, 1.288, 1.483, 1.613, 1.882, 2.076, 2.248, 2.348, 2.427, 2.399, 2.273, 1.993, 1.47, 0.408, -0.401, -0.723, -0.673, -0.627, -0.596, -0.566, -0.528, -0.504],
            "θ13": [-0.0135, -0.0135, -0.0138, -0.0142, -0.0145, -0.0153, -0.0162, -0.0172, -0.0183, -0.0206, -0.0231, -0.0256, -0.0296, -0.0363, -0.0493, -0.061, -0.0711, -0.0798, -0.0935, -0.098, -0.098, -0.098, -0.098],
            "θ14": [-0.4, -0.4, -0.4, -0.4, -0.4, -0.4, -0.35, -0.31, -0.28, -0.23, -0.19, -0.16, -0.12, -0.07, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "θ15": [0.9996, 0.9996, 1.103, 1.2732, 1.3042, 1.26, 1.223, 1.16, 1.05, 0.8, 0.662, 0.58, 0.48, 0.33, 0.31, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
            "θ16": [-1, -1, -1.18, -1.36, -1.36, -1.3, -1.25, -1.17, -1.06, -0.78, -0.62, -0.5, -0.34, -0.14, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        })

    def _get_coeffs(self, T):
        coeff = self.coeff_df[self.coeff_df['T'] == T].iloc[0]
        coeff_0 = self.coeff_df[self.coeff_df['T'] == 0].iloc[0]
        return coeff, coeff_0
    
    def _mag(self, C0, C1, C2, C3, C4, m):
        if(m<=4.5):
            return C0 + C1*m
        elif(4.5<m<=5):
            return C0 + C1*m + C2*(m-4.5)
        elif(5.5<m<=6):
            return C0 + C1*m + C2*(m-4.5)+C3*(m-5.5)
        else:
            return C0 + C1*m + C2*(m-4.5)+C3*(m-5.5)+C4*(m-6.5)

    def _dist(self, C5, C6, m, Rrup, C7):
        return (C5+C6*m)*np.log(np.sqrt(Rrup**2+C7**2))

    def _flt(self, C8, C9, Frv, Fnm, m):
        if(m<=4.5):
            return 0
        elif(4.5<m<5.5):
            return (C8*Frv+C9*Fnm)*(m-4.5)
        else:
            return C8*Frv+C9*Fnm

    def _hng(self, C10, Fhng_Rx, Fhng_Rrup, Fhng_M, Fhng_Z, Fhng_delta):
        return C10 * Fhng_Rx * Fhng_Rrup * Fhng_M * Fhng_Z * Fhng_delta

    def _hanging_rx(self, Rx, h1, h2, h3, h4, h5, h6, m, w, delta):
        R1 = w*np.cos(delta)
        R2 = 62*m-350
        if(Rx<0):
            return 0
        elif(0<=Rx<R1):
            return h1 + h2*(Rx/R1) + h3*((Rx/R1)**2)
        else:
            return h4 + h5*(Rx-R1)/(R2-R1) + h6*(((Rx-R1)/(R2-R1))**2)

    def _hanging_rrup(self, Rrup, Rjb):
        if(Rrup==0):
            return 1
        else:
            return (Rrup-Rjb)/Rjb

    def _hanging_mag(self, m, a2):
        if(m<=5.5):
            return 0
        elif(5.5<m<=5.5):
            return (m-5.5)*(1+a2*(m-6.5))
        else:
            return 1+a2*(m-6.5)

    def _hanging_z(self, Ztor):
        if(Ztor<16.66):
            return 1-0.06*Ztor
        else:
            return 0

    def _hanging_delta(self, delta):
        return (90-delta)/45

    def _site_G(self, C11, Vs30, k1, k2, A1100, C, n):
        if(Vs30<=k1):
            return C11*np.log(Vs30/k1) + k2*(np.log(A1100 + C*(Vs30/k1)**n)-np.log(A1100+C))
        else:
            return (C11 + k2*n)*np.log(Vs30/k1)

    def _site_J(self, C12, C13, k1, k2, n, Vs30, Sj):
        if(Vs30<200):
            return Sj*(C12 + k2*n)*(np.log(Vs30/k1)-np.log(200/k1))
        else:
            return Sj*(C13 + k2*n)*np.log(Vs30/k1)
        
    def _sed(self, C14, C15, C16, Sj, Z25, k3):
        if(Z25<1):
            return (C14 - C15*Sj)*(Z25-1)
        elif(1<Z25<=3):
            return 0
        else:
            return C16*k3*np.exp(-0.75)*(1-np.exp(-0.25*(Z25-3)))

    def _hypo(self, hypo_H, hypo_M):
        return hypo_H*hypo_M

    def _hypo_H(self, Zhyp):
        if(Zhyp<7):
            return 0
        elif(7<Zhyp<20):
            return Zhyp-7
        else:
            return 13

    def _hypo_M(self, C17, C18, m):
        if(m<=5.5):
            return C17
        elif(5.5<m<=6.5):
            return C17 + (C18-C17)*(m-5.5)
        else:
            return C18  

    def _dip(self, C19, delta, m):
        if(m<=4.5):
            return C19*delta
        elif(4.5<m<=5.5):
            return C19*(5.5-m)*delta
        else:
            return 0

    def _atn(self, C20, deltaC20, Rrup):
        if (Rrup>80):
            return ((C20+deltaC20)*(Rrup-80))
        else:
            return 0
        
    def get_mag(self, M, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._mag(coeff['c0'], coeff['c1'], coeff['c2'], coeff['c3'], coeff['c4'], M)
    
    def get_dist(self, M, Rrup, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._dist(coeff['c5'], coeff['c6'], M, Rrup, coeff['c7'])
    
    def get_flt(self, M, Frv, Fnm, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._flt(coeff['c8'], coeff['c9'], Frv, Fnm, M)
    
    def get_hng(self, M, Rx, Rrup, Rjb, W, delta, Ztor, T):
        coeff, coeff_0 = self._get_coeffs(T)
        hng_rx_val = self._hanging_rx(Rx, coeff['h1'], coeff['h2'], coeff['h3'], coeff['h4'], coeff['h5'], coeff['h6'], M, W, delta)
        hng_rrup_val = self._hanging_rrup(Rrup, Rjb)
        hng_mag_val = self._hanging_mag(M, coeff['a2'])
        hng_z_val = self._hanging_z(Ztor)
        hng_delta_val = self._hanging_delta(delta)
        return self._hng(coeff['c10'], hng_rx_val, hng_rrup_val, hng_mag_val, hng_z_val, hng_delta_val)
    
    def get_hng_rx(self, Rx, M, W, delta, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._hanging_rx(Rx, coeff['h1'], coeff['h2'], coeff['h3'], coeff['h4'], coeff['h5'], coeff['h6'], M, W, delta)
    
    def get_hng_rrup(self, Rrup, Rjb):
        return self._hanging_rrup(Rrup, Rjb) 

    def get_hng_mag(self, M, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._hanging_mag(M, coeff['a2'])

    def get_hng_z(self, Ztor):
        return self._hanging_z(Ztor)    

    def get_hng_delta(self, delta):
        return self._hanging_delta(delta)

    def get_site_G(self, Vs30, PGAR, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._site_G(coeff['c11'], Vs30, coeff['k1'], coeff['k2'], PGAR, coeff['c'], coeff['n'])

    def get_site_J(self, Vs30, Sj, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._site_J(coeff['c12'], coeff['c13'], coeff['k1'], coeff['k2'], coeff['n'], Vs30, Sj)

    def get_sed(self, Z25, Sj, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._sed(coeff['c14'], coeff['c15'], coeff['c16'], Sj, Z25, coeff['k3'])

    def get_hypo(self, Zhyp, M, T):
        coeff, coeff_0 = self._get_coeffs(T)
        hypo_H_val = self._hypo_H(Zhyp)
        hypo_M_val = self._hypo_M(coeff['c17'], coeff['c18'], M)
        return self._hypo(hypo_H_val, hypo_M_val)

    def get_hypo_H(self, Zhyp):
        return self._hypo_H(Zhyp)

    def get_hypo_M(self, M, T):
        coeff, coeff_0 = self._get_coeffs(T)    
        return self._hypo_M(coeff['c17'], coeff['c18'], M)

    def get_dip(self, delta, M, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._dip(coeff['c19'], delta, M)

    def get_atn(self, Rrup, T):
        coeff, coeff_0 = self._get_coeffs(T)
        Δc20 = coeff['Δc20JI'] if coeff['Region'] == 'Japan' else coeff['Δc20CH']
        return self._atn(coeff['c20'], Δc20, Rrup)

    def calculate(self, M, Rrup, Rx, Rjb, W, delta, Ztor, Z25, Zhyp, λ, Region, Vs30, T):
        coeff, coeff_0 = self._get_coeffs(T)

        # Mechanism flag
        Frv = 1 if 30 < λ < 150 else 0
        Fnm = 1 if -120 < λ < -60 else 0

        Sj = 1 if Region == 'Japan' else 0

        # Extract coefficients for any T
        c0, c1, c2, c3 = coeff['c0'], coeff['c1'], coeff['c2'], coeff['c3']
        c4, c5, c6, c7, c8 = coeff['c4'], coeff['c5'], coeff['c6'], coeff['c7'], coeff['c8']
        c9, c10, c11, c12, c13, c14, c15 = coeff['c9'], coeff['c10'], coeff['c11'], coeff['c12'], coeff['c13'], coeff['c14'], coeff['c15']
        c16, c17, c18, c19, c20, c = coeff['c16'], coeff['c17'], coeff['c18'], coeff['c19'], coeff['c20'], coeff['c']
        n, Δc20JI, Δc20CH = coeff['n'], coeff['Δc20JI'], coeff['Δc20CH']
        k1, k2, k3 = coeff['k1'], coeff['k2'], coeff['k3']
        a2, h1, h2, h3, h4, h5, h6 = coeff['a2'], coeff['h1'], coeff['h2'], coeff['h3'], coeff['h4'], coeff['h5'], coeff['h6']

        # Extract coeff_0icients for PGAR
        c0_0, c1_0, c2_0, c3_0 = coeff_0['c0'], coeff_0['c1'], coeff_0['c2'], coeff_0['c3']
        c4_0, c5_0, c6_0, c7_0, c8_0 = coeff_0['c4'], coeff_0['c5'], coeff_0['c6'], coeff_0['c7'], coeff_0['c8']
        c9_0, c10_0, c11_0, c12_0, c13_0, c14_0, c15_0 = coeff_0['c9'], coeff_0['c10'], coeff_0['c11'], coeff_0['c12'], coeff_0['c13'], coeff_0['c14'], coeff_0['c15']
        c16_0, c17_0, c18_0, c19_0, c20_0, c_0 = coeff_0['c16'], coeff_0['c17'], coeff_0['c18'], coeff_0['c19'], coeff_0['c20'], coeff_0['c']
        n_0, Δc20JI_0, Δc20CH_0 = coeff_0['n'], coeff_0['Δc20JI'], coeff_0['Δc20CH']
        k1_0, k2_0, k3_0 = coeff_0['k1'], coeff_0['k2'], coeff_0['k3']
        a2_0, h1_0, h2_0, h3_0, h4_0, h5_0, h6_0 = coeff_0['a2'], coeff_0['h1'], coeff_0['h2'], coeff_0['h3'], coeff_0['h4'], coeff_0['h5'], coeff_0['h6']

        # Compute each term for PGAR
        mag_val_PGA = self._mag(c0_0, c1_0, c2_0, c3_0, c4_0, M)
        dist_val_PGA = self._dist(c5_0, c6_0, M, Rrup, c7_0) 
        flt_val_PGA = self._flt(c8_0, c9_0, Frv, Fnm, M)

        hng_rx_val_PGA = self._hanging_rx(Rx, h1_0, h2_0, h3_0, h4_0, h5_0, h6_0, M, W, delta)
        hng_rrup_val_PGA = self._hanging_rrup(Rrup, Rjb)
        hng_mag_val_PGA = self._hanging_mag(M, a2_0)
        hng_z_val_PGA = self._hanging_z(Ztor)
        hng_delta_val_PGA = self._hanging_delta(delta)
        hng_val_PGA = self._hng(c10_0, hng_rx_val_PGA, hng_rrup_val_PGA, hng_mag_val_PGA, hng_z_val_PGA, hng_delta_val_PGA)

        Δc20_0 = Δc20JI_0 if Region == 'Japan' else Δc20CH_0

        sed_val_PGA = self._sed(c14_0, c15_0, c16_0, Sj, Z25, k3_0)
        hypo_H_val_PGA = self._hypo_H(Zhyp)
        hypo_M_val_PGA = self._hypo_M(c17_0, c18_0, M)
        hypo_val_PGA = self._hypo(hypo_H_val_PGA, hypo_M_val_PGA)
        atn_val_PGA = self._atn(c20_0, Δc20_0, Rrup)

        PGAR = np.exp(mag_val_PGA + dist_val_PGA + flt_val_PGA + hng_val_PGA + sed_val_PGA + hypo_val_PGA + atn_val_PGA)

        # Compute each term for SA
        mag_val = self._mag(c0, c1, c2, c3, c4, M)
        dist_val = self._dist(c5, c6, M, Rrup, c7)
        flt_val = self._flt(c8, c9, Frv, Fnm, M)

        hng_rx_val = self._hanging_rx(Rx, h1, h2, h3, h4, h5, h6, M, W, delta)
        hng_rrup_val = self._hanging_rrup(Rrup, Rjb)
        hng_mag_val = self._hanging_mag(M, a2)
        hng_z_val = self._hanging_z(Ztor)
        hng_delta_val = self._hanging_delta(delta)
        hng_val = self._hng(c10, hng_rx_val, hng_rrup_val, hng_mag_val, hng_z_val, hng_delta_val)

        site_G_val = self._site_G(c11, Vs30, k1, k2, PGAR, c, n) 
        site_J_val = self._site_J(c12, c13, k1, k2, n, Vs30, Sj)
        site_val = site_G_val*site_J_val

        Δc20 = Δc20JI if Region == 'Japan' else Δc20CH
        sed_val = self._sed(c14, c15, c16, Sj, Z25, k3)
        hypo_H_val = self._hypo_H(Zhyp)
        hypo_M_val = self._hypo_M(c17, c18, M)
        hypo_val = self._hypo(hypo_H_val, hypo_M_val)
        atn_val = self._atn(c20, Δc20, Rrup)

        return np.exp(mag_val + dist_val + flt_val + hng_val + site_val + sed_val + hypo_val + atn_val)
    
class ChiouYoungs: 
    def __init__(self):
        # Load coefficients
        self.coeff_df = pd.DataFrame({
            "T": [0,-1,0.01,0.02,0.03,0.04,0.05,0.075,0.1,0.12,0.15,0.17,0.1,0.25,0.2,0.3,0.4,0.75,1,1.5,2,3,4,5,7.5,10],
            "c1": [-1.5065,2.3549,-1.5065,-1.4798,-1.2972,-1.1007,-0.9292,-0.658,-0.5613,-0.5342,-0.5462,-0.5858,-0.6798,-0.8663,-1.0514,-1.3794,-1.6508,-2.1511,-2.5365,-3.0686,-3.4148,-3.9013,-4.2466,-4.5143,-5.0009,-5.3461],
            "c1a": [0.165,0.165,0.165,0.165,0.165,0.165,0.165,0.165,0.165,0.165,0.165,0.165,0.165,0.165,0.165,0.165,0.165,0.165,0.165,0.165,0.1645,0.1168,0.0732,0.0484,0.022,0.0124],
            "c1b": [-0.255,-0.0626,-0.255,-0.255,-0.255,-0.255,-0.255,-0.254,-0.253,-0.252,-0.25,-0.248,-0.2449,-0.2382,-0.2313,-0.2146,-0.1972,-0.162,-0.14,-0.1184,-0.11,-0.104,-0.102,-0.101,-0.101,-0.1],
            "c1c": [-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.165,-0.1645,-0.1168,-0.0732,-0.0484,-0.022,-0.0124],
            "c1d": [0.255,0.0626,0.255,0.255,0.255,0.255,0.255,0.254,0.253,0.252,0.25,0.248,0.2449,0.2382,0.2313,0.2146,0.1972,0.162,0.14,0.1184,0.11,0.104,0.102,0.101,0.101,0.1],
            "cn": [16.0875,3.3024,16.0875,15.7118,15.8819,16.4556,17.6453,20.1772,19.9992,18.7106,16.6246,15.3709,13.7012,11.2667,9.1908,6.5459,5.2305,3.7896,3.3024,2.8498,2.5417,2.1488,1.8957,1.7228,1.5737,1.5265],
            "cM": [4.9993,5.423,4.9993,4.9993,4.9993,4.9993,4.9993,5.0031,5.0172,5.0315,5.0547,5.0704,5.0939,5.1315,5.167,5.2317,5.2893,5.4109,5.5106,5.6705,5.7981,5.9983,6.1552,6.2856,6.5428,6.7415],
            "c3": [1.9636,2.3152,1.9636,1.9636,1.9636,1.9636,1.9636,1.9636,1.9636,1.9795,2.0362,2.0823,2.1521,2.2574,2.344,2.4709,2.5567,2.6812,2.7474,2.8161,2.8514,2.8875,2.9058,2.9169,2.932,2.9396],
            "c5": [6.4551,5.8096,6.4551,6.4551,6.4551,6.4551,6.4551,6.4551,6.8305,7.1333,7.3621,7.4365,7.4972,7.5416,7.56,7.5735,7.5778,7.5808,7.5814,7.5817,7.5818,7.5818,7.5818,7.5818,7.5818,7.5818],
            "cHM": [3.0956,3.0514,3.0956,3.0963,3.0974,3.0988,3.1011,3.1094,3.2381,3.3407,3.43,3.4688,3.5146,3.5746,3.6232,3.6945,3.7401,3.7941,3.8144,3.8284,3.833,3.8361,3.8369,3.8376,3.838,3.838],
            "c6": [0.4908,0.4407,0.4908,0.4925,0.4992,0.5037,0.5048,0.5048,0.5048,0.5048,0.5045,0.5036,0.5016,0.4971,0.4919,0.4807,0.4707,0.4575,0.4522,0.4501,0.45,0.45,0.45,0.45,0.45,0.45],
            "c7": [0.0352,0.0324,0.0352,0.0352,0.0352,0.0352,0.0352,0.0352,0.0352,0.0352,0.0352,0.0352,0.0352,0.0352,0.0352,0.0352,0.0352,0.0352,0.0352,0.0352,0.0352,0.016,0.0062,0.0029,0.0007,0.0003],
            "c7b": [0.0462,0.0097,0.0462,0.0472,0.0533,0.0596,0.0639,0.063,0.0532,0.0452,0.0345,0.0283,0.0202,0.009,-0.0004,-0.0155,-0.0278,-0.0477,-0.0559,-0.063,-0.0665,-0.0516,-0.0448,-0.0424,-0.0348,-0.0253],
            "c8": [0,0.2154,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.0991,0.1982,0.2154,0.2154,0.2154,0.2154,0.2154,0.2154,0.2154,0.2154],
            "c8b": [0.4833,5,0.4833,1.2144,1.6421,1.9456,2.181,2.6087,2.9122,3.1045,3.3399,3.4719,3.6434,3.8787,4.0711,4.3745,4.6099,5.0376,5.3411,5.7688,6.0723,6.5,6.8035,7.0389,7.4666,7.77],            
            "c9": [0.9228,0.3079,0.9228,0.9296,0.9396,0.9661,0.9794,1.026,1.0177,1.0008,0.9801,0.9652,0.9459,0.9196,0.8829,0.8302,0.7884,0.6754,0.6196,0.5101,0.3917,0.1244,0.0086,0,0,0],
            "c9a": [0.1202,0.1,0.1202,0.1217,0.1194,0.1166,0.1176,0.1171,0.1146,0.1128,0.1106,0.115,0.1208,0.1208,0.1175,0.106,0.1061,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1],
            "c9b": [6.8607,6.5,6.8607,6.8697,6.9113,7.0271,7.0959,7.3298,7.2588,7.2372,7.2109,7.2491,7.2988,7.3691,6.8789,6.5334,6.526,6.5,6.5,6.5,6.5,6.5,6.5,6.5,6.5,6.5],
            "c11b": [-0.4536,-0.3834,-0.4536,-0.4536,-0.4536,-0.4536,-0.4536,-0.4536,-0.4536,-0.4536,-0.4536,-0.4536,-0.444,-0.3539,-0.2688,-0.1793,-0.1428,-0.1138,-0.1062,-0.102,-0.1009,-0.1003,-0.1001,-0.1001,-0.1,-0.1],
            "cg1": [-0.007146,-0.001852,-0.007146,-0.007249,-0.007869,-0.008316,-0.008743,-0.009537,-0.00983,-0.009913,-0.009896,-0.009787,-0.009505,-0.008918,-0.008251,-0.007267,-0.006492,-0.005147,-0.004277,-0.002979,-0.002301,-0.001344,-0.001084,-0.00101,-0.000964,-0.00095],
            "cg2": [-0.006758,-0.007403,-0.006758,-0.006758,-0.006758,-0.006758,-0.006758,-0.00619,-0.005332,-0.004732,-0.003806,-0.00328,-0.00269,-0.002128,-0.001812,-0.001274,-0.001074,-0.001115,-0.001197,-0.001675,-0.002349,-0.003306,-0.003566,-0.00364,-0.003686,-0.0037],
            "cg3": [4.2542,4.3439,4.2542,4.2386,4.2519,4.296,4.3578,4.5455,4.7603,4.8963,5.0644,5.1371,5.188,5.2164,5.1954,5.0899,4.7854,4.3304,4.1667,4.0029,3.8949,3.7928,3.7443,3.709,3.6632,3.623],
            "Φ1": [-0.521,-0.7936,-0.521,-0.5055,-0.4368,-0.3752,-0.3469,-0.3747,-0.444,-0.4895,-0.5477,-0.5922,-0.6693,-0.7766,-0.8501,-0.9431,-1.0044,-1.0602,-1.0941,-1.1142,-1.1154,-1.1081,-1.0603,-0.9872,-0.8274,-0.7053],
            "Φ2": [-0.1417,-0.0699,-0.1417,-0.1364,-0.1403,-0.1591,-0.1862,-0.2538,-0.2943,-0.3077,-0.3113,-0.3062,-0.2927,-0.2662,-0.2405,-0.1975,-0.1633,-0.1028,-0.0699,-0.0425,-0.0302,-0.0129,-0.0016,0,0,0],
            "Φ3": [-0.00701,-0.008444,-0.00701,-0.007279,-0.007354,-0.006977,-0.006467,-0.005734,-0.005604,-0.005696,-0.005845,-0.005959,-0.006141,-0.006439,-0.006704,-0.007125,-0.007435,-0.00812,-0.008444,-0.007707,-0.004792,-0.001828,-0.001523,-0.00144,-0.001369,-0.001361],
            "Φ4": [0.102151,5.41,0.102151,0.10836,0.119888,0.133641,0.148927,0.190596,0.230662,0.253169,0.266468,0.26506,0.255253,0.231541,0.207277,0.165464,0.133828,0.085153,0.058595,0.031787,0.019716,0.009643,0.005379,0.003223,0.001134,0.000515],
            "Φ5": [0,0.0202,0,0,0,0,0,0,0,0,0,0,0,0,0.001,0.004,0.01,0.034,0.067,0.143,0.203,0.277,0.309,0.321,0.329,0.33],
            "Φ6": [300,300,300,300,300,300,300,300,300,300,300,300,300,300,300,300,300,300,300,300,300,300,300,300,300,300] 
        })

    def _get_coeffs(self, T):
        coeff = self.coeff_df[self.coeff_df['T'] == T].iloc[0]
        coeff_0 = self.coeff_df[self.coeff_df['T'] == 0].iloc[0]
        return coeff, coeff_0
    
    def _frv(self, C1, Frv, C1a, C1c, m):
        return C1 + Frv*(C1a + C1c/(np.cosh(2*max(m-4.5,0))))

    def _fnm(self, C1b, C1d, m, Fnm):
        return Fnm*(C1b + C1d/(np.cosh(2*max(m-4.5,0))))

    def _dZtor(self, C7, C7b, m, ΔZtor):
        return ΔZtor*(C7 + C7b/(np.cosh(2*max(m-4.5,0))))

    def _dip(self, C11, C11b, m, delta):
        return (np.cos(delta)**2)*(C11 + C11b/(np.cosh(2*max(m-4.5,0))))

    def _mag(self, C2, m, C3, Cn, Cm):
        return C2*(m-6) + ((C2-C3)/Cn)*np.log(1 + np.exp(Cn*(Cm-m)))

    def _dist(self, C4, Rrup, C5, C6, Chm, m, C4a, Crb, Cy1, Cy2, Cy3):
        return C4*np.log(Rrup + C5*np.cosh(C6*max(m-Chm,0))) + (C4a-C4)*np.log(np.sqrt(Rrup**2+Crb**2)) + Rrup*(Cy1 + Cy2/(np.cosh(max(m-Cy3,0))))

    def _DPP(self, C8, Rrup, m, C8a, C8b, deltaDPP):
        return C8*max(1-(max(Rrup-40,0)/30), 0)*min(max(m-5.5,0)/0.8, 1)*np.exp(-C8a*((m-C8b)**2))*deltaDPP

    def _fhw(self, C9, Fhw, delta, C9a, C9b, Rx, Rrup, Rjb, Ztor):
        return C9*Fhw*np.cos(delta)*(C9a+(1-C9a)*np.tanh(Rx/C9b))*(1 - (np.sqrt(Rjb**2+Ztor**2))/(Rrup+1))

    def _site(self, theta1, theta2, theta3, theta4, Vs30, n, Yref):
        return theta1*min(np.log(Vs30/1130), 0) + theta2*(np.exp(theta3*(min(Vs30, 1130)-360))-np.exp(theta3*(1130-360)))*np.log((Yref*np.exp(n)+theta4)/theta4)

    def _basin(self, theta5, deltaZ1, theta6):
        return theta5*(1-np.exp(-deltaZ1/theta6))

    def _fdpp(self, C8, C8a, C8b, Rrup, m):
        return C8*max(0, 1 - max(Rrup-40,0)/30)*min(1,max(m-5.5,0)/30)*np.exp(-C8a*((m-C8b)**2))

    def Sum_SA(self, frv, fnm, Ztor, dip, mag, dist, Site, basin):
        return frv + fnm + Ztor + dip + mag + dist + Site + basin
    
    def get_frv(self, Frv, M, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._frv(coeff['c1'], Frv, coeff['c1a'], coeff['c1c'], M)

    def get_fnm(self, Fnm, M, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._fnm(coeff['c1b'], coeff['c1d'], M, Fnm)

    def get_dZtor(self, M, ΔZtor, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._dZtor(coeff['c7'], coeff['c7b'], M, ΔZtor)
    
    def get_dip(self, M, delta, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._dip(coeff['c11'], coeff['c11b'], M, delta)
    
    def get_mag(self, M, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._mag(coeff['c2'], M, coeff['c3'], coeff['cn'], coeff['cM'])

    def get_dist(self, M, Rrup, T): 
        coeff, coeff_0 = self._get_coeffs(T)
        return self._dist(coeff['c4'], Rrup, coeff['c5'], coeff['c6'], coeff['cHM'], M, coeff['c4a'], coeff['cRB'], coeff['cγ1'], coeff['cγ2'], 4)

    def get_fhw(self, Fhw, delta, Rx, Rrup, Rjb, Ztor, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._fhw(coeff['c9'], Fhw, delta, coeff['c9a'], coeff['c9b'], Rx, Rrup, Rjb, Ztor)
    
    def get_site(self, Vs30, Yref, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._site(coeff['Φ1'], coeff['Φ2'], coeff['Φ3'], coeff['Φ4'], Vs30, 0, Yref=1)
 
    def get_basin(self, deltaZ1, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._basin(self, coeff['Φ5'], deltaZ1, coeff['Φ6'])

    def get_fdpp(self, M, Rrup, T):
        coeff, coeff_0 = self._get_coeffs(T)
        return self._fdpp(coeff['c8'], coeff['c8a'], coeff['c8b'], Rrup, M)

    def calculate(self, M, Rrup, Rx, Rjb, delta, Ztor, Z25, Zhyp, λ, Region, Vs30, T):
        coeff, coeff_0 = self._get_coeffs(T)

        # Mechanism flag
        Frv = 1 if 30 < λ < 150 else 0
        Fnm = 1 if -150 < λ < -30 else 0
        Fhw = 1 if Rx >= 0 else 0

        # Period - Independent Coefficients
        c2, c2_0 = 1.06, 1.06
        c4, c4_0 = -2.1, -2.1
        c4a, c4a_0 = -0.5, -0.5
        cRB, cRB_0 = 50, 50
        c8a, c8a_0 = 0.2695, 0.2695
        c11, c11_0 = 0, 0
        n = 0 

        # Extract coefficients for any T
        c1, c1a, c1b, c1c, c1d = coeff['c1'], coeff['c1a'], coeff['c1b'], coeff['c1c'], coeff['c1d']
        cn, cM, c3, c5, cHM = coeff['cn'], coeff['cM'], coeff['c3'], coeff['c5'], coeff['cHM']
        c6, c7, c7b, c8, c8b, c9, c9a, c9b = coeff['c6'], coeff['c7'], coeff['c7b'], coeff['c8'], coeff['c8b'], coeff['c9'], coeff['c9a'], coeff['c9b']
        c11b, cg1, cg2, cg3 = coeff['c11b'], coeff['cg1'], coeff['cg2'], coeff['cg3']
        Φ1, Φ2, Φ3, Φ4, Φ5, Φ6 = coeff['Φ1'], coeff['Φ2'], coeff['Φ3'], coeff['Φ4'], coeff['Φ5'], coeff['Φ6']
        cy1, cy2, cy3 = coeff['cγ1'], coeff['cγ1'], 4

        # Extract coefficients for PGAR
        c1_0, c1a_0, c1b_0, c1c_0, c1d_0 = coeff_0['c1'], coeff_0['c1a'], coeff_0['c1b'], coeff_0['c1c'], coeff_0['c1d']
        cn_0, cM_0, c3_0, c5_0, cHM_0 = coeff_0['cn'], coeff_0['cM'], coeff_0['c3'], coeff_0['c5'], coeff_0['cHM']
        c6_0, c7_0, c7b_0, c8_0, c8b_0, c9_0, c9a_0, c9b_0 = coeff_0['c6'], coeff_0['c7'], coeff_0['c7b'], coeff_0['c8'], coeff_0['c8b'], coeff_0['c9'], coeff_0['c9a'], coeff_0['c9b']
        c11b_0, cg1_0, cg2_0, cg3_0 = coeff_0['c11b'], coeff_0['cg1'], coeff_0['cg2'], coeff_0['cg3']
        Φ1_0, Φ2_0, Φ3_0, Φ4_0, Φ5_0, Φ6_0 = coeff_0['Φ1'], coeff_0['Φ2'], coeff_0['Φ3'], coeff_0['Φ4'], coeff_0['Φ5'], coeff_0['Φ6']
        cy1_0, cy2_0, cy3_0 = coeff_0['cγ1'], coeff_0['cγ2'], 4

        # Compute each term for PGAR
        frv_PGA = self._frv(c1_0, Frv, c1a_0, c1c_0, M)
        fnm_PGA = self._fnm(c1b_0, c1d_0, M, Fnm)
        #dztor_PGA = dZtor(c7_0, c7b_0, M, ΔZtor) 
        dip_PGA = self._dip(c11_0, c11b_0, M, delta)
        mag_PGA = self._mag(c2_0, M, c3_0, cn_0, cM_0)
        dist_PGA = self._dist(c4_0, Rrup, c5_0, c6_0, cHM_0, M, c4a_0, cRB_0, cy1_0, cy2_0, cy3_0)
        fhw_PGA = self._fhw(c9_0, Fhw, delta, c9a_0, c9b_0, Rx, Rrup, Rjb, Ztor)
        #basin_PGA = self._basin(Φ5_0, deltaZ1, Φ6_0)

        Yref = np.exp(frv_PGA + fnm_PGA + dip_PGA + mag_PGA + dist_PGA + fhw_PGA)

        # Compute each term for SA
        frv_val = self._frv(c1, Frv, c1a, c1c, M)
        fnm_val = self._fnm(c1b, c1d, M, Fnm)
        #dztor_PGA = dZtor(c7, c7b, M, ΔZtor) 
        dip_val = self._dip(c11, c11b, M, delta)
        mag_val = self._mag(c2, M, c3, cn, cM)
        dist_val = self._dist(c4, Rrup, c5, c6, cHM, M, c4a, cRB, cy1, cy2, cy3)
        fhw_val = self._fhw(c9, Fhw, delta, c9a, c9b, Rx, Rrup, Rjb, Ztor)
        site_val = self._site(Φ1, Φ2, Φ3, Φ1, Vs30, n, Yref)

        return np.exp(frv_val + fnm_val + dip_val + mag_val + dist_val + fhw_val + site_val)
    





