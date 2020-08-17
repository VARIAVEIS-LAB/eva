from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from listabomba import *
from inicequip import *

import platform
import ast
import pylab as plt
import numpy as np
import os
import time

RPM = []
Sentido = []
Tempo = []
Volume = []
Vazao = []
Unidade = []
Temperatura = []
Tempo2 = []
Unidade2 = []
UnidadeT = []
UnidadeVa = []
UnidadeVo = []
porta = []
cont = 0
bpresume = False
inresume = False


class Header(BoxLayout):
    pass
  
class Menu(BoxLayout):
    pass

class RootWidget(ScreenManager):
    tempo = ObjectProperty()
    rpm = ObjectProperty()
    tempo2 = ObjectProperty()
    temperatura = ObjectProperty()
    mstemperatura = ObjectProperty()
    msrpm = ObjectProperty()
    selec = NumericProperty(0)
    selec2 = NumericProperty(0)
    graf = StringProperty('')
        
    def orgporta(self):
        sistema = platform.system()
        if sistema == "Windows":
            port='COM'
        else:
            port='/dev/ttyUSB'
        for i in range(1,21):
            porta.append(port + str(i))
        return porta

    def listar(self, R, S, T, U, Selec2):
        if Selec2 == 1:
            RPM.append(float(R))
            Sentido.append(S)
            Tempo.append(float(T))
            Unidade.append(U)
        elif Selec2 == 2:
            Temperatura.append(float(R))
            UnidadeT.append(S)
            Tempo2.append(float(T))
            Unidade2.append(U)
        elif Selec2 == 3:
            Vazao.append(float(R))
            UnidadeVa.append(S)
            Volume.append(float(T))
            UnidadeVo.append(U)

    def limparlistar(self, Selec2):
        if Selec2 == 1:
            global RPM, Sentido, Tempo, Unidade
            RPM = []
            Sentido = []
            Tempo = []
            Unidade = []
        elif Selec2 == 2:
            global Temperatura, UnidadeT, Tempo2, Unidade2
            Temperatura = []
            UnidadeT = []
            Tempo2 = []
            Unidade2 = []
        elif Selec2 == 3:
            global Vazao, UnidadeVa, Volume, UnidadeVo
            Vazao = []
            UnidadeVa = []
            Volume = []
            UnidadeVo = []
            
    def iniciar(self, portabomba, repetir, modelo, modo, Mtubo):
        global bpresume, inresume, funportempo, funportempo2, mqtt, mqtt2
        if bpresume ==False:
            bpresume = True
            if modelo == "Type AK": #"MasterFlex 7550-30":
                sinalSentido = []
                if modo == 1:
                    for i in range(len(Sentido)):
                        if Sentido[i] == "clockwise":
                            sinalSentido.append("+")
                        else:
                            sinalSentido.append("-")
                if modo == 3:
                    tubosdic = {'L/S 13': 0.06, 'L/S 14': 0.22, 'L/S 16': 0.8, 'L/S 25': 1.7, 'L/S 17': 2.8, 'L/S 18': 3.8}
                    for i in range(len(UnidadeVa)):
                        sinalSentido.append("+")
                        Unidade.append("minutes")
                        if UnidadeVa[i] == "mL/min":
                            print ("hey")
                            RPM.append(Vazao[i]/tubosdic[Mtubo])
                            if UnidadeVo[i] == "mL":
                                Tempo.append(Volume[i]/Vazao[i])
                            if UnidadeVo[i] == "L":
                                Tempo.append((Volume[i]*1000)/Vazao[i])
                        if UnidadeVa[i] == "mL/sec":
                            RPM.append((Vazao[i]*60)/tubosdic[Mtubo])
                            if UnidadeVo[i] == "mL":
                                Tempo.append(Volume[i]/(Vazao[i]*60))
                            if UnidadeVo[i] == "L":
                                Tempo.append((Volume[i]*1000)/(Vazao[i]*60))
                funportempo, mqtt = listabomba(portabomba, RPM, Tempo, sinalSentido, Unidade, repetir)
        else:
            funportempo.resume()
        if inresume == False:
            if modelo == "Type RQ": #"Galaxy 170 R":
                TempemC = []
                for i in range(len(UnidadeT)):
                    if UnidadeT[i] == 'Celsius':
                        TempemC.append(Temperatura[i])
                    elif UnidadeT[i] == 'Fahrenheit':
                        FemC = (Temperatura[i]-32)/1.8
                        TempemC.append(FemC)
                funportempo2, mqtt2 = listaincubadora(portabomba,TempemC, Tempo2, Unidade2, repetir)
                inresume = True
        else:
            funportempo2.resume()

    def tempfunc(self, portaagit, modelo2, func, MStemp, MSvel):
        if modelo2 == "Type HC": #"MS7-H550-S":
            ser3 = MS7H550S(portaagit)
            if func == "Start":
                hvel, lvel = divmod(int(MSvel), 256)
                htemp, ltemp = divmod(int(MStemp*10), 256)
                somavel = divmod(hvel + lvel + 177, 256)
                somatemp = divmod(htemp + ltemp + 178, 256)
                ser3.write(serial.to_bytes([0xfe,0xb1,hvel,lvel,0x00,somavel[1]]))
                time.sleep(10)
                ser3.write(serial.to_bytes([0xfe,0xb2,htemp,ltemp,0x00,somatemp[1]]))
                #ser3.close()
            elif func == "Stop":
                #ser3.write(serial.to_bytes([0xfe,0xb1,0x00,0x00,0x00,0xb1]))
                time.sleep(1)
                #ser3.write(serial.to_bytes([0xfe,0xb2,0x00,0x00,0x00,0xb2]))
                #ser3.close()

    def pausar(self, modelo):
        global funportempo, funportempo2
        if modelo == "Type AK":
            funportempo.pause()
        if modelo == "Type RQ":
            funportempo2.pause()

    def parar(self, modelo):
        global bpresume, inresume, funportempo, funportempo2
        if modelo == "Type AK":
            if bpresume == True:
                bpresume = False
                funportempo.stop()
        if modelo == "Type RQ":
            if inresume == True:
                inresume = False
                funportempo2.stop()

    def iniciardata(self, dtlgrtime, dtlgrunit):
        global mqtt, mqtt2
        if dtlgrunit == "minutes":
            dtlgrtime *= 60
        try:
            if mqtt.is_alive() == True:
                mqtt.resume(dtlgrtime)
        except NameError:
            pass
        try:
            if mqtt2.is_alive() == True:
                mqtt2.resume(dtlgrtime)
        except NameError:
            pass

    def parardata(self):
        global mqtt, mqtt2
        try:
            if mqtt.is_alive() == True:
                mqtt.pause()
        except NameError:
            pass
        try:
            if mqtt2.is_alive() == True:
                mqtt2.pause()
        except NameError:
            pass

    def salvar(self, filename, Selec2):
        global cont
        tipo = []
        if filename == "":
            filename = str(cont)
            cont += 1
        if Selec2 == 1:
            tipo = [0]*len(RPM)
            with open ("Documentos\\Peristaltica\\" + filename, "w") as arquivo:
                arquivo.write(str(tipo) + "\n")
                arquivo.write(str(RPM) + "\n")
                arquivo.write(str(Tempo) + "\n")
                arquivo.write(str(Sentido) + "\n")
                arquivo.write(str(Unidade))
        elif Selec2 == 2:
            with open ("Documentos\\Incubadora\\" + filename, "w") as arquivo:
                arquivo.write(str(Temperatura) + "\n")
                arquivo.write(str(UnidadeT) + "\n")
                arquivo.write(str(Tempo2) + "\n")
                arquivo.write(str(Unidade2))
        elif Selec2 == 3:
            tipo = [1]*len(RPM)
            with open ("Documentos\\Peristaltica\\" + filename, "w") as arquivo:
                arquivo.write(str(tipo) + "\n")
                arquivo.write(str(Vazao) + "\n")
                arquivo.write(str(UnidadeVa) + "\n")
                arquivo.write(str(Volume) + "\n")
                arquivo.write(str(UnidadeVo))

    def abrir(self, filename, Selec2): 
        listext = []
        print ("hey")
        if Selec2 == 1 | Selec2 == 3:
            with open (filename[0], "r") as arquivo:
                print(a)
                if ast.literal_eval(arquivo.readline)[1] == "0":
                    print(b)
                    global RPM, Tempo, Sentido, Unidade
                    RPM = ast.literal_eval(arquivo.readline())
                    Tempo = ast.literal_eval(arquivo.readline())
                    Sentido = ast.literal_eval(arquivo.readline())
                    Unidade = ast.literal_eval(arquivo.readline())
                    for i in range(len(RPM)): 
                        listext.append(str(RPM[i]) + " " + Sentido[i] + ", " + str(Tempo[i]) + " " + Unidade[i])
                    print(c)
                    return listext
                elif ast.literal_eval(arquivo.readline)[1] == "1":
                    global Vazao, UnidadeVa, Volume, UnidadeVo
                    Vazao = ast.literal_eval(arquivo.readline())
                    UnidadeVa = ast.literal_eval(arquivo.readline())
                    Volume = ast.literal_eval(arquivo.readline())
                    UnidadeVo = ast.literal_eval(arquivo.readline())
                    for i in range(len(Vazao)):
                        listext.append(str(Vazao[i]) + " " + UnidadeVa[i] + ", "+ str(Volume[i])+ " " + UnidadeVo[i])
        if Selec2 == 2:
            with open (filename[0], "r") as arquivo:
                global Temperatura, UnidadeT, Tempo2, Unidade2
                Temperatura = ast.literal_eval(arquivo.readline())
                UnidadeT = ast.literal_eval(arquivo.readline())
                Tempo2 = ast.literal_eval(arquivo.readline())
                Unidade2 = ast.literal_eval(arquivo.readline())
            for i in range(len(Temperatura)): 
                listext.append(str(Temperatura[i]) + " " + Unidade[i] + " , " + str(Tempo2[i]) + " " + Unidade2[i])
            return listext
            
    def backward(self, express):
        if express:
            return express[:-1]
        else:
            return express

    def calculate(self, express):
        if not express: return ''
        try:
            return str(eval(express))
        except Exception:
            return 'error'
        
    def Test(self,Resultado, Selec):
        try:
            Resultado = float(Resultado)
        except ValueError:
            Resultado = 0
        if Resultado <= 0:
            Resultado = 0
        if Selec == 1:
            if Resultado >= 600:
                Resultado = 600
            self.rpm.text = str(Resultado)
        elif Selec == 2:
            self.tempo.text = str(Resultado)
        elif Selec == 3:
            self.temperatura.text = str(round(Resultado,1))
        elif Selec == 4:
            if Resultado >= 60:
                Resultado = 60
            self.tempo2.text = str(Resultado)
        elif Selec == 5:
            self.rpm.text = str(Resultado)
        elif Selec == 6:
            self.tempo.text = str(Resultado)
        elif Selec == 7:
            if Resultado >=550:
                Resultado = 550
            self.mstemperatura.text = str(round(Resultado,1))
        elif Selec == 8:
            Resultado = int(Resultado)
            if Resultado >= 1500:
                Resultado = 1500
            self.msrpm.text = str(Resultado)

class MainApp(App):
    '''This is the main class of your app.5
       Define any app wide entities here.
       This class can be accessed anywhere inside the kivy app as,
       in python::

         app = App.get_running_app()
         print (app.title)

       in kv language::
    
         on_release: print(app.title)
       Name of the .kv file that is auto-loaded is derived from the name
       of this class::

         MainApp = main.kv
         MainClass = mainclass.kv

       The App part is auto removed and the whole name is lowercased.
    '''
    icon = "Imagens\\Icon.png"
    title = "Eva Cairo"

    def build(self):
        '''Your app will be build from here.
           Return your root widget here.
        '''
        return RootWidget()

    def on_pause(self):
        '''This is necessary to allow your app to be paused on mobile os.
           refer http://kivy.org/docs/api-kivy.app.html#pause-mode .
        '''
        return True
        
if __name__ == '__main__':
    MainApp().run()

