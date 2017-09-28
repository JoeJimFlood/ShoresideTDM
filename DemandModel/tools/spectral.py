from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from math import pi, log, exp, factorial as f
from scipy.optimize import *
from scipy.integrate import simps
from scipy.special import i0, i1, iv
import datetime

class fs():
    
    def __init__(self, c):
        self.c = np.array(c)
        self.K = len(c) - 1

    def __len__(self):
        return len(self.c)

    def __getitem__(self, key):
        return self.c[key]

    def __setitem__(self, key, value):
        self.c[key] = value

    def __repr__(self):
        out = '{0} + ({1})cos(x) + ({2})sin(x)'.format(np.real(self.c[0]), 2*np.real(self.c[1]), -2*np.imag(self.c[1]))
        for k in range(2, self.K+1):
            out += ' + ({0})cos({1}x) + ({2})sin({3}x)'.format(2*np.real(self.c[k]), k, -2*np.imag(self.c[k]), k)
        return out

    def __add__(self, other):
        M = len(self)
        N = len(other)
        if N == M:
            return fs(self + other)
        diff = abs(N - M)
        if N > M: #other longer than self
            return fs(np.append(self.c, np.zeros(diff, np.complex)) + other.c)
        else: #Self longer than other
            return fs(self.c + np.append(other.c, np.zeros(diff, np.complex)))

    def __neg__(self):
        return fs(-1*self.c)

    def __sub__(self, other):
        new_c = self.c.copy()
        new_c[0] -= other
        return fs(new_c)

    def __mul__(self, other):
        #import pdb
        #pdb.set_trace()
        return fs(other*self.c)

    def expand(self):
        self.c = np.append(self.c, np.conj(np.fliplr(np.reshape(self.c, (1, self.K+1))[:, 1:])[0]))

    def contract(self):
        self.c = self.c[:self.K+1]

    def power(self, n):

        if n == 0:
            return fs([1])
        
        self.expand()
        result = np.fft.fftshift(self.c)
        coeff = result
        #pdb.set_trace()
        for i in range(1, n):
            result = np.convolve(result, coeff)
        #pdb.set_trace()
        result = np.fft.ifftshift(result)
        K = len(result)//2
        self.contract()
        return fs(result[:K+1])

    def __pow__(self, n):
        return self.power(n)

    def log(self, tol = 2**-11, maxiter = 1000):

        a = 2*abs(self.c).sum()
        P = fs(self.c/a)
        P[0] -= 1

        #print P

        out = fs([0])

        for n in range(1, maxiter):
            change = (P**n)*((-1)**(n+1)/n)
            #print np.linalg.norm(change.c)
            #print max(abs(change.c))/abs(change.c).sum()
            out += change
            if np.linalg.norm(change.c) < tol:            
                break

        out[0] += np.log(a)

        return out
    
    def eval(self, x):
        y = np.real(self.c[0])*np.ones_like(x)
        for k in range(1, self.K+1):
            y += np.real(self.c[k]*np.exp(1j*k*x) + np.conj(self.c[k])*np.exp(-1j*k*x))
        return y

    def plot(self, N = 288, **kwargs):
        x = np.linspace(0, 2*np.pi, N)
        y = self.eval(x)
        plt.plot(x, y, **kwargs)
        #plt.show()

    def adjust_area(self):
        m = moment_calculator(self)
        self[0] -= np.log(np.real(m[0]))

class moment_calculator():

    def __init__(self, fs):

        self.fs = fs

    def __getitem__(self, n):
        assert type(n) == int, 'Moment number must be an integer'
        m = 0
        a = np.real(self.fs[0])
        for i in range(1000):
            try:
                change = 2*pi/f(i)*np.conj(((self.fs)**i)[n])
            except IndexError:
                continue
            m += change
            if abs(change) < 2**-10:
                break
        return m

    def __len__(self):
        amp = []
        for i in range(1000):
            new_amp = abs(self[i])
            if new_amp < 2**-10:
                return len(amp)
            else:
                amp += [new_amp]

    def __repr__(self):
        moments = []
        for i in range(len(self)):
            moments += [self[i]]
        return str(moments)

class Profile():

    def __init__(self, L, total):
        L.adjust_area()
        self.L = L
        self.moments = moment_calculator(L)
        self.total = total
        self.mean = np.angle(self.moments[1]) % 2*pi

        mean_t = 12/pi*self.mean
        #print mean_t
        mean_hr = int(mean_t // 1)
        mean_min = int(60*(mean_t % 1) // 1)
        self.mean_time = datetime.time(mean_hr, mean_min).strftime('%I:%M %p')

        self.var = 1 - abs(self.moments[1])
        self.disp = (1 - abs(self.moments[2]))/(2*abs(self.moments[1])**2)

    def __getitem__(self, key):
        if type(key) == slice:
            if key.step is None:
                return self.count_events(key.start, key.stop)
            else:
                out = []
                t = np.arange(key.start, key.stop + key.step, key.step)
                for i in range(len(t)-1):
                    out.append(self.count_events(t[i], t[i+1]))
                return np.array(out)
        elif key == 'hourly':
            return self[0:24:1]
        elif key == '15min':
            return self[0:24:0.25]
        else:
            raise KeyError('Invalid Profile key')

    @classmethod
    def from_bins(cls, bins, breaks, K):
       
        p = bins / bins.sum()

        L_init = np.zeros(2*K + 1, np.complex)
        L_init[0] = -log(24)

        def realify(array):
            '''
            Converts a Fourier series into an array of the real components, then the imaginary components
            '''
            return np.hstack((np.real(array), np.imag(array)))

        def complexify(array):
            '''
            Inverse of realify
            '''
            N = int(len(array)/2)
            try:
                return array[:N] + 1j*array[N:]
            except TypeError:
                print(N)
                raise Exception

        def contract(array):
            '''
            Returns the zero and positive-indexed Fourier series components
            '''
            N = len(array)
            return array[:int((N+1)/2)]

        def expand(array):
            '''
            Inverse of expand
            '''
            N = len(array)
            array = np.append(array, np.zeros(N-1, array.dtype))
            for i in range(1, N):
                array[-i] = np.conj(array[i])
            return array

        #Initial coefficients
        L_init = realify(contract(L_init))

        def coef_error(coeffs):
            '''
            Returns the error between coefficients of the log-pdf and observed hourly counts
            '''
            
    
            L = expand(complexify(coeffs))

            #Create array of Fourie coefficients to apply the inverse DFT to
            N = 1440
            t = np.linspace(0, 24, N+1)
            l_t = np.zeros(N, np.complex)
            for k in range(K):
                l_t[k] = L[k]
                l_t[-k] = L[-k]

            #Apply the inverse transform to get the log-pdf at each minute
            l = np.real(np.fft.ifft(l_t))*N
    
            #Exponentiate to get the pdf at each minute
            p_fit = np.exp(l)

            #Add point at the end
            p_fit = np.append(p_fit, p_fit[0])

            p_hr = [] #List of fit hourly flows
            #Now, integrate p_fit for each hour of the day
            for hr in range(len(breaks)):
                a = breaks[hr]
                if hr == len(breaks) - 1:
                    b = 24
                else:
                    b = np.array(breaks)[hr+1]
                x = t[int(a*(1440/24)):int(b*(1440/24)+1)]
                y = p_fit[int(a*(1440/24)):int(b*(1440/24)+1)]
                try:
                    p_hr += [simps(y, x)]
                except IndexError:
                    import pdb
                    pdb.set_trace()
                    
            p_hr = np.array(p_hr)

            return np.linalg.norm(p - p_hr) #Return the 2-norm of the error

        res = minimize(coef_error, L_init, method = 'L-BFGS-B') #Find optimal parameters using the linear approximation as an initial guess
        L = res['x']
        L = complexify(L)

        return cls(fs(L), bins.sum())

    def pdf(self, x):
        return (pi/12)*np.exp(self.L.eval(x*pi/12))

    def count_events(self, a, b):
        x = np.arange(a, b + 1/36000, 1/36000)
        y = self.total*self.pdf(x)
        #import pdb
        #pdb.set_trace()
        return simps(y, x)

    def plot(self, N, pdf = True, **kwargs):
        if pdf:
            mult = 1
        else:
            mult = self.total
        x = np.linspace(0, 24, N)
        plt.plot(x, mult*self.pdf(x), **kwargs)