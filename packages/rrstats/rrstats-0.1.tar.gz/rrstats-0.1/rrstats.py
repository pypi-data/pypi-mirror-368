import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math

class StatsQuantiles(list):

    def __init__(self, data):
        super().__init__(sorted(data))
        self.n = len(self)
        self.j_values = np.arange(self.n)+0.5
        self.p_values = self.j_values / self.n
    
    def Qj(self,j):
        """
        j -> x
        Retourne la valeur tel que j valeurs sont en-dessous de cette valeur.
        Ici en-dessous ne signifie pas inférieur, ni égal, mais inférieur avec interpolation
        """
        #print("j =", j)
        i = j+0.5
        if i < 1:
            return self[0] 
        if i > self.n:
            return self[-1]

        i_ent = int(i)
        i_dec = i % 1

        if not i_dec:
            return self[i_ent-1]
        return self[i_ent-1]*(1-i_dec) + self[i_ent]*i_dec
    
    def Qj_c(self,j):
        """
        n-j -> x
        Retourne la valeur tel que j valeurs sont au-dessus de cette valeur.
        """
        return self.Qj(self.n - j)
    
    def Qp(self,p):
        """
        p -> x
        Retourne la valeur tel que p% des valeurs sont en-dessous de cette valeur.
        Ici en-dessous ne signifie pas inférieur, ni égal, mais inférieur avec interpolation
        """
        return self.Qj(p*len(self))
    
    def Qp_c(self,p):
        """
        1-p -> x
        Retourne la valeur tel que p% des valeurs sont au-dessus de cette valeur.
        """
        return self.Qp(1 - p)
    
    def Fj(self,x):
        """
        x -> j
        Retourne le nombre de valeurs en-dessous de x.
        """
        if x in self:
            n_inf = self.index(x)
            n_eq = self.count(x)
            return n_inf + n_eq/2
        else:
            n_inf = 0
            while self[n_inf] < x:
                n_inf += 1
                if n_inf == self.n:
                    return self.n
            if n_inf == 0:
                return 0
            n_dec = (x - self[n_inf-1]) / (self[n_inf] - self[n_inf-1])
            #print(n_dec)
            return n_inf + n_dec - 0.5
        
    def Fj_c(self,x):
        """
        x -> n-j
        Retourne le nombre de valeurs en-dessus de x
        """
        return self.n - self.Fj(x)
    
    def Fp(self,x):
        """
        x -> p
        Retourne le pourcentage de valeurs en-dessous de x.
        """
        return self.Fj(x) / self.n

    def Fp_c(self,x):
        """
        x -> 1-p
        Retourne le pourcentage de valeurs en-dessus de x.
        """
        return 1 - self.Fp(x)
    def Qj_graph(self):
        plt.plot(self.j_values, self)
        plt.show()

    def Qj_c_graph(self):
        plt.plot(self.n - self.j_values, self)
        plt.show()

    def Qp_graph(self):
        plt.plot(self.p_values, self)
        plt.show()

    def Qp_c_graph(self):
        plt.plot(1-self.p_values, self)
        plt.show()

    def Fj_graph(self):
        plt.plot(self, self.j_values)
        plt.show()

    def Fj_c_graph(self):
        plt.plot(self, self.n - self.j_values)
        plt.show()

    def Fp_graph(self):
        plt.plot(self, self.p_values)
        plt.show()

    def Fp_c_graph(self):
        plt.plot(self, 1 - self.p_values)
        plt.show()

class MyRolling:
    def __init__(self,series,window):
        self.data = series.rolling(window)
        self.window = window

    def mean(self):
        return self.data.mean()
    
    def sum(self):
        return self.data.sum()
    
    def trimmed_mean(self,n_trimmed):
        n_trimmed_int = int(n_trimmed)
        n_trimmed_dec = n_trimmed - n_trimmed_int

        def apply_func(values):
            v = values[n_trimmed_int+1:-n_trimmed_int-1]
            up = (sum(v) + (1-n_trimmed_dec)*(values[n_trimmed_int]+values[-n_trimmed_int-1]))
            return up / (self.window - 2 * n_trimmed)
       

        return self.data.apply(apply_func, raw=True)
    
    def trimmed_mean_p(self,p_trimmed,rounded=""):
        n_trimmed = self.window*p_trimmed
        print(n_trimmed)
        if rounded:
            if rounded=="up":
                n_trimmed = math.ceil(n_trimmed)
            elif rounded=="down":
                n_trimmed = math.floor(n_trimmed)
            elif rounded=="closest":
                n_trimmed = round(n_trimmed)
            else:
                raise ValueError(f"Unknown rounded: {rounded!r}")
        print(n_trimmed)
        return self.trimmed_mean(n_trimmed)
class StatsSeries:
    hello="ss"
    def __init__(self, data):
        self.data = pd.Series(data)
        self.quantiles = StatsQuantiles(data)

    def myrolling(self, window):
        rolling = MyRolling(self.data,window)
        return rolling
