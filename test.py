import app.saving as saving
import app.scraping as scraping 


scraper = scraping.AlberletHuScraper('https://www.alberlet.hu/kiado_alberlet/ingatlan-tipus:lakas/megye:budapest/keres:normal/limit:24', limit=100)
saver = saving.CSVSaver(scraper)
saver.saveDB()