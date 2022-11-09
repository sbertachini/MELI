import requests
from multiprocessing import Pool

url = 'https://6f008c57-99e0-4a2e-8d80-782a71cf99db.mock.pstmn.io'

def func_GetLinea(orden_id):

    url_orden = url + '/orders/' + orden_id
    data = requests.get(url_orden)

    if data.status_code == 200:
        data = data.json()
        #ID Orden
        linea = str(data['id'])

        if (int(orden_id) == int(linea)):

            #Tomo el ID de envio
            idenvio = data['shipping']['id']

            for oi in data['order_items']:
                #ID Item
                linea = linea + ';' + oi['item']['id']
                #Descripción Producto
                linea = linea + ';' + oi['item']['title']

                #Si el Producto tiene variación
                for va in oi['item']['variation_attributes']:
                    linea = linea + ' - ' + va['id'] + ' ' + va['value_name']

            #ID Envio
            linea = linea + ';' + str(idenvio)

            url_envio = url + '/shipments/' + str(idenvio)
            envio = requests.get(url_envio)

            if envio.status_code == 200:
                envio = envio.json()
                #Estado
                linea = linea + ';' + envio['status']
                #SubEstado
                linea = linea + ';' + envio['substatus']
                #Tipo de Logística
                linea = linea + ';' + envio['logistic_type']

                #Destino de envio
                agencia = envio['receiver_address']['agency']

                if agencia == None:
                    #Es Domicilio
                    linea = linea + ';' + 'Domicilio'
                    #Dirección del Receptor
                    linea = linea + ';' + envio['receiver_address']['street_name']
                    linea = linea + ' ' + envio['receiver_address']['street_number']
                    linea = linea + ' ' + envio['receiver_address']['state']['name']
                    linea = linea + ' ' + str(envio['receiver_address']['zip_code'])

                else:
                    #Es Agencia
                    linea = linea + ';' + 'Agencia'
                    #Dirección del Receptor
                    linea = linea + ';' + str(envio['receiver_address']['agency']['agency_id'])
                    linea = linea + ' ' + envio['receiver_address']['agency']['description']
                    linea = linea + ' ' + str(envio['receiver_address']['agency']['carrier_id'])

            else:
                linea = linea + ';No hay datos del Envío.'

        else:
                linea = orden_id + ';El ID de la Orden obtenida no es correcto.'

    return linea


#Programa Principal

#Abro archivo de Salida
arch_salida = open("OrderTrack.csv", "w")

#Imprimo Titulos
header = 'ID Orden;ID Item;Descripción Producto;ID Envio;Estado;SubEstado;Tipo de Logística;Destino de envio;Dirección Receptor\n'
caract_especial = "'"

#Vuelco el contenido del archivo en una lista
with open("Ordenes.txt", "r") as arch_ordenes:
    lista = list(map(str.rstrip, arch_ordenes))

if __name__ == '__main__':
    salida = str(Pool().map(func_GetLinea, lista))
    salida = salida.replace('[', '')
    salida = salida.replace(']', '')
    salida = salida.replace(caract_especial, '')
    salida = salida.replace(', ', '\n')

    salida = header + salida
    print(arch_salida.write(salida))

arch_ordenes.close()
arch_salida.close()
