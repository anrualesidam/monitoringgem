from django.shortcuts import render,redirect
from .forms import ArchivoForm
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
import os

import pandas as pd
from django.conf import settings
import json
import string
from django.core.mail import send_mail

# 
# 
import cv2
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import base64
import io
import numpy as np

from reportlab.pdfgen import canvas

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.utils import ImageReader

from PIL import Image, ImageOps
from io import BytesIO
from colorama import Fore, Style
from matplotlib.transforms import Bbox

from pandas.plotting import table

from .models import MiTabla
import datetime


from django.contrib.auth import authenticate, login
# 
# import matplotlib.pyplot as plt
# from .forms import ContactForm
# from django.template.loader import render_to_string
# from django.core.mail import send_mail, BadHeaderError
# from django.shortcuts import redirect
# from django.utils.html import strip_tags

# #emails
# 
# PDF
# import re
# from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Paragraph,Image
# from reportlab.lib.pagesizes import letter
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle 
# from reportlab.lib.enums import TA_CENTER
# import PIL as PL
# from io import BytesIO

class minitoringLogin:
    def login(self, request):
        if request.method == 'POST':

            self.username = request.POST.get('username')

            self.password = request.POST.get('password')

            print(self.username,self.password)

            user = authenticate(
                request, username=self.username.lower(), password=self.password)

            context = {'contenido': self.username.lower()}
            if user is not None:
                login(request, user)
                request.session['minitoring_username'] = self.username.lower()
                return redirect('cargar_archivo')
                #return render(request, 'cargar_archivo.html', context)
            else:
                # messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
                messages.warning(
                    request, 'Incorrect password or user name, please check! ')
                return render(request, 'alert_nofile_login.html')

        return render(request, 'login.html')

class Home:
    def home(self, request):
        return render(request, "home.html")

    def contactin(self, request):
        if request.method == 'POST':
            # form = ContactForm(request.POST)

            name = request.POST['name']
            email = request.POST['email']
            subject = request.POST['subject']
            message = request.POST['message']

            # Crear un objeto MIMEText con el mensaje y el tipo de contenido
            # Send the email
            subject = 'GEM platform support - ' + subject
            from_email = 'alruba40@gmail.com'
            to_email = [email, 'arualesb.1@cern.ch']

            message_with_sender = f"Hello {string.capwords(name)}: \n\n \
                        Thank you very much for contacting us!!. \n\n \
                        We will be contacting you shortly by email {email}  to resolve the concern \n\n \
                        \"{message}\" \n\n Best regards \n Alexis Ruales!!"

            # Send the email
            send_mail(subject, message_with_sender, from_email, to_email)

            messages.success(request, f'We will process the request with the email {email.upper()}, \n\n \
                                    ¿Is that correct?')
            return render(request, "confirmation_send_emailin.html")
        else:
            return render(request, "contactin.html")

class minitoringGem:

    # SEARCH FILES

    def searchfilege21(self,request):
        #query = request.GET.get('query', '')

    # Realiza la búsqueda en la base de datos por columna2
        #resultados = MiTabla.objects.filter(columna2__icontains=query)
        #nuevo_registro = MiTabla(name_rbo="Nombre del registro", info_rbo="Información del registro", fechas="2023-09-17")
        #nuevo_registro.save()

        queryset = MiTabla.objects.using('robdb').all()
        dft = pd.DataFrame(list(queryset.values()))

        list_id=list(dft.name_rbo.unique())

        selected_optiones =list_id[0]
        contenido = dft[dft["name_rbo"]==selected_optiones].tail(1)['info_rbo'].values[0]
        

        df,name_board,user_name,fechab=self.procesor_data(contenido)

        #print("select:",selected_optiones)
        #print("Df select::::",df)
        #print(df)
        request.session['dfdata'] = df.to_dict()
        request.session['name_board'] = name_board
        request.session['user_name'] = user_name
        request.session['fechab'] = fechab

        response =self.search_view(request)
        img_plot = base64.b64encode(response.content).decode("utf-8")
        
        #llamar imagenes

        #imagen_response=self.mostrar_plot(df)

        #llamar imagen ping c
        img_pings_c=self.view_image_ping(request,mode="C")
        
        try:
            imagen_base64ping_c = base64.b64encode(img_pings_c.content).decode('utf-8')
        except:
            imagen_base64ping_c = None 
        
        #llamar imagen ping c
        img_pings_d=self.view_image_ping(request,mode="D")
        
        try:
            imagen_base64ping_d = base64.b64encode(img_pings_d.content).decode('utf-8')
        except:
            imagen_base64ping_d = None

        if request.method == 'POST':
            list_id=list(["None"])+list_id
            selected_optiones = request.POST.get('selected_option')
            contenido = dft[dft["name_rbo"]==selected_optiones].tail(1)['info_rbo'].values[0]
            

            df,name_board,user_name,fechab=self.procesor_data(contenido)

            #print("select:",selected_optiones)
            #print("Df select::::",df)
            #print(df)
            request.session['dfdata'] = df.to_dict()
            request.session['name_board'] = name_board
            request.session['user_name'] = user_name
            request.session['fechab'] = fechab

            response =self.search_view(request)
            img_plot = base64.b64encode(response.content).decode("utf-8")
            
            #llamar imagenes

            #imagen_response=self.mostrar_plot(df)

            #llamar imagen ping c
            img_pings_c=self.view_image_ping(request,mode="C")
            
            try:
                imagen_base64ping_c = base64.b64encode(img_pings_c.content).decode('utf-8')
            except:
                imagen_base64ping_c = None 
            
            #llamar imagen ping c
            img_pings_d=self.view_image_ping(request,mode="D")
            
            try:
                imagen_base64ping_d = base64.b64encode(img_pings_d.content).decode('utf-8')
            except:
                imagen_base64ping_d = None 

        # Convierte los resultados a un formato JSON
        #results_data = [{'columna2': item.columna2} for item in resultados]
        #print(["list_id"])
        return render(request, 'searchfile.html',{'options':list_id,
                                                  'contenido': contenido,
                                                  'img_plot': img_plot,
                                                  'imagen_generada_pingc': imagen_base64ping_c,
                                                  'imagen_generada_pingd': imagen_base64ping_d})
        """
        if request.method == 'POST':
            columna1 = request.POST['columna1']
            columna2 = request.POST['columna2']
            columna3 = request.POST['columna3']

            # Crea un nuevo registro en la base de datos
            mi_registro = MiTabla(columna1=columna1, columna2=columna2, columna3=columna3)
            mi_registro.save()


           # return redirect('formulario_completo')  # Redirige a una página de confirmación o a donde desees

        return render(request, 'searchfile.html')"""
    
    
    
    def uploaddatabase(self,request):
        if request.method == 'POST':
            if 'archivos' not in request.FILES:
                messages.warning(request, 'You must select a file to upload')
                return render(request, 'alert_nofile_db.html')
            
            else:
                archivo = request.FILES['archivos'] 

                #print(archivo)
                
                extension = self.obtener_extension(archivo.name)

                #print("ARCHIVO",archivo,extension)

                if extension == '.txt':
                    
                    contenido = archivo.read().decode('utf-8') # leer el contenido del archivo
                    
                    df,name_board,user_name,fechab=self.procesor_data(contenido)

                    time_data=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    name_boarddb=name_board[:-1].split(":")[1].replace(" ", "").replace("-", "_").replace("-", "_")

                    #print(time_data)
                    #print(name_boarddb)

                    nuevo_registro = MiTabla(name_rbo=name_boarddb, info_rbo=contenido, fechas=time_data)
                    nuevo_registro.save(using='robdb')

                    messages.warning(request, 'Database updated with boar {} on date {}'.format(name_boarddb,time_data))

                    return render(request, 'fileuploaddb.html')
                
                else:
                    messages.warning(request, 'You must load a file with a .txt extension Ex: GE21-RO-M2-0008_20210916_11-02.txt ')
                    return render(request, 'fileuploaddb.html')
        else:
            return render(request, 'searchfile.html')        

        

    # CARGA DE ARCHIVOS      

    def cargar_archivo(self,request):
        context = {'contenido': request.session.get('minitoring_username')}   
        print("aquiiiii",context)     
        if request.method == 'POST':
            if 'archivo' not in request.FILES:
                messages.warning(request, 'You must select a file to upload')
                return render(request, 'alert_nofile.html')
            
            else:
                name_data = request.session.get('minitoring_username')
                archivo = request.FILES['archivo'] 
                
                extension = self.obtener_extension(archivo.name)

                if extension == '.txt':
                    
                    contenido = archivo.read().decode('utf-8') # leer el contenido del archivo
                    
                    df,name_board,user_name,fechab=self.procesor_data(contenido)
                    #print(df)
                    request.session['dfdata'] = df.to_dict()
                    request.session['name_board'] = name_board
                    request.session['user_name'] = user_name
                    request.session['fechab'] = fechab

                    response =self.search_view(request)
                    img_plot = base64.b64encode(response.content).decode("utf-8")
                    
                    #llamar imagenes

                    #imagen_response=self.mostrar_plot(df)

                    #llamar imagen ping c
                    img_pings_c=self.view_image_ping(request,mode="C")
                    
                    try:
                        imagen_base64ping_c = base64.b64encode(img_pings_c.content).decode('utf-8')
                    except:
                        imagen_base64ping_c = None 
                    
                    #llamar imagen ping c
                    img_pings_d=self.view_image_ping(request,mode="D")
                    
                    try:
                        imagen_base64ping_d = base64.b64encode(img_pings_d.content).decode('utf-8')
                    except:
                        imagen_base64ping_d = None 

                    context = {
                            'contenido': contenido,
                            'img_plot': img_plot,
                            'imagen_generada_pingc': imagen_base64ping_c,
                            'imagen_generada_pingd': imagen_base64ping_d,
                        }
                               #'df': df,
                               #'img_path': imagen_response,'img_ping':img_pings}


                    #generate_pdf = reverse("generate_pdf") + f"?df={df}"

                    # Incluir la URL en el contexto que se pasa a la función `render`
                    #context["generate_pdf"] = generate_pdf
                    return render(request, 'archivo_cargado.html', context)
                
                    # hacer algo con el contenido
                else:
                    messages.warning(request, 'You must load a file with a .txt extension Ex: GE21-RO-M2-0008_20210916_11-02.txt ')
                    return render(request, 'alert_nofile.html')
            
        else:
            return render(request, 'cargar_archivo.html',context)
        
    # VISTA DE LOS VFAT
    def search_view(self,request):
        df_data = request.session.get('dfdata')
        if df_data is not None:
            df = pd.DataFrame.from_dict(df_data) 
            processed_image =self.mostrar_plot_all(df)
            # Convertir la figura en bytes usando PIL y base64
            _, buffer = cv2.imencode('.png', processed_image)
            response = HttpResponse(buffer.tobytes(), content_type='image/png')
            return response
        else:
            return HttpResponse("No hay datos para generar la imagen.")
    
    # VISTA DE LOS PING
    def view_image_ping(self,request,mode):
        df_data = request.session.get('dfdata')
        if df_data is not None:
            try:
                df = pd.DataFrame.from_dict(df_data) 
                processed_image =self.mostrar_ping_all(df,mode)
                buf = BytesIO()
                processed_image.canvas.print_png(buf)

                # Obtener el contenido RGBA desde el búfer
                buf.seek(0)
                processed_image = np.array(Image.open(buf), dtype=np.uint8)
                _, buffer = cv2.imencode('.png', processed_image)
                response = HttpResponse(buffer.tobytes(), content_type='image/png')
                return response
            except:
                HttpResponse("No hay datos para generar la imagen.")
        else:
            return HttpResponse("No hay datos para generar la imagen.")
    
    def mostrar_ping_all(self,df,mode,pdf=False): 

        #listadd=df[len(df["DISCONNECTED_CHANNELS"])>0]#.POSITION.unique()

        dfmode=df.copy()
        dfmode['DISCONNECTED_CHANNELS']=dfmode['DISCONNECTED_CHANNELS'].astype(str)
        dfmode['SHORT_CIRCUITED_CHANNELS']=dfmode['SHORT_CIRCUITED_CHANNELS'].astype(str)
        tittle=""
        if mode=="D":
            
            list_pos=dfmode[dfmode['DISCONNECTED_CHANNELS']!= str([""])].POSITION.unique()
            tittle="DISCONNECTED"
        
        if mode=="C":
            
            list_pos=dfmode[dfmode['SHORT_CIRCUITED_CHANNELS']!= str([""])].POSITION.unique()
            tittle="SHORT_CIRCUITED"
        
        len_plot=len(list_pos)
        fig1 = plt.figure(figsize=(20, 4*len_plot),frameon=False)
        fig1.subplots_adjust(hspace=0.5, wspace=0.5)
        j=1

        #list_pos=df.POSITION.unique()
        
        


        for i in list_pos:             
            df_p=df[df["POSITION"]==i]
            prueba=df_p.iloc[0,1]
            if prueba=="FAILED":
                ax = fig1.add_subplot(len_plot, 1, j)
                vfat=list(df_p.POSITION)[0]
                ax.axis("off")        
                ping_d,imag6=self.img_ping(df_p,mode,pdf)
                j=j+1
                
                ax.set_title('{} - {}:{}'.format(vfat,tittle, ping_d), fontsize=32,
                              fontweight="bold", loc='center')
                ax.imshow(imag6)              
            

            else:
                fig1.subplots_adjust(hspace=0.5, wspace=0.5)
        
                    
        return fig1
        
    # GENERACION DE PLOT VFAT
    def mostrar_plot_all(self,df,pdf=False):
        # crear el plot con matplotlib
        confi_vfat=self.open_jsonVfat()
        # convertir el plot en una imagen con OpenCV
        ruta_imagen = os.path.join(settings.BASE_DIR, 'viewGem/static/images/input_2GM2.png')
        img = cv2.imread(ruta_imagen)
        img=cv2.resize(img, (2480,1580))
        list_pos=df.POSITION.unique()

        for i in list_pos:

            df_p=df[df["POSITION"]==i]
            prueba=df_p.iloc[0,1]
            overlay = img.copy()
            pts = np.array(confi_vfat[i], np.int32)          
            
            if prueba=="PASSED":
                cv2.fillPoly(overlay, [pts], (0, 128, 0))
            else:
                if pdf:
                    cv2.fillPoly(overlay, [pts], (255, 0,0))
                else:
                    cv2.fillPoly(overlay, [pts], (0, 0, 255))

            img=cv2.addWeighted(overlay, 0.5, img, 1 - 0.5, 1.0)
        
        return img
    
    #GENERACION DE PDF

    def getpdf(self, request, *args, **kwargs):
        # ... Tu lógica para obtener y generar el PDF ...

        # Llamar a la función para generar el PDF con la imagen
        df_data = request.session.get('dfdata')
        name_board = request.session.get('name_board')
        user_name = request.session.get('user_name')
        fechab = request.session.get('fechab')

        if df_data is not None:
            df = pd.DataFrame.from_dict(df_data) 
            #VFAT
            processed_image =self.mostrar_plot_all(df,pdf=True)

            #PING SHORT
            processed_image_ping_short =self.mostrar_ping_all(df,mode="C",pdf=True)

            es_ceros = any(dim == 0 for dim in processed_image_ping_short.get_size_inches())
            n_images=processed_image_ping_short.get_size_inches()[1]
            

            if es_ceros:
                
                processed_image_ping_short=np.array([], dtype=np.uint8)
            else:
                
                buf = BytesIO()            
                processed_image_ping_short.canvas.print_png(buf)           

               # # Obtener el contenido RGBA desde el búfer
                buf.seek(0)
                processed_image_ping_short = np.array(Image.open(buf), dtype=np.uint8)


            #PING SHORT
            processed_image_ping_disconect =self.mostrar_ping_all(df,mode="D",pdf=True)

            es_cerosd = any(dim == 0 for dim in processed_image_ping_disconect.get_size_inches())
            n_imaged=processed_image_ping_disconect.get_size_inches()[1]
            

            if es_cerosd:
                
                processed_image_ping_disconect=np.array([], dtype=np.uint8)
            else:
                bufd = BytesIO()            
                processed_image_ping_disconect.canvas.print_png(bufd)           

               # # Obtener el contenido RGBA desde el búfer
                bufd.seek(0)
                processed_image_ping_disconect = np.array(Image.open(bufd), dtype=np.uint8)

            

            pdf_buffer = self.generate_pdf_with_image(df,processed_image,
                                                      processed_image_ping_short,n_images,
                                                      processed_image_ping_disconect,n_imaged,
                                                      name_board,user_name,fechab)

            # Devolver el PDF como una respuesta HTTP con el encabezado de descarga
            response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Report_{}.pdf"'.format(name_board[:-1].split(":")[1])
            return response
        
    # CREACION DE PDF
    def generate_pdf_with_image(self,df_r,image,
                                imag_short,n_images,
                                image_ping_disconect,n_imaged,
                                name_board,user_name,fechab):
        # Crear un objeto BytesIO para almacenar el PDF

        
        
        pdf_buffer = BytesIO()

        # Crear el PDF usando ReportLab
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        #c.drawString(100, 750, "Ejemplo de PDF con Imagen")

        #Creacion imagen

        img_width, img_height = Image.fromarray(image).size
        # Calcular la posición para centrar la imagen
        canvas_width, canvas_height = landscape(letter)

        img_width=400
        img_height=300
        x_pos = (canvas_height - img_width) / 2
        y_pos = (canvas_height - img_height) / 2
        
        # Guardar la imagen en un búfer temporal
        # Guardar la imagen en un búfer temporal
        img_temp = BytesIO()
        image_pil = Image.fromarray(image)
        image_pil.save(img_temp, format='PNG')
        img_temp.seek(0)

        # Agregar la imagen al PDF
        img = ImageReader(img_temp)


        #Estruct of PDF
        # ==Titulo
        widtht, heightt = letter

        # Calcular la posición horizontal centrada para el título       
        
        titulo = "REPORT GE21"
        # Obtener el ancho del título formateado        
        titulo_width = c.stringWidth(titulo, "Helvetica-Bold", 24)            

        x = (widtht - titulo_width/2) / 2
        # Agregar el título centrado
        c.drawString(x, 750, titulo)


        # == information board

        c.drawString(canvas_height/2-380/2, 710, name_board[:-1])
        c.drawString(canvas_height/2-380/2, 695, user_name[:-1])
        c.drawString(canvas_height/2-380/2, 680, fechab[:-1])

        # ==== DataFrame============
        fig, ax = plt.subplots(figsize=(18, 11))

        # Ocultar ejes en la figura
        ax.axis('tight')
        ax.axis('off')
       

        # Crear una tabla de Pandas en la figura
        tabla = ax.table(cellText=df_r.values, colLabels=df_r.columns, cellLoc='center', loc='center')

        # Establecer el estilo de la tabla
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(12)

        altura_aumentada = 0.04
        for i, key in enumerate(tabla.get_celld().keys()):
            
            cell = tabla.get_celld()[key]
            if key[0] == 0:  # Fila de encabezado
                cell.set_fontsize(14)  # Ajusta el tamaño de la fuente del encabezado
                cell.set_text_props(weight='bold')
                cell.set_facecolor('#FFFF00')
            
            if key[0]% 2 == 0:
                cell.set_facecolor('#f2f2f2')

            cell.set_height(altura_aumentada)  # Aumenta la altura de la fila
        


        # Cambiar el color de fondo de las filas pares


        # Guardar la figura como una imagen en memoria (BytesIO)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches=Bbox([[2.2, 3.15], [16.3,7.75]]))
        
        buffer.seek(0)
        c.drawImage(ImageReader(buffer), canvas_height/2-380/2, 510,width=380, height=160) 

        # ==Imagen VFAT


        titulovfat = "Read-Out Board (ROB)"
        # Obtener el ancho del título formateado        
        titulo_widthvfat = c.stringWidth(titulovfat, "Helvetica-Bold", 24)            

        xvfat = (widtht - titulo_widthvfat/2) / 2
        # Agregar el título centrado
        c.drawString(xvfat, 480, titulovfat)

        #plot VFAT

        c.drawImage(img, canvas_height/2-400/2, canvas_height-460, width=img_width, height=img_height)

        


        es_ceroshort = all(dim > 0 for dim in imag_short.shape)

        

        if es_ceroshort:
            c.showPage()

            titulo = "VFAT'S - SHORT CIRCUITED CHANNELS"
            # Obtener el ancho del título formateado        
            titulo_width = c.stringWidth(titulo, "Helvetica-Bold", 24)            

            x = (widtht - titulo_width/2) / 2
            # Agregar el título centrado
            c.drawString(x, 740, titulo)



            img_tempshort = BytesIO()
            image_pilshort = Image.fromarray(imag_short)
            
            if image_pilshort.mode == 'RGBA':
                alpha = image_pilshort.split()[3]
                bgmask = alpha.point(lambda x: 255-x)
                image_pilshort = image_pilshort.convert('RGB')
                image_pilshort.paste((255,255,255), None, bgmask)
            
            image_pilshort = image_pilshort.resize((2000, 4800))

            if n_images<12:
                image_pilshort = image_pilshort.crop((500, 0, 2000-450, 4800-300))
            else:
                image_pilshort = image_pilshort.crop((500, 300, 2000-450, 4800-300))

            image_pilshort.save(img_tempshort, format='PNG')
            

            img_tempshort.seek(0)

            # Agregar la imagen al PDF
            imgshort = ImageReader(img_tempshort)
            if n_images<=12:
                widthshort=canvas_height-200
                img_heightshort=150*(n_images/4)
                canvasw=canvas_height-30-img_heightshort/1.3

            else:
                widthshort=canvas_height-200
                img_heightshort=canvas_height
                canvasw=canvas_height-30-img_heightshort/1.3
            
            

            c.drawImage(imgshort, canvas_height/2-widthshort/2,canvasw,width=widthshort, height=img_heightshort)
        
        

        # DESCONECTED
        es_cerodisconected = all(dim > 0 for dim in image_ping_disconect.shape)

        

        if es_cerodisconected:
            c.showPage()

            titulo = "VFAT'S - DISCONNECTED CHANNELS "
            # Obtener el ancho del título formateado        
            titulo_width = c.stringWidth(titulo, "Helvetica-Bold", 24)            

            x = (widtht - titulo_width/2) / 2
            # Agregar el título centrado
            c.drawString(x, 740, titulo)



            img_tempshort = BytesIO()
            image_pilshort = Image.fromarray(image_ping_disconect)
            
            if image_pilshort.mode == 'RGBA':
                alpha = image_pilshort.split()[3]
                bgmask = alpha.point(lambda x: 255-x)
                image_pilshort = image_pilshort.convert('RGB')
                image_pilshort.paste((255,255,255), None, bgmask)
            
            image_pilshort = image_pilshort.resize((2000, 4800))

            

            if n_imaged<12:
                image_pilshort = image_pilshort.crop((500, 0, 2000-450, 4800-300))
            else:
                image_pilshort = image_pilshort.crop((500, 300, 2000-450, 4800-300))

            image_pilshort.save(img_tempshort, format='PNG')

            img_tempshort.seek(0)

            # Agregar la imagen al PDF
            imgshort = ImageReader(img_tempshort)

            if n_imaged<=12:
                widthshort=canvas_height-200
                img_heightshort=150*(n_imaged/4)
                canvasw=canvas_height-30-img_heightshort/1.3

            else:
                widthshort=canvas_height-200
                img_heightshort=canvas_height
                canvasw=canvas_height-30-img_heightshort/1.3
            

            c.drawImage(imgshort, canvas_height/2-widthshort/2,canvasw,width=widthshort, height=img_heightshort)




        c.save()

        # Regresar el objeto BytesIO con el contenido del PDF
        pdf_buffer.seek(0)
        return pdf_buffer
    

        
    
        
    

    def contac(self,request):
        if request.method == 'POST':
                #form = ContactForm(request.POST)

                name = request.POST['name']
                email = request.POST['email'] 
                subject = request.POST['subject']
                message = request.POST['message']
                

                # Crear un objeto MIMEText con el mensaje y el tipo de contenido
                # Send the email
                subject = 'GEM platform support - ' + subject
                from_email = 'alruba40@gmail.com'
                to_email = [email,'arualesb.1@cern.ch']
                
                message_with_sender = f"Hello {string.capwords(name)}: \n\n \
                    Thank you very much for contacting us!!. \n\n \
                    We will be contacting you shortly by email {email}  to resolve the concern \n\n \
                    \"{message}\" \n\n Best regards \n Alexis Ruales!!"

                
                # Send the email
                send_mail(subject,message_with_sender, from_email,to_email)
    
                messages.success(request, f'We will process the request with the email {email.upper()}, \n\n \
                                 ¿Is that correct?')
                return render(request, "confirmation_send_email.html")
        
        else:
            #form = ContactForm()
            #return render(request, "contact.html")

         #       form = ContactForm()
            return render(request, "contact.html")



        #OLD
        
    



    #Procesar la data 

    def procesor_data(self,contenido):
        list_text=contenido.split("\n")
        name_board=list_text[0]
        user_name=list_text[1]
        fecha=list_text[2]
        titulos=list_text[3].upper().replace("-","_").replace(" ","_").replace("\r","").split("\t")
    
        data_new=[j.split("\t") for j in list_text[4:] if j!=""]
        data_dicc=[]
        
        data_dicc.append([j[0].upper() for j in data_new])
        data_dicc.append([j[1].upper() for j in data_new])
        data_dicc.append([j[2].replace("-","").upper().split(",") for j in data_new])
        data_dicc.append([j[3].replace("-","").replace("\r","").upper().split(",") for j in data_new])

        dicc = {} 
        for i in range(len(titulos)):
            dicc[titulos[i]] = data_dicc[i]
        
        df=pd.DataFrame(dicc)


        return df,name_board,user_name,fecha


    #PLOT DE VFAT

    def mostrar_plot(self,df):

        
        # crear el plot con matplotlib
        confi_vfat=self.open_jsonVfat()
        # convertir el plot en una imagen con OpenCV
        ruta_imagen = os.path.join(settings.BASE_DIR, 'viewGem/static/images/input_2GM2.png')
        img = cv2.imread(ruta_imagen)
        img=cv2.resize(img, (2480,1580))
        list_pos=df.POSITION.unique()

        for i in list_pos:

            df_p=df[df["POSITION"]==i]
            prueba=df_p.iloc[0,1]


            overlay = img.copy()
            pts = np.array(confi_vfat[i], np.int32)

            
            
            if prueba=="PASSED":
                cv2.fillPoly(overlay, [pts], (0, 128, 0))
            else:
                cv2.fillPoly(overlay, [pts], (0, 0, 255))

            img=cv2.addWeighted(overlay, 0.5, img, 1 - 0.5, 1.0)

        # enviar la imagen a la plantilla utilizando la función render
        imagen_jpeg = cv2.imencode('.jpeg', img)[1].tostring()
        imagen_base64 = base64.b64encode(imagen_jpeg).decode('utf-8')
        #contexto = {'imagen_base64': imagen_base64}
        return imagen_base64#render(request, 'imagen.html', contexto)

    #IMAGEN DE PINGS
    def img_ping(self,df_p,mode,pdf):
        ruta_imagen_ping = os.path.join(settings.BASE_DIR, 'viewGem/static/images/Connector_with_border.jpg')
        img3 = cv2.imread(ruta_imagen_ping) 
        img3=cv2.resize(img3, (1552, 355))

        if mode=="C":
            ping_d=list(df_p.SHORT_CIRCUITED_CHANNELS)[0]
            colorimage=(0, 255, 255)
            colorpdf=(255, 255, 0)
        if mode=="D":
            ping_d=list(df_p.DISCONNECTED_CHANNELS)[0]
            colorimage=(0, 0, 255)
            colorpdf=(255, 0, 0)


        
        confi_pin=self.open_jsonPing()
        try:
            for j in ping_d:
                if pdf:
                    color = colorpdf
                else:
                    color = colorimage

                img3 = cv2.line(img3, confi_pin[j]["pos"][0], confi_pin[j]["pos"][1], color, confi_pin[j]["thick"])    
        except:
            pass
               
        return ping_d,img3




    def open_jsonVfat(self):
        ruta_configVFAT = os.path.join(settings.BASE_DIR, 'viewGem/static/config/config_VFAT.json')
        confi_vfat= json.load(open(ruta_configVFAT))
        return confi_vfat


    def open_jsonPing(self):
        ruta_configPing = os.path.join(settings.BASE_DIR, 'viewGem/static/config/config_ping.json')
        confi_ping= json.load(open(ruta_configPing))
        return confi_ping

    def obtener_extension(self,nombre_archivo):
        _, ext = os.path.splitext(nombre_archivo)
        return ext.lower()

    #CREAR PDF


