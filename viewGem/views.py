from django.shortcuts import render
from .forms import ArchivoForm
from django.contrib import messages
import os

import pandas as pd
from django.conf import settings
import json
import cv2
import numpy as np
import base64
import matplotlib.pyplot as plt
# Create your views here.



class minitoringGem:        

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
                    contenido2 = archivo.read().decode('utf-8')
                    df=self.procesor_data(contenido)
                    #print(df)
                    
                    
                    #llamar imagenes

                    imagen_response=self.mostrar_plot(df)

                    #llamar imagen ping
                    img_pings=self.image_ping(df)

                    context = {'contenido': contenido,
                               'df': df,
                               'img_path': imagen_response,'img_ping':img_pings}


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
        #print(df)

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
        #print(df_p)
        ping_d=list(df_p.SHORT_CIRCUITED_CHANNELS)[0]
        confi_pin=self.open_jsonPing()
        #print(ping_d)
        #print("ping_d",type(ping_d))
        try:
            for j in ping_d:
                #print("j",j)
                img3 = cv2.line(img3, confi_pin[j]["pos"][0], confi_pin[j]["pos"][1], 255, confi_pin[j]["thick"])    
        except:
            pass
            #print("revisar archivo")    
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
        #print(img)

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


