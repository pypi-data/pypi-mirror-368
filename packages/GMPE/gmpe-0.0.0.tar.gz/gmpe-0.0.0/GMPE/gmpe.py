import numpy as np
import pandas as pd

class BCHydroGMPE:
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

class BooreGMPE:
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

gmpe = BCHydroGMPE()
result = gmpe._site('Intraslab', 'Forearc', m=6.5, Rrup=20, Rhypo=20, Vs30=400, Zh=5, T=0)
print(result)  # {'Y': value}





