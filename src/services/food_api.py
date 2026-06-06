import os
import requests
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class FatSecretAPI:
    def __init__(self):
        self.client_id = os.getenv("FATSECRET_CLIENT_ID")
        self.client_secret = os.getenv("FATSECRET_CLIENT_SECRET")
        self.base_url = "https://platform.fatsecret.com/rest/server.api"
        self.token_url = "https://oauth.fatsecret.com/connect/token"
        self._access_token = None
        
        # Sistema de caché local precargado con los 14 alimentos más comunes
        # Esto evita las peticiones externas y da una respuesta instantánea (0ms)
        self._cache_busquedas = {
            "pollo": [
                {"id": "33719", "nombre": "Pechuga de Pollo", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 165kcal | Grasas: 3,57g | Carbohidratos: 0,00g | Proteínas: 31,02g"},
                {"id": "33716", "nombre": "Pollo (Carne Blanca)", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 114kcal | Grasas: 2,52g | Carbohidratos: 0,00g | Proteínas: 21,39g"}
            ],
            "huevo": [
                {"id": "33814", "nombre": "Huevo Entero (Cocido)", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 155kcal | Grasas: 10,61g | Carbohidratos: 1,12g | Proteínas: 12,58g"},
                {"id": "33811", "nombre": "Huevo Frito", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 196kcal | Grasas: 14,84g | Carbohidratos: 0,83g | Proteínas: 13,61g"}
            ],
            "atun": [
                {"id": "35165", "nombre": "Atún en Agua (Enlatado)", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 116kcal | Grasas: 0,82g | Carbohidratos: 0,00g | Proteínas: 25,51g"},
                {"id": "35167", "nombre": "Atún en Aceite (Enlatado)", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 198kcal | Grasas: 8,21g | Carbohidratos: 0,00g | Proteínas: 29,13g"}
            ],
            "carne": [
                {"id": "33664", "nombre": "Carne de Res Molida (Magra)", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 176kcal | Grasas: 8,45g | Carbohidratos: 0,00g | Proteínas: 23,24g"},
                {"id": "33687", "nombre": "Filete de Res (Asado)", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 252kcal | Grasas: 15,10g | Carbohidratos: 0,00g | Proteínas: 27,27g"}
            ],
            "papa": [
                {"id": "39137", "nombre": "Papa Cocida (Sin Piel)", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 87kcal | Grasas: 0,10g | Carbohidratos: 20,13g | Proteínas: 1,87g"},
                {"id": "39144", "nombre": "Papas Fritas", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 312kcal | Grasas: 14,73g | Carbohidratos: 41,44g | Proteínas: 3,43g"}
            ],
            "arroz": [
                {"id": "38766", "nombre": "Arroz Blanco Cocido", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 130kcal | Grasas: 0,28g | Carbohidratos: 28,17g | Proteínas: 2,69g"},
                {"id": "38791", "nombre": "Arroz Integral Cocido", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 112kcal | Grasas: 0,83g | Carbohidratos: 23,51g | Proteínas: 2,32g"}
            ],
            "avena": [
                {"id": "38634", "nombre": "Avena en Hojuelas (Cruda)", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 389kcal | Grasas: 6,90g | Carbohidratos: 66,27g | Proteínas: 16,89g"},
                {"id": "38635", "nombre": "Avena Cocida en Agua", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 62kcal | Grasas: 0,91g | Carbohidratos: 11,54g | Proteínas: 2,47g"}
            ],
            "leche": [
                {"id": "33777", "nombre": "Leche Entera", "marca": "Genérico", "descripcion": "Por 100ml - Calorías: 61kcal | Grasas: 3,25g | Carbohidratos: 4,80g | Proteínas: 3,15g"},
                {"id": "33791", "nombre": "Leche Descremada", "marca": "Genérico", "descripcion": "Por 100ml - Calorías: 34kcal | Grasas: 0,08g | Carbohidratos: 4,96g | Proteínas: 3,37g"}
            ],
            "pan": [
                {"id": "38205", "nombre": "Pan Blanco", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 265kcal | Grasas: 3,20g | Carbohidratos: 49,10g | Proteínas: 9,10g"},
                {"id": "38221", "nombre": "Pan Integral de Trigo", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 247kcal | Grasas: 3,43g | Carbohidratos: 41,30g | Proteínas: 12,96g"}
            ],
            "banano": [
                {"id": "39433", "nombre": "Banano / Plátano", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 89kcal | Grasas: 0,33g | Carbohidratos: 22,84g | Proteínas: 1,09g"}
            ],
            "aguacate": [
                {"id": "39395", "nombre": "Aguacate / Palta", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 160kcal | Grasas: 14,66g | Carbohidratos: 8,53g | Proteínas: 2,00g"}
            ],
            "manzana": [
                {"id": "39402", "nombre": "Manzana (Con Piel)", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 52kcal | Grasas: 0,17g | Carbohidratos: 13,81g | Proteínas: 0,26g"}
            ],
            "ensalada": [
                {"id": "39945", "nombre": "Ensalada Verde Mixta", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 17kcal | Grasas: 0,20g | Carbohidratos: 3,20g | Proteínas: 1,20g"}
            ],
            "lentejas": [
                {"id": "39016", "nombre": "Lentejas Cocidas", "marca": "Genérico", "descripcion": "Por 100g - Calorías: 116kcal | Grasas: 0,38g | Carbohidratos: 20,13g | Proteínas: 9,02g"}
            ]
        }

    def _obtener_token(self):
        if not self.client_id or not self.client_secret:
            print("Error: Falta FATSECRET_CLIENT_ID o FATSECRET_CLIENT_SECRET en el archivo .env")
            return False
        
        try:
            response = requests.post(
                self.token_url,
                auth=(self.client_id, self.client_secret),
                data={"grant_type": "client_credentials", "scope": "basic"},
                timeout=10
            )
            if response.status_code == 200:
                datos = response.json()
                self._access_token = datos.get("access_token")
                return True
            else:
                print(f"Error al obtener Token FatSecret: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Excepción al conectar con el servidor de autenticación: {str(e)}")
            return False

    def buscar_alimento(self, texto_busqueda: str):
        if not self._access_token and not self._obtener_token():
            print("No se pudo obtener el token de acceso.")
            return []

        # Normalizar el texto (quitar espacios, pasar a minúsculas)
        termino_limpio = texto_busqueda.lower().strip()

        # CACHÉ HIT: Si existe en la precarga o búsquedas pasadas, responde INSTANTÁNEO
        if termino_limpio in self._cache_busquedas:
            print(f"Cache Hit: Recuperando resultados instantáneos para '{termino_limpio}'")
            return self._cache_busquedas[termino_limpio]

        try:
            # CACHÉ MISS: Si es un alimento raro, se procesa de forma dinámica
            print(f"Cache Miss: Traduciendo término de búsqueda: '{texto_busqueda}'...")
            termino_en_ingles = GoogleTranslator(source='es', target='en').translate(texto_busqueda)

            headers = {"Authorization": f"Bearer {self._access_token}"}
            params = {
                "method": "foods.search",
                "search_expression": termino_en_ingles,
                "format": "json",
                "max_results": 5
            }

            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 401:
                if self._obtener_token():
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    response = requests.get(self.base_url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                datos = response.json()
                
                if "error" in datos:
                    print(f"Error interno devuelto por la API: {datos['error'].get('message')}")
                    return []
                
                foods_wrapper = datos.get("foods", {})
                if not foods_wrapper or "food" not in foods_wrapper:
                    return []
                
                lista_alimentos = foods_wrapper["food"]
                if isinstance(lista_alimentos, dict):
                    lista_alimentos = [lista_alimentos]
                
                resultados_limpios = []
                for f in lista_alimentos:
                    nombre_en = f.get("food_name", "")
                    desc_en = f.get("food_description", "")
                    
                    try:
                        nombre_es = GoogleTranslator(source='en', target='es').translate(nombre_en)
                        desc_preparada = desc_en.replace("Per", "Por").replace("Calories", "Calorías").replace("Fat", "Grasas").replace("Carbs", "Carbohidratos").replace("Protein", "Proteínas")
                        desc_es = GoogleTranslator(source='en', target='es').translate(desc_preparada)
                    except Exception as trans_err:
                        print(f"Aviso: Falló la traducción. Usando strings originales. ({str(trans_err)})")
                        nombre_es = nombre_en
                        desc_es = desc_en

                    resultados_limpios.append({
                        "id": f.get("food_id"),
                        "nombre": nombre_es,
                        "marca": f.get("brand_name", "Genérico"),
                        "descripcion": desc_es
                    })
                
                # Guardar el alimento recién buscado en caché para optimizar futuras consultas
                self._cache_busquedas[termino_limpio] = resultados_limpios
                return resultados_limpios
            else:
                print(f"Error en respuesta HTTP: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Excepción en buscador FatSecret: {str(e)}")
            return []

    def obtener_macros_alimento(self, food_id: str):
        if not self._access_token and not self._obtener_token():
            return None

        headers = {"Authorization": f"Bearer {self._access_token}"}
        params = {
            "method": "food.get.v2",
            "food_id": food_id,
            "format": "json"
        }

        try:
            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 401:
                if self._obtener_token():
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    response = requests.get(self.base_url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                datos = response.json()
                
                if "error" in datos:
                    print(f"Error al obtener detalle del alimento: {datos['error'].get('message')}")
                    return None
                    
                food_data = datos.get("food", {})
                if not food_data:
                    return None

                servings_wrapper = food_data.get("servings", {})
                serving_list = servings_wrapper.get("serving", [])
                
                if isinstance(serving_list, dict):
                    serving_list = [serving_list]
                
                if not serving_list:
                    return None
                
                s = serving_list[0]
                
                return {
                    "nombre": food_data.get("food_name", "Alimento Desconocido"),
                    "calorias": float(s.get("calories", 0)),
                    "proteinas": float(s.get("protein", 0)),
                    "carbohidratos": float(s.get("carbohydrate", 0)),
                    "grasas": float(s.get("fat", 0)),
                    "porcion_texto": s.get("serving_description", "1 porción")
                }
        except Exception as e:
            print(f"Error procesando macros detallados: {str(e)}")
            return None
        return None