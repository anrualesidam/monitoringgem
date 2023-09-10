from django.shortcuts import render
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
from tabulate import tabulate
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.utils import ImageReader
from PIL import Image
from io import BytesIO
from colorama import Fore, Style


from pandas.plotting import table
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


class minitoringGem:  

    # CARGA DE ARCHIVOS      

    def cargar_archivo(self,request):
        if request.method == 'POST':
            if 'archivo' not in request.FILES:
                messages.warning(request, 'You must select a file to upload')
                return render(request, 'alert_nofile.html')
            
            else:
                archivo = request.FILES['archivo'] 
                
                extension = self.obtener_extension(archivo.name)

                if extension == '.txt':
                    
                    contenido = archivo.read().decode('utf-8') # leer el contenido del archivo
                    
                    df=self.procesor_data(contenido)
                    request.session['dfdata'] = df.to_dict() 

                    response =self.search_view(request)
                    img_plot = base64.b64encode(response.content).decode("utf-8")
                    
                    #llamar imagenes

                    #imagen_response=self.mostrar_plot(df)

                    #llamar imagen ping
                    img_pings=self.view_image_ping(request)
                    
                    try:
                        imagen_base64ping = base64.b64encode(img_pings.content).decode('utf-8')
                    except:
                        imagen_base64ping = None 

                    context = {
                            'contenido': contenido,
                            'img_plot': img_plot,
                            'imagen_generada': imagen_base64ping,
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
            return render(request, 'cargar_archivo.html')
        
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
    def view_image_ping(self,request):
        df_data = request.session.get('dfdata')
        if df_data is not None:
            try:
                df = pd.DataFrame.from_dict(df_data) 
                processed_image =self.mostrar_ping_all(df)
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
    
    def mostrar_ping_all(self,df):
        
        len_plot=len(df[df["RESULT"]=="FAILED"])
        fig1 = plt.figure(figsize=(20, 4*len_plot),frameon=False)
        fig1.subplots_adjust(hspace=0.5, wspace=0.5)
        j=1

        list_pos=df.POSITION.unique()

        for i in list_pos: 
            
            df_p=df[df["POSITION"]==i]
            prueba=df_p.iloc[0,1]           
            if prueba=="FAILED":
                ax = fig1.add_subplot(len_plot, 1, j)
                vfat=list(df_p.POSITION)[0]
                ax.axis("off")        
                ping_d,imag6=self.img_ping(df_p)
                j=j+1
                
                ax.set_title('{} - SHORT_CIRCUITED:{}'.format(vfat, ping_d), fontsize=32,
                              fontweight="bold", loc='center')
                ax.imshow(imag6)              
            

            else:
                fig1.subplots_adjust(hspace=0.5, wspace=0.5)
                    
        return fig1
        
    # GENERACION DE PLOT VFAT
    def mostrar_plot_all(self,df):
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
        
        return img
    
    #GENERACION DE PDF

    def getpdf(self, request, *args, **kwargs):
        # ... Tu lógica para obtener y generar el PDF ...

        # Llamar a la función para generar el PDF con la imagen
        df_data = request.session.get('dfdata')
        if df_data is not None:
            df = pd.DataFrame.from_dict(df_data) 
            processed_image =self.mostrar_plot_all(df)
            pdf_buffer = self.generate_pdf_with_image(df,processed_image)

            # Devolver el PDF como una respuesta HTTP con el encabezado de descarga
            response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="report.pdf"'
            return response
        
    # CREACION DE PDF
    def generate_pdf_with_image(self,df_r,image):
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

        # ==== DataFrame============
        fig, ax = plt.subplots(figsize=(18, 11))

        # Ocultar ejes en la figura
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
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        c.drawImage(ImageReader(buffer), canvas_height/2-380/2, 400,width=380, height=280) 

        # ==Imagen VFAT
        c.drawImage(img, canvas_height/2-400/2, canvas_height-400, width=img_width, height=img_height)

        c.showPage()
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
        
    


    def generate_pdf(self,request):

        # Crea la parte inicial del reporte
        s= request.GET.get('df')
        parametro1 =re.sub( r'][0-9]+', ']', s).replace("S0","S").replace(" ",":").replace(",:",",")
        parametro1 = np.array(parametro1.split(':'))[np.array(parametro1.split(':'))!='']
        titulos=parametro1[0:4]
        
        data=[[],[],[],[]]

        for i in range(12):
            data[0].append(parametro1[4+4*i])
            data[1].append(parametro1[5+4*i])
            data[2].append(parametro1[6+4*i])
            data[3].append(parametro1[7+4*i])
        dicc={}

        for i in range(len(titulos)):
            dicc[titulos[i]]=data[i]
        
        df = pd.DataFrame(dicc)
        

        # Agregar el título al PDF
        #buffer = BytesIO()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="mi_archivo.pdf"'
        doc = SimpleDocTemplate(response, pagesize=letter)
        
        #title = Paragraph("Reporte de Personas", styles['Heading1'])
        
        
        
            # Agregar el DataFrame a una tabla
            
        df_table = Table([df.columns.to_list()] + df.values.tolist())
        df_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                    ('FONTSIZE', (0, 1), (-1, -1), 8)
                                    ]))
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(name='TitleStyle',
            parent=styles['Title'],
            alignment=TA_CENTER
        )

        elements = []

        estilo_titulo = styles['Heading1']
        estilo_parrafo = styles['Normal']
        titulo = Paragraph("REPORT GE21", title_style)
        #doc.build([titulo])
        elements.append(titulo)

        texto = Paragraph("Este es un ejemplo de texto.", title_style)

        elements.append(texto)

        elements.append(df_table)

        # IMAGEN VFAT

        imagen_bytes=base64.b64decode(self.mostrar_plot(df))


        imagen_pil = PL.Image.open(BytesIO(imagen_bytes))
        imagen_pil = imagen_pil.resize((int(550), int(300)))

        # Convertir la imagen a OpenCV
        imagen_cv2 = cv2.cvtColor(np.array(imagen_pil), cv2.COLOR_RGB2BGR)

        # Guardar la imagen en un archivo temporal
        _, imagen_temp = cv2.imencode(".jpg", imagen_cv2)
        imagen_bytes = imagen_temp.tobytes()

        # Agregar la imagen al contenido del PDF
        imagen = Image(BytesIO(imagen_bytes))
        elements.append(imagen)

        # IMAGEN PINGS

        imagen_bytes_b=base64.b64decode(self.image_ping(df))


        imagen_pil_b = PL.Image.open(BytesIO(imagen_bytes_b))
        imagen_pil_b = imagen_pil_b.resize((int(imagen_pil_b.width /3), int(imagen_pil_b.height/3)))

        # Convertir la imagen a OpenCV
        imagen_cv2_b = cv2.cvtColor(np.array(imagen_pil_b), cv2.COLOR_RGB2BGR)

        # Guardar la imagen en un archivo temporal
        _, imagen_temp_b = cv2.imencode(".jpg", imagen_cv2_b)
        imagen_bytes_b1 = imagen_temp_b.tobytes()

        # Agregar la imagen al contenido del PDF
        imagen_b = Image(BytesIO(imagen_bytes_b1))
        elements.append(imagen_b)



        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        

        doc.build(elements)#[titulo,texto,df_table,imagen_response])

        #imagen

        response.write(buffer.getvalue())
        
        

        return response

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
        data_dicc.append([j[2].upper() for j in data_new])
        data_dicc.append([j[3].replace("\r","").upper().split(",") for j in data_new])

        dicc = {} 
        for i in range(len(titulos)):
            dicc[titulos[i]] = data_dicc[i]
        
        df=pd.DataFrame(dicc)


        return df#,name_board,user_name,fecha


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
    def img_ping(self,df_p):
        ruta_imagen_ping = os.path.join(settings.BASE_DIR, 'viewGem/static/images/Connector_with_border.jpg')
        img3 = cv2.imread(ruta_imagen_ping) 
        img3=cv2.resize(img3, (1552, 355))
        
        ping_d=list(df_p.SHORT_CIRCUITED_CHANNELS)[0]
        confi_pin=self.open_jsonPing()
        try:
            for j in ping_d:
                color = (0, 0, 255)
                img3 = cv2.line(img3, confi_pin[j]["pos"][0], confi_pin[j]["pos"][1], color, confi_pin[j]["thick"])    
        except:
            pass
               
        return ping_d,img3

    def image_ping(self,df):
        len_plot=len(df[df["RESULT"]=="FAILED"])
        fig1 = plt.figure(figsize=(20, 4*len_plot),frameon=False)
        fig1.subplots_adjust(hspace=0.5, wspace=0.5)
        j=1

        list_pos=df.POSITION.unique()

        for i in list_pos:    
            df_p=df[df["POSITION"]==i]
            prueba=df_p.iloc[0,1]
            if prueba=="FAILED":
                ax = fig1.add_subplot(len_plot, 1, j)
                vfat=list(df_p.POSITION)[0]
                ax.axis("off")        
                ping_d,imag6=self.img_ping(df_p)
                j=j+1
                ax.set_title('{} - SHORT_CIRCUITED:{}'.format(vfat,ping_d),fontsize = 32,
                             fontweight="bold")
                ax.imshow(imag6)
                
            

            else:
                pass

        plt.savefig("ping.jpg", bbox_inches='tight',pad_inches = 0.2)


        ruta_imagen_ping_t = os.path.join(settings.BASE_DIR, 'ping.jpg')
        img = cv2.imread(ruta_imagen_ping_t) 
        

        imagen_jpeg1 = cv2.imencode('.jpeg', img)[1].tostring()
        imagen_base64 =base64.b64encode(imagen_jpeg1).decode('utf-8')  
        
        return imagen_base64


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


