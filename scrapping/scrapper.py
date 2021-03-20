from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# On crée une instance du web-driver Firefox et on va sur la page de eBay.fr
driver = webdriver.Chrome()driver.get("http://www.ebay.fr")
 
# En fonction de notre connection et des performance de notre machine il faudra attendre
 
# que la page charge avant de passer à la suite
sleep(10)

# On recupere la bar de recherche, on la remplit avec "iphone" puis on appuie "Entrez"
search_bar = driver.find_element_by_name("_nkw")
search_bar.send_keys("iphone")
search_bar.send_keys(Keys.ENTER)
