import os
import time
import shutil
import subprocess
import glob
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# =====================================================================
# 1. CONFIGURACIÓN DINÁMICA DE RUTAS Y PROYECTO GUAJIRA
# =====================================================================
CARPETA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
CARPETA_DOWNLOADS_GENERAL = os.path.join(os.path.expanduser("~"), "Downloads")

URL_SIPREM = "https://sipremsol.co/index.php?opcion=Perfil"
URL_CASUISTICA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQOJkGvpBZwgK7sM6UafZJ5ocYI3lAAF_dUBXwZjXZq-SRB6nvjxLGJpakZq7EBUA/pub?output=csv"

USUARIO_SIPREM = "1082895533"
PASSWORD_SIPREM = "1082895533" 
CODIGO_EMPRESA = "2210"

print(f"📁 Ruta del proyecto activa [GUAJIRA]: {CARPETA_PROYECTO}")

# ---------------------------------------------------------------------
# CREACIÓN AUTOMÁTICA DE README.MD
# ---------------------------------------------------------------------
readme_path = os.path.join(CARPETA_PROYECTO, "README.md")
if not os.path.exists(readme_path):
    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("# Master Dashboard Operativo - DELTEC ING VOA GUAJIRA\n\nRepositorio automatizado de seguimiento de ordenes para Guajira.")
        print("📄 Archivo 'README.md' asegurado.")
    except Exception as e:
        print(f"⚠️ No se pudo generar README.md: {e}")

# ---------------------------------------------------------------------
# GESTIÓN INTELIGENTE DEL TOKEN
# ---------------------------------------------------------------------
def obtener_token_github():
    posibles_tokens = [
        os.path.join(CARPETA_PROYECTO, "Token github.txt"),
        os.path.join(CARPETA_PROYECTO, "github_token.txt")
    ]
    
    token = ""
    for ruta in posibles_tokens:
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                token = f.read().strip()
                if token.startswith("ghp_"):
                    break
            
    if not token or not token.startswith("ghp_"):
        print("\n🔑 CONFIGURACIÓN INICIAL DE GITHUB [GUAJIRA]:")
        token = input("👉 Pega tu Token de GitHub (ghp_...) y presiona ENTER: ").strip()
        archivo_encontrado = os.path.join(CARPETA_PROYECTO, "github_token.txt")
        with open(archivo_encontrado, "w", encoding="utf-8") as f:
            f.write(token)
        print("✅ Token guardado de forma segura.\n")
        
    return token

TOKEN_GITHUB = obtener_token_github()

if TOKEN_GITHUB and TOKEN_GITHUB.startswith("ghp_"):
    URL_REPO_GITHUB = f"https://{TOKEN_GITHUB}@github.com/vikano27-debug/Dashboard_ING_VOA_Guajira.git"
else:
    URL_REPO_GITHUB = "https://github.com/vikano27-debug/Dashboard_ING_VOA_Guajira.git"

# =====================================================================
# 2. CONFIGURACIÓN DE CHROME
# =====================================================================
print("🤖 Iniciando el navegador Chrome [GUAJIRA]...")
opciones = Options()
opciones.add_argument("--incognito")
opciones.add_argument("--start-maximized")
opciones.add_argument("--disable-features=PasswordLeakDetection")

opciones.add_experimental_option("prefs", {
    "download.default_directory": CARPETA_PROYECTO,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

driver = webdriver.Chrome(options=opciones)

driver.execute_cdp_cmd("Page.setDownloadBehavior", {
    "behavior": "allow",
    "downloadPath": CARPETA_PROYECTO
})

acciones = ActionChains(driver)

try:
    # =====================================================================
    # 3. PROCESO DE LOGUEO INFALIBLE
    # =====================================================================
    print("🌐 Entrando a la plataforma de SIPREM...")
    driver.get(URL_SIPREM)
    
    time.sleep(4)
    wait = WebDriverWait(driver, 25)
    
    print("🔑 Ingresando credenciales...")
    input_user = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='username' or @name='usuario' or @placeholder='Usuario']"))) 
    input_pass = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='password' or @name='password' or @placeholder='Contraseña']")))
    input_empresa = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='codempresa' or @name='codempresa' or @placeholder='Codigo Empresa']"))) 
    
    input_user.clear()
    input_user.send_keys(USUARIO_SIPREM)
    
    input_pass.clear()
    input_pass.send_keys(PASSWORD_SIPREM)
    
    input_empresa.clear()
    input_empresa.send_keys(CODIGO_EMPRESA)
    
    print("🚀 Iniciando sesión (Enviando ENTER)...")
    try:
        boton_entrar = driver.find_element(By.XPATH, "//button[contains(text(), 'LOGIN')] | //*[@id='btn-login'] | //button[@type='submit']")
        boton_entrar.click()
    except:
        input_empresa.send_keys(Keys.ENTER)
    
    try:
        boton_si = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/form/div[2]/a[1]")))
        print("⚠️ Sesión previa detectada. Cerrando...")
        boton_si.click()
        time.sleep(4)
    except:
        pass

    time.sleep(6) 

    # =====================================================================
    # 4. NAVEGACIÓN Y DESCARGA (SELECCIÓN EXACTA: DELTEC GUAJ)
    # =====================================================================
    print("🗺️ Seleccionando Territorio: GUAJIRA -> DELTEC GUAJ...")
    
    # 1. Clic en el menú Territorio/Aliado
    menu_territorio = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/ul/li[2]/a/i')))
    menu_territorio.click()
    time.sleep(2)
    
    # 2. Poner el ratón sobre el elemento 'GUAJIRA' para desplegar el submenú
    opcion_guajira = wait.until(EC.presence_of_element_located((By.XPATH, "//b[contains(text(), 'GUAJIRA')] | //a[contains(text(), 'GUAJIRA')]")))
    acciones.move_to_element(opcion_guajira).perform()
    time.sleep(2)
    
    # 3. Hacer clic en el submenú 'DELTEC GUAJ'
    btn_deltec_guaj = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div/ul/li[2]/ul/div[2]/div/li/a | //a[contains(text(), 'DELTEC GUAJ')]")))
    btn_deltec_guaj.click()
    time.sleep(5)

    print("⚙️ Navegando al Centro Tecnico...")
    wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/ul/li[4]/a/i'))).click()
    time.sleep(3)
    wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/ul/li[4]/ul/li[4]/a'))).click()
    time.sleep(5) 

    # Limpiar temporales antiguos
    for ruta_limpia in [CARPETA_PROYECTO, CARPETA_DOWNLOADS_GENERAL]:
        for f in glob.glob(os.path.join(ruta_limpia, "ordenes*.xls*")):
            try:
                os.remove(f)
            except Exception:
                pass

    print("📥 Buscando el botón de descarga Consolidado...")
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="layout"]/div/div/div/div/div[2]/form[1]/div[2]/button[1]'))).click()
    time.sleep(5)
    
    boton_descarga = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="layout"]/div/div/div/div/div[2]/form[1]/div[2]/a')))
    boton_descarga.click()
    
    print("⏳ Esperando la descarga del archivo fresco [GUAJIRA]...")
    
    # Bucle de detección de descarga
    archivo_nuevo = None
    for _ in range(15):
        time.sleep(2)
        candidatos = []
        
        candidatos += [
            f for f in glob.glob(os.path.join(CARPETA_PROYECTO, "*.xls*")) 
            if not f.endswith("siprem_latest.xlsx") 
            and not f.endswith("bdi_latest.xlsx") 
            and not f.endswith(".crdownload")
        ]
        
        candidatos += [
            f for f in glob.glob(os.path.join(CARPETA_DOWNLOADS_GENERAL, "ordenes*.xls*")) 
            if not f.endswith(".crdownload")
        ]
        
        if candidatos:
            archivo_nuevo = max(candidatos, key=os.path.getctime)
            break

    # =====================================================================
    # 5. REEMPLAZO EXACTO DE 'siprem_latest.xlsx'
    # =====================================================================
    if archivo_nuevo and os.path.exists(archivo_nuevo):
        archivo_destino = os.path.join(CARPETA_PROYECTO, "siprem_latest.xlsx")
        shutil.move(archivo_nuevo, archivo_destino)
        print("✅ SIPREM Guajira actualizado exitosamente como 'siprem_latest.xlsx'.")
    else:
        print("⚠️ No se detectó un archivo nuevo descargado.")

except Exception as e:
    print(f"\n❌ ERROR CRÍTICO [GUAJIRA]:\n{e}\n")

finally:
    driver.quit()
    print("🔒 Navegador cerrado correctamente.")

# =====================================================================
# 6. DESCARGA DE CASUÍSTICA (Google Sheets)
# =====================================================================
print("\n📥 Descargando Casuística de Google Sheets...")
try:
    ruta_casuistica = os.path.join(CARPETA_PROYECTO, "casuistica_latest.csv")
    urllib.request.urlretrieve(URL_CASUISTICA, ruta_casuistica)
    print("✅ Casuística guardada en la carpeta del proyecto.")
except Exception as e:
    print(f"⚠️ Error descargando casuística: {e}")

# =====================================================================
# 7. SINCRONIZACIÓN AUTOMÁTICA Y FORZADA A GITHUB GUAJIRA
# =====================================================================
print("\n☁️ Sincronizando repositorio con GitHub [GUAJIRA]...")

gitignore_path = os.path.join(CARPETA_PROYECTO, ".gitignore")
try:
    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write(
            "*\n\n"
            "!README.md\n"
            "!index.html\n"
            "!bdi_latest.xlsx\n"
            "!casuistica_latest.csv\n"
            "!siprem_latest.xlsx\n"
            "!RobotSiprem_Guajira.py\n\n"
            ".gitignore\n"
            "github_token.txt\n"
            "Token github.txt\n"
            "ArrancarRobot_Guajira.bat\n"
            "LanzadorSilencioso_Guajira.vbs\n"
        )
    print("🛡️ Filtro .gitignore asegurado.")
except Exception as e:
    print(f"⚠️ No se pudo actualizar .gitignore: {e}")

git_cmd = shutil.which("git")

if not git_cmd:
    carpetas_escaneo = [
        os.path.join(os.path.expanduser("~"), "Desktop", "Herramientas de desarrollo"),
        os.path.join(os.path.expanduser("~"), "AppData", "Local", "Programs"),
        r"C:\Program Files",
        r"C:\Program Files (x86)"
    ]
    for carpeta in carpetas_escaneo:
        if os.path.exists(carpeta):
            for root, dirs, files in os.walk(carpeta):
                if "git.exe" in files and ("cmd" in root.lower() or "bin" in root.lower()):
                    git_cmd = os.path.join(root, "git.exe")
                    break
            if git_cmd:
                break

if git_cmd:
    try:
        os.chdir(CARPETA_PROYECTO)

        if not os.path.exists(os.path.join(CARPETA_PROYECTO, ".git")):
            subprocess.run([git_cmd, "init"], check=True)

        subprocess.run([git_cmd, "config", "user.name", "vikano27-debug"], check=True)
        subprocess.run([git_cmd, "config", "user.email", "vikano27-debug@users.noreply.github.com"], check=True)

        subprocess.run([git_cmd, "remote", "add", "origin", URL_REPO_GITHUB], check=False)
        subprocess.run([git_cmd, "remote", "set-url", "origin", URL_REPO_GITHUB], check=False)

        subprocess.run([git_cmd, "add", "."], check=True)
        subprocess.run([git_cmd, "commit", "-m", "Actualizacion automatica SIPREM y Casuistica GUAJIRA"], check=False)
        subprocess.run([git_cmd, "branch", "-M", "main"], check=False)

        print("🚀 Subiendo actualizaciones a GitHub Guajira...")
        subprocess.run([git_cmd, "push", "-u", "origin", "main", "--force"], check=True)
        print("\n🔥 ¡MISIÓN CUMPLIDA! GitHub Guajira actualizado al 100%.")

    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error durante la ejecución de Git: {e}")
    except Exception as e:
        print(f"❌ Error durante la subida a GitHub: {e}")