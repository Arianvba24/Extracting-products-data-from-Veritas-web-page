from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd
import re
import asyncio
from playwright.async_api import async_playwright

def buscar_numero(text):
    # pass
    # return float(re.findall("[0-9]*,[0-9]*",text)[0].replace(",","."))
    if len(text) > 0:
        
        value = re.findall("[0-9]{1,2},[0-9]{1,2}",text)
        
        value1 = value[0].replace(",",".")
        return float(value1)
    else:

        return None



def buscar_segundo_numero(text):
    value = re.findall("[0-9]*,[0-9]*",text)
    if len(value) > 1:
        return float(value[1].replace(",","."))
    else:
        return float(value[0].replace(",","."))

class Spider():
    def __init__(self):
        pass
    
    def from_dataframe_to_data(self,df,extension,adress):
        self.extension = extension
        self.df = df 
        if self.extension == "csv":
            return self.df.to_csv(adress,index = False)
        elif self.extension == "xlsx":
            return self.df.to_excel(adress,index = False)
        elif self.extension == "sql":
            return self.df.to_sql(adress,index = False)
        elif self.extension == "json":
            return self.df.to_json(adress,index = False)
        elif self.extension == "parquet":
            return self.df.to_parquet(adress,index = False)
        
    async def javascript_multidata_extract(self):
        """
        This function executes Javascript function in order to return hidden data usually from
        another webpage with Playwright in JSON format
        """
        
       
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Cargar una página web
            await page.goto(r"https://shop.veritas.es/categorias/frescos/20")

            # Hacer clic en el botón que ejecuta el script de JavaScript------------------------------
            # await page.evaluate("_ProductosFoodPortlet_WAR_comerzziaportletsfood_obtenerMasResultados();")
            while 1:

                await page.evaluate("_ProductosFoodPortlet_WAR_comerzziaportletsfood_obtenerMasResultados();")

                # Esperar a que se complete la ejecución del script (ajusta el tiempo según sea necesario)-----------------------
                await page.wait_for_timeout(800)  # Espera 5 segundos (ajusta el tiempo según sea necesario)
                html = await page.content()
                soup = BeautifulSoup(html, "lxml")
                try:

                    value = soup.find("div", class_="wrap-maspagina max-width-results")
                    if value.a.text == "Ver más resultados":
                        pass

                except:
                    print("except")
                    break
            html = await page.content()

            bs = BeautifulSoup(html,"lxml")
            soup = bs.find_all("div",class_="info-articulo")
#         Loop straight to labels(a,h1,h2,div) or go to the class
#         Defining variables to create the dictionary and afeterwards the dataframe-----------
            title_value = []
            brand_value = []
            price_value = []
            price_kg_value = []
            
            for text in soup:
                title = text.find("p",class_="nombre").text
                brand = text.find("p",class_="marca").text
                
                price = buscar_segundo_numero(text.find("p",class_="precio").text)
                # print(text)
                price_kg = buscar_numero(text.find("div",class_="texto-porKilo").text)
    #             Stablishing dictionary's values for Dataframe-------------------------------
                title_value.append(title)
                brand_value.append(brand)
                price_value.append(price)
                price_kg_value.append(price_kg)
                # print(title_value)
    #         Creating Pandas Dataframe
            await browser.close()
            data = {
                
                "Title" : title_value,
                "Brand" : brand_value,
                "Price" : price_value,
                "Price_kg" : price_kg_value
                
            }

            df = pd.DataFrame(data)
            
            return df
            
               
        asyncio.get_event_loop().run_until_complete(main())
        
    def run_javascript_multidata_extract(self):
        return asyncio.run(self.javascript_multidata_extract())
        



if __name__=="__main__":
    spider = Spider()
    
    df = spider.run_javascript_multidata_extract()
    print(df)


